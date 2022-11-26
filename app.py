import os
from flask import Flask, render_template, redirect, request, url_for
import jinja_partials
from decorators import validate_person, validate_topset, validate_workout
from db import DataBase
from utils import get_people_and_exercise_rep_maxes
from flask_htmx import HTMX

app = Flask(__name__)
app.config.from_pyfile('config.py')
jinja_partials.register_extensions(app)
db = DataBase(app)
htmx = HTMX(app)


@ app.route("/")
def dashboard():
    all_topsets = db.get_all_topsets()
    people_and_exercise_rep_maxes = get_people_and_exercise_rep_maxes(
        all_topsets)
    if htmx:
        return render_template('partials/page/dashboard.html',
                               model=people_and_exercise_rep_maxes), 200, {"HX-Trigger": "updatedPeople"}
    return render_template('dashboard.html', model=people_and_exercise_rep_maxes)


@ app.route("/person/list", methods=['GET'])
def get_person_list():
    people = db.get_people_and_workout_count(-1)
    return render_template('partials/people_link.html', people=people)


@ app.route("/person/<int:person_id>")
@ validate_person
def get_person(person_id):
    selected_exercise_ids = [int(i)
                             for i in request.args.getlist('exercise_id')]
    person = db.get_person(person_id)

    if selected_exercise_ids:
        filtered_exercises = filter(
            lambda e: e['ExerciseId'] in selected_exercise_ids, person['Exercises'])
        person['FilteredExercises'] = list(filtered_exercises)
        if htmx:
            return render_template('partials/page/person.html',
                                   person=person, is_filtered=True, selected_exercise_ids=selected_exercise_ids), 200, {"HX-Trigger": "updatedPeople"}

        return render_template('person.html', person=person, is_filtered=True, selected_exercise_ids=selected_exercise_ids)

    if htmx:
        return render_template('partials/page/person.html',
                               person=person, is_filtered=False), 200, {"HX-Trigger": "updatedPeople"}

    return render_template('person.html', person=person)


@ app.route("/person/<int:person_id>/workout", methods=['POST'])
@ validate_person
def create_workout(person_id):
    new_workout_id = db.create_workout(person_id)
    if htmx:
        workout = db.get_workout(person_id, new_workout_id)
        return render_template('partials/page/workout.html',
                               workout=workout), 200, {"HX-Trigger": "updatedPeople", "HX-Push": url_for('get_workout', person_id=person_id, workout_id=new_workout_id)}
    return redirect(url_for('get_workout', person_id=person_id, workout_id=new_workout_id))


@ app.route("/person/<int:person_id>/workout/<int:workout_id>")
@ validate_workout
def get_workout(person_id, workout_id):
    workout = db.get_workout(person_id, workout_id)
    if htmx:
        return render_template('partials/page/workout.html',
                               workout=workout), 200, {"HX-Trigger": "updatedPeople"}
    return render_template('workout.html', workout=workout)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/delete", methods=['DELETE'])
@ validate_workout
def delete_workout(person_id, workout_id):
    db.delete_workout(workout_id)
    person = db.get_person(person_id)
    return render_template('partials/page/person.html',
                           person=person, is_filtered=False), 200, {"HX-Trigger": "updatedPeople", "HX-Push": url_for('get_person', person_id=person_id)}


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/start_date_edit_form", methods=['GET'])
@ validate_workout
def get_workout_start_date_edit_form(person_id, workout_id):
    workout = db.get_workout(person_id, workout_id)
    return render_template('partials/start_date.html', person_id=person_id, workout_id=workout_id, start_date=workout['StartDate'], is_edit=True)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/start_date", methods=['PUT'])
@ validate_workout
def update_workout_start_date(person_id, workout_id):
    new_start_date = request.form.get('start-date')
    db.update_workout_start_date(workout_id, new_start_date)
    return render_template('partials/start_date.html', person_id=person_id, workout_id=workout_id, start_date=new_start_date)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/start_date", methods=['GET'])
@ validate_workout
def get_workout_start_date(person_id, workout_id):
    workout = db.get_workout(person_id, workout_id)
    return render_template('partials/start_date.html', person_id=person_id, workout_id=workout_id, start_date=workout['StartDate'])


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>", methods=['GET'])
@ validate_topset
def get_topset(person_id, workout_id, topset_id):
    topset = db.get_topset(person_id, workout_id, topset_id)
    return render_template('partials/topset.html', person_id=person_id, workout_id=workout_id, topset_id=topset_id, exercise_name=topset['ExerciseName'], repetitions=topset['Repetitions'], weight=topset['Weight'])


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>/edit_form", methods=['GET'])
@ validate_topset
def get_topset_edit_form(person_id, workout_id, topset_id):
    exercises = db.get_exercises()
    topset = db.get_topset(person_id, workout_id, topset_id)
    return render_template('partials/topset.html', person_id=person_id, workout_id=workout_id, topset_id=topset_id, exercises=exercises, repetitions=topset['Repetitions'], weight=topset['Weight'], is_edit=True)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset", methods=['POST'])
