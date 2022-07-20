from flask import Flask, abort, render_template, g, redirect, request, url_for
from flasgger import Swagger, swag_from
from functools import wraps
import sqlite3

from db import DataBase
from decorators import validate_person, validate_topset, validate_workout

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
app.config.from_pyfile('config.py')
swagger = Swagger(app, template=template)

db = DataBase(app)


@ app.route("/")
@ swag_from('swagger/dashboard.yml')
def dashboard():
    return render_template('index.html')


@ app.route("/person/<int:person_id>")
@ swag_from('swagger/get_person.yml')
@ validate_person
def get_person(person_id):
    person = db.get_person_final(person_id)
    return render_template('workouts.html', person=person)


@ app.route("/person/<int:person_id>/workout", methods=['POST'])
@ swag_from('swagger/create_workout.yml')
@ validate_person
def create_workout(person_id):
    new_workout_id = db.create_workout(person_id)
    return redirect(url_for('get_workout', person_id=person_id, workout_id=new_workout_id))


@ app.route("/person/<int:person_id>/workout/<int:workout_id>")
@ swag_from('swagger/get_workout.yml')
@ validate_workout
def get_workout(person_id, workout_id):
    workout = db.get_workout_final(person_id, workout_id)
    return render_template('workout.html', workout=workout)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/delete", methods=['GET', 'DELETE'])
@ swag_from('swagger/delete_workout.yml')
@ validate_workout
def delete_workout(person_id, workout_id):
    db.delete_workout(workout_id)
    return redirect(url_for('get_person', person_id=person_id))


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>", methods=['GET', 'POST'])
@ swag_from('swagger/get_topset.yml')
@ validate_topset
def get_topset(person_id, workout_id, topset_id):
    if request.method == 'POST':
        exercise_id = request.form.get("exercise_id")
        repetitions = request.form.get("repetitions")
        weight = request.form.get("weight")

        db.update_topset(exercise_id, repetitions, weight, topset_id)

        return redirect(url_for('get_workout', person_id=person_id, workout_id=workout_id))

    topset = db.get_topset_final(person_id, workout_id, topset_id)
    return render_template('topset.html', topset=topset)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset", methods=['POST'])
@ swag_from('swagger/create_topset.yml')
@ validate_workout
def create_topset(person_id, workout_id):
    exercise_id = request.form.get("exercise_id")
    repetitions = request.form.get("repetitions")
    weight = request.form.get("weight")

    db.create_topset(workout_id, exercise_id, repetitions, weight)
    return redirect(url_for('get_workout', person_id=person_id, workout_id=workout_id))


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>/delete", methods=['GET', 'DELETE'])
@ swag_from('swagger/delete_topset.yml')
@ validate_topset
def delete_topset(person_id, workout_id, topset_id):
    db.delete_topset(topset_id)
    return redirect(url_for('get_workout', person_id=person_id, workout_id=workout_id))


@ app.context_processor
def my_utility_processor():

    def is_selected_page(url):
        if url == request.path:
            return 'bg-gray-200'
        return ''

    def get_list_of_people_and_workout_count():
        person_id = -1
        if 'person_id' in request.view_args:
            person_id = request.view_args['person_id']

        return db.get_people_and_workout_count(person_id)

    def get_first_element_from_list_with_matching_attribute(list, attribute, value):
        for element in list:
            if element[attribute] == value:
                return element
        return None

    return dict(get_list_of_people_and_workout_count=get_list_of_people_and_workout_count, is_selected_page=is_selected_page, get_first_element_from_list_with_matching_attribute=get_first_element_from_list_with_matching_attribute)
