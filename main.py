#!/usr/bin/env python3
import bcrypt
import mariadb
from decimal import Decimal
from config import DB_CONFIG


def get_connection():
    return mariadb.connect(**DB_CONFIG)


def print_menu(title, options):
    print(f"\n{'='*40}")
    print(f" {title}")
    print(f"{'='*40}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print(f"{'='*40}")


def register():
    print("\n--- Register New User ---")
    username = input("Username: ")
    password = input("Password: ")
    full_name = input("Full Name: ")
    email = input("Email: ")
    phone = input("Phone (optional): ") or None
    address = input("Address (optional): ") or None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'customer')",
            (username, hashed)
        )
        user_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO customers (user_id, full_name, email, phone, address) VALUES (%s, %s, %s, %s, %s)",
            (user_id, full_name, email, phone, address)
        )
        conn.commit()
        print(f"✓ Registered successfully! Your User ID: {user_id}")
    except mariadb.Error as e:
        print(f"✗ Error: {e}")
    finally:
        conn.close()


def login():
    print("\n--- Login ---")
    username = input("Username: ")
    password = input("Password: ")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        cursor.execute("SELECT * FROM customers WHERE user_id = %s", (user['id'],))
        customer = cursor.fetchone()
        conn.close()
        print(f"✓ Welcome, {user['username']}!")
        return user, customer
    conn.close()
    print("✗ Invalid credentials")
    return None, None


def create_account(customer_id):
    print("\n--- Create Account ---")
    print("  1. Checking")
    print("  2. Savings")
    print("  3. Loan")
    print("  4. Credit")
    choice = input("Account type (1-4): ")
    types = {'1': 'checking', '2': 'savings', '3': 'loan', '4': 'credit'}
    acc_type = types.get(choice, 'checking')
    
    initial = float(input("Initial deposit (0 for none): ") or 0)
    
    import random, string
    acc_num = ''.join(random.choices(string.digits, k=16))
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO accounts (customer_id, account_number, account_type, balance) VALUES (%s, %s, %s, %s)",
            (customer_id, acc_num, acc_type, initial)
        )
        conn.commit()
        print(f"✓ Account created: {acc_num}")
    except mariadb.Error as e:
        print(f"✗ Error: {e}")
    finally:
        conn.close()


def view_accounts(customer_id):
    print("\n--- Your Accounts ---")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM accounts WHERE customer_id = %s", (customer_id,))
    accounts = cursor.fetchall()
    conn.close()
    
    if not accounts:
        print("No accounts found.")
        return None
    
    for acc in accounts:
        print(f"\n  Account: {acc['account_number']}")
        print(f"  Type: {acc['account_type']} | Balance: ${acc['balance']:.2f}")
        print(f"  Status: {acc['status']}")
    return accounts


def deposit():
    acc_num = input("\nAccount number: ")
    amount = float(input("Amount: "))
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_number = %s", (amount, acc_num))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, description) VALUES ((SELECT id FROM accounts WHERE account_number=%s), 'deposit', %s, 'Deposit')",
            (acc_num, amount)
        )
        conn.commit()
        print(f"✓ Deposited ${amount:.2f}")
    except mariadb.Error as e:
        print(f"✗ Error: {e}")
    finally:
        conn.close()


def withdraw():
    acc_num = input("\nAccount number: ")
    amount = float(input("Amount: "))
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (acc_num,))
        acc = cursor.fetchone()
        
        if not acc or acc['balance'] < amount:
            print("✗ Insufficient funds")
            conn.close()
            return
        
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", (amount, acc_num))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, description) VALUES ((SELECT id FROM accounts WHERE account_number=%s), 'withdrawal', %s, 'Withdrawal')",
            (acc_num, amount)
        )
        conn.commit()
        print(f"✓ Withdrew ${amount:.2f}")
    except mariadb.Error as e:
        print(f"✗ Error: {e}")
    finally:
        conn.close()


def transfer():
    from_acc = input("\nFrom account: ")
    to_acc = input("To account: ")
    amount = float(input("Amount: "))
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT balance, id FROM accounts WHERE account_number = %s", (from_acc,))
        acc = cursor.fetchone()
        
        if not acc or acc['balance'] < amount:
            print("✗ Insufficient funds")
            conn.close()
            return
        
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", (amount, from_acc))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_number = %s", (amount, to_acc))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, description, related_account_id) VALUES (%s, 'transfer', %s, 'Transfer', (SELECT id FROM accounts WHERE account_number=%s))",
            (acc['id'], amount, to_acc)
        )
        conn.commit()
        print(f"✓ Transferred ${amount:.2f}")
    except mariadb.Error as e:
        print(f"✗ Error: {e}")
    finally:
        conn.close()


def transaction_history():
    acc_num = input("\nAccount number: ")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT t.*, a.account_number FROM transactions t JOIN accounts a ON t.account_id = a.id WHERE a.account_number = %s ORDER BY t.created_at DESC LIMIT 20",
        (acc_num,)
    )
    txs = cursor.fetchall()
    conn.close()
    
    if not txs:
        print("No transactions found.")
        return
    
    print("\n--- Transaction History ---")
    for tx in txs:
        print(f"  {tx['transaction_type'].upper()}: ${tx['amount']:.2f} | {tx['created_at']}")


def customer_menu(user, customer):
    while True:
        print_menu(f"Customer Menu ({customer['full_name']})", [
            "View Accounts",
            "Create Account",
            "Deposit",
            "Withdraw",
            "Transfer",
            "Transaction History",
            "Logout"
        ])
        choice = input("Select option: ")
        
        if choice == '1':
            view_accounts(customer['id'])
        elif choice == '2':
            create_account(customer['id'])
        elif choice == '3':
            deposit()
        elif choice == '4':
            withdraw()
        elif choice == '5':
            transfer()
        elif choice == '6':
            transaction_history()
        elif choice == '7':
            break


def admin_menu():
    print("\n--- Admin Menu ---")
    print("Admin features coming soon...")


def main():
    print("="*40)
    print(" Welcome to Simple Banking CLI")
    print("="*40)
    
    while True:
        print_menu("Main Menu", [
            "Register",
            "Login",
            "Exit"
        ])
        choice = input("Select option: ")
        
        if choice == '1':
            register()
        elif choice == '2':
            user, customer = login()
            if user:
                if user['role'] == 'admin':
                    admin_menu()
                else:
                    customer_menu(user, customer)
        elif choice == '3':
            print("\nGoodbye!")
            break


if __name__ == '__main__':
    main()
