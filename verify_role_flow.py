import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

from apps.users.models import User

def verify_flow():
    username = 'test_new_user'
    password = 'password123'
    
    # 1. Create User
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
    
    user = User.objects.create_user(username=username, password=password)
    print(f"Created user {username} with role: {user.role}")
    if user.role != 'UNASSIGNED':
        print("FAIL: Default role is not UNASSIGNED")
        return

    c = Client()
    
    # 2. Login
    response = c.post('/login/', {'username': username, 'password': password})
    
    # Check redirect. Should redirect to /role-selection/
    if response.status_code == 302:
        print(f"Login redirect location: {response.url}")
        if response.url == '/role-selection/':
             print("PASS: Redirected to role selection.")
        else:
             print("FAIL: Redirected to wrong location.")
    else:
        print(f"FAIL: Login did not redirect. Status: {response.status_code}")

    # 3. Access Role Selection Page
    c.login(username=username, password=password)
    response = c.get('/role-selection/')
    if response.status_code == 200:
        print("PASS: Accessed Role Selection Page")
    else:
        print(f"FAIL: Could not access Role Selection Page. Status: {response.status_code}")

    # 4. Select Role (Customer)
    response = c.post('/role-selection/', {'role': 'CUSTOMER'})
    if response.status_code == 302:
        print(f"Role Selection redirect: {response.url}")
        if response.url == '/customer/order/': # Assuming reversible url name 'customer_order' maps here
            print("PASS: Redirected to customer order page.")
        else:
             print(f"FAIL: Redirected to {response.url}")
    else:
        print(f"FAIL: Role selection POST failed. Status: {response.status_code}")

    user.refresh_from_db()
    print(f"User role after selection: {user.role}")
    if user.role == 'CUSTOMER':
        print("PASS: User role updated to CUSTOMER")
    else:
        print("FAIL: User role not updated.")

    # 5. Access Landing Page as Customer
    response = c.get('/')
    if response.status_code == 302 and response.url == '/customer/order/':
         print("PASS: Landing page redirects customer to order page.")
    else:
         print(f"FAIL: Landing page behavior incorrect. Status: {response.status_code}, Url: {getattr(response, 'url', '')}")


if __name__ == '__main__':
    verify_flow()
