import os
import re
from datetime import datetime, timedelta
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
# from user_management import add_user, load_users, update_user

DB_FILE = 'tether_menu_users.db'


class TetherMenuManager(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.label = Label(text="WiFi Hotspot Manager", font_size='20sp')
        self.add_widget(self.label)

        self.user_input = TextInput(hint_text="Username")
        self.add_widget(self.user_input)

        self.pass_input = TextInput(hint_text="Password", password=True)
        self.add_widget(self.pass_input)

        self.login_button = Button(text="Login", on_press=self.login)
        self.add_widget(self.login_button)

        self.register_1h_button = Button(
            text="Register 1 Hour", on_press=lambda instance: self.register(1))
        self.add_widget(self.register_1h_button)

        self.register_2h_button = Button(
            text="Register 2 Hours", on_press=lambda instance: self.register(2))
        self.add_widget(self.register_2h_button)

        self.devices_label = Label(text="Connected Devices:", font_size='16sp')
        self.add_widget(self.devices_label)

        Clock.schedule_interval(self.update_devices, 10)
        self.users = self.load_users()

    def register(self, duration):
        username, password, expiry_time = self.add_user(duration)
        self.label.text = f"Registered - Username: {username}, Password: {password}, Expires at: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.users = self.load_users()

    def login(self, instance):
        username = self.user_input.text
        password = self.pass_input.text
        if username in self.users and self.users[username]['password'] == password:
            if self.update_user(username):
                self.label.text = f"Welcome {username}. Session updated."
                self.grant_access(username)
            else:
                self.label.text = "Error updating session."
        else:
            self.label.text = "Invalid username or password."

    def update_devices(self, dt):
        devices = self.get_connected_devices()
        self.devices_label.text = "Connected Devices:\n" + "\n".join(devices)

    def get_connected_devices(self):
        devices = []
        with open('/var/log/syslog', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if 'dnsmasq-dhcp' in line and 'DHCPACK' in line:
                    match = re.search(r'DHCPACK.* (\S+)', line)
                    if match:
                        devices.append(match.group(1))
        return devices

    def add_user(self, duration):
        username, password = self.generate_credentials()
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

    def load_users(self):
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

    def update_user(self, username):
        users = self.load_users()
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

    def grant_access(self, username):
        # Implement method to allow internet access based on username
        pass


class TetherMenuApp(App):
    def build(self):
        return TetherMenuManager()


if __name__ == '__main__':
    TetherMenuApp().run()
