from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import datetime
from user_management import update_user

app = Flask(__name__)
DB_FILE = 'teher_menu_users.db'


@app.route('/')
def login_page():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
    </head>
    <body>
        <h2>WiFi Hotspot Login</h2>
        <form action="/login" method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    </body>
    </html>
    ''')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT password, expiry_time FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        db_password, expiry_time = row
        if db_password == password:
            if update_user(username):
                # Grant access and redirect to a success page
                return redirect("http://success_page.com")
    return redirect("/")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
