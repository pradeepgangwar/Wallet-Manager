from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Month, Transactions

app = Flask(__name__)

engine = create_engine('sqlite:///mywallet.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON return function for APIs
@app.route('/month/<int:month_id>/data/JSON')
def monthTransctionJSON(month_id):
    month = session.query(Month).filter_by(id=month_id).one()
    items = session.query(Transactions).filter_by(month_id=month_id).all()
    return jsonify(Transactions=[i.serialize for i in items])


# Home page of Site
@app.route('/')
@app.route('/wallet')
def wallet():
    months = session.query(Month).all()
    return render_template('Home.html', months = months)

# Add a new month to database
@app.route('/month/new', methods = ['POST', 'GET'])
def monthNew():
    if request.method == 'POST':
        newData = Month(name = request.form['name'],year = request.form['year'], open_bal = request.form['balance'],
            curr_bal = request.form['balance'],credits = 0, debits = 0, transactions = 0)
        session.add(newData)
        session.commit()
        return redirect(url_for('wallet'))
    else:
        return render_template('newMonth.html')

#Delete a month from database
@app.route('/month/<int:month_id>/delete', methods = ['POST', 'GET'])
def monthDelete(month_id):
    deleteMonth = session.query(Month).filter_by(id = month_id).one()
    if request.method == 'POST':
        session.delete(deleteMonth)
        session.commit()
        return redirect(url_for('wallet'))
    else:
        return render_template('deleteMonth.html', month_id = month_id, i = deleteMonth)

#Edit Month
@app.route('/month/<int:month_id>/edit', methods = ['POST', 'GET'])
def monthEdit(month_id):
    editMonth = session.query(Month).filter_by(id = month_id).one()
    return render_template('editMonth.html', month_id = month_id, i= editMonth)


#see all transactions of a month
@app.route('/month/<int:month_id>/')
def transactions(month_id):
    month = session.query(Month).filter_by(id = month_id).one()
    items = session.query(Transactions).filter_by(month_id = month.id, name = "Debit")
    items1 = session.query(Transactions).filter_by(month_id = month.id, name="Credit")
    return render_template('transaction.html', month = month, items = items, items1 = items1)

#Add a new Transactions
@app.route('/month/<int:month_id>/new/', methods = ['GET','POST'])
def newTransaction(month_id):
    if request.method == 'POST':
        newItem = Transactions(name = request.form['option'], description = request.form['description'],cost = request.form['price'],month_id = month_id)
        if request.form['option'] == 'Debit':
            month = session.query(Month).filter_by(id = month_id).one()
            month.curr_bal = month.curr_bal - int(request.form['price'])
            month.debits = month.debits + int(request.form['price'])
            month.transactions = month.transactions+1;
        if request.form['option'] == 'Credit':
            month = session.query(Month).filter_by(id = month_id).one()
            month.curr_bal = month.curr_bal + int(request.form['price'])
            month.credits = month.credits + int(request.form['price'])
            month.transactions = month.transactions+1;
        session.add(newItem)
        session.commit()
        return redirect(url_for('transactions', month_id = month_id))
    else:
        return render_template('newTransaction.html', month_id = month_id)


# Delete a Transaction
@app.route('/month/<int:month_id>/<int:transactions_id>/delete/', methods = ['GET', 'POST'])
def deleteTransaction(month_id, transactions_id):
    deleteTransaction = session.query(Transactions).filter_by(id = transactions_id).one()
    if request.method == 'POST':
        if deleteTransaction.name == 'Debit':
            month = session.query(Month).filter_by(id = month_id).one()
            month.curr_bal = month.curr_bal + int(deleteTransaction.cost)
            month.debits = month.debits - int(deleteTransaction.cost)
            month.transactions = month.transactions-1;
        if deleteTransaction.name == 'Credit':
            month = session.query(Month).filter_by(id = month_id).one()
            month.curr_bal = month.curr_bal - int(deleteTransaction.cost)
            month.credits = month.credits - int(deleteTransaction.cost)
            month.transactions = month.transactions-1;
        session.delete(deleteTransaction)
        session.commit()
        return redirect(url_for('transactions', month_id = month_id))
    else:
        return render_template('deleteTransaction.html', month_id = month_id, transactions_id = transactions_id, i = deleteTransaction)


#Edit Transaction
@app.route('/month/<int:month_id>/<int:transactions_id>/edit/', methods = ['POST', 'GET'])
def transactionEdit(month_id, transactions_id):
    editTransaction = session.query(Transactions).filter_by(id = transactions_id).one()
    return render_template('transactionEdit.html', month_id = month_id,transactions_id = transactions_id, i= editTransaction)

'''@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods = ['GET' , 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editMenuItem.html', restaurant_id = restaurant_id, menu_id = menu_id, i = editedItem)
'''
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)