import os
from flask import Flask, render_template, redirect, request, url_for
from decorators import validate_person, validate_topset, validate_workout
from db import DataBase
from utils import get_people_and_exercise_rep_maxes

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = DataBase(app)


@ app.route("/")
def dashboard():
    all_topsets = db.get_all_topsets()
    people_and_exercise_rep_maxes = get_people_and_exercise_rep_maxes(
        all_topsets)
    return render_template('index.html', model=people_and_exercise_rep_maxes)


@ app.route("/person/<int:person_id>")
@ validate_person
def get_person(person_id):
    person = db.get_person(person_id)
    return render_template('person.html', person=person)


@ app.route("/person/<int:person_id>/workout", methods=['POST'])
@ validate_person
def create_workout(person_id):
    new_workout_id = db.create_workout(person_id)
    return redirect(url_for('get_workout', person_id=person_id, workout_id=new_workout_id))


@ app.route("/person/<int:person_id>/workout/<int:workout_id>")
@ validate_workout
def get_workout(person_id, workout_id):
    workout = db.get_workout(person_id, workout_id)
    return render_template('workout.html', workout=workout)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/delete", methods=['GET', 'DELETE'])
@ validate_workout
def delete_workout(person_id, workout_id):
    db.delete_workout(workout_id)
    return redirect(url_for('get_person', person_id=person_id))


@ app.route("/person/<int:person_id>/workout/<int:workout_id>", methods=['POST'])
@ validate_workout
def update_workout(person_id, workout_id):
    db.update_workout(workout_id, request.form)
    return redirect(url_for('get_workout', person_id=person_id, workout_id=workout_id))


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>", methods=['GET', 'POST'])
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
@ validate_workout
def create_topset(person_id, workout_id):
    exercise_id = request.form.get("exercise_id")
    repetitions = request.form.get("repetitions")
    weight = request.form.get("weight")

    db.create_topset(workout_id, exercise_id, repetitions, weight)
    return redirect(url_for('get_workout', person_id=person_id, workout_id=workout_id))


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>/delete", methods=['GET', 'DELETE'])
@ validate_topset
def delete_topset(person_id, workout_id, topset_id):
    db.delete_topset(topset_id)
    return redirect(url_for('get_workout', person_id=person_id, workout_id=workout_id))


@ app.route("/person", methods=['POST'])
def create_person():
    name = request.form.get("name")
    db.create_person(name)
    return redirect(url_for('settings'))


@ app.route("/person/<int:person_id>/delete", methods=['GET', 'POST'])
def delete_person(person_id):
    db.delete_person(person_id)
    return redirect(url_for('settings'))


@ app.route("/exercise", methods=['POST'])
def create_exercise():
    name = request.form.get("name")
    db.create_exercise(name)
    return redirect(url_for('settings'))


@ app.route("/exercise/<int:exercise_id>/delete", methods=['GET', 'POST'])
def delete_exercise(exercise_id):
    db.delete_exercise(exercise_id)
    return redirect(url_for('settings'))


@ app.route("/settings")
def settings():
    people = db.get_people()
    exercises = db.get_exercises()
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

    return dict(get_list_of_people_and_workout_count=get_list_of_people_and_workout_count, is_selected_page=is_selected_page, get_first_element_from_list_with_matching_attribute=get_first_element_from_list_with_matching_attribute)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
