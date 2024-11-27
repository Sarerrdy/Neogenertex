import sqlite3
import random
import string
from datetime import datetime, timedelta

DB_FILE = 'tether_menu_users.db'


def generate_credentials():
    username = ''.join(random.choices(
        string.ascii_letters + string.digits, k=8))
    password = ''.join(random.choices(
        string.ascii_letters + string.digits, k=8))
    return username, password


def add_user(duration):
    username, password = generate_credentials()
    expiry_time = datetime.now() + timedelta(hours=duration)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password, expiry_time, duration)
        VALUES (?, ?, ?, ?)
    ''', (username, password, expiry_time.isoformat(), duration))
    conn.commit()
    conn.close()

    return username, password, expiry_time


def load_users():
    users = {}
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT username, password, expiry_time, duration FROM users')
    rows = cursor.fetchall()
    for row in rows:
        username, password, expiry_time, duration = row
        expiry_time = datetime.fromisoformat(expiry_time)
        users[username] = {
            'password': password,
            'expiry_time': expiry_time,
            'duration': duration
        }
    conn.close()
    return users


def update_user(username):
    users = load_users()
    if username in users:
        user = users[username]
        remaining_time = user['expiry_time'] - datetime.now()
        if remaining_time.total_seconds() > 0:
            user['expiry_time'] = datetime.now() + remaining_time
        else:
            user['expiry_time'] = datetime.now(
            ) + timedelta(hours=user['duration'])

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET expiry_time = ?
            WHERE username = ?
        ''', (user['expiry_time'].isoformat(), username))
        conn.commit()
        conn.close()
        return True
    return False
