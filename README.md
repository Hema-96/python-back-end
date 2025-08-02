# Tamil Nadu Engineering College Counselling Backend

A professional FastAPI backend for the Tamil Nadu Engineering College Counselling system with role-based authentication and comprehensive user management.

## Features

- **Role-based Authentication**: Admin, College, and Student roles
- **JWT Token Authentication**: Secure access and refresh tokens
- **Comprehensive User Management**: Profile creation and management for each role
- **College Approval System**: Admin can approve college registrations
- **Professional API Structure**: Well-organized, maintainable codebase
- **Database Integration**: PostgreSQL with SQLModel ORM
- **Input Validation**: Comprehensive data validation and sanitization
- **Error Handling**: Professional error handling and logging

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── auth.py          # Authentication endpoints
│       ├── users.py         # User management endpoints
│       ├── router.py        # Main API router
│       └── __init__.py
├── core/
│   ├── config.py           # Application configuration
│   ├── database.py         # Database configuration
│   └── security.py         # Security utilities
├── models/
│   ├── user.py             # User models
│   └── __init__.py
├── schemas/
│   ├── auth.py             # Authentication schemas
│   ├── user.py             # User schemas
│   └── __init__.py
├── services/
│   └── auth_service.py     # Authentication business logic
├── middleware/
│   └── auth.py             # Authentication middleware
├── utils/
│   ├── helpers.py          # Utility functions
│   └── __init__.py
├── tests/                  # Test files
├── docs/                   # Documentation
└── main.py                 # Application entry point
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd python-back-end
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   DEBUG=True
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/password-reset` - Request password reset
- `POST /api/v1/auth/password-change` - Change password

### User Management
- `POST /api/v1/users/admin/profile` - Create admin profile
- `POST /api/v1/users/college/profile` - Create college profile
- `POST /api/v1/users/student/profile` - Create student profile
- `GET /api/v1/users/admin/profile` - Get admin profile
- `GET /api/v1/users/college/profile` - Get college profile
- `GET /api/v1/users/student/profile` - Get student profile
- `GET /api/v1/users/all` - Get all users (admin only)
- `GET /api/v1/users/colleges` - Get all colleges (admin only)
- `PUT /api/v1/users/college/{id}/approve` - Approve college (admin only)
- `PUT /api/v1/users/profile` - Update user profile
- `DELETE /api/v1/users/{id}` - Delete user (admin only)

## User Roles

### Admin
- Full system access
- Can approve college registrations
- Can manage all users
- Can view all data

### College
- Can create and manage college profile
- Can view approved status
- Limited access to other data

### Student
- Can create and manage student profile
- Can view personal information
- Limited access to other data

## Database Models

### User
- Basic user information
- Role-based access control
- Authentication fields

### AdminProfile
- Admin-specific information
- Department and permissions

### CollegeProfile
- College information
- Approval status
- Contact details

### StudentProfile
- Student personal information
- Academic details
- Document references

## Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Tokens**: Secure authentication with access and refresh tokens
- **Role-based Access**: Fine-grained permission control
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error responses

## Development

### Running Tests
```bash
# Add test files to app/tests/
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## Deployment

1. **Set production environment variables**
2. **Configure database connection**
3. **Set up logging**
4. **Deploy using your preferred method**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

