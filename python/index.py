from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="cset155",
    database="rj_bank"
)
cursor = conn.cursor(dictionary=True)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        fname = request.form['first_name']
        lname = request.form['last_name']
        ssn = request.form['ssn']
        address = request.form['address']
        phone = request.form['phone']
        password = request.form['password']

        cursor.execute("SELECT * FROM Users WHERE Username = %s OR SSN = %s OR Phone_Num = %s",
                       (username, ssn, phone))
        existing = cursor.fetchone()

        if existing:
            flash("User already exists.")
            return redirect('/signup')

        user_id = random.randint(10000, 99999)
        cursor.execute("""
            INSERT INTO Users (User_Id, Username, First_name, Last_name, SSN, Address, Phone_Num, Password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, username, fname, lname, ssn, address, phone, password))
        conn.commit()

        flash("Signup complete. Wait for admin approval.")
        return redirect('/login')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

     
        cursor.execute("SELECT * FROM Admins WHERE Username = %s AND Password = %s", (username, password))
        admin = cursor.fetchone()

        if admin:
            session['admin'] = True
            session['username'] = username
            return redirect('/admin_dashboard')

        
        cursor.execute("SELECT * FROM Users WHERE Username = %s AND Password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['User_Id']
            session['username'] = user['Username']

            cursor.execute("SELECT * FROM Bank_Accounts WHERE User_Id = %s", (user['User_Id'],))
            account = cursor.fetchone()

            if not account:
                flash("Account pending admin approval.")
                return redirect('/login')

            session['account_num'] = account['Account_Num']
            return redirect('/dashboard')

        flash("Invalid login.")
        return redirect('/login')

    return render_template('login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/login')

    cursor.execute("SELECT * FROM Users WHERE User_Id NOT IN (SELECT User_Id FROM Bank_Accounts)")
    pending_users = cursor.fetchall()
    return render_template('admin.html', users=pending_users)

@app.route('/approve/<int:user_id>')
def approve(user_id):
    if not session.get('admin'):
        return redirect('/login')

    account_num = random.randint(10000000, 99999999)
    cursor.execute("INSERT INTO Bank_Accounts (Account_Num, User_Id, Balance) VALUES (%s, %s, %s)",
                   (account_num, user_id, 0.00))
    conn.commit()
    flash(f"User {user_id} approved.")
    return redirect('/admin_dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect('/login')
    return f"Welcome, {session['username']}! Your account number is {session['account_num']}."


if __name__ == '__main__':
    app.run(debug=True)