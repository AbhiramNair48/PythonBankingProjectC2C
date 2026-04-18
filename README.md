# Simple Banking CLI Application

A command-line banking application built with Python and MariaDB/MySQL.

## Prerequisites

- **Python 3.8+**
- **MariaDB or MySQL** database server
- **pip** (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd PythonBankingProjectC2C
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install bcrypt mariadb python-dotenv
```

### 4. Configure Database

Start your MariaDB/MySQL server, then create the database and tables:

```bash
mysql -u root -p < db_setup.sql
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env  # Or create manually
```

Edit `.env` with your database credentials:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=banking
```

## Running the Application

### Option 1: Using the run script

```bash
chmod +x run.sh
./run.sh
```

### Option 2: Direct Python execution

```bash
python main.py
```

## Usage

Once running, you can:

1. **Register** - Create a new user account
2. **Login** - Access your existing account
3. **Exit** - Close the application

### Customer Features

After logging in, customers can:
- View all accounts
- Create new accounts (Checking, Savings, Loan, Credit)
- Deposit money
- Withdraw money
- Transfer between accounts
- View transaction history

## Project Structure

```
PythonBankingProjectC2C/
├── main.py          # Main application logic
├── config.py        # Database configuration
├── db_setup.sql     # Database schema setup
├── .env             # Environment variables (create this)
├── .env.example     # Example environment file
├── run.sh           # Convenience run script
└── venv/            # Virtual environment (not in git)
```

## Security Notes

- Change the default database credentials in `db_setup.sql` for production
- Never commit `.env` files with real credentials to version control
- Passwords are hashed using bcrypt before storage
