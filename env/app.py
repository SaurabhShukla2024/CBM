from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app =  Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///test.db'
db = SQLAlchemy(app)

class Admin(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	admin = db.Column(db.String(200), nullable=False)
	password = db.Column(db.String(200), nullable=False)
	bots = db.relationship('ChatBot', backref = 'owner')

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
	owner_id = db.Column(db.Integer, db.ForeignKey('admin.id'))


	def __repr__(self):
		return '<Task %r>' % self.id

@app.route('/')

def index():

	# if request.method == 'POST':
	# 	task_content = request.form['content']
	# 	new_task = Todo(content=task_content)

	# 	try:
	# 		db.session.add(new_task)
	# 		db.session.commit()

	# 		return redirect('/')

	# 	except:
	# 		return 'Database Error'

	# else:

	# 	tasks = Todo.query.order_by(Todo.date_created).all()

		return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])

def login():
	# task_to_delete = Todo.query.get_or_404(id)

	# try:
	# 	db.session.delete(task_to_delete)
	# 	db.session.commit()

	# 	return redirect('/')

	# except:
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

	# task = Todo.query.get_or_404(id)

	# if request.method == 'POST':
	# 	task.content = request.form['content']
	# 	try:
	# 		db.session.commit()
	# 		return redirect('/')
	# 	except:
	# 		return "Update Error"
	# else:

	if request.method == 'POST':
		if request.form['usertype'] == 'admin':
			admin = request.form['username']
			pwd = request.form['password']
			repwd = request.form['repassword']
			if pwd == repwd:
				newAdmin = Admin(admin=admin, password=pwd)
			else:
				return "both passwords are different"

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
			if pwd == repwd:
				newUser = User(user=user, password=pwd)
			else:
				return "both passwords are different"

			try:
				db.session.add(newAdmin)
				db.session.commit()

				return redirect('/login')

			except:
				return 'Database Error'
	else:
		return render_template('signup.html')



	

if __name__ == "__main__":
	app.run(debug=True)

