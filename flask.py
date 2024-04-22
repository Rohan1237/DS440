from flask import Flask, render_template, request, redirect, session, url_for
from sqlite3 import *
from flask_mail import Mail, Message
import smtplib
from random import randrange
import flask
import os

app = Flask(__name__)
app.secret_key = "rohanheart"
# Function to create the 'user' table
def create_user_table():
    try:
        con = connect("monicaheart.db")
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        con.commit()
    except Exception as e:
        print("Error creating user table:", e)
    finally:
        if con:
            con.close()

# Call the function to create the table when the application starts
create_user_table()

@app.route("/")
def home():
	if 'username' in session:
		return render_template("home.html", name = session['username'])
	else:
		return redirect(url_for('signup'))

@app.route("/find")
def find():
	if 'username' in session:
		return render_template("find.html", name = session['username'])
	else:
		return redirect(url_for('home'))

@app.route("/check", methods = ["POST"])
def check():
	if request.method == "POST":
		if 'username' in session:
			name = session['username']
		age = float(request.form["age"])
		r1 = request.form["r1"]
		if r1 == "1":
			cp = 1
		elif r1 == "2":
			cp = 2
		elif r1 == "3":
			cp = 3
		else:
			cp = 4
		BP = float(request.form["BP"])
		CH = float(request.form["CH"])
		maxhr = float(request.form["maxhr"])
		STD = float(request.form["STD"])
		fluro = float(request.form["fluro"])
		Th = float(request.form["Th"])
		d = [[age, cp, BP, CH, maxhr, STD, fluro, Th]]
		with open("/home/rbp5453/mysite/heartdiseaseprediction.model","rb") as f:
			model = pickle.load(f)
		res = model.predict(d)
		return render_template("find.html", msg = res, name = session['username'])
	else:
		return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        un = request.form["un"]
        pw = request.form["pw"]  # Assuming the password is entered directly without email
        con = None
        try:
            con = connect("monicaheart.db")
            cursor = con.cursor()
            sql = "INSERT INTO user (username, password) VALUES (?, ?)"
            cursor.execute(sql, (un, pw))
            con.commit()
            return render_template("login.html", msg="Successfully signed up!")
        except Exception as e:
            con.rollback()
            return render_template("signup.html", msg="Failed to sign up: " + str(e))
        finally:
            if con:
                con.close()
    else:
        return render_template("signup.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
	if request.method == "POST":
		un = request.form["un"]
		pw = request.form["pw"]
		con = None
		try:
			con = connect("monicaheart.db")
			cursor = con.cursor()
			sql = "select * from user where username = '%s' and password = '%s'"
			cursor.execute(sql % (un,pw))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("login.html", msg = "invalid login")
			else:
				session['username'] = un
				return redirect( url_for('home'))

		except Exception as e:
			msg = "Issue " + str(e)
			return render_template("login.html", msg = msg)
	else:
		return render_template("login.html")

@app.route("/forgot", methods = ["GET", "POST"])
def forgot():
	if request.method == "POST":
		un = request.form["un"]
		em = request.form["em"]
		con = None
		try:
			con = connect('monicaheart.db')
			cursor = con.cursor()
			sql = "select * from user where username = '%s'"
			cursor.execute(sql % (un))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("forgot.html", msg = "invalid login")
			else:
				session['username'] = un
				pw1 = ""
				text = "0123456789"
				for i in range(6):
					pw1 = pw1 + text[randrange(len(text))]
				print(pw1)
				msg = Message("Hello again from HeartDiseasePrediction", sender = "heartdiseaserp@yahoo.com", recipients = [em])
				msg.body = "Greetings from HeartDiseasePredictor! Seems like you forgot your password. Your new password is " + str(pw1)
				mail.send(msg)
				try:
					con = connect("monicaheart.db")
					cursor = con.cursor()
					sql = "update user set password = '%s' where username = '%s'"
					con.execute(sql % (pw1, un))
					con.commit()
					return render_template("login.html", msg = "Password has been mailed to you")
				except Exception as e:
					con.rollback()
					return render_template("forgot.html", msg = "Some Issue: " + str(e))
		except Exception as e:
			msg = "Issue " + str(e)
			return render_template("forgot.html", msg = msg)
	else:
		return render_template("forgot.html")

@app.route("/logout", methods = ["POST"])
def logout():
	session.clear()
	return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug = True, port=7999)