from flask import Flask, flash, render_template, request, redirect, url_for, session, send_from_directory
from flask_mysqldb  import MySQL
import numpy as np
import os
from flask import jsonify
from werkzeug.utils import secure_filename

app=Flask(__name__)
app.secret_key = 'your-secret-key'

#mysqlconfiguration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB'] = 'amccdb'

#folder configurations
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/signin', methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        role = request.form['role']  # Assuming you have a select input for role

        cur = mysql.connection.cursor()

        # Check if the user exists in either the student or company table based on role
        if role == 'Student':
            cur.execute(f"SELECT username, email, password, id, sub1, sub2, sub3, cv_path FROM student WHERE email='{email}'")
        elif role == 'Company':
            cur.execute(f"SELECT username, email, password, id FROM company WHERE email='{email}'")

        user = cur.fetchone()

        if user and pwd == user[2]:  # Check if the user exists and password matches
            session['username'] = user[0]
            session['email'] = user[1]
            session['id'] = user[3]
            session['role'] = role
            
            # For students
            if role == 'Student':
                session['sub1'] = user[4]
                session['sub2'] = user[5]
                session['sub3'] = user[6]
                if user[7] is not None:
                    session['cvname'] = os.path.basename(user[7])
            
            # Redirect to the appropriate profile page based on role
            if role == 'Student':
                cur.close()
                return redirect(url_for('profile', id=session['id']))
            elif role == 'Company':
                cur.execute("SELECT title, description FROM job WHERE user_id = %s", (session['id'],))
                jobs = cur.fetchall()
                session['jobs'] = jobs
                cur.close()
                return redirect(url_for('comprofile', id=session['id']))
        else:
            return render_template('signin.html', error='Invalid data')
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
        role = request.form['role']
        if role == 'Student':
            cur.execute("insert into student (username, email, password) VALUES (%s, %s, %s)", (username, email, pwd))
        else:
            cur.execute("insert into company (username, email, password) VALUES (%s, %s, %s)", (username, email, pwd))
        mysql.connection.commit()
        cur.close()
        reg=True
    return render_template('register.html',reg=reg)

@app.route('/profile/<int:id>')
def profile(id):
    if session.get('sub1') is not None and session.get('sub2') is not None and session.get('sub3') is not None:
        sub1_int = int(session.get('sub1', 0))
        sub2_int = int(session.get('sub2', 0))
        sub3_int = int(session.get('sub3', 0))
        marks_array = np.array([sub1_int, sub2_int, sub3_int])
        average = round(np.mean(marks_array),2)
        gpa = round(np.interp(average, [0, 100], [0, 4]),2)
        session['average']=average
        session['gpa'] = gpa
    return render_template('profile.html')
@app.route('/comprofile/<int:id>')
def comprofile(id):
    return render_template('comprofile.html')
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
@app.route('/compedit', methods=['GET', 'POST'])
def compedit():
    success = False
    if request.method == 'POST':
        id = session['id']
        username = request.form['username']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE company SET username=%s, email=%s WHERE id=%s",
                    (username, email, id))
        mysql.connection.commit()
        cur.close()
        success = True
        session['username']=username
        session['email']=email
        return redirect(url_for('comprofile',id=id))
    return render_template('comprofile.html', success=success)
@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'cv' not in request.files:
        #flash('No file part')
        return redirect(request.url)
    
    cv_file = request.files['cv']
    
    if cv_file.filename == '':
        #flash('No selected file')
        #session['nofile']=True
        return render_template('profile.html', nofile=True)
     # Delete the old CV file if it exists
    cur = mysql.connection.cursor()
    cur.execute("SELECT cv_path FROM student WHERE id = %s", (session['id'],))
    old_cv_path = cur.fetchone()
    if old_cv_path is not None:
        try:
            os.remove(old_cv_path[0])  # Delete the file
        except (FileNotFoundError, TypeError):
            pass  # File not found or invalid path, nothing to delete

    if cv_file:
        # Generate a unique filename using the user ID
        user_name = session['username']
        user_id = session['id']
        original_filename = secure_filename(cv_file.filename)
        _, file_extension = os.path.splitext(original_filename)
        new_filename = f"user_{user_name}_{user_id}_{original_filename}"
        
        # Save the file with the new filename
        cv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        
        # Update the database with the file path for the current user
        cv_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        cur.execute("UPDATE student SET cv_path = %s WHERE id = %s", (cv_path, session['id']))
        mysql.connection.commit()
        cur.close()
        session['cvname']=new_filename
        #flash('CV uploaded successfully')
        return redirect(url_for('profile',id=session['id']))
@app.route('/download_cv/<filename>', methods=['GET'])
def download_cv(filename):
    cv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/create_job', methods=['POST'])
def create_job():
    if request.method == 'POST':
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        
        # Insert into job table
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO job (user_id, title, description) VALUES (%s, %s, %s)", (session['id'], job_title, job_description))
        mysql.connection.commit()
        
        # Fetch the updated list of jobs
        cur.execute("SELECT title, description FROM job WHERE user_id = %s", (session['id'],))
        jobs = cur.fetchall()
        session['jobs'] = jobs
        cur.close()
        
        return redirect(url_for('comprofile',id=session['id']))
    

@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('home'))

if  __name__ == '__main__':
    app.run(debug = True)