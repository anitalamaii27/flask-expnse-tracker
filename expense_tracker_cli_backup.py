import csv
import os
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
import shutil
import time
from colorama import Fore, Style, init
from tabulate import tabulate


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for flashing messages

# Path to your CSV file
DATA_FILE = '/home/your_username/expenses.csv'

# Helper functions to interact with CSV data
def get_all_expenses():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data[1:]  # Skip header row

def add_expense_to_csv(date, category, amount, note):
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, category, f"{amount:.2f}", note])

# Routes

@app.route('/')
def index():
    expenses = get_all_expenses()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = float(request.form['amount'])
        note = request.form['note']

        # Default date to today if left blank
        if not date:
            date = datetime.today().strftime('%Y-%m-%d')

        # Add expense to CSV
        add_expense_to_csv(date, category, amount, note)

        flash('Expense added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_expense.html')


# ---------------------- CONFIG ------------------------
DATA_FILE = "expenses.csv"
BACKUP_DIR = "backups"
PASSWORD_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # 'password'
INACTIVITY_LIMIT = 30 * 60  # 30 minutes in seconds

# Default budget values (to be overridden by user input)
DEFAULT_YEARLY_BUDGET = 12000
MONTHLY_BUDGET = 0
YEARLY_BUDGET = DEFAULT_YEARLY_BUDGET

# ---------------------- SECURITY ----------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password():
    print(Fore.CYAN + "🔐 Welcome to your Secure Expense Tracker\n")
    password = input("🔑 Enter your password: ")
    if hash_password(password) != PASSWORD_HASH:
        print(Fore.RED + "❌ Access Denied.\n")
        exit()
    print(Fore.GREEN + "✅ Access Granted.\n")

# ---------------------- SETUP -------------------------
def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Category', 'Amount', 'Note'])

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def set_budgets():
    global MONTHLY_BUDGET, YEARLY_BUDGET
    while True:
        try:
            MONTHLY_BUDGET = float(input(Fore.YELLOW + "Please enter your monthly budget: $"))
            if MONTHLY_BUDGET <= 0:
                print(Fore.RED + "❗ Monthly budget must be positive.")
                continue
            break
        except ValueError:
            print(Fore.RED + "❗ Invalid number.")

    yearly_input = input(Fore.YELLOW + "Would you like to set a yearly budget? (y/n): ").strip().lower()
    if yearly_input == 'y':
        while True:
            try:
                YEARLY_BUDGET = float(input(Fore.YELLOW + "Enter your yearly budget: $"))
                if YEARLY_BUDGET <= 0:
                    print(Fore.RED + "❗ Yearly budget must be positive.")
                    continue
                break
            except ValueError:
                print(Fore.RED + "❗ Invalid number.")
    else:
        YEARLY_BUDGET = MONTHLY_BUDGET * 12

# ---------------------- OPERATIONS ---------------------
def add_expense():
    print(Fore.MAGENTA + "\n➕ Add a New Expense\n")
    date = input("📅 Date (YYYY-MM-DD) [Leave blank for today]: ").strip()
    if not date:
        date = datetime.today().strftime('%Y-%m-%d')
    category = input("📂 Category: ").strip()
    try:
        amount = float(input("💲 Amount (e.g. -45.99 for expenses): "))
    except ValueError:
        print(Fore.RED + "❗ Invalid amount.")
        return
    note = input("📝 Note (optional): ").strip()

    if get_total_for_current_month() + amount > MONTHLY_BUDGET:
        print(Fore.RED + f"❗ Monthly Budget Exceeded! ${MONTHLY_BUDGET:.2f}")
        return
    if get_total_for_current_year() + amount > YEARLY_BUDGET:
        print(Fore.RED + f"❗ Yearly Budget Exceeded! ${YEARLY_BUDGET:.2f}")
        return

    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, category, f"{amount:.2f}", note])
    print(Fore.GREEN + "✔️ Expense added!")

