from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from typing import List, Dict, Any
from app.core.database import get_session
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/endpoints", tags=["Endpoints"])

@router.get("/list", summary="Get all available endpoints (Admin only)")
async def get_all_endpoints(
    request: Request,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get a comprehensive list of all available endpoints in the system.
    
    **Required Role:** Admin
    
    Returns detailed information about each endpoint including:
    - HTTP method
    - Path
    - Description
    - Authentication requirements
    - Tags/categories
    - Request/response schemas (if available)
    """
    try:
        # Get all routes from the FastAPI app using request.app
        app = request.app
        routes = app.routes
        
        endpoints = []
        
        for route in routes:
            # Skip middleware and other non-endpoint routes
            if not hasattr(route, 'path'):
                continue
                
            # Get route information
            path = route.path
            methods = []
            
            # Extract HTTP methods
            if hasattr(route, 'methods'):
                methods = list(route.methods)
            elif hasattr(route, 'endpoint'):
                # For function-based routes, try to get method from endpoint
                if hasattr(route.endpoint, '__name__'):
                    # This is a simplified approach - in practice, you'd need more complex logic
                    methods = ['GET']  # Default assumption
            
            # Get route tags
            tags = []
            if hasattr(route, 'tags'):
                tags = route.tags or []
            
            # Get route summary/description
            summary = ""
            if hasattr(route, 'summary'):
                summary = route.summary or ""
            elif hasattr(route, 'description'):
                summary = route.description or ""
            
            # Determine authentication requirement
            requires_auth = True  # Default assumption
            if path in ['/docs', '/redoc', '/openapi.json', '/', '/health']:
                requires_auth = False
            elif path.startswith('/api/v1/auth/'):
                # Auth endpoints don't require auth
                requires_auth = False
            elif path.startswith('/api/v1/stages/current') or path.startswith('/api/v1/stages/check-registration'):
                # Public stage endpoints
                requires_auth = False
            
            # Get response model info if available
            response_model = None
            if hasattr(route, 'response_model'):
                response_model = str(route.response_model) if route.response_model else None
            
            # Create endpoint info
            endpoint_info = {
                "path": path,
                "methods": methods,
                "summary": summary,
                "tags": tags,
                "requires_auth": requires_auth,
                "response_model": response_model,
                "full_url": f"http://localhost:8000{path}" if path.startswith('/') else path
            }
            
            endpoints.append(endpoint_info)
        
        # Group endpoints by tags
        grouped_endpoints = {}
        for endpoint in endpoints:
            if endpoint['tags']:
                for tag in endpoint['tags']:
                    if tag not in grouped_endpoints:
                        grouped_endpoints[tag] = []
                    grouped_endpoints[tag].append(endpoint)
            else:
                if 'Uncategorized' not in grouped_endpoints:
                    grouped_endpoints['Uncategorized'] = []
                grouped_endpoints['Uncategorized'].append(endpoint)
        
        # Create comprehensive response
        response = {
            "message": "All endpoints retrieved successfully",
            "total_endpoints": len(endpoints),
            "grouped_by_tags": grouped_endpoints,
            "flat_list": endpoints,
            "statistics": {
                "total_endpoints": len(endpoints),
                "authenticated_endpoints": len([e for e in endpoints if e['requires_auth']]),
                "public_endpoints": len([e for e in endpoints if not e['requires_auth']]),
                "tags_count": len(grouped_endpoints),
                "methods_distribution": {}
            }
        }
        
        # Calculate method distribution
        method_counts = {}
        for endpoint in endpoints:
            for method in endpoint['methods']:
                method_counts[method] = method_counts.get(method, 0) + 1
        response['statistics']['methods_distribution'] = method_counts
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving endpoints: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving endpoints: {str(e)}"
        )

@router.get("/auth-required", summary="Get endpoints that require authentication (Admin only)")
async def get_auth_required_endpoints(
    request: Request,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get list of endpoints that require authentication.
    
    **Required Role:** Admin
    """
    try:
        # Get all endpoints first
        all_endpoints_response = await get_all_endpoints(request, current_user, session)
        all_endpoints = all_endpoints_response['flat_list']
        
        # Filter for authenticated endpoints
        auth_endpoints = [ep for ep in all_endpoints if ep['requires_auth']]
        
        return {
            "message": "Authenticated endpoints retrieved successfully",
            "total_authenticated_endpoints": len(auth_endpoints),
            "endpoints": auth_endpoints
        }
        
    except Exception as e:
        logger.error(f"Error retrieving authenticated endpoints: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving authenticated endpoints: {str(e)}"
        )

@router.get("/public", summary="Get public endpoints (Admin only)")
async def get_public_endpoints(
    request: Request,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get list of public endpoints that don't require authentication.
    
    **Required Role:** Admin
    """
    try:
        # Get all endpoints first
        all_endpoints_response = await get_all_endpoints(request, current_user, session)
        all_endpoints = all_endpoints_response['flat_list']
        
        # Filter for public endpoints
        public_endpoints = [ep for ep in all_endpoints if not ep['requires_auth']]
        
        return {
            "message": "Public endpoints retrieved successfully",
            "total_public_endpoints": len(public_endpoints),
            "endpoints": public_endpoints
        }
        
    except Exception as e:
        logger.error(f"Error retrieving public endpoints: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving public endpoints: {str(e)}"
        )

@router.get("/by-tag/{tag}", summary="Get endpoints by tag (Admin only)")
async def get_endpoints_by_tag(
    tag: str,
    request: Request,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get all endpoints grouped under a specific tag.
    
    **Required Role:** Admin
    
    **Parameters:**
    - tag: The tag to filter by (e.g., 'Authentication', 'Users', 'Colleges')
    """
    try:
        # Get all endpoints first
        all_endpoints_response = await get_all_endpoints(request, current_user, session)
        grouped_endpoints = all_endpoints_response['grouped_by_tags']
        
        # Get endpoints for the specified tag
        tag_endpoints = grouped_endpoints.get(tag, [])
        
        return {
            "message": f"Endpoints for tag '{tag}' retrieved successfully",
            "tag": tag,
            "total_endpoints": len(tag_endpoints),
            "endpoints": tag_endpoints
        }
        
    except Exception as e:
        logger.error(f"Error retrieving endpoints by tag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving endpoints by tag: {str(e)}"
        )

@router.get("/tags", summary="Get all available tags (Admin only)")
async def get_all_tags(
    request: Request,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get list of all available tags in the system.
    
    **Required Role:** Admin
    """
    try:
        # Get all endpoints first
        all_endpoints_response = await get_all_endpoints(request, current_user, session)
        grouped_endpoints = all_endpoints_response['grouped_by_tags']
        
        # Extract tags and their endpoint counts
        tags_info = []
        for tag, endpoints in grouped_endpoints.items():
            tags_info.append({
                "tag": tag,
                "endpoint_count": len(endpoints),
                "endpoints": [ep['path'] for ep in endpoints]
            })
        
        return {
            "message": "All tags retrieved successfully",
            "total_tags": len(tags_info),
            "tags": tags_info
        }
        
    except Exception as e:
        logger.error(f"Error retrieving tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tags: {str(e)}"
        )

@router.get("/search", summary="Search endpoints (Admin only)")
async def search_endpoints(
    query: str,
    request: Request,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Search endpoints by path, summary, or tags.
    
    **Required Role:** Admin
    
    **Query Parameters:**
    - query: Search term to look for in endpoint paths, summaries, or tags
    """
    try:
        # Get all endpoints first
        all_endpoints_response = await get_all_endpoints(request, current_user, session)
        all_endpoints = all_endpoints_response['flat_list']
        
        # Search in endpoints
        search_results = []
        query_lower = query.lower()
        
        for endpoint in all_endpoints:
            # Search in path
            if query_lower in endpoint['path'].lower():
                search_results.append(endpoint)
                continue
            
            # Search in summary
            if endpoint['summary'] and query_lower in endpoint['summary'].lower():
                search_results.append(endpoint)
                continue
            
            # Search in tags
            for tag in endpoint['tags']:
                if query_lower in tag.lower():
                    search_results.append(endpoint)
                    break
        
        return {
            "message": f"Search results for '{query}'",
            "query": query,
            "total_results": len(search_results),
            "results": search_results
        }
        
    except Exception as e:
        logger.error(f"Error searching endpoints: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching endpoints: {str(e)}"
        )
