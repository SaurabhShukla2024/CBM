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

@app.route('/', methods=['POST', 'GET'])

def index():

	if request.method == 'POST':
		task_content = request.form['content']
		new_task = Todo(content=task_content)

		try:
			db.session.add(new_task)
			db.session.commit()

			return redirect('/')

		except:
			return 'Database Error'

	else:

		tasks = Todo.query.order_by(Todo.date_created).all()

		return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')

def delete(id):
	task_to_delete = Todo.query.get_or_404(id)

	try:
		db.session.delete(task_to_delete)
		db.session.commit()

		return redirect('/')

	except:

		return 'Error deleting'


@app.route('/update/<int:id>', methods=['GET', 'POST'])

def update(id):

	task = Todo.query.get_or_404(id)

	if request.method == 'POST':
		task.content = request.form['content']
		try:
			db.session.commit()
			return redirect('/')
		except:
			return "Update Error"
	else:
		return render_template('update.html', task=task)



	

if __name__ == "__main__":
	app.run(debug=True)

