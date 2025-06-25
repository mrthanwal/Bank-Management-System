# Bank Management System

A full-featured Python-based banking system with separate **Admin** and **User** web portals. Includes support for account management, transactions, fixed deposits, loan applications, and integrated email notifications using Gmail SMTP.

---

## 🚀 Features

### 🧑‍💼 Admin Portal
- Create and delete user accounts
- View all transactions
- Manage fixed deposits and loan requests

### 🙋 User Portal
- Register and login
- Deposit and withdraw money
- Create fixed deposits
- Apply for loans
- Receive email notifications for key actions

---

## 📬 Email Notification System

- Uses Gmail SMTP to send alerts and confirmations.
- Requires a `.env` file containing your email and Google App Password:

EMAIL=your-email@gmail.com
APP_PASSWORD=your-google-app-password


> 🔐 **Note**: Enable 2-Step Verification in your Google account to generate an App Password.

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/mrthanwal/Bank-Management-System.git
cd Bank-Management-System

python create_db.py
python model.py

python admin/app.py
python user/app.py


---

Let me know if you want me to add this to your repo via a `README.md` file or need help pushing it with Git.

