import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.conf import settings
# Ensure testserver is allowed
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS += ['testserver']

from apps.users.models import User

def verify_public_flow():
    c = Client()
    
    print("--- Verifying Public Access ---")
    # 1. Landing Page
    response = c.get('/')
    if response.status_code == 200:
        print("PASS: Public Landing Page accessible (200 OK)")
    else:
        print(f"FAIL: Landing Page status {response.status_code}")

    # 2. Product List
    response = c.get('/products/')
    if response.status_code == 200:
        print("PASS: Public Product List accessible (200 OK)")
    else:
        print(f"FAIL: Product List status {response.status_code}")

    # 3. Studio List
    response = c.get('/studios/')
    if response.status_code == 200:
        print("PASS: Public Studio List accessible (200 OK)")
    else:
        print(f"FAIL: Studio List status {response.status_code}")

    print("\n--- Verifying Protected Access ---")
    # 4. Protected Page (Order)
    response = c.get('/customer/order/')
    if response.status_code == 302:
        if '/login/' in response.url:
            print("PASS: /customer/order/ redirects to login")
        else:
            print(f"FAIL: Redirected to {response.url} instead of login")
    else:
        print(f"FAIL: Protected page returned {response.status_code}")

    print("\n--- Verifying Login Redirect ---")
    # 5. Login Redirect
    username = 'test_customer_pub'
    password = 'password123'
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
    
    user = User.objects.create_user(username=username, password=password) # Default role is CUSTOMER
    
    response = c.post('/login/', {'username': username, 'password': password})
    if response.status_code == 302:
        if response.url == '/' or response.url == '/landing_page': # Checking if it goes to landing page
             print("PASS: Login redirected to Landing Page (/)")
        else:
             print(f"WARNING: Login redirected to {response.url}. Check if this is intended.")
    else:
        print(f"FAIL: Login failed status {response.status_code}")

if __name__ == '__main__':
    verify_public_flow()
