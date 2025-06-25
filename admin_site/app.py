from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime,timedelta
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import time
import random

app = Flask(__name__, template_folder="templates")
app.secret_key = "admin_secret_key"  # This should be a strong key for session management

load_dotenv()  # Load from .env file
EMAIL_ADDRESS = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASS')



DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bank.db'))

# Function to establish a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing rows by column name
    return conn

def send_login_email_admin(to_email, full_name):
    msg = EmailMessage()
    msg['Subject'] = 'Login Alert - JAM Bank'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    msg.set_content(f"""
    Hello {full_name},

    This is a notification that you just log in Your Admin account.
    If this wasn't you, please contact us.

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
        

def send_welcome_email_admin(to_email, full_name):
    msg = EmailMessage()
    msg['Subject'] = 'Welcome to JAM Bank!'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    msg.set_content(f"""
    Hello {full_name},

    Welcome to JAM Bank! We're excited to have you on board.
    You can now log in to Bank system and start your work.
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
        
def send_account_open_email(to_email, full_name,account_number,account_type):
    msg = EmailMessage()
    msg['Subject'] = 'Welcome to JAM Bank - Your Account Has Been Successfully Created!'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    msg.set_content(f"""
    Hello {full_name},

    Thank you for choosing JAM Bank. We’re excited to welcome you as our valued customer.
    Your new bank account has been successfully created, and you can now enjoy a wide range of convenient and secure banking services.

    Here are your account details:
    Account Number: {account_number}
    Account Type: {account_type}
    Branch: MNIT Jaipur

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
        
def send_logout_email_admin(to_email, username):
    msg = EmailMessage()
    msg['Subject'] = 'Logout Alert - JAM Bank'
    msg['From'] = f"JAM Bank <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    msg.set_content(f"""
    Hello {username},

    You have successfully logged out of JAM Bank.
    If this wasn't you, please contact our support team immediately.

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
        
        
        
        
# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Admin login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if there's a matching admin with the given username and password
        cur.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        admin = cur.fetchone()
        conn.close()

        if admin:
            session['admin_id'] = admin['admin_id']
            session['admin_username'] = admin['username']
            session['admin_role'] = admin['role']  # 'manager' or 'clerk'

            send_login_email_admin(admin['email'], admin['full_name'])
            # Redirect based on role
            if admin['role'] == 'manager':
                return redirect(url_for('manager_dashboard'))
            elif admin['role'] == 'clerk':
                return redirect(url_for('clerk_dashboard'))
            else:
                error = "Unknown role. Please contact support."
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)


# Route for the admin registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        email= request.form['email']
        password = request.form['password']
        role = request.form['role']
        bank_password = request.form['bank_password']

        # Check if the provided bank password is correct
        if bank_password != 'BankbyJAM':
            flash('Invalid bank password. Only authorized bank employees can register.', 'danger')
            return render_template('register.html')

        # Check if username already exists in the admins table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        existing_admin = cursor.fetchone()

        if existing_admin:
            flash('Username already exists. Please choose another one.', 'danger')
            return render_template('register.html')

        # If username is available and bank password is correct, insert the new admin
        cursor.execute(''' 
            INSERT INTO admins (username, password, full_name, role, email) 
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password, full_name, role, email))
        conn.commit()
        conn.close()

        send_welcome_email_admin(email,full_name)
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Manager dashboard route (only accessible when logged in)
@app.route('/manager-dashboard')
def manager_dashboard():
    # Check if the user is logged in by verifying the session
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # Ensure the user is a manager
    role = session.get('admin_role')
    if role != 'manager':
        return redirect(url_for('login'))  # Redirect if not a manager
    
    # Fetch manager details for the dashboard
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, username FROM admins WHERE admin_id = ?", (session['admin_id'],))
    admin_data = cursor.fetchone()
    conn.close()

    # Pass the full_name and username to the template
    return render_template('manager_dashboard.html', full_name=admin_data['full_name'], username=admin_data['username'])


#clerk daskboard route.
@app.route('/clerk-dashboard')
def clerk_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    role= session.get('admin_role')
    if role!='clerk':
        return redirect(url_for('login'))
    
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT full_name, username FROM admins WHERE admin_id = ?", (session['admin_id'],))
    admin_data = cursor.fetchone()
    conn.close()
    
    return render_template('clerk_daskboard.html', full_name=admin_data['full_name'], username=admin_data['username'])
    
    

# Route for View Accounts
@app.route('/view-accounts')
def view_accounts():
    # Make sure an admin is logged in
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    # Ensure the admin is a manager
    if session.get('admin_role') != 'manager':
        flash("Access denied: only managers can view all accounts.", "danger")
        return redirect(url_for('manager_dashboard'))

    # Get filter parameters
    account_id = request.args.get('account_id')
    user_id = request.args.get('user_id')
    account_type = request.args.get('account_type')

    # Build dynamic query
    query = "SELECT account_id, user_id, balance, account_type, created_at FROM accounts WHERE 1=1"
    params = []

    if account_id:
        query += " AND account_id = ?"
        params.append(account_id)

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    if account_type and account_type != 'all':
        query += " AND account_type = ?"
        params.append(account_type)

    # Fetch from DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    accounts = cursor.fetchall()
    conn.close()

    return render_template(
        'view_accounts.html',
        accounts=accounts,
        account_id=account_id,
        user_id=user_id,
        account_type=account_type
    )


# Route to create new bank account
@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    if 'admin_id' not in session or session.get('admin_role') != 'manager':
        flash("Access denied.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        account_type = request.form['account_type']
        balance = float(request.form['balance'])

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user_id from username
        cursor.execute("SELECT user_id, email FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            user_email = result[1]  # Retrieve the email address

            # Insert into accounts table
            cursor.execute('''
                INSERT INTO accounts (user_id, account_type, balance, created_at)
                VALUES (?, ?, ?, datetime('now'))
            ''', (user_id, account_type, balance))
            conn.commit()
            conn.close()
            
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT account_id  FROM accounts WHERE user_id = ?", (user_id,))   
            account_row = cursor.fetchone()
            if account_row:
                account_id = account_row[0]  # or account_row['account_id'] if you're using row_factory
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")            
                cursor.execute('''INSERT INTO transactions (account_id, type, amount, performed_by, timestamp)
                                VALUES (?, 'deposit', ?, ?, ?)''',
                            (account_id, balance,session['admin_username'], timestamp))
                conn.commit()
            

            flash('Account created successfully and email sent!', 'success')
            send_account_open_email(user_email,username,account_id,account_type)
            return redirect(url_for('view_accounts'))
        else:
            conn.close()
            flash('Username not found!', 'danger')

    return render_template('create_account.html')

@app.route('/delete-account', methods=['GET', 'POST'])
def delete_account():
    if 'admin_id' not in session or session.get('admin_role') != 'manager':
        flash("Access denied.", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        account_id = request.form['account_id']
        reason = request.form['reason']

        # Validate if account exists
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the account exists
        cursor.execute('SELECT * FROM accounts WHERE account_id = ? AND user_id IN (SELECT user_id FROM users WHERE username = ?)', (account_id, username))
        account = cursor.fetchone()

        if not account:
            flash('Account not found or username mismatch', 'danger')
            return render_template('delete_account.html')

        # Add to closed_accounts table
        cursor.execute('''
            INSERT INTO closed_accounts (account_id, user_id, closed_at, reason) 
            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
        ''', (account[0], account[1], reason))

        # Delete from accounts table
        cursor.execute('DELETE FROM accounts WHERE account_id = ?', (account_id,))
        conn.commit()

        flash('Account successfully deleted and archived!', 'success')
        return redirect(url_for('manager_dashboard'))  # Redirect to the manager dashboard or any page you wish

    return render_template('delete_account.html')


# Route for Deposit
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    # Check if logged in and is manager
    if 'admin_id' not in session or session.get('admin_role') !='manager':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))


    if request.method == 'POST':
        username = request.form['username']
        account_number = request.form['account_number']
        amount = request.form['amount']

        try:
            amount = float(amount)
            if amount <= 0:
                flash("Amount must be greater than 0.", "danger")
                return redirect(url_for('deposit'))
        except ValueError:
            flash("Invalid amount.", "danger")
            return redirect(url_for('deposit'))

        conn = get_db_connection()
        c = conn.cursor()

        # Get user_id from username
        c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user = c.fetchone()

        if not user:
            flash("Username not found.", "danger")
            conn.close()
            return redirect(url_for('deposit'))

        user_id = user[0]

        # Check account belongs to user
        c.execute("SELECT balance FROM accounts WHERE account_id = ? AND user_id = ?", (account_number, user_id))
        acc = c.fetchone()

        if not acc:
            flash("Account not found for the given user.", "danger")
            conn.close()
            return redirect(url_for('deposit'))

        old_balance = acc[0]
        new_balance = old_balance + amount

        # Update balance
        c.execute("UPDATE accounts SET balance = ? WHERE account_id = ?", (new_balance, account_number))

        # Record transaction
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")    
        c.execute('''INSERT INTO transactions (account_id, type, amount, performed_by, timestamp)
                     VALUES (?, 'deposit',?, ?, ?)''',
                  (account_number, amount, session['admin_username'], timestamp))

        conn.commit()
        conn.close()

        flash(f"Successfully deposited ₹{amount:.2f} to account {account_number}.", "success")
        return redirect(url_for('deposit'))

    return render_template('deposit.html')

# Route for Clerk Deposit
@app.route('/deposit_clerk', methods=['GET', 'POST'])
def deposit_clerk():
    # Check if logged in and is clerk or manager
    if 'admin_id' not in session or session.get('admin_role') !='clerk':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        account_number = request.form['account_number']
        amount = request.form['amount']

        try:
            amount = float(amount)
            if amount <= 0:
                flash("Amount must be greater than 0.", "danger")
                return redirect(url_for('deposit_clerk'))
        except ValueError:
            flash("Invalid amount.", "danger")
            return redirect(url_for('deposit_clerk'))

        conn = get_db_connection()
        c = conn.cursor()

        # Get user_id from username
        c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user = c.fetchone()

        if not user:
            flash("Username not found.", "danger")
            conn.close()
            return redirect(url_for('deposit_clerk'))

        user_id = user[0]

        # Check account belongs to user
        c.execute("SELECT balance FROM accounts WHERE account_number = ? AND user_id = ?", (account_number, user_id))
        acc = c.fetchone()

        if not acc:
            flash("Account not found for the given user.", "danger")
            conn.close()
            return redirect(url_for('deposit_clerk'))

        old_balance = acc[0]
        new_balance = old_balance + amount

        # Update balance
        c.execute("UPDATE accounts SET balance = ? WHERE account_number = ?", (new_balance, account_number))

        # Record transaction
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
        c.execute('''INSERT INTO transactions (account_number, type, amount, date_time)
                     VALUES (?, 'deposit', ?, ?)''',
                  (account_number, amount, timestamp))

        conn.commit()
        conn.close()

        flash(f"Successfully deposited ₹{amount:.2f} to account {account_number}.", "success")
        return redirect(url_for('deposit_clerk'))

    return render_template('deposit_clerk.html')



# Route for withdrawing money
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    # Check if the user is logged in and has the correct role (admin or clerk)
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get the withdrawal amount, account number (account_id), and username from the form
        account_number = request.form['account_number']
        username = request.form['username']
        amount = request.form['amount']

        # Validate the amount
        try:
            amount = float(amount)
            if amount <= 0:
                flash("Amount must be greater than 0.", "danger")
                return redirect(url_for('withdraw'))
        except ValueError:
            flash("Invalid amount.", "danger")
            return redirect(url_for('withdraw'))

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user_id from the username
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            flash("Username not found.", "danger")
            conn.close()
            return redirect(url_for('withdraw'))

        user_id = user[0]

        # Check if the account belongs to the user
        cursor.execute("SELECT balance FROM accounts WHERE account_id = ? AND user_id = ?", (account_number, user_id))
        account = cursor.fetchone()

        if not account:
            flash("Account not found or doesn't belong to the user.", "danger")
            conn.close()
            return redirect(url_for('withdraw'))

        # Check if sufficient balance is available
        old_balance = account['balance']
        if old_balance < amount:
            flash("Insufficient funds.", "danger")
            conn.close()
            return redirect(url_for('withdraw'))

        # Deduct the amount from the balance
        new_balance = old_balance - amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE account_id = ?", (new_balance, account_number))

        # Record the withdrawal transaction
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        cursor.execute('''INSERT INTO transactions (account_id, type, amount, date_time)
                          VALUES (?, 'withdrawal', ?, ?)''', 
                          (account_number, amount, timestamp))

        # Commit the transaction
        conn.commit()
        conn.close()

        flash(f"Successfully withdrew ₹{amount:.2f} from account {account_number}.", "success")
        return redirect(url_for('withdraw'))  # Redirect to the withdrawal page

    return render_template('withdraw.html')  # Render the withdrawal page

#clerk withdraw
@app.route('/withdraw_clerk', methods=['GET', 'POST'])
def withdraw_clerk():
    # Check if the user is logged in and has the correct role (manager or clerk)
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get the withdrawal amount, account number, and username from the form
        account_number = request.form['account_number']
        username = request.form['username']
        amount = request.form['amount']

        # Validate the amount
        try:
            amount = float(amount)
            if amount <= 0:
                flash("Amount must be greater than 0.", "danger")
                return redirect(url_for('withdraw_clerk'))
        except ValueError:
            flash("Invalid amount.", "danger")
            return redirect(url_for('withdraw_clerk'))

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user_id from the username
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            flash("Username not found.", "danger")
            conn.close()
            return redirect(url_for('withdraw_clerk'))

        user_id = user[0]

        # Check if the account belongs to the user
        cursor.execute("SELECT balance FROM accounts WHERE account_id = ? AND user_id = ?", (account_number, user_id))
        account = cursor.fetchone()

        if not account:
            flash("Account not found or doesn't belong to the user.", "danger")
            conn.close()
            return redirect(url_for('withdraw_clerk'))

        # Check if sufficient balance is available
        old_balance = account['balance']
        if old_balance < amount:
            flash("Insufficient funds.", "danger")
            conn.close()
            return redirect(url_for('withdraw_clerk'))

        # Deduct the amount from the balance
        new_balance = old_balance - amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE account_id = ?", (new_balance, account_number))

        # Record the withdrawal transaction
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        cursor.execute('''INSERT INTO transactions (account_id, type, amount, date_time)
                          VALUES (?, 'withdrawal', ?, ?)''', 
                          (account_number, amount, timestamp))

        # Commit the transaction
        conn.commit()
        conn.close()

        flash(f"Successfully withdrew ₹{amount:.2f} from account {account_number}.", "success")
        return redirect(url_for('withdraw_clerk'))

    return render_template('withdraw_clerk.html')


# Route for View FDs
@app.route('/view-fds')
def view_fds():
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    account_id = request.args.get('account_id', '').strip()
    start_date = request.args.get('start_date', '').strip()
    status = request.args.get('status', 'all')

    query = """
        SELECT fd_id, accounts.account_id, amount, interest_rate, duration_days, start_date, 
               status, maturity_date
        FROM fd
        JOIN accounts ON fd.account_id = accounts.account_id
        WHERE 1=1
    """
    params = []

    if account_id:
        query += " AND accounts.account_id = ?"
        params.append(account_id)

    if start_date:
        query += " AND DATE(start_date) = DATE(?)"
        params.append(start_date)

    if status and status.lower() != 'all':
        query += " AND status = ?"
        params.append(status)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    fds = cursor.fetchall()
    conn.close()

    return render_template('view_fds.html', fds=fds)

#clerk view fds
@app.route('/view_fds_clerk')
def view_fds_clerk():
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    account_id = request.args.get('account_id', '').strip()
    start_date = request.args.get('start_date', '').strip()
    status = request.args.get('status', 'all')

    query = """
        SELECT fd_id, accounts.account_id, amount, interest_rate, duration_days, start_date, 
               status, maturity_date
        FROM fd
        JOIN accounts ON fd.account_id = accounts.account_id
        WHERE 1=1
    """
    params = []

    if account_id:
        query += " AND accounts.account_id = ?"
        params.append(account_id)

    if start_date:
        query += " AND DATE(start_date) = DATE(?)"
        params.append(start_date)

    if status and status.lower() != 'all':
        query += " AND status = ?"
        params.append(status)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    fds = cursor.fetchall()
    conn.close()

    return render_template('view_fds_clerk.html', fds=fds)



@app.route('/create-fd', methods=['GET', 'POST'])
def create_fd():
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get the data from the form
        account_id = request.form['account_id']
        amount = request.form['amount']
        duration_days = request.form['duration_days']
        interest_rate = request.form['interest_rate']
        start_date = request.form['start_date']

        # Validate if the account_id exists in the accounts table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,))
        account = cursor.fetchone()

        if not account:
            flash("Account ID not found.", "danger")
            conn.close()
            return redirect(url_for('create_fd'))  # Redirect back to form if account not found

        # Check if the account has sufficient balance for the FD
        account_balance = account['balance']
        if float(amount) > account_balance:
            flash("Insufficient balance to create FD.", "danger")
            conn.close()
            return redirect(url_for('create_fd'))  # Redirect back if balance is insufficient

        # Reduce the account balance
        new_balance = account_balance - float(amount)
        cursor.execute("""
            UPDATE accounts
            SET balance = ?
            WHERE account_id = ?
        """, (new_balance, account_id))

        # Insert a transaction for the FD creation
        transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO transactions (account_id, transaction_type, amount, transaction_date, description)
            VALUES (?, ?, ?, ?, ?)
        """, (account_id, 'FD Creation', amount, transaction_date, f"Created FD with amount ₹{amount}"))

        # Calculate maturity date based on the duration
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        maturity_date_obj = start_date_obj + timedelta(days=int(duration_days))
        maturity_date = maturity_date_obj.strftime('%Y-%m-%d')

        # Default status is Active
        status = 'Active'

        # Insert the new FD into the database
        cursor.execute("""
            INSERT INTO fixed_deposits (account_id, amount, interest_rate, duration_days, start_date, status, maturity_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (account_id, amount, interest_rate, duration_days, start_date, status, maturity_date))
        conn.commit()
        conn.close()

        flash("Fixed Deposit created successfully!", "success")
        return redirect(url_for('view_fds'))  # Redirect to a page that shows all FDs

    return render_template('create_fd.html')  # Show form if GET request

@app.route('/view-loans', methods=['GET', 'POST'])
def view_loans():
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    filters = []
    values = []

    # Get filter parameters from request.args (GET)
    account_number = request.args.get('account_number', '').strip()
    approved_by = request.args.get('approved_by', '').strip()
    approved_date = request.args.get('approved_date', '').strip()

    if account_number:
        filters.append("a.account_id = ?")
        values.append(account_number)

    if approved_by:
        filters.append("l.approved_by LIKE ?")
        values.append(f"%{approved_by}%")

    if approved_date:
        filters.append("DATE(l.approved_date) = ?")
        values.append(approved_date)

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT l.loan_id, l.amount, l.interest_rate, l.duration_months, 
               l.approved_by, l.approved_date, a.account_id, u.username
        FROM loans l
        JOIN accounts a ON l.account_id = a.account_id
        JOIN users u ON a.user_id = u.user_id
        {where_clause}
        ORDER BY l.loan_id DESC
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(values))
    loans = cursor.fetchall()
    conn.close()

    return render_template('view_loans.html', loans=loans,
                           account_number=account_number,
                           approved_by=approved_by,
                           approved_date=approved_date)


@app.route('/create-loan', methods=['GET', 'POST'])
def create_loan():
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get the data from the form
        account_id = request.form['account_id']
        amount = request.form['amount']
        duration_months = request.form['duration_months']
        interest_rate = request.form['interest_rate']

        # Validate if the account exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,))
        account = cursor.fetchone()

        if not account:
            flash("Account number not found.", "danger")
            conn.close()
            return redirect(url_for('create_loan'))

        
        approved_by = session.get('admin_username')
        approved_date = datetime.now().strftime('%Y-%m-%d')

        cursor.execute("""
            INSERT INTO loans (account_id, amount, interest_rate, duration_months, approved_by, approved_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (account_id, amount, interest_rate, duration_months, approved_by, approved_date))

        conn.commit()
        conn.close()

        flash("Loan created successfully!", "success")
        return redirect(url_for('view_loans'))

    return render_template('create_loan.html')


@app.route('/view-transactions')
def view_transactions():
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    account_id = request.args.get('account_id', '').strip()
    txn_type = request.args.get('type', '').strip().lower()
    performed_by = request.args.get('performed_by', '').strip()

    query = """
        SELECT transaction_id, account_id, type, amount, performed_by, timestamp
        FROM transactions
        WHERE 1=1
    """
    params = []

    if account_id:
        query += " AND account_id = ?"
        params.append(account_id)

    if txn_type:
        query += " AND type = ?"
        params.append(txn_type)

    if performed_by:
        query += " AND performed_by LIKE ?"
        params.append(f"%{performed_by}%")

    query += " ORDER BY timestamp DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()

    return render_template('view_transactions.html', transactions=transactions)

@app.route('/view-transactions_clerk')
def view_transactions_clerk():
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    account_id = request.args.get('account_id', '').strip()
    txn_type = request.args.get('type', '').strip().lower()
    performed_by = request.args.get('performed_by', '').strip()

    query = """
        SELECT transaction_id, account_id, type, amount, performed_by, timestamp
        FROM transactions
        WHERE 1=1
    """
    params = []

    if account_id:
        query += " AND account_id = ?"
        params.append(account_id)

    if txn_type:
        query += " AND type = ?"
        params.append(txn_type)

    if performed_by:
        query += " AND performed_by LIKE ?"
        params.append(f"%{performed_by}%")

    query += " ORDER BY timestamp DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()

    return render_template('view_transactions_clerk.html', transactions=transactions)

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if 'admin_id' not in session or session.get('admin_role') not in ['manager', 'clerk']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    admin_id = session["admin_id"]

    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]

        # Check if username is taken by another admin
        cur.execute("SELECT admin_id FROM admins WHERE username = ? AND admin_id != ?", (new_username, admin_id))
        if cur.fetchone():
            return render_template("edit_profile.html", admin={"username": new_username, "email": new_email}, message="Username already taken")

        # Update the admin's profile
        cur.execute("UPDATE admins SET username = ?, email = ? WHERE admin_id = ?", (new_username, new_email, admin_id))
        conn.commit()
        session["username"] = new_username
        flash("Profile updated successfully.", "success")
        return render_template("edit_profile.html", admin={"username": new_username, "email": new_email})

    # GET request: Pre-fill form with current admin info
    cur.execute("SELECT username, email FROM admins WHERE admin_id = ?", (admin_id,))
    admin = cur.fetchone()
    return render_template("edit_profile.html", admin=admin)

@app.route("/edit_profile_clerk", methods=["GET", "POST"])
def edit_profile_clerk():
    if 'admin_id' not in session or session.get('admin_role') != 'clerk':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    admin_id = session["admin_id"]

    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]

        # Check if username is taken by another admin
        cur.execute("SELECT admin_id FROM admins WHERE username = ? AND admin_id != ?", (new_username, admin_id))
        if cur.fetchone():
            return render_template("edit_profile_clerk.html", admin={"username": new_username, "email": new_email}, message="Username already taken")

        # Update the admin's profile
        cur.execute("UPDATE admins SET username = ?, email = ? WHERE admin_id = ?", (new_username, new_email, admin_id))
        conn.commit()
        session["username"] = new_username
        flash("Profile updated successfully.", "success")
        return render_template("edit_profile_clerk.html", admin={"username": new_username, "email": new_email})

    # GET request: Pre-fill form with current admin info
    cur.execute("SELECT username, email FROM admins WHERE admin_id = ?", (admin_id,))
    admin = cur.fetchone()
    return render_template("edit_profile_clerk.html", admin=admin)

@app.route("/update-password", methods=["GET", "POST"])
def update_password():
    if 'admin_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    admin_id = session["admin_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # 1. Check if current password matches
        cur.execute("SELECT password FROM admins WHERE admin_id = ?", (admin_id,))
        row = cur.fetchone()

        if not row or row["password"] != current_password:
            return render_template("update_password.html", message="Current password is incorrect.")

        # 2. Check new passwords match
        if new_password != confirm_password:
            return render_template("update_password.html", message="New passwords do not match.")

        # 3. Update password
        cur.execute("UPDATE admins SET password = ? WHERE admin_id = ?", (new_password, admin_id))
        conn.commit()
        conn.close()
        return render_template("update_password.html", message="Password updated successfully!")

    # For GET request
    return render_template("update_password.html")


@app.route("/update_password_clerk", methods=["GET", "POST"])
def update_password_clerk():
    if 'admin_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    admin_id = session["admin_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # 1. Check if current password matches
        cur.execute("SELECT password FROM admins WHERE admin_id = ?", (admin_id,))
        row = cur.fetchone()

        if not row or row["password"] != current_password:
            return render_template("update_password.html", message="Current password is incorrect.")

        # 2. Check new passwords match
        if new_password != confirm_password:
            return render_template("update_password_clerk.html", message="New passwords do not match.")

        # 3. Update password
        cur.execute("UPDATE admins SET password = ? WHERE admin_id = ?", (new_password, admin_id))
        conn.commit()
        conn.close()
        return render_template("update_password_clerk.html", message="Password updated successfully!")

    # For GET request
    return render_template("update_password_clerk.html")

# Route for logout
@app.route('/logout')
def logout():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM admins WHERE username = ?', (session['admin_username'],))
    admin = cur.fetchone()
    send_logout_email_admin(session['admin_username'],admin[0])
    session.clear()  # Clear the session data
    return redirect(url_for('login'))



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
        
        # Fetch user from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            # Generate 6-digit OTP
            otp = random.randint(100000, 999999)

            # Send OTP to the user's email
            send_otp_email(admin['email'], admin['full_name'], otp)
            
            # Store OTP in session
            session['otp'] = otp
            session['otp_attempts'] = 0
            session['otp_timestamp'] = time.time()
            session['admin_id'] = admin['admin_id']
            session['username']=username
            session['email']=admin['email']

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
        admin_otp = session.get('otp')
        otp_timestamp = session.get('otp_timestamp')

        if not admin_otp:
            flash("OTP has expired. Please request a new OTP.", 'danger')
            return redirect('/forgot_password')

        if entered_otp == str(admin_otp):
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
    admin_id = session.get('admin_id')

    if not admin_id:
        flash("Session expired. Please start over.", "danger")
        return redirect(url_for('forgot_password'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE user_id = ?", (admin_id,))
    admin = cursor.fetchone()
    conn.close()

    if admin:
        otp = random.randint(100000, 999999)
        send_otp_email(admin['email'], admin['full_name'], otp)

        session['otp'] = otp
        session['otp_timestamp'] = time.time()
        flash("OTP resent to your email.", "info")
    else:
        flash("User not found. Please start over.", "danger")
        return redirect(url_for('forgot_password'))

    return redirect(url_for('verify_otp'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'admin_id' not in session:
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
        cursor.execute("UPDATE admins SET password = ? WHERE admin_id = ?", (password, session['admin_id']))
        conn.commit()
        conn.close()

        send_update_password_email(session['email'],session['username'])
        # Clear session after reset
        session.clear()

        flash("Password reset successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html')

# Running the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)