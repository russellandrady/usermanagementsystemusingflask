from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb  import MySQL

app=Flask(__name__)
app.secret_key = 'your-secret-key'

#mysqlconfiguration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB'] = 'amccdb'

mysql = MySQL(app)
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/signin', methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        email=request.form['email']
        pwd=request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT username,email,password,id FROM student WHERE email='{email}'")#find where is the email
        user = cur.fetchone()
        cur.close()
        if user and pwd ==user[2]:
            session['username']=user[0]
            session['id']=user[3]
            return redirect(url_for('profile',id=session['id']))
        else:
            return render_template('signin.html', error='invalid data')
    else:
        return render_template('signin.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    reg=False
    if request.method =='POST':
        username = request.form['username']
        email = request.form['email']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("insert into student (username, email, password) VALUES (%s, %s, %s)", (username, email, pwd))
        mysql.connection.commit()
        cur.close()
        reg=True
    return render_template('register.html',reg=reg)

@app.route('/profile/<int:id>')
def profile(id):
    return render_template('profile.html')


if  __name__ == '__main__':
    app.run(debug = True)