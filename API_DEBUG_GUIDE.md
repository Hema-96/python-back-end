# API Debug Guide - College Submission

## 🔍 **Issues Found in Your cURL Request**

### 1. **Invalid JSON Format for `seat_matrix`**
❌ **Your request:**
```bash
-F 'seat_matrix={ "User": { "id": "number", "name": "string" } }'
```

✅ **Correct format:**
```bash
-F 'seat_matrix=[{"course_name":"Computer Science Engineering","intake_capacity":60,"general_seats":30,"sc_seats":9,"st_seats":5,"obc_seats":16,"minority_seats":0}]'
```

### 2. **Invalid JSON Format for `document_types`**
❌ **Your request:**
```bash
-F 'document_types=[1]'
```

✅ **Correct format:**
```bash
-F 'document_types=["AICTE Approval Certificate","NAAC Certificate","University Affiliation Certificate"]'
```

### 3. **Invalid Enum Value for `type`**
❌ **Your request:**
```bash
-F 'type=Private'
```

✅ **Correct format:**
```bash
-F 'type=Private'
```
*Note: This is actually correct, but the API now validates enum values properly*

## 🛠️ **Fixes Applied**

### 1. **Improved Error Handling**
- Added detailed validation for JSON formats
- Added enum value validation
- Added seat matrix field validation
- Better error messages with specific details

### 2. **Enhanced Validation**
- Validates that `seat_matrix` is a JSON array
- Validates that `document_types` is a JSON array
- Validates required fields in seat matrix data
- Validates enum values for `type` and `counselling_type`

### 3. **Better Error Messages**
- Specific JSON format errors
- Enum value validation errors
- Field validation errors
- File count validation errors

## 📝 **Corrected cURL Command**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/colleges/submit' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'Content-Type: multipart/form-data' \
  -F 'college_code=TEST001' \
  -F 'name=Test Engineering College' \
  -F 'short_name=TEC' \
  -F 'type=Private' \
  -F 'university_affiliation=Anna University' \
  -F 'year_established=2020' \
  -F 'naac_grade=A' \
  -F 'nba_status=false' \
  -F 'aicte_approved=false' \
  -F 'counselling_type=UG' \
  -F 'address_line1=123 Test Street' \
  -F 'address_line2=Test Area' \
  -F 'city=Chennai' \
  -F 'district=Chennai' \
  -F 'state=Tamil Nadu' \
  -F 'pincode=600001' \
  -F 'phone=0441234567' \
  -F 'mobile=9876543210' \
  -F 'email=test@college.com' \
  -F 'website=https://testcollege.com' \
  -F 'principal_name=Dr. Test Principal' \
  -F 'principal_designation=Principal' \
  -F 'principal_phone=0441234568' \
  -F 'principal_email=principal@testcollege.com' \
  -F 'seat_matrix=[{"course_name":"Computer Science Engineering","intake_capacity":60,"general_seats":30,"sc_seats":9,"st_seats":5,"obc_seats":16,"minority_seats":0}]' \
  -F 'hostel_available=false' \
  -F 'transport_available=false' \
  -F 'wifi_available=false' \
  -F 'lab_facilities=Computer labs, Electronics labs' \
  -F 'placement_cell=false' \
  -F 'bank_name=Test Bank' \
  -F 'branch=Chennai Main' \
  -F 'account_number=1234567890' \
  -F 'ifsc_code=TEST0001234' \
  -F 'upi_id=testcollege@testbank' \
  -F 'document_types=["AICTE Approval Certificate","NAAC Certificate","University Affiliation Certificate"]' \
  -F 'logo_file=@logo.png' \
  -F 'principal_id_proof_file=@id_proof.pdf' \
  -F 'cancelled_cheque_file=@cheque.pdf' \
  -F 'document_files=@aicte_cert.pdf' \
  -F 'document_files=@naac_cert.pdf' \
  -F 'document_files=@affiliation_cert.pdf'
```

## 🧪 **Testing Tools**

### 1. **Debug Script**
Run the debug script to test the API:
```bash
python test_api_debug.py
```

### 2. **Corrected cURL Script**
Use the corrected cURL script:
```bash
bash corrected_curl_example.sh
```

## 📊 **Valid Enum Values**

### College Types
- `Private`
- `Government`
- `Aided`
- `Self Financing`

### Counselling Types
- `UG`
- `PG`
- `Diploma`

## 🔧 **Required Seat Matrix Fields**

Each seat matrix item must contain:
- `course_name`
- `intake_capacity`
- `general_seats`
- `sc_seats`
- `st_seats`
- `obc_seats`
- `minority_seats`

## 📁 **File Requirements**

- **Logo file**: Optional, image format
- **Principal ID proof**: Optional, document format
- **Cancelled cheque**: Optional, document format
- **Document files**: Required, must match number of document types

## 🚀 **Next Steps**

1. **Test with the debug script** to see detailed error messages
2. **Use the corrected cURL command** with proper JSON formatting
3. **Check the server logs** for detailed error information
4. **Verify your token** is valid and has college admin permissions

The API should now provide much better error messages to help you identify and fix any remaining issues! 