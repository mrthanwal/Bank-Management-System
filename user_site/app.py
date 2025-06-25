from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import make_response
import sqlite3
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, url_for, flash
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time


app = Flask(__name__)
app.secret_key = 'your_secret_key'

load_dotenv()  # Load from .env file
EMAIL_ADDRESS = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASS')


# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('bank.db')
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

# Function to fetch user data from the database
def get_user_data(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to fetch user accounts and their transactions
def get_user_accounts(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
    accounts = cursor.fetchall()

    account_data = []
    for account in accounts:
        cursor.execute('SELECT * FROM transactions WHERE account_id = ?', (account['account_id'],))
        transactions = cursor.fetchall()
        account_data.append({
            'account': account,
            'transactions': transactions
        })
    
    conn.close()
    return account_data

# Function to update user profile
def update_user_profile(user_id, new_full_name, new_email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET full_name = ?, email = ? WHERE user_id = ?',
                   (new_full_name, new_email, user_id))
    conn.commit()
    conn.close()

# Function to validate old password
def validate_old_password(user_id, old_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    # Check if the old password matches the stored password
    return user and user['password'] == old_password

def send_login_email(to_email, full_name):
    msg = EmailMessage()
    msg['Subject'] = 'Login Alert - JAM Bank'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    msg.set_content(f"""
    Hello {full_name},

    This is a notification that your account was just accessed.

    If this wasn't you, please contact customer support immediately.

    Thank you,
    JAM Bank Security Team
    """)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Login email sent!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def send_welcome_email(to_email, full_name):
    msg = EmailMessage()
    msg['Subject'] = 'Welcome to JAM Bank!'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    msg.set_content(f"""
    Hello {full_name},

    Welcome to JAM Bank! We're excited to have you on board.

    You can now log in to your account and start using our services.

    If you have any questions, feel free to reach out.

    Best regards,
    JAM Bank Team
    """)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Welcome email sent!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def send_logout_email(to_email, username):
    msg = EmailMessage()
    msg['Subject'] = 'Logout Alert - JAM Bank'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    msg.set_content(f"""
    Hello {username},

    You have successfully logged out of JAM Bank.

    If this wasn't you, please contact our support team immediately.

    Thank you for using JAM Bank!

    Best regards,
    JAM Bank Security Team
    """)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Logout email sent!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")



def send_transaction_email(recipient_email, username, transaction_type, amount, updated_balance):
    # Compose the email
    msg = EmailMessage()
    msg['Subject'] = 'Transaction Notification - JAM Bank'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = recipient_email

    # Transaction details
    if transaction_type == 'withdraw':
        transaction_message = f"""
        Dear {username},

        Your recent transaction has been processed successfully.

        Transaction Details:
        - Amount Debited: {amount}₹
        - Your Updated Balance: {updated_balance}₹

        If you did not initiate this transaction, please contact our support team immediately.

        Best regards,
        JAM Bank Team
        """
    elif transaction_type == 'deposit':
        transaction_message = f"""
        Dear {username},

        Your recent transaction has been processed successfully.

        Transaction Details:
        - Amount Credited: {amount}₹
        - Your Updated Balance: {updated_balance}₹

        If you did not initiate this transaction, please contact our support team immediately.

        Best regards,
        JAM Bank Team
        """

    msg.set_content(transaction_message)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Transaction email sent to {recipient_email}!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def send_create_fd_email(username,email,amonut,duration_days,interest_rate,start_date,maturity_date):
    msg = EmailMessage()
    msg['Subject'] = 'FD create Notification - JAM Bank'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = email
    
    message = f"""
        Dear {username},

        Your FD has been created successfully.

        FD Details:
        - Amount: {amonut}₹
        - Duration: {duration_days}
        - Rate: {interest_rate}
        - Start Date: {start_date}
        - Maturity Date: {maturity_date}

        If you did not create this FD, please contact our support team immediately.

        Best regards,
        JAM Bank Team
        """
    msg.set_content(message)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ fd create email sent to {email}!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        
        
def send_edit_profile_email(email,username):
    msg = EmailMessage()
    msg['Subject'] = 'Profile Update Notification - JAM Bank'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = email
    
    message = f"""
        Dear {username},

        Your profile has been updated successfully.

        FD Details:
        - new username: {username}
        - new email: {email}

        If you did not update profile, please contact our support team immediately.

        Best regards,
        JAM Bank Team
        """
    msg.set_content(message)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ profile update email sent to {email}!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        

def send_update_password_email(email,username):
    msg = EmailMessage()
    msg['Subject'] = 'Password Update Notification - JAM Bank'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = email
    
    message = f"""
        Dear {username},

        Your password has been updated successfully.
        
        If you did not update profile, please contact our support team immediately.

        Best regards,
        JAM Bank Team
        """
    msg.set_content(message)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ password update email sent to {email}!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the username and password match (no hashing)
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['email']= user['email']

            # Send email
            send_login_email(user['email'], user['full_name'])

            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username, email already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username is already taken', 'danger')
            return render_template('register.html')

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            flash('Email is already registered', 'danger')
            return render_template('register.html')

        # Create new user if no conflicts
        cursor.execute('INSERT INTO users (full_name, username, email, password) VALUES (?, ?, ?, ?)',
                       (full_name, username, email, password))
        conn.commit()

        # Send a welcome email
        send_welcome_email(email, full_name)

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Fetch user data from the database
    user_data = get_user_data(user_id)  # Fetch user info like full name, username
    if not user_data:
        return redirect(url_for('login'))

    full_name = user_data['full_name']
    username = user_data['username']

    # Fetch user's accounts and their transactions
    account_data = get_user_accounts(user_id)  # This function should return a list of accounts and their transactions
    if not account_data:
        flash('No accounts found.', 'warning')

    # Render the dashboard template with the data
    return render_template('dashboard.html', user=user_data, account_data=account_data)

# Route for logging out
@app.route('/logout')
def logout():
    # Get the username or email from session to send the logout email
    username = session.get('username')
    email = session.get('email')  # Assuming email is stored in session
    session.clear()

    # Send a logout email
    send_logout_email(email, username)

    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/transfer/<int:acc_number>', methods=['GET', 'POST'])
def transfer_money(acc_number):
    con = sqlite3.connect('bank.db')
    cur = con.cursor()

    # Get sender's username from session
    username = session['username']
    cur.execute("SELECT user_id, password, email FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    if not user:
        flash("User not found", "danger")
        return redirect('/login')
    user_id, correct_password, user_email = user

    if request.method == 'POST':
        if 'password' in request.form:
            # Confirm transfer with password
            recipient_acc = request.form['recipient_acc']
            recipient_name = request.form['recipient_name']
            amount = float(request.form['amount'])
            entered_password = request.form['password']

            if entered_password != correct_password:
                flash("Incorrect password. Please try again.", "danger")
                return render_template('confirm_transfer.html',
                                       recipient_acc=recipient_acc,
                                       recipient_name=recipient_name,
                                       amount=amount)

            # Proceed with transfer
            cur.execute("SELECT account_id, balance FROM accounts WHERE account_id = ? AND user_id = ?", (acc_number, user_id))
            sender = cur.fetchone()
            if not sender:
                flash("Sender account not found.", "danger")
                return redirect('/dashboard')
            if sender[1] < amount:
                flash("Insufficient balance.", "danger")
                return redirect(f"/transfer/{acc_number}")

            cur.execute("SELECT account_id, user_id FROM accounts WHERE account_id = ?", (recipient_acc,))
            recipient = cur.fetchone()
            if not recipient:
                flash("Recipient account not found.", "danger")
                return redirect(f"/transfer/{acc_number}")

            # Check name match
            cur.execute("SELECT full_name FROM users WHERE user_id = ?", (recipient[1],))
            expected_name = cur.fetchone()
            if not expected_name or expected_name[0].lower() != recipient_name.lower():
                flash("Recipient name does not match.", "danger")
                return redirect(f"/transfer/{acc_number}")

            # Perform transfer
            cur.execute("UPDATE accounts SET balance = balance - ? WHERE account_id = ?", (amount, acc_number))
            cur.execute("UPDATE accounts SET balance = balance + ? WHERE account_id = ?", (amount, recipient_acc))

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert transactions for both sender and recipient
            cur.execute("""INSERT INTO transactions (account_id, type, amount, performed_by, timestamp)
                           VALUES (?, 'withdraw', ?, ?, ?)""", (acc_number, amount, username, timestamp))

            cur.execute("""INSERT INTO transactions (account_id, type, amount, performed_by, timestamp)
                           VALUES (?, 'deposit', ?, ?, ?)""", (recipient_acc, amount, username, timestamp))

            con.commit()

            # Get updated balances for sender and recipient
            cur.execute("SELECT balance FROM accounts WHERE account_id = ?", (acc_number,))
            sender_balance = cur.fetchone()[0]
            cur.execute("SELECT balance FROM accounts WHERE account_id = ?", (recipient_acc,))
            recipient_balance = cur.fetchone()[0]

            # Send email to both sender and recipient
            send_transaction_email(user_email, username, 'withdraw', amount, sender_balance)
            cur.execute("SELECT email FROM users WHERE user_id = ?", (recipient[1],))
            recipient_email = cur.fetchone()[0]
            send_transaction_email(recipient_email, recipient_name, 'deposit', amount, recipient_balance)

            return redirect('/dashboard')

        else:
            # First form submission → show confirmation
            recipient_acc = request.form['recipient_acc']
            recipient_name = request.form['recipient_name']
            amount = request.form['amount']
            return render_template('confirm_transfer.html',
                                   recipient_acc=recipient_acc,
                                   recipient_name=recipient_name,
                                   amount=amount)

    con.close()
    return render_template('transfer.html', account_id=acc_number)


@app.route('/transactions/<int:account_id>', methods=['GET'])
def view_transactions(account_id):
    print(f"Account ID received: {account_id}")  # Debugging line

    # Get filters from query parameters
    txn_type = request.args.get('type')
    txn_date = request.args.get('date')  # format: YYYY-MM-DD

    # Establish DB connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Base query and parameters
    query = 'SELECT * FROM transactions WHERE account_id = ?'
    params = [account_id]

    # Add filters to query if provided
    if txn_type:
        query += ' AND type = ?'
        params.append(txn_type)

    if txn_date:
        query += ' AND DATE(timestamp) = ?'
        params.append(txn_date)

    print(f"Final SQL Query: {query}, Params: {params}")  # Debug print

    # Execute query
    cursor.execute(query, params)
    transactions = cursor.fetchall()

    # Close DB connection
    cursor.close()
    conn.close()

    # Render page with filtered transactions
    return render_template('transactions.html', account_id=account_id, transactions=transactions)


@app.route('/view_fd/<int:account_id>')
def view_fd(account_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('bank.db')  # change to your DB file name
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fd_id, amount, interest_rate, duration_days, start_date, maturity_date, status 
        FROM fd 
        WHERE account_id = ?
        ORDER BY start_date DESC
    """, (account_id,))
    
    fds = cursor.fetchall()
    conn.close()

    return render_template('view_fd.html', account_id=account_id, fds=fds)

@app.route('/create_fd/<int:account_id>', methods=['GET', 'POST'])
def create_fd(account_id):
    if 'user_id' not in session:
        return redirect('/login')  # Redirect to login page if user is not logged in

    if request.method == 'POST':
        # Retrieve data from form
        amount = float(request.form['amount'])  # Ensure the amount is treated as a float
        duration_days = int(request.form['duration_days'])
        start_date = request.form['start_date']

        # Determine the interest rate based on the duration
        if duration_days <= 365:
            interest_rate = 5  # 1 year FD
        elif duration_days <= 730:
            interest_rate = 6  # 2 year FD
        else:
            interest_rate = 7  # 3+ years FD

        # Calculate maturity date
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        maturity_date_obj = start_date_obj + timedelta(days=duration_days)  # Calculate maturity date
        maturity_date = maturity_date_obj.strftime('%Y-%m-%d')

        # Set FD status
        status = 'Active'

        # Get the username (performed_by) from the session
        performed_by = session['username']  # Assuming the username is stored in session

        # Connect to the database
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # Insert the new FD record into the database
        cursor.execute("""
            INSERT INTO fd (account_id, amount, interest_rate, duration_days, start_date, maturity_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (account_id, amount, interest_rate, duration_days, start_date, maturity_date, status))

        # Reduce the balance in the accounts table
        cursor.execute("""
            UPDATE accounts
            SET balance = balance - ?
            WHERE account_id = ?
        """, (amount, account_id))

        # Add a transaction to the transaction history (FD type)
        cursor.execute("""
            INSERT INTO transactions (account_id, type, amount, performed_by)
            VALUES (?, ?, ?, ?)
        """, (account_id, 'FD', amount, performed_by))

        username=session['username']
        cursor.execute("SELECT email FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        user_email = user
        send_create_fd_email(username,user_email,amount,duration_days,interest_rate,start_date,maturity_date)
        # Commit the transaction
        conn.commit()
        conn.close()

        # Redirect to the FD view page for the account
        return redirect(url_for('view_fd', account_id=account_id))

    return render_template('create_fd.html', account_id=account_id)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect('/login')  # Redirect to login page if user is not logged in

    user_id = session['user_id']  # Get the logged-in user ID

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # Check if the new username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            # If the username is taken, show an error message
            return render_template('edit_profile.html', error="Username is already taken.", username=username, email=email)

        # Update the username and email in the database
        cursor.execute("""
            UPDATE users
            SET username = ?, email = ?
            WHERE user_id = ?
        """, (username, email, user_id))

        send_edit_profile_email(email,username)
        
        conn.commit()
        conn.close()

        # Redirect back to the dashboard with a success message
        return render_template('edit_profile.html', message="Profile updated successfully.", username=username, email=email)

    # If the method is GET, load the current user data to show in the form
    cursor.execute("SELECT username, email FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    conn.close()

    return render_template('edit_profile.html', username=user[0], email=user[1])

@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        username = session['username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return redirect('/update_password')

        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect('/update_password')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch current user details (password, user_id, email)
        cursor.execute("SELECT user_id, password, email FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user['password'] == current_password:  # WARNING: No hashing
            user_id = user['user_id']
            user_email = user['email']

            # Send password update email
            send_update_password_email(user_email, username)

            # Update password
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (new_password, user_id))
            conn.commit()
            conn.close()

            flash('Password updated successfully!', 'success')
            return redirect('/dashboard')
        else:
            flash('Current password is incorrect', 'danger')
            return redirect('/update_password')

    return render_template('update_password.html')

        
def send_otp_email(to_email, full_name,otp):
    msg = EmailMessage()
    msg['Subject'] = 'Password Reset OTP- JAM Bank'
    msg['From'] = f"MyBank <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    msg.set_content(f"""
    Hello {full_name},

    Your OTP for password reset is: {otp}.

    Thank you,
    JAM Bank Security Team
    """)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Login email sent!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")        
        

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        # Fetch user from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Generate 6-digit OTP
            otp = random.randint(100000, 999999)

            # Send OTP to the user's email
            send_otp_email(user['email'], user['full_name'], otp)
            
            # Store OTP in session
            session['otp'] = otp
            session['otp_attempts'] = 0
            session['otp_timestamp'] = time.time()
            session['user_id'] = user['user_id']

            flash("OTP sent to your email", "success")
            return redirect(url_for('verify_otp'))
        else:
            flash("Username not found", "danger")
            return redirect(url_for('forgot_password'))

    
    return render_template('forgot_password.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        user_otp = session.get('otp')
        otp_timestamp = session.get('otp_timestamp')

        if not user_otp:
            flash("OTP has expired. Please request a new OTP.", 'danger')
            return redirect('/forgot_password')

        if entered_otp == str(user_otp):
            if time.time() - otp_timestamp <= 300:
                flash("OTP verified successfully. You can now reset your password.", 'success')
                return redirect('/reset_password')
            else:
                flash("OTP has expired. Please request a new OTP.", 'danger')
                return redirect('/forgot_password')
        else:
            flash("Invalid OTP. Please try again.", 'danger')
            return redirect('/verify_otp')

    # Mask email
    email = session.get('email')
    masked_email = None
    if email:
        local, domain = email.split('@')
        masked_email = local[:2] + '*' * (len(local) - 2) + '@' + domain

    return render_template('verify_otp.html', email=masked_email)

@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    user_id = session.get('user_id')

    if not user_id:
        flash("Session expired. Please start over.", "danger")
        return redirect(url_for('forgot_password'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        otp = random.randint(100000, 999999)
        send_otp_email(user['email'], user['full_name'], otp)

        session['otp'] = otp
        session['otp_timestamp'] = time.time()
        flash("OTP resent to your email.", "info")
    else:
        flash("User not found. Please start over.", "danger")
        return redirect(url_for('forgot_password'))

    return redirect(url_for('verify_otp'))


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' not in session:
        flash("Session expired. Please request a new OTP.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('reset_password'))


        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (password, session['user_id']))
        
        

        # Clear session after reset
        

        flash("Password reset successful. Please log in.", "success")
        
        username=session['username']
        cursor.execute("SELECT email FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        user_email = user
        send_update_password_email(user_email,username)
        session.clear()
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    

    return render_template('reset_password.html')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)