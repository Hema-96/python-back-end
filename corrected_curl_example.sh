#!/bin/bash

# Corrected cURL command for college submission
# This fixes the JSON format issues and enum values

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