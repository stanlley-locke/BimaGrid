import django
django.setup()
from django.test.client import Client
import json

c = Client(HTTP_HOST='localhost:8000')
# 1. Register
reg_res = c.post('/api/v1/accounts/register/', {
    "username": "test_user_quote",
    "email": "test_user_quote@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "Farmer",
    "phone": "+254712345678"
}, content_type="application/json")
print("Reg:", reg_res.status_code)

# 2. Login
log_res = c.post('/api/v1/accounts/login/', {
    "username": "test_user_quote",
    "password": "password123"
}, content_type="application/json")
print("Login:", log_res.status_code)
token = log_res.json().get('token')

# 3. Quote
quote_res = c.post('/api/v1/pricing/quote/', {
    "crop": "MAIZE",
    "acreage": 2.5,
    "h3_index": "8928308280fffff"
}, HTTP_AUTHORIZATION=f'Token {token}', content_type="application/json")
print("Quote Status:", quote_res.status_code)
print("Quote Content:", quote_res.content)
