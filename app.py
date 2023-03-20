from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import os
from flask import Flask, render_template, redirect, request, url_for
import jinja_partials
from decorators import validate_person, validate_topset, validate_workout
from db import DataBase
from utils import get_people_and_exercise_rep_maxes, convert_str_to_date, get_earliest_and_latest_workout_date, filter_workout_topsets, get_exercise_ids_from_workouts, first_and_last_visible_days_in_month
from flask_htmx import HTMX
import minify_html
from urllib.parse import urlparse

app = Flask(__name__)
app.config.from_pyfile('config.py')
jinja_partials.register_extensions(app)
db = DataBase(app)
htmx = HTMX(app)


@app.after_request
def response_minify(response):
    """
    minify html response to decrease site traffic
    """
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(
            minify_html.minify(response.get_data(
                as_text=True), minify_js=True, remove_processing_instructions=True)
        )

        return response
    return response


@ app.route("/")
def dashboard():
    all_topsets = db.get_all_topsets()

    exercises = db.get_exercises()
    people = db.get_people()

    selected_person_ids = [int(i)
                           for i in request.args.getlist('person_id')]
    if not selected_person_ids and htmx.trigger_name != 'person_id':
        selected_person_ids = [p['PersonId'] for p in people]

    selected_exercise_ids = [int(i)
                             for i in request.args.getlist('exercise_id')]
    if not selected_exercise_ids and htmx.trigger_name != 'exercise_id':
        selected_exercise_ids = [e['ExerciseId'] for e in exercises]

    min_date = convert_str_to_date(request.args.get(
        'min_date'), '%Y-%m-%d') or min([t['StartDate'] for t in all_topsets])
    max_date = convert_str_to_date(request.args.get(
        'max_date'), '%Y-%m-%d') or max([t['StartDate'] for t in all_topsets])

    people_and_exercise_rep_maxes = get_people_and_exercise_rep_maxes(
        all_topsets, selected_person_ids, selected_exercise_ids, min_date, max_date)

    if htmx:
        return render_template('partials/page/dashboard.html',
                               model=people_and_exercise_rep_maxes, people=people, exercises=exercises, min_date=min_date, max_date=max_date, selected_person_ids=selected_person_ids, selected_exercise_ids=selected_exercise_ids), 200, {"HX-Trigger": "updatedPeople"}
    return render_template('dashboard.html', model=people_and_exercise_rep_maxes, people=people, exercises=exercises, min_date=min_date, max_date=max_date, selected_person_ids=selected_person_ids, selected_exercise_ids=selected_exercise_ids)


@ app.route("/person/list", methods=['GET'])
def get_person_list():
    people = db.get_people_and_workout_count(-1)
    return render_template('partials/people_link.html', people=people)


@ app.route("/person/<int:person_id>/workout/list", methods=['GET'])
@ validate_person
def get_person(person_id):
    person = db.get_person(person_id)

    (min_date, max_date) = get_earliest_and_latest_workout_date(person)

    min_date = convert_str_to_date(request.args.get(
        'min_date'), '%Y-%m-%d') or min_date
    max_date = convert_str_to_date(request.args.get(
        'max_date'), '%Y-%m-%d') or max_date

    selected_exercise_ids = [int(i)
                             for i in request.args.getlist('exercise_id')]
    if not selected_exercise_ids and htmx.trigger_name != 'exercise_id':
        selected_exercise_ids = [e['ExerciseId'] for e in person['Exercises']]

    person['Workouts'] = [filter_workout_topsets(workout, selected_exercise_ids) for workout in person['Workouts'] if
                          workout['StartDate'] <= max_date and workout['StartDate'] >= min_date]

    active_exercise_ids = get_exercise_ids_from_workouts(person['Workouts'])

    # Filter out workouts that dont contain any of the selected exercises
    person['Workouts'] = [workout for workout in person['Workouts'] if
                          workout['TopSets']]

    filtered_exercises = filter(
        lambda e: e['ExerciseId'] in active_exercise_ids, person['Exercises'])
    person['FilteredExercises'] = list(filtered_exercises)
    if htmx:
        return render_template('partials/page/person.html',
                               person=person, selected_exercise_ids=active_exercise_ids, max_date=max_date, min_date=min_date), 200, {"HX-Trigger": "updatedPeople"}

    return render_template('person.html', person=person, selected_exercise_ids=active_exercise_ids, max_date=max_date, min_date=min_date), 200, {"HX-Trigger": "updatedPeople"}


