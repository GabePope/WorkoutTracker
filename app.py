from flask import Flask, jsonify, render_template, g, redirect, request, url_for
from flasgger import Swagger
import sqlite3
import datetime

template = {
    "swagger": "2.0",
    "info": {
        "title": "WorkoutTracker API",
        "description": "API for tracking topsets of workouts",
        "contact": {
            "responsibleOrganization": "ME",
            "responsibleDeveloper": "Me",
            "email": "me@me.com",
            "url": "www.me.com",
        },
        "version": "0.0.1"
    },
    "schemes": [
        "http",
        "https"
    ],
    "operationId": "getmyData"
}

app = Flask(__name__)
swagger = Swagger(app, template=template)

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
    cur.connection.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/")
def dashboard():
    """Dashboard page
    Displays stats and a list of all people and there rep maxes for each exercise
    ---
    tags:
      - Dashboard
    responses:
      200:
        description: A list of all people and there rep maxes for each exercise
    """
    return render_template('index.html')


@app.route("/person/<int:person_id>")
def display_workouts_for_person(person_id):
    """Display all workouts for a person
    Displays stats and a list of all people and there rep maxes for each exercise
    ---
    tags:
      - Person
    parameters:
      - name: person_id
        in: path
        type: number
        required: true

    responses:
      200:
        description: A list of all people and there rep maxes for each exercise
    """
    person = query_db('SELECT * FROM Person WHERE PersonId=?',
                      [person_id], one=True)

    if person is None:
        return render_template('error.html', error='404', message=f'Unable to find Person({person_id})', url='/')

    workouts = query_db("""
        SELECT
            W.WorkoutId,
            W.StartDate,
            T.TopSetId,
            E.ExcerciseId,
            E.Name,
            T.Repetitions || ' x ' || T.Weight || 'kg' AS TopSet
        FROM
            Workout W
            LEFT JOIN TopSet T ON W.WorkoutId = T.WorkoutId
            LEFT JOIN Excercise E ON T.ExcerciseId = E.ExcerciseId
        WHERE
            W.PersonId = ?""",
                        [person_id])

    exercises = query_db('select * from Excercise')

    unique_workout_ids = set([w['WorkoutId'] for w in workouts])

    transformed_workouts = []
    for workout_id in unique_workout_ids:
        # topsets = [w for w in workouts if w['WorkoutId' == workout_id]]
        topsets = []
        for workout in workouts:
            if workout['WorkoutId'] == workout_id:
                topsets.append(workout)
        topset_exercises = {}
        for exercise in exercises:
            for topset in topsets:
                if topset['ExcerciseId'] == exercise['ExcerciseId']:
                    topset_exercises[exercise['ExcerciseId']
                                     ] = topset['TopSet']

        workout = [w for w in workouts if w['WorkoutId'] == workout_id][0]
        transformed_workouts.append(
            {"workout_id": workout['WorkoutId'], "start_date": workout['StartDate'], "topset_exercises": topset_exercises})

    return render_template('workouts.html', person_id=person_id, person=person, workouts=transformed_workouts, exercises=exercises)


@app.route("/person/<int:person_id>/workout", methods=['POST'])
def new_workout_for_person(person_id):
    """Create new workout
    Creates a workout with current date and then redirects to newly created workout
    ---
    tags:
      - Workout
    parameters:
      - name: person_id
        in: path
        type: number
        required: true

    responses:
      200:
        description: View of newly created workout
    """
    person = query_db('SELECT * FROM Person WHERE PersonId=?',
                      [person_id], one=True)

    if person is None:
        return render_template('error.html', error='404', message=f'Unable to find Person({person_id})', url='/')

    now = datetime.datetime.now()
    date_string = now.strftime('%Y-%m-%d')
    print(f'Creating workout for {person_id} at {date_string}')
    query_db('INSERT INTO Workout (PersonId, StartDate) VALUES	(?, ?)', [
        person_id, date_string])
    w = query_db('SELECT MAX(WorkoutId) AS WorkoutId FROM Workout WHERE PersonId=?', [
        person_id], one=True)

    return redirect(url_for('show_workout_for_person', person_id=person_id, workout_id=w['WorkoutId']))


