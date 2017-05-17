import sys,os
from sqlalchemy import Column ,ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key = True)
	username = Column(String(250), nullable = False)
	password = (Column(String(450),nullable = False))
	email = Column(String(250),nullable = False)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

class Month(Base):
	__tablename__ = 'month'
	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	curr_bal = Column(Integer, nullable = False)
	open_bal = Column(Integer, nullable = False)
	debits = Column(Integer, nullable = False)
	credits = Column(Integer, nullable = False)
	transactions = Column(Integer, nullable = False)
	year = Column(String(250), nullable = False)
	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship(User)
	
class Transactions(Base):
	__tablename__ = 'transactions'
	name = Column(String(250), nullable = False)
	id = Column(Integer, primary_key = True)
	description = Column(String(250))
	cost = Column(String(8))
	month_id = Column(Integer, ForeignKey('month.id'))
	month = relationship(Month)
	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship(User)

	@property
	def serialize(self):

		return {
			'name': self.name,
			'id' : self.id,
			'description': self.description,
			'amount': self.cost,
		}


engine = create_engine('sqlite:///mywallet.db')

Base.metadata.create_all(engine)
