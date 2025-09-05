from flask import Flask, render_template, request, redirect, url_for, Response
import csv
import os
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# Path to your expenses CSV file
CSV_FILE = 'expenses.csv'

# Read expenses from CSV
def read_expenses():
    expenses = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                expenses.append(row)
    return expenses

# Write expenses to CSV
def write_expenses(expenses):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["date", "description", "amount"])
        writer.writeheader()
        writer.writerows(expenses)

# Route to add a new expense
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        date = request.form['date'] or datetime.today().strftime('%Y-%m-%d')
        description = request.form['description']
        amount = request.form['amount']

        # Read existing expenses
        expenses = read_expenses()

        # Add the new expense
        expenses.append({
            'date': date,
            'description': description,
            'amount': amount
        })

        # Write the updated expenses to CSV
        write_expenses(expenses)

        return redirect(url_for('index'))

    return render_template('add_expense.html')

# Route to view all expenses
@app.route('/')
def index():
    expenses = read_expenses()
    return render_template('index.html', expenses=expenses)

# Route to delete an expense
@app.route('/delete/<int:index>', methods=['GET'])
def delete_expense(index):
    expenses = read_expenses()
    if index < len(expenses):
        del expenses[index]  # Remove the expense by index
        write_expenses(expenses)  # Update the CSV

    return redirect(url_for('index'))

# Route to export expenses to CSV
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

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)