@ validate_workout
def create_topset(person_id, workout_id):
    exercise_id = request.form.get("exercise_id")
    repetitions = request.form.get("repetitions")
    weight = request.form.get("weight")

    new_topset_id = db.create_topset(
        workout_id, exercise_id, repetitions, weight)
    exercise = db.get_exercise(exercise_id)

    return render_template('partials/topset.html', person_id=person_id, workout_id=workout_id, topset_id=new_topset_id, exercise_name=exercise['Name'], repetitions=repetitions, weight=weight), 200, {"HX-Trigger": "topsetAdded"}


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>", methods=['PUT'])
@ validate_workout
def update_topset(person_id, workout_id, topset_id):
    exercise_id = request.form.get("exercise_id")
    repetitions = request.form.get("repetitions")
    weight = request.form.get("weight")

    db.update_topset(exercise_id, repetitions, weight, topset_id)
    exercise = db.get_exercise(exercise_id)

    return render_template('partials/topset.html', person_id=person_id, workout_id=workout_id, topset_id=topset_id, exercise_name=exercise['Name'], repetitions=repetitions, weight=weight)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>/delete", methods=['DELETE'])
@ validate_topset
def delete_topset(person_id, workout_id, topset_id):
    db.delete_topset(topset_id)
    return ""


@ app.route("/person", methods=['POST'])
def create_person():
    name = request.form.get("name")
    new_person_id = db.create_person(name)
    return render_template('partials/person.html', person_id=new_person_id, name=name), 200, {"HX-Trigger": "updatedPeople"}


@ app.route("/person/<int:person_id>/delete", methods=['DELETE'])
def delete_person(person_id):
    db.delete_person(person_id)
    return "", 200, {"HX-Trigger": "updatedPeople"}


@ app.route("/person/<int:person_id>/edit_form", methods=['GET'])
def get_person_edit_form(person_id):
    person = db.get_person(person_id)
    return render_template('partials/person.html', person_id=person_id, name=person['PersonName'], is_edit=True)


@ app.route("/person/<int:person_id>/name", methods=['PUT'])
def update_person_name(person_id):
    new_name = request.form.get("name")
    db.update_person_name(person_id, new_name)
    return render_template('partials/person.html', person_id=person_id, name=new_name), 200, {"HX-Trigger": "updatedPeople"}


@ app.route("/person/<int:person_id>/name", methods=['GET'])
def get_person_name(person_id):
    person = db.get_person(person_id)
    return render_template('partials/person.html', person_id=person_id, name=person['PersonName'])


@ app.route("/exercise", methods=['POST'])
def create_exercise():
    name = request.form.get("name")
    new_exercise_id = db.create_exercise(name)
    return render_template('partials/exercise.html', exercise_id=new_exercise_id, name=name)


@ app.route("/exercise/<int:exercise_id>", methods=['GET'])
def get_exercise(exercise_id):
    exercise = db.get_exercise(exercise_id)
    return render_template('partials/exercise.html', exercise_id=exercise_id, name=exercise['Name'])


@ app.route("/exercise/<int:exercise_id>/edit_form", methods=['GET'])
def get_exercise_edit_form(exercise_id):
    exercise = db.get_exercise(exercise_id)
    return render_template('partials/exercise.html', exercise_id=exercise_id, name=exercise['Name'], is_edit=True)


@ app.route("/exercise/<int:exercise_id>/update", methods=['PUT'])
def update_exercise(exercise_id):
    new_name = request.form.get('name')
    db.update_exercise(exercise_id, new_name)
    return render_template('partials/exercise.html', exercise_id=exercise_id, name=new_name)


@ app.route("/exercise/<int:exercise_id>/delete", methods=['DELETE'])
def delete_exercise(exercise_id):
    db.delete_exercise(exercise_id)
    return ""


@ app.route("/settings")
def settings():
    people = db.get_people()
    exercises = db.get_exercises()
    if htmx:
        return render_template('partials/page/settings.html',
                               people=people, exercises=exercises), 200, {"HX-Trigger": "updatedPeople"}
    return render_template('settings.html', people=people, exercises=exercises)


@ app.context_processor
def my_utility_processor():

    def is_selected_page(url):
        if url == request.path:
            return 'bg-gray-200'
        return ''

    def get_list_of_people_and_workout_count():
        person_id = request.view_args.get('person_id')
        return db.get_people_and_workout_count(person_id)

    def get_first_element_from_list_with_matching_attribute(list, attribute, value):
        for element in list:
            if element[attribute] == value:
                return element
        return None

    def is_checked(val, checked_vals):
        if not checked_vals:
            return 'checked'
        return 'checked' if val in checked_vals else ''

    return dict(get_list_of_people_and_workout_count=get_list_of_people_and_workout_count, is_selected_page=is_selected_page, get_first_element_from_list_with_matching_attribute=get_first_element_from_list_with_matching_attribute, is_checked=is_checked)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
