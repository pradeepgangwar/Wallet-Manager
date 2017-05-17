from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from database_setup import Base, User, Month, Transactions
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import exists
from forms import SignupForm, LoginForm

app = Flask(__name__)
bcrypt = Bcrypt(app)

engine = create_engine('sqlite:///mywallet.db')


Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).filter(User.id == int(user_id)).first()

@app.before_request
def before_request():
    g.user = current_user

# JSON return function for APIs
@app.route('/month/<int:month_id>/data/JSON')
def monthTransctionJSON(month_id):
    month = session.query(Month).filter_by(id=month_id).one()
    items = session.query(Transactions).filter_by(month_id=month_id).all()
    return jsonify(Transactions=[i.serialize for i in items])


# Home page of Site
@app.route('/', methods = ['POST', 'GET'])
@app.route('/wallet', methods = ['POST', 'GET'])
def wallet():
    error = None
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html' ,error = error)

#Login_Page
@app.route('/login', methods = ['POST', 'GET'])
def login():
    error = None
    form  = LoginForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        registered_user = session.query(User).filter_by(username = username).first()
        if registered_user is not None and bcrypt.check_password_hash(registered_user.password, password):
            login_user(registered_user)
            return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials ! Try Again'
    return render_template('login.html',form = form ,error = error)

#Logout user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('wallet')) 

#Home page of User
@app.route('/home')
@login_required
def home():
    error = None
    months = session.query(Month).filter_by(user_id = current_user.id).all()
    if not months:
        error = 'No Months Available'
    return render_template('Home.html', months = months, error = error)

#Signup page of User
@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    error  = None
    form  = SignupForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            username = request.form['username']
            user = session.query(exists().where(User.username == username)).scalar()
            if (user == False):
                newUser = User(username = request.form['username'], password = bcrypt.generate_password_hash(request.form['password']),
                     email = request.form['email'])
                session.add(newUser)
                session.commit()
                error = 'User created successfully.'
            else:
                error = 'Username already taken'
                return render_template('signup.html',form = form, error = error)
        else:
            return render_template('signup.html', form = form, error = error)
    return render_template('signup.html', form = form, error = error)

@app.route('/update-email', methods = ['POST', 'GET'])
@login_required
def updateemail():
    error = None
    return render_template('cons.html',error = error)

@app.route('/update-pass', methods = ['POST', 'GET'])
@login_required
def updatepass():
    error = None
    return render_template('cons.html',error = error)

# Add a new month to database
@app.route('/month/new', methods = ['POST', 'GET'])
@login_required
def monthNew():
    if request.method == 'POST':
        newData = Month(name = request.form['name'],year = request.form['year'], open_bal = request.form['balance'],
            curr_bal = request.form['balance'],credits = 0, debits = 0, transactions = 0)
        newData.user = g.user
        session.add(newData)
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('newMonth.html')

#Delete a month from database
@app.route('/month/<int:month_id>/delete', methods = ['POST', 'GET'])
@login_required
def monthDelete(month_id):
    deleteMonth = session.query(Month).filter_by(id = month_id).first()
    deleteTransaction = session.query(Transactions).filter_by(month_id = month_id).all()
    if request.method == 'POST':
        session.delete(deleteMonth)
        for i in deleteTransaction:
            session.delete(i)
        session.commit()
        return redirect(url_for('wallet'))
    else:
        if (deleteMonth == None):
            return render_template('unexist.html')
        if (deleteMonth.user_id != current_user.id):
            return render_template('unauthorize.html')    
        return render_template('deleteMonth.html', month_id = month_id, i = deleteMonth)

#Edit Month
@app.route('/month/<int:month_id>/edit', methods = ['POST', 'GET'])
@login_required
def monthEdit(month_id):
    editMonth = session.query(Month).filter_by(id = month_id).first()
    if (editMonth == None):
            return render_template('unexist.html')
    if (editMonth.user_id != current_user.id):
        return render_template('unauthorize.html')
    return render_template('editMonth.html', month_id = month_id, i= editMonth)


#see all transactions of a month
@app.route('/month/<int:month_id>/')
@login_required
def transactions(month_id):
    month = session.query(Month).filter_by(id = month_id).first()
    if (month != None):
        items = session.query(Transactions).filter_by(month_id = month.id, name = "Debit")
        items1 = session.query(Transactions).filter_by(month_id = month.id, name="Credit")
    if (month == None):
            return render_template('unexist.html')
    if (month.user_id != current_user.id):
        return render_template('unauthorize.html')
    return render_template('transaction.html', month = month, items = items, items1 = items1)

