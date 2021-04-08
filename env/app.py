from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import shutil
from flask import Flask,jsonify,json



app =  Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///test.db'
db = SQLAlchemy(app)

class Admin(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	admin = db.Column(db.String(200), nullable=False)
	password = db.Column(db.String(200), nullable=False)

	def __repr__(self):
		return '<Task %r>' % self.id


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String(200), nullable=False)
	password = db.Column(db.String(200), nullable=False)

	def __repr__(self):
		return '<Task %r>' % self.id

class ChatBot(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	bot = db.Column(db.String(200), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Task %r>' % self.id

@app.route('/')

def index():

		return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])

def login():

	if request.method == 'POST':
		if request.form['usertype'] == 'admin':
			admin = Admin.query.filter_by(admin=request.form['username']).first()
			password = Admin.query.filter_by(password=request.form['password']).first()
			if admin.id==password.id:
				return redirect('/admin')
			else:
				return "incorrect username password pair"

		elif request.form['usertype'] == 'user':
			user = User.query.filter_by(user=request.form['username']).first()
			password = User.query.filter_by(password=request.form['password']).first()
			if user.id==password.id:
				return redirect('/user')
			else:
				return "incorrect username password pair"
		else:
			return "Error logging in"
	else:
		return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])

def signup():

	if request.method == 'POST':
		if request.form['usertype'] == 'admin':
			admin = request.form['username']
			pwd = request.form['password']
			repwd = request.form['repassword']
			if pwd == repwd and admin!=Admin.query.filter_by(admin=admin).first():
				newAdmin = Admin(admin=admin, password=pwd)
			else:
				return "both passwords are different or username taken"

			try:
				db.session.add(newAdmin)
				db.session.commit()

				return redirect('/login')

			except:
				return 'Database Error'

		elif request.form['usertype'] == 'user':
			user = request.form['username']
			pwd = request.form['password']
			repwd = request.form['repassword']
			if pwd == repwd and user!=User.query.filter_by(user=user).first().user:
				newUser = User(user=user, password=pwd)
			else:
				return "both passwords are different or username taken"

			try:
				db.session.add(newAdmin)
				db.session.commit()

				return redirect('/login')

			except:
				return 'Database Error'
	else:
		return render_template('signup.html')

@app.route('/admin', methods=['GET', 'POST'])

def admin():
	if request.method == 'POST':
		bot_name = request.form['botName']
		botName = ChatBot(bot=bot_name)

		try:

			shutil.copytree('baseCB', bot_name)
			db.session.add(botName)
			db.session.commit()

			return render_template('createbot,html', bot_name=bot_name)

		except:
			return 'Dat'

	else:

		bots = ChatBot.query.order_by(ChatBot.date_created).all()

		return render_template('admin.html', bots=bots)

@app.route('/user', methods=['GET', 'POST'])

def user():

	return render_template('user.html')

@app.route('/createbot', methods=['GET', 'POST'])

def createbot():
	if request.method == 'POST':
		
		try:
			

			return redirect('/createbot')

		except:
			return 'Database Error'

	else:

		

		return render_template('createbot.html')


	

if __name__ == "__main__":
	app.run(debug=True)