@app.route("/person/<int:person_id>/workout/<int:workout_id>")
def show_workout_for_person(person_id, workout_id):
    """Display a workout
    Displays a selected workout with options to edit/delete existing and add new topsets
    ---
    tags:
      - Workout
    parameters:
      - name: person_id
        in: path
        type: number
        required: true
      - name: workout_id
        in: path
        type: number
        required: true
    responses:
       200:
         description: A list of topsets in a selected workout
    """
    workout_info = query_db("""
        SELECT
            P.Name,
            W.StartDate
        FROM
            Person P
            LEFT JOIN Workout W ON P.PersonId = W.PersonId
        WHERE
            P.PersonId = ?
            AND W.WorkoutId = ?
        LIMIT 1""",
                            [person_id, workout_id], one=True)

    if workout_info is None:
        return render_template('error.html', error='404', message=f'Unable to find Workout({workout_id}) completed by Person({person_id})', url=url_for('display_workouts_for_person', person_id=person_id))

    top_sets = query_db("""
        SELECT
            T.TopSetId,
            E.Name,
            T.Repetitions || ' x ' || T.Weight || 'kg' AS TopSet
        FROM
            Person P
            LEFT JOIN Workout W ON P.PersonId = W.PersonId
            INNER JOIN TopSet T ON W.WorkoutId = T.WorkoutId
            INNER JOIN Excercise E ON T.ExcerciseId = E.ExcerciseId
        WHERE
            P.PersonId = ?
            AND W.WorkoutId = ?""",
                        [person_id, workout_id])

    return render_template('workout.html', person_id=person_id, workout_id=workout_id, workout_info=workout_info, top_sets=top_sets, exercises=query_db('select * from Excercise'))


@app.route("/person/<int:person_id>/workout/<int:workout_id>/delete", methods=['GET', 'DELETE'])
def delete_workout_from_person(person_id, workout_id):
    """Delete workout
    Deletes selected workout completed by a person
    ---
    tags:
      - Workout
    parameters:
      - name: person_id
        in: path
        type: number
        required: true
      - name: workout_id
        in: path
        type: number
        required: true
    responses:
       200:
         description: Redirect to workouts list page for person
    """

    workout_info = query_db("""
        SELECT
            P.Name,
            W.StartDate
        FROM
            Person P
            LEFT JOIN Workout W ON P.PersonId = W.PersonId
        WHERE
            P.PersonId = ?
            AND W.WorkoutId = ?
        LIMIT 1""",
                            [person_id, workout_id], one=True)

    if workout_info is None:
        return render_template('error.html', error='404', message=f'Unable to find Workout({workout_id}) completed by Person({person_id})', url=url_for('display_workouts_for_person', person_id=person_id))

    query_db('DELETE FROM Workout WHERE WorkoutId=?',
             [workout_id])

    return redirect(url_for('display_workouts_for_person', person_id=person_id))


@app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>", methods=['GET', 'POST'])
def show_topset_from_workout_for_person(person_id, workout_id, topset_id):
    """Display/Create new top set
    Displays stats and a list of all people and there rep maxes for each exercise
    ---
    tags:
      - Topset
    parameters:
      - name: person_id
        in: path
        type: number
        required: true
      - name: workout_id
        in: path
        type: number
        required: true
      - name: topset_id
        in: path
        type: number
        required: true
    responses:
       200:
         description: A list of topsets in a selected workout
    """
    topset = query_db("""
        SELECT
            P.Name,
            W.StartDate,
            E.ExcerciseId,
            E.Name,
            T.Repetitions,
            T.Weight
        FROM
            Person P
            LEFT JOIN Workout W ON P.PersonId = W.PersonId
            INNER JOIN TopSet T ON W.WorkoutId = T.WorkoutId
            INNER JOIN Excercise E ON T.ExcerciseId = E.ExcerciseId
        WHERE
            P.PersonId = ?
            AND W.WorkoutId = ?
            AND T.TopSetId = ?""",
                      [person_id, workout_id, topset_id], one=True)

    if topset is None:
        return render_template('error.html', error='404', message=f'Unable to find TopSet({topset_id}) in Workout({workout_id}) completed by Person({person_id})', url=url_for('show_workout_for_person', person_id=person_id, workout_id=workout_id))

    if request.method == 'POST':
        exercise_id = request.form.get("exercise_id")
        repetitions = request.form.get("repetitions")
        weight = request.form.get("weight")

        query_db('UPDATE TopSet SET ExcerciseId=?, Repetitions=?, Weight=? WHERE TopSetId=?', [
            exercise_id, repetitions, weight, topset_id])

        return redirect(url_for('show_workout_for_person', person_id=person_id, workout_id=workout_id))

    return render_template('topset.html', person_id=person_id, workout_id=workout_id, topset_id=topset_id, topset=topset, exercises=query_db('select * from Excercise'))


