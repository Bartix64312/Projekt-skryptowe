from app import create_app

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False

def test_security():
    client = app.test_client()
    
    # 1. Access protected API without login
    print("Test 1: Access API without login...")
    response = client.get('/api/hosts')
    if response.status_code in [401, 302]:
        print("PASS: Access denied (401/302)")
    else:
        print(f"FAIL: Expected 401/302, got {response.status_code}")

    # 2. Login
    print("\nTest 2: Login...")
    login_response = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    if b'Zalogowano' in login_response.data or login_response.status_code == 200:
        print("PASS: Login successful")
    else:
        print(f"FAIL: Login failed or message not found. Status: {login_response.status_code}")
        # print(login_response.data.decode())

    # 3. Access protected API with login
    print("\nTest 3: Access API with login...")
    response = client.get('/api/hosts')
    if response.status_code == 200:
        print("PASS: Access granted (200)")
    else:
        print(f"FAIL: Expected 200, got {response.status_code}")

if __name__ == '__main__':
    test_security()
