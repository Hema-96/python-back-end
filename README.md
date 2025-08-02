# Tamil Nadu Engineering College Counselling Backend

A comprehensive backend system for Tamil Nadu Engineering College Counselling with role-based authentication and college data management.

## 🏗️ Project Structure

```
python-back-end/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── users.py         # User management endpoints
│   │       ├── colleges.py      # College data submission endpoints
│   │       └── router.py        # API router
│   ├── core/
│   │   ├── config.py           # Application settings
│   │   ├── database.py         # Database configuration
│   │   └── security.py         # JWT and password utilities
│   ├── middleware/
│   │   └── auth.py             # Authentication middleware
│   ├── models/
│   │   ├── user.py             # User and profile models
│   │   ├── college.py          # College data models
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py             # Authentication schemas
│   │   ├── user.py             # User profile schemas
│   │   ├── college.py          # College data schemas
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py     # Authentication business logic
│   │   └── college_service.py  # College data business logic
│   ├── utils/
│   │   └── helpers.py          # Utility functions
│   └── main.py                 # FastAPI application
├── requirements.txt
└── README.md
```

## 🚀 Features

### 🔐 Authentication System
- **JWT Token Authentication** with access and refresh tokens
- **Role-Based Access Control** with three user roles:
  - **Admin (1)**: System administrators
  - **College Admin (2)**: College administrators
  - **Student (3)**: Students
- **Password Security** with bcrypt hashing
- **Token Refresh** mechanism

### 🏫 College Data Management
- **Comprehensive College Data Submission** with detailed information
- **Admin Verification System** for college approvals
- **Seat Matrix Management** with category-wise seat allocation
- **Document Management** for college certificates and approvals
- **Bank Details Management** for payment processing

## 📊 Database Schema

### User Management
- **User**: Basic user information and authentication
- **AdminProfile**: Admin-specific profile data
- **CollegeProfile**: College admin profile data
- **StudentProfile**: Student-specific profile data

### College Data
- **College**: Basic college information
- **CollegePrincipal**: Principal details
- **CollegeSeatMatrix**: Course-wise seat allocation
- **CollegeFacilities**: Available facilities
- **CollegeDocuments**: Required documents
- **CollegeBankDetails**: Bank account information
- **CollegeVerificationStatus**: Admin verification status

## 🔧 Installation

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
   Create a `.env` file with:
   ```env
   DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "college@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": 2
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "college@example.com",
  "password": "password123"
}
```

### College Data Submission

#### Submit College Data
```http
POST /api/v1/colleges/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "college": {
    "college_code": "ABC123",
    "name": "ABC Engineering College",
    "short_name": "ABC",
    "type": "Private",
    "university_affiliation": "Anna University",
    "year_established": 1999,
    "naac_grade": "A",
    "nba_status": true,
    "aicte_approved": true,
    "counselling_type": "UG",
    "address": {
      "line1": "123 Main Rd",
      "line2": "Near Bus Stand",
      "city": "Chennai",
      "district": "Chennai",
      "state": "Tamil Nadu",
      "pincode": "600001"
    },
    "contact": {
      "phone": "044-1234567",
      "mobile": "9876543210",
      "email": "admin@abcengg.edu.in",
      "website": "https://abcengg.edu.in"
    },
    "logo_url": "https://cdn.site.com/logos/abc_logo.png"
  },
  "principal": {
    "name": "Dr. Raj Kumar",
    "designation": "Principal",
    "phone": "9876543211",
    "email": "principal@abcengg.edu.in",
    "id_proof_url": "https://cdn.site.com/docs/principal_id.png"
  },
  "seat_matrix": [
    {
      "course_name": "Computer Science and Engineering",
      "intake_capacity": 120,
      "general_seats": 60,
      "sc_seats": 20,
      "st_seats": 10,
      "obc_seats": 25,
      "minority_seats": 5
    }
  ],
  "facilities": {
    "hostel_available": true,
    "transport_available": true,
    "wifi_available": true,
    "lab_facilities": "CSE, ECE, Mechanical, Civil",
    "placement_cell": true
  },
  "documents": [
    {
      "doc_type": "AICTE Approval",
      "doc_url": "https://cdn.site.com/docs/aicte.pdf"
    },
    {
      "doc_type": "Affiliation Certificate",
      "doc_url": "https://cdn.site.com/docs/affiliation.pdf"
    }
  ],
  "bank_details": {
    "bank_name": "State Bank of India",
    "branch": "Anna Nagar",
    "account_number": "123456789012",
    "ifsc_code": "SBIN0001234",
    "upi_id": "abcengg@upi",
    "cancelled_cheque_url": "https://cdn.site.com/docs/cheque.png"
  }
}
```

#### Get My College Data
```http
GET /api/v1/colleges/my-college
Authorization: Bearer <token>
```

### Admin Endpoints

#### Get All Colleges
```http
GET /api/v1/colleges/all?skip=0&limit=20&status=pending
Authorization: Bearer <admin_token>
```

#### Get Pending Colleges
```http
GET /api/v1/colleges/pending?skip=0&limit=20
Authorization: Bearer <admin_token>
```

#### Verify College
```http
POST /api/v1/colleges/{college_id}/verify?is_approved=true&notes=All documents verified
Authorization: Bearer <admin_token>
```

#### Get College Details
```http
GET /api/v1/colleges/{college_id}
Authorization: Bearer <admin_token>
```

### Public Endpoints

#### Get Approved Colleges
```http
GET /api/v1/colleges/approved?skip=0&limit=20
```

## 🔐 Default Admin Credentials

- **Email**: `admin@tncounselling.com`
- **Password**: `admin123`

## 📋 Role Permissions

### Admin (Role: 1)
- ✅ View all colleges
- ✅ Verify/reject college submissions
- ✅ Manage all users
- ✅ Access admin dashboard

### College Admin (Role: 2)
- ✅ Submit college data
- ✅ View own college data
- ✅ Update college information
- ❌ Cannot verify other colleges

### Student (Role: 3)
- ✅ View approved colleges
- ✅ Access student dashboard
- ❌ Cannot submit college data

## 🛠️ Development

### Database Migrations
The application automatically creates and manages database tables. To reset the database:

```python
# In app/core/database.py
def create_db_and_tables():
    drop_all_tables()  # This will drop all tables
    SQLModel.metadata.create_all(engine)  # This will recreate them
```

### Adding New Features
1. Create models in `app/models/`
2. Create schemas in `app/schemas/`
3. Create services in `app/services/`
4. Create API endpoints in `app/api/v1/`
5. Update router in `app/api/v1/router.py`

## 📝 API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚀 Deployment

### Environment Variables
```env
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=False
ENVIRONMENT=production
```

### Production Settings
- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Configure proper `DATABASE_URL`
- Set up proper CORS origins

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please contact the development team or create an issue in the repository.

