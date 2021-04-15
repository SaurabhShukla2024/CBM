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
		if request.form['usertype'] == "admin":
			adminv = Admin.query.filter_by(admin=request.form['username']).first()
			passwordv = Admin.query.filter_by(password=request.form['password']).first()
			try:	
				
				if adminv.id==passwordv.id:
					bots = ChatBot.query.order_by(ChatBot.date_created).all()
					return render_template('admin.html', bots=bots)
				else:
					return "incorrect username password pair"
			except:
				return "incorrect UP pair"

		elif request.form['usertype'] == "user":
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


			data = {}
			data['intents']=[]

			pack=json.dumps(data)

			return render_template('createbot.html', bot_name=bot_name, pack=pack)

		except:
			return 'Dat'

	else:

		bots = ChatBot.query.order_by(ChatBot.date_created).all()

		return render_template('admin.html', bots=bots)

@app.route('/user', methods=['GET', 'POST'])

def user():

	return render_template('user.html')

@app.route('/createbot/<pack>/<bot_name>', methods=['GET', 'POST'])

def createbot(pack, bot_name):
	if request.method == 'POST':
		
		try:
			data=json.loads(pack)
			fileName=bot_name+"/intents.json"
			with open(fileName, 'w') as outfile:
    				json.dump(data, outfile)
			

			return redirect('/')

		except:
			return 'Database Error'

	else:

		data = {}
		data["intents"]=[]

		return render_template('createbot.html',data=data)

@app.route('/addintent/<pack>/<bot_name>', methods=['GET', 'POST'])

def addintent(pack, bot_name):
	if request.method == 'POST':
		data=json.loads(pack)
		data['intents'].append({"tag":request.form["tag"] ,
	 		"patterns" : [request.form["pattern1"], request.form["pattern2"], request.form["pattern3"], request.form["pattern4"], request.form["pattern5"]],
	 		"responses": [request.form["response1"], request.form["response2"], request.form["response3"], request.form["response4"], request.form["response5"]],
	 		"context": [request.form["context"]]
		 })

		pack=json.dumps(data)
		return render_template('createbot.html', bot_name=bot_name, pack=pack)
	else:

		return "intents"

	

if __name__ == "__main__":
	app.run(debug=True)

