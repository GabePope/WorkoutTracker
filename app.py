from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)

DATABASE = 'workout.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/")
def hello_world():
    rows = query_db('select * from TopSet')
    print(rows[0]['TopSetId'])
    return render_template('index.html', name='peter')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
