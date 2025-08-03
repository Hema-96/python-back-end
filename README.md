# Tamil Nadu Engineering College Counselling Backend API

A comprehensive FastAPI backend for managing engineering college counselling in Tamil Nadu.

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
- **File Upload Support** with Supabase storage integration

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

5. **Start the server**
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
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "9876543210",
  "role": 2
}
```

#### Login User
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "college@example.com",
  "password": "securepassword123"
}
```

### College Data Endpoints

#### Submit College Data (with File Uploads)
```http
POST /api/v1/colleges/submit
Content-Type: multipart/form-data

# Form fields for college data
# File uploads for documents, logos, etc.
```

For detailed file upload documentation, see [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md)

## 🗄️ Database Management

### Database Persistence
The database now **persists data between application restarts**. The application will:
- Create tables if they don't exist
- Preserve existing data
- Only initialize default admin user if not present

### Manual Database Reset
If you need to reset the database (clear all data), use the reset script:

```bash
python reset_db.py
```

⚠️ **Warning**: This will delete ALL data in the database!

### Database Migrations
The application automatically creates and manages database tables. To reset the database:

```python
# In app/core/database.py
def reset_database():
    drop_all_tables()  # This will drop all tables
    create_db_and_tables()  # This will recreate them
    init_db()  # This will add default data
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

## 📁 File Upload System

### Supabase Storage
Files are automatically uploaded to Supabase storage with the following features:
- **Secure storage** in Supabase cloud
- **Public URLs** for file access
- **Unique filenames** with UUID to prevent conflicts
- **File validation** for type and size
- **Automatic organization** by file type

### File Types Supported
- **Images**: JPEG, PNG, GIF
- **Documents**: PDF, DOC, DOCX
- **Maximum size**: 10MB per file

### Testing File Upload
```bash
# Test Supabase upload
python test_supabase_upload.py

# Test with cURL
bash corrected_curl_example.sh
```

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
- Supabase storage is already configured

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

