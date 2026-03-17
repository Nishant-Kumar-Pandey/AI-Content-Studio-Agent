"""
Standalone script to create a test user in the local SQLite database.
Run from the backend directory:
    python create_test_user.py

Test credentials:
    Email:    tester@studio.com
    Password: Test1234!
"""
import sys
import os

# Set required env vars before importing app modules
os.environ.setdefault('ENCRYPTION_KEY', 'lY-vX9yD-qPq9R5VwK1o9D9W3X4S6Z7Y8B9C0D1E2F3=')
os.environ.setdefault('SECRET_KEY', 'super-secret-auth-key-for-content-studio')

import uuid

from services.auth_service import hash_password, verify_password
from tools.database import get_user_by_email, create_user

TEST_EMAIL = 'tester@studio.com'
TEST_PASS = 'Test1234!'
TEST_NAME = 'Studio Tester'

existing = get_user_by_email(TEST_EMAIL)

if existing:
    print(f"\n✅ Test user already exists!")
    print(f"   Email:    {TEST_EMAIL}")
    print(f"   Password: {TEST_PASS}")
    print(f"   ID:       {existing['id']}")
    # Verify password still works
    if existing.get('hashed_password') and verify_password(TEST_PASS, existing['hashed_password']):
        print(f"\n🔐 Password check: OK")
    else:
        print(f"\n⚠️  Password check: FAILED (wrong hash or OAuth user)")
else:
    uid = str(uuid.uuid4())
    hashed = hash_password(TEST_PASS)
    create_user(uid, TEST_EMAIL, hashed, TEST_NAME)
    user = get_user_by_email(TEST_EMAIL)
    print(f"\n✅ Test user created successfully!")
    print(f"   Email:    {TEST_EMAIL}")
    print(f"   Password: {TEST_PASS}")
    print(f"   ID:       {user['id']}")

print("\n--- Use these credentials to test login/signup ---")