def get_total_for_current_month():
    total = 0.0
    current_month = datetime.today().strftime('%Y-%m')
    with open(DATA_FILE, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        for row in data[1:]:
            if row[0].startswith(current_month):
                total += float(row[2])
    return total

def get_total_for_current_year():
    total = 0.0
    current_year = datetime.today().strftime('%Y')
    with open(DATA_FILE, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        for row in data[1:]:
            if row[0].startswith(current_year):
                total += float(row[2])
    return total

def view_expenses():
    print(Fore.CYAN + "\n📋 All Expenses:\n")
    with open(DATA_FILE, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        if len(data) > 1:
            print(tabulate(data[1:], headers=data[0], tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "No expenses recorded.")

def delete_expense():
    view_expenses()
    entry_id = input(Fore.YELLOW + "Enter row number to delete: ")
    try:
        entry_id = int(entry_id)
        with open(DATA_FILE, newline='') as f:
            data = list(csv.reader(f))
        deleted = data.pop(entry_id)
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        print(Fore.GREEN + f"✅ Deleted: {deleted}")
    except Exception as e:
        print(Fore.RED + f"❗ Error: {str(e)}")

def monthly_summary():
    print(Fore.MAGENTA + "\n📆 Monthly Summary\n")
    month = input("📆 Enter month (YYYY-MM): ").strip()
    total = 0.0
    with open(DATA_FILE, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        summary = [row for row in data[1:] if row[0].startswith(month)]
        for row in summary:
            total += float(row[2])
    if summary:
        print(tabulate(summary, headers=data[0], tablefmt="fancy_grid"))
        print(Fore.CYAN + f"\n📊 Total for {month}: ${total:.2f}")
    else:
        print(Fore.YELLOW + "📭 No data for this month.")

def yearly_summary():
    print(Fore.MAGENTA + "\n📆 Yearly Summary\n")
    year = input("📆 Enter year (YYYY): ").strip()
    total = 0.0
    with open(DATA_FILE, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        summary = [row for row in data[1:] if row[0].startswith(year)]
        for row in summary:
            total += float(row[2])
    if summary:
        print(tabulate(summary, headers=data[0], tablefmt="fancy_grid"))
        print(Fore.CYAN + f"\n📊 Total for {year}: ${total:.2f}")
    else:
        print(Fore.YELLOW + "📭 No data for this year.")

def backup_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BACKUP_DIR}/expenses_backup_{timestamp}.csv"
    shutil.copy(DATA_FILE, filename)
    print(Fore.GREEN + f"📦 Backup saved as {filename}")

# ---------------------- INACTIVITY ----------------------
def check_inactivity(last_active_time):
    if time.time() - last_active_time > INACTIVITY_LIMIT:
        print(Fore.YELLOW + "\n⏳ Session timed out.")
        main()

# ---------------------- MAIN MENU ----------------------
def main_menu():
    last_active = time.time()
    while True:
        check_inactivity(last_active)
        print(Fore.MAGENTA + "\n📘 Expense Tracker Menu\n")
        print(Fore.YELLOW + "1. ➕ Add Expense")
        print(Fore.YELLOW + "2. 👁️ View Expenses")
        print(Fore.YELLOW + "3. ❌ Delete Expense")
        print(Fore.YELLOW + "4. 📈 Monthly Summary")
        print(Fore.YELLOW + "5. 📅 Yearly Summary")
        print(Fore.YELLOW + "6. 💾 Backup Data")
        print(Fore.YELLOW + "7. 🚪 Exit\n")

        choice = input("Choose an option (1–7): ").strip()
        last_active = time.time()

        if choice == '1':
            add_expense()
        elif choice == '2':
            view_expenses()
        elif choice == '3':
            delete_expense()
        elif choice == '4':
            monthly_summary()
        elif choice == '5':
            yearly_summary()
        elif choice == '6':
            backup_data()
        elif choice == '7':
            print(Fore.CYAN + "\n👋 Exiting. Stay financially smart!")
            time.sleep(1)
            exit()
        else:
            print(Fore.RED + "❗ Invalid option. Please try again.")

# ---------------------- ENTRY POINT ----------------------
def main():
    ensure_data_file()
    ensure_backup_dir()
    verify_password()
    set_budgets()
    print(Fore.GREEN + "✅ Ready! Launching menu...")
    main_menu()

if __name__ == "__main__":
    main()

