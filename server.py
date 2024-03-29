from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb  import MySQL
import numpy as np

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
        cur.execute(f"SELECT username,email,password,id,sub1,sub2,sub3 FROM student WHERE email='{email}'")#find where is the email
        user = cur.fetchone()
        cur.close()
        if user and pwd ==user[2]:
            session['username']=user[0]
            session['email']=user[1]
            session['id']=user[3]
            session['sub1']=user[4]
            session['sub2']=user[5]
            session['sub3']=user[6]
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
    if 'sub1' in session and 'sub2' in session and 'sub3' in session:
        sub1_int = int(session.get('sub1', 0))
        sub2_int = int(session.get('sub2', 0))
        sub3_int = int(session.get('sub3', 0))
        marks_array = np.array([sub1_int, sub2_int, sub3_int])
        average = np.mean(marks_array)
        total = sub1_int+sub2_int+sub3_int
        session['average']=average
        gpa = np.interp(total, [0, 300], [0, 4])
        session['gpa'] = gpa
    return render_template('profile.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    success = False
    if request.method == 'POST':
        id = session['id']
        username = request.form['username']
        email = request.form['email']
        sub1 = request.form['sub1']
        sub2 = request.form['sub2']
        sub3 = request.form['sub3']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE student SET username=%s, email=%s, sub1=%s, sub2=%s, sub3=%s WHERE id=%s",
                    (username, email, sub1, sub2, sub3, id))
        mysql.connection.commit()
        cur.close()
        success = True
        session['sub1']=sub1
        session['sub2']=sub2
        session['sub3']=sub3
        session['username']=username
        session['email']=email
        return redirect(url_for('profile',id=id))
    return render_template('profile.html', success=success)


@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('home'))

if  __name__ == '__main__':
    app.run(debug = True)