@app.route("/person/<int:person_id>/workout/<int:workout_id>/topset", methods=['POST'])
def add_topset_to_workout_for_person(person_id, workout_id):
    """Add top set to workout
    Add a topset to a workout completed by a person
    ---
    tags:
      - Topset
    parameters:
      - name: person_id
        in: path
        type: number
        required: true
      - name: workout_id
        in: path
        type: number
        required: true
    responses:
       200:
         description: A list of topsets in a selected workout
    """
    workout_info = query_db("""
        SELECT
            P.Name,
            W.StartDate
        FROM
            Person P
            LEFT JOIN Workout W ON P.PersonId = W.PersonId
        WHERE
            P.PersonId = ?
            AND W.WorkoutId = ?
        LIMIT 1""",
                            [person_id, workout_id], one=True)

    if workout_info is None:
        return render_template('error.html', error='404', message=f'Unable to find Workout({workout_id}) completed by Person({person_id})', url=url_for('display_workouts_for_person', person_id=person_id))

    exercise_id = request.form.get("exercise_id")
    repetitions = request.form.get("repetitions")
    weight = request.form.get("weight")

    query_db('INSERT INTO TopSet (WorkoutId, ExcerciseId, Repetitions, Weight) VALUES (?, ?, ?, ?)', [
             workout_id, exercise_id, repetitions, weight])

    return redirect(url_for('show_workout_for_person', person_id=person_id, workout_id=workout_id))


@app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>/delete", methods=['GET', 'DELETE'])
def delete_topset_from_workout_for_person(person_id, workout_id, topset_id):
    """Delete top set
    Add a topset to a workout completed by a person
    ---
    tags:
      - Topset
    parameters:
      - name: person_id
        in: path
        type: number
        required: true
      - name: workout_id
        in: path
        type: number
        required: true
      - name: topset_id
        in: path
        type: number
        required: true
    responses:
       200:
         description: A list of topsets in a selected workout
    """
    topset = query_db("""
        SELECT
            P.Name,
            W.StartDate,
            E.ExcerciseId,
            E.Name,
            T.Repetitions,
            T.Weight
        FROM
            Person P
            LEFT JOIN Workout W ON P.PersonId = W.PersonId
            INNER JOIN TopSet T ON W.WorkoutId = T.WorkoutId
            INNER JOIN Excercise E ON T.ExcerciseId = E.ExcerciseId
        WHERE
            P.PersonId = ?
            AND W.WorkoutId = ?
            AND T.TopSetId = ?""",
                      [person_id, workout_id, topset_id], one=True)

    if topset is None:
        return render_template('error.html', error='404', message=f'Unable to find TopSet({topset_id}) in Workout({workout_id}) completed by Person({person_id})', url=url_for('show_workout_for_person', person_id=person_id, workout_id=workout_id))

    query_db('DELETE FROM TopSet WHERE TopSetId=?', [
             topset_id])

    return redirect(url_for('show_workout_for_person', person_id=person_id, workout_id=workout_id))


@app.context_processor
def my_utility_processor():

    def is_selected_page(url):
        if url == request.path:
            return 'bg-gray-200'
        return ''

    def get_list_of_people_and_workout_count():
        person_id = -1
        if 'person_id' in request.view_args:
            person_id = request.view_args['person_id']

        return query_db("""
                    SELECT
                    P.PersonId,
                    P.Name,
                    COUNT(W.WorkoutId) AS NumberOfWorkouts,
                    CASE P.PersonId 
                        WHEN ? 
                            THEN 1 
                            ELSE 0 
                    END IsActive
                FROM
                    Person P
                    LEFT JOIN Workout W ON P.PersonId = W.PersonId
                GROUP BY
                    P.PersonId""", [person_id])

    return dict(get_list_of_people_and_workout_count=get_list_of_people_and_workout_count, is_selected_page=is_selected_page)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
