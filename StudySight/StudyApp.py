from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template, g
import sqlite3

from flask import request
from flask import url_for
from requests import session

app = Flask(__name__)
app.debug = True
app.database = "C:\\Users\\15mik_000\\PycharmProjects\\StudyApp\\room.db"

app.secret_key ="mike"

def connect_db():
    return sqlite3.connect(app.database)



@app.route('/')
def home():
    '''
    g.db = connect_db()
    cur = g.db.execute('select * from posts')
    posts = [dict(title=row[0],
                  description=row[1]) for row in cur.fetchall()]
    g.db.close()'''
    return render_template(
        'google.html')

@app.route('/places')
def study():
    g.db = connect_db()
    cur = g.db.execute('select * from locations')
    locations = [dict(name=row[0],
                  latitude=row[1],longitude=row[2]) for row in cur.fetchall()]
    g.db.close()
    return render_template(
        'areas.html', locations=locations)

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error ='Invalid credentials'
        else:
            session['logged_in']= True
            flash('You were just logged in!')
            return redirect(url_for('home'))

    return render_template('login.html',error=error)

@app.route('/logout')
def logout():
    session().pop('logged_in',None)
    flash("You were just logged out!")
    return  redirect(url_for('study'))

@app.route('/run')
def run():
    g.db = connect_db()
    cur = g.db.execute('select * from room')
    room = [dict(name=row[0],
                  latitude=row[1],longitude=row[2],capacity=row[3],actualCap=row[4],picture=row[5],description=row[6]) for row in cur.fetchall()]
    g.db.close()
    return render_template(
        'index.html', room=room)



if __name__ == '__main__':
    app.run()