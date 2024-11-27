import time
from datetime import datetime
from user_management import load_users, revoke_access


def check_sessions():
    users = load_users()
    for username, user in users.items():
        if user['expiry_time'] <= datetime.now():
            revoke_access(username)


while True:
    check_sessions()
    time.sleep(60)  # Check every minute
