from flask import Flask, render_template, send_file, request, redirect, session
import sqlite3 as sql
import os


app = Flask(__name__, static_folder='public', static_url_path='')


# Handle the index (home) page
@app.route('/')
def index():
    return render_template('index.html')

# Handle any files that begin "/course" by loading from the course directory
@app.route('/course/<path:path>')
def base_static(path):
    return send_file(os.path.join(app.root_path, '..', 'course', path))

# Handle any unhandled filename by loading its template
@app.route('/<name>')
def generic(name):
    return render_template(name + '.html')


# Any additional handlers that go beyond simply loading a template
# (e.g., a handler that needs to pass data to a template) can be added here
@app.route('/usersrec',methods = ['POST', 'GET'])
def usersrec():
	if request.method == 'POST':
		try:
			fnm = request.form['fname']
			lnm = request.form['lname']
			enm = request.form['ename']
			unm = request.form['uname']
			pwd = request.form['pwd']
			
			with sql.connect("cs530.db") as con:
				cur = con.cursor()
				cur.execute("INSERT INTO Users (fname,lname,email,uname,pwd) VALUES (?,?,?,?,?)",(fnm,lnm,enm,unm,pwd))
				con.commit()
				msg = "Record successfully added"
				
		except:
			con.rollback()
			msg = "error in insert operation"
				
		finally:
			 return render_template("signup.html",msg = msg)
			 con.close()

@app.route('/regrec',methods = ['POST', 'GET'])
def regrec():
	if request.method == 'POST':
		try:
			styl = request.form['styles']
			ld = request.form['lastdate']
			enm = request.form['ename']
			
			with sql.connect("cs530.db") as con:
				cur = con.cursor()
				cur.execute("INSERT INTO Registration (class,email,enddate) VALUES (?,?,?)",(styl,enm,ld))
				con.commit()
				mesg = "Registered successfully"
				
		except:
			con.rollback()
			mesg = "error in registration"
				
		finally:
			 return render_template("register.html",mesg = mesg)
			 con.close()

@app.route('/profile',methods = ['POST', 'GET'])
def profile():
	con = sql.connect("cs530.db")
	c = con.cursor()
	c.execute("SELECT fname, lname, email FROM Users WHERE uname = ?",(session['user'],))
	info = c.fetchall()
	fname = info[0][0]
	lname = info[0][1]
	email = info[0][2]
	c.execute("SELECT class FROM Registration WHERE email = ?",(email,))
	st = c.fetchone()
	if not st:
		mg = "You have not registered for any classes yet."
		style = " "
	else:
		style = st[0]
		mg = " "
	return render_template('profile.html',fname=fname, lname=lname, email=email, style=style, msg= mg)

@app.route('/logintry',methods = ['POST', 'GET'])
def logintry():
	if request.method == 'POST':
		username = request.form['uname']
		password = request.form['psw']
		if username and password:
			con = sql.connect("cs530.db")
			c = con.cursor()
			c.execute("SELECT uname FROM Users WHERE uname = ?",(username,))
			user = c.fetchone()
			if user[0]:
				c.execute("SELECT uname, pwd FROM Users WHERE uname = ? AND pwd = ?",(username,password))		
				pswrd = c.fetchone()
				if not pswrd:
					msg = "Incorrect credentials"
				elif password == pswrd[0]:
					session['user'] = user[0]
					return redirect('/')
				else:
					msg = "Try again"
			else:
				msg = "User does not exist"
		else:
			msg = "Please fill all the fields"
	return render_template('login.html',msg=msg)

@app.route('/logout',methods = ['POST', 'GET'])
def logout():
	session.clear()
	msg = "You have logged out"
	return render_template('login.html',msg=msg)

if __name__ == "__main__":
	app.secret_key = 'idontknowwhattoset'
	app.run(host='0.0.0.0', port=8144, debug=False)