#Add a new Transactions
@app.route('/month/<int:month_id>/new/', methods = ['GET','POST'])
@login_required
def newTransaction(month_id):
    if request.method == 'POST':
        newItem = Transactions(name = request.form['option'], description = request.form['description'],cost = request.form['price'],month_id = month_id)
        newItem.user = g.user
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
        month = session.query(Month).filter_by(id = month_id).first()
        if (month == None):
            return render_template('unexist.html')
        if (month.user_id != current_user.id):
            return render_template('unauthorize.html')
        return render_template('newTransaction.html', month_id = month_id)


# Delete a Transaction
@app.route('/month/<int:month_id>/<int:transactions_id>/delete/', methods = ['GET', 'POST'])
@login_required
def deleteTransaction(month_id, transactions_id):
    deleteTransaction = session.query(Transactions).filter_by(id = transactions_id).first()
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
        month = session.query(Month).filter_by(id = month_id).first()
        if (deleteTransaction == None):
            return render_template('unexist.html')
        if (month == None):
            return render_template('unexist.html')
        if (deleteTransaction.month_id != month_id):
            return render_template('unauthorize.html')
        if (month.user_id != current_user.id or deleteTransaction.user_id != current_user.id):
            return render_template('unauthorize.html')
        return render_template('deleteTransaction.html', month_id = month_id, transactions_id = transactions_id, i = deleteTransaction)


#Edit Transaction
@app.route('/month/<int:month_id>/<int:transactions_id>/edit/', methods = ['POST', 'GET'])
@login_required
def transactionEdit(month_id, transactions_id):
    editTransaction = session.query(Transactions).filter_by(id = transactions_id).first()
    if request.method == 'POST':
        if editTransaction.name == 'Debit':
            if request.form['option'] == 'Debit':
                month = session.query(Month).filter_by(id = month_id).one()
                editTransaction.name = request.form['option']
                month.curr_bal += int(editTransaction.cost)
                month.curr_bal -= int(request.form['price'])
                month.debits -= int(editTransaction.cost)
                month.debits += int(request.form['price'])
                editTransaction.cost = int(request.form['price'])
                editTransaction.description = request.form['description']
            if request.form['option'] == 'Credit':
                month = session.query(Month).filter_by(id = month_id).one()
                editTransaction.name = request.form['option']
                month.curr_bal += int(editTransaction.cost)
                month.curr_bal += int(request.form['price'])
                month.debits -= int(editTransaction.cost)
                month.credits += int(request.form['price'])
                editTransaction.cost = request.form['price']
                editTransaction.description = request.form['description']
        if editTransaction.name == 'Credit':
            if request.form['option'] == 'Debit':
                month = session.query(Month).filter_by(id = month_id).one()
                editTransaction.name = request.form['option']
                month.curr_bal -= int(editTransaction.cost)
                month.curr_bal -= int(request.form['price'])
                month.credits -= int(editTransaction.cost)
                month.debits += int(request.form['price'])
                editTransaction.cost = int(request.form['price'])
                editTransaction.description = request.form['description']
            if request.form['option'] == 'Credit':
                month = session.query(Month).filter_by(id = month_id).one()
                editTransaction.name = request.form['option']
                month.curr_bal -= int(editTransaction.cost)
                month.curr_bal += int(request.form['price'])
                month.credits -= int(editTransaction.cost)
                month.credits += int(request.form['price'])
                editTransaction.cost = request.form['price']
                editTransaction.description = request.form['description']
        session.add(editTransaction)
        session.commit()
        return redirect(url_for('transactions', month_id = month_id))
    else: 
        month = session.query(Month).filter_by(id = month_id).first()
        if (editTransaction == None):
            return render_template('unexist.html')
        if (month == None):
            return render_template('unexist.html')
        if (editTransaction.month_id != month_id):
            return render_template('unauthorize.html')
        if (month.user_id != current_user.id or editTransaction.user_id != current_user.id):
            return render_template('unauthorize.html')
        return render_template('transactionEdit.html', month_id = month_id,transactions_id = transactions_id, i= editTransaction)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
