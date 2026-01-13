import requests
import sys

base_url = 'http://127.0.0.1:5000'

def test_output_status(status, text):
    if status == 'pass':
        print(f'\033[92m[PASS]\033[0m {text}')
    elif status == 'info':
        print(f'\033[96m[INFO]\033[0m {text}')
    else:
        print(f'\033[91m[FAIL]\033[0m {text}')
        sys.exit(1)

# =========================
# 1️⃣ Login com user normal (asmith)
# =========================
test_output_status('info', 'User login (asmith)')

login_response = requests.post(
    f'{base_url}/login',
    json={'username': 'asmith', 'password': 'T3MP-password-32'}
)

login_data = login_response.json()

if login_data['status'] != 'Ok':
    test_output_status('fail', 'Login failed')

user_id = login_data['user_id']
token = login_data['token']

test_output_status('pass', 'User login successful')

# =========================
# 2️⃣ Logout
# =========================
test_output_status('info', 'Logout')

logout_response = requests.post(
    f'{base_url}/logout',
    json={'user_id': user_id, 'token': token}
)

logout_data = logout_response.json()

if logout_data['status'] != 'Ok':
    test_output_status('fail', 'Logout failed')

test_output_status('pass', 'Logout successful')
