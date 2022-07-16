from flask import Flask, render_template, g, redirect, url_for
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
def dashboard():
    rows = query_db('select * from TopSet')
    print(rows[0]['TopSetId'])
    return render_template('index.html', name='peter')


@app.route("/person/<int:person_id>")
def display_workouts_for_person(person_id):
    return render_template('workouts.html', person_id=person_id)


@app.route("/person/<int:person_id>/new_workout")
def new_workout_for_person(person_id):
    # hardcoded workout_id, need to create record in Workout table and return workout_id
    return redirect(url_for('show_workout_for_person', person_id=person_id, workout_id=1))


@app.route("/person/<int:person_id>/workout/<int:workout_id>")
def show_workout_for_person(person_id, workout_id):
    return render_template('workout.html', person_id=person_id, workout_id=workout_id)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