@ app.route("/person/<int:person_id>/calendar")
@ validate_person
def get_calendar(person_id):
    person = db.get_person(person_id)

    selected_date = convert_str_to_date(request.args.get(
        'date'), '%Y-%m-%d') or date.today()
    selected_view = request.args.get('view') or 'month'

    if selected_view == 'all':
        return redirect(url_for('get_person', person_id=person_id))

    next_date = selected_date + (timedelta(
        365/12) if selected_view == 'month' else timedelta(365))
    previous_date = selected_date + (timedelta(
        -365/12) if selected_view == 'month' else timedelta(-365))

    first_date_of_view = selected_date.replace(
        day=1) if selected_view == 'month' else selected_date.replace(month=1, day=1)
    last_date_of_view = first_date_of_view + \
        (timedelta(365/12) if selected_view == 'month' else timedelta(365))

    start = dict([(6, 0), (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)])
    start_date = first_date_of_view - \
        timedelta(days=start[first_date_of_view.weekday()])

    end = dict([(6, 6), (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0)])
    end_date = last_date_of_view + \
        timedelta(days=end[last_date_of_view.weekday()])

    if selected_view == 'year':
        start_date = first_date_of_view
        end_date = last_date_of_view

    if htmx:
        return render_template('partials/page/calendar.html',
                               person=person, selected_date=selected_date, selected_view=selected_view, next_date=next_date, previous_date=previous_date, start_date=start_date, end_date=end_date)
    return render_template('calendar.html', person=person, selected_date=selected_date, selected_view=selected_view, next_date=next_date, previous_date=previous_date, start_date=start_date, end_date=end_date)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/modal", methods=['GET'])
@ validate_workout
def get_workout_modal(person_id, workout_id):
    workout = db.get_workout(person_id, workout_id)
    return render_template('partials/workout_modal.html', workout=workout)


@ app.route("/person/<int:person_id>/workout", methods=['POST'])
@ validate_person
def create_workout(person_id):
    new_workout_id = db.create_workout(person_id)
    workout = db.get_workout(person_id, new_workout_id)
    return render_template('partials/workout_modal.html',
                           workout=workout), 200, {"HX-Trigger": "updatedPeople"}


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/delete", methods=['DELETE'])
@ validate_workout
def delete_workout(person_id, workout_id):
    db.delete_workout(workout_id)
    return "", 200, {"HX-Trigger": "updatedPeople"}


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
    return render_template('partials/start_date.html', person_id=person_id, workout_id=workout_id, start_date=convert_str_to_date(new_start_date, '%Y-%m-%d'))


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
    return render_template('partials/topset.html', person_id=person_id, workout_id=workout_id, topset_id=topset_id, exercises=exercises, exercise_name=topset['ExerciseName'], repetitions=topset['Repetitions'], weight=topset['Weight'], exercise_id=topset['ExerciseId'], is_edit=True)


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
        # if htmx:
        #    parsed_url = urlparse(htmx.current_url)
        #    return 'bg-gray-200' if url == parsed_url.path else ''
        if url == request.path:
            return 'bg-gray-200'
        return ''

    def get_list_of_people_and_workout_count():
        person_id = request.view_args.get('person_id')
        return db.get_people_and_workout_count(person_id)

    def get_first_element_from_list_with_matching_attribute(list, attribute, value):
        if not list:
            return None
        for element in list:
            if element[attribute] == value:
                return element
        return None

    def in_list(val, checked_vals, attr='checked'):
        if not checked_vals:
            return attr
        return attr if val in checked_vals else ''

    def strftime(date, format="%b %d %Y"):
        return date.strftime(format)

    def list_to_string(list):
        return [str(i) for i in list]

    return dict(get_list_of_people_and_workout_count=get_list_of_people_and_workout_count, is_selected_page=is_selected_page, get_first_element_from_list_with_matching_attribute=get_first_element_from_list_with_matching_attribute, in_list=in_list, strftime=strftime, datetime=datetime, timedelta=timedelta, relativedelta=relativedelta, first_and_last_visible_days_in_month=first_and_last_visible_days_in_month, list_to_string=list_to_string)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
