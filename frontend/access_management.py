import os
from datetime import datetime
from user_management import load_users


# IP address field return None
def get_user_ip(username):
    with open('/var/lib/misc/dnsmasq.leases', 'r') as f:
        for line in f:
            if username in line:
                parts = line.split()
                return parts[2]  # IP address field
    return None


def grant_access(username):
    # Logic to grant internet access based on username
    users = load_users()
    if username in users:
        user = users[username]
        remaining_time = (user['expiry_time'] - datetime.now()).total_seconds()
        if remaining_time > 0:
            user_ip = get_user_ip(username)
            if user_ip:
                os.system(f'sudo iptables -A FORWARD -s {user_ip} -j ACCEPT')
                os.system(f'sudo iptables -A FORWARD -d {user_ip} -j ACCEPT')
                return True
    return False


def revoke_access(username):
    user_ip = get_user_ip(username)
    if user_ip:
        os.system(f'sudo iptables -D FORWARD -s {user_ip} -j ACCEPT')
        os.system(f'sudo iptables -D FORWARD -d {user_ip} -j ACCEPT')


# Example usage
if __name__ == '__main__':
    grant_access('username')
