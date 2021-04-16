from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import shutil
from flask import Flask,jsonify,json
import os
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from keras.models import load_model
import random


def clean_up_sentence(sentence, bot_name):
    intents = json.loads(open(bot_name+'/intents.json').read())
    words = pickle.load(open(bot_name+'/words.pkl','rb'))
    classes = pickle.load(open(bot_name+'/classes.pkl','rb'))
    model = load_model(bot_name+'/chatbot_model.h5')
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, bot_name, show_details=True):
    intents = json.loads(open(bot_name+'/intents.json').read())
    words = pickle.load(open(bot_name+'/words.pkl','rb'))
    classes = pickle.load(open(bot_name+'/classes.pkl','rb'))
    model = load_model(bot_name+'/chatbot_model.h5')
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence, bot_name)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model, bot_name):
    intents = json.loads(open(bot_name+'/intents.json').read())
    words = pickle.load(open(bot_name+'/words.pkl','rb'))
    classes = pickle.load(open(bot_name+'/classes.pkl','rb'))
    model = load_model(bot_name+'/chatbot_model.h5')
    # filter out predictions below a threshold
    p = bow(sentence, words, bot_name, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json, bot_name):
    intents = json.loads(open(bot_name+'/intents.json').read())
    words = pickle.load(open(bot_name+'/words.pkl','rb'))
    classes = pickle.load(open(bot_name+'/classes.pkl','rb'))
    model = load_model(bot_name+'/chatbot_model.h5')
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg,bot_name):
    intents = json.loads(open(bot_name+'/intents.json').read())
    words = pickle.load(open(bot_name+'/words.pkl','rb'))
    classes = pickle.load(open(bot_name+'/classes.pkl','rb'))
    model = load_model(bot_name+'/chatbot_model.h5')
    ints = predict_class(msg, model, bot_name)
    res = getResponse(ints, intents, bot_name)
    return res


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
			if pwd == repwd and user!=User.query.filter_by(user=user).first():
				newUser = User(user=user, password=pwd)
			else:
				return "both passwords are different or username taken"

			try:
				db.session.add(newUser)
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
	bots = ChatBot.query.order_by(ChatBot.date_created).all()

	return render_template('user.html', bots=bots)

@app.route('/createbot/<pack>/<bot_name>', methods=['GET', 'POST'])
def createbot(pack, bot_name):
	if request.method == 'POST':
		
		try:
			data=json.loads(pack)
			fileName=bot_name+"/intents.json"
			with open(fileName, 'w') as outfile:
    				json.dump(data, outfile)

			exec = "python3 "+bot_name+"/train_chatbot.py"

			os.system('python3 tmp/CopyPasteFolderTest.py')
			bots = ChatBot.query.order_by(ChatBot.date_created).all()

			return render_template('admin.html', bots=bots)

		except:
			return 'Database Error'

	else:

		

		return render_template("error.html")

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

@app.route('/viewbot/<bot_name>')
def viewbot(bot_name):
	

	chatLog=" "

	return render_template("viewbot.html", bot_name=bot_name, chatLog=chatLog)

@app.route('/chatbot/<bot_name>/<chatLog>', methods=['GET', 'POST'])
def chatbot(bot_name,chatLog):
	if request.method == 'POST':
		msg = request.form['msg']
		res = chatbot_response(msg, bot_name)

		chatLog=chatLog +"You: "+msg+"<br>Bot: "+res+"<br>"

		return render_template("viewbot.html", bot_name=bot_name, chatLog=chatLog)
		

	else:

		
		chatLog=""
		return render_template("viewbot.html", bot_name=bot_name, chatLog=chatLog)


if __name__ == "__main__":
	app.run(debug=True)

