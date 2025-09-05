from flask import Flask, render_template, request, redirect, url_for, Response
import csv
import os
from datetime import datetime

application = Flask(__name__) 
CSV_FILE = 'expenses.csv'  # Relative path for Render

# ------------------ CSV Operations ------------------ #
def read_expenses():
    """Read all expenses from CSV."""
    expenses = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                expenses.append(row)
    return expenses

def write_expenses(expenses):
    """Write all expenses to CSV."""
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["date", "description", "amount"])
        writer.writeheader()
        writer.writerows(expenses)

# ------------------ Routes ------------------ #

# Home page: list all expenses
@app.route('/')
def index():
    expenses = read_expenses()
    return render_template('index.html', expenses=expenses)

# Add a new expense
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        date = request.form['date'] or datetime.today().strftime('%Y-%m-%d')
        description = request.form['description']
        amount = request.form['amount']

        # Read existing expenses
        expenses = read_expenses()
        # Add new expense
        expenses.append({'date': date, 'description': description, 'amount': amount})
        # Write back to CSV
        write_expenses(expenses)

        return redirect(url_for('index'))

    return render_template('add_expense.html')

# Delete an expense by index
@app.route('/delete/<int:index>')
def delete_expense(index):
    expenses = read_expenses()
    if index < len(expenses):
        del expenses[index]
        write_expenses(expenses)
    return redirect(url_for('index'))

# Export expenses to CSV
@app.route('/export')
def export_csv():
    expenses = read_expenses()
    output = "date,description,amount\n"
    for expense in expenses:
        output += f"{expense['date']},{expense['description']},{expense['amount']}\n"
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=expenses.csv"}
    )

# ------------------ Main ------------------ #
if __name__ == '__main__':
    app.run()


