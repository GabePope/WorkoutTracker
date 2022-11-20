import os
from flask import Flask, render_template, redirect, request, url_for
import jinja_partials
from decorators import validate_person, validate_topset, validate_workout
from db import DataBase
from utils import get_people_and_exercise_rep_maxes

app = Flask(__name__)
app.config.from_pyfile('config.py')
jinja_partials.register_extensions(app)
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


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/start_date_edit_form", methods=['GET'])
@ validate_workout
def get_workout_start_date_edit_form(person_id, workout_id):
    workout = db.get_workout(person_id, workout_id)
    return f"""
        <div class="relative">
            <div class="flex absolute inset-y-0 left-0 items-center pl-3 pointer-events-none">
                <svg aria-hidden="true" class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="currentColor"
                    viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd"
                        d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                        clip-rule="evenodd"></path>
                </svg>
            </div>
            <input type="date"
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full md:w-1/4"
                name="start-date" value="{workout['StartDate']}">
        </div>

        <a
            class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer"
            hx-put="{url_for('update_workout_start_date', person_id=person_id, workout_id=workout_id)}"
            hx-include="[name='start-date']">
            Update
        </a>
        <a 
            hx-get="{url_for('get_workout_start_date', person_id=person_id, workout_id=workout_id)}"
            hx-target="#edit-start-date"
            class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
            Cancel
        </a>
    """


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/start_date", methods=['PUT'])
@ validate_workout
def update_workout_start_date(person_id, workout_id):
    new_start_date = request.form.get('start-date')
    db.update_workout_start_date(workout_id, new_start_date)
    return f"""
    <span class="text-base font-normal text-gray-500">{new_start_date}</span>
    <a class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer"
        hx-get="{ url_for('get_workout_start_date_edit_form', person_id=person_id, workout_id=workout_id) }"
        hx-target="#edit-start-date">
        Edit
    </a>
    """


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/start_date", methods=['GET'])
@ validate_workout
def get_workout_start_date(person_id, workout_id):
    workout = db.get_workout(person_id, workout_id)
    return f"""
    <span class="text-base font-normal text-gray-500">{workout['StartDate']}</span>
    <a class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer"
        hx-get="{ url_for('get_workout_start_date_edit_form', person_id=person_id, workout_id=workout_id) }"
        hx-target="#edit-start-date">
        Edit
    </a>
    """


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>", methods=['GET'])
@ validate_topset
def get_topset(person_id, workout_id, topset_id):
    topset = db.get_topset(person_id, workout_id, topset_id)
    return f"""
    <tr class="text-gray-500">
                    <th class="border-t-0 px-4 align-middle text-l font-normal whitespace-nowrap p-4 text-left">
                        { topset['ExerciseName'] }</th>
                    </th>
                    <td class="border-t-0 px-4 align-middle text-l font-medium text-gray-900 whitespace-nowrap p-4">
                        { topset['Repetitions'] } x { topset['Weight'] }kg</td>
                    <td class="border-t-0 px-4 align-middle text-xs whitespace-nowrap p-4">
                        <a hx-get="{ url_for('get_topset_edit_form',person_id=person_id, workout_id=workout_id, topset_id=topset_id) }"
                            class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                            Edit
                        </a>
                        <a hx-delete="{ url_for('delete_topset', person_id=person_id, workout_id=workout_id, topset_id=topset_id) }"
                            class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                            Delete
                        </a>
                    </td>
                </tr>
    """


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>/edit_form", methods=['GET'])
@ validate_topset
def get_topset_edit_form(person_id, workout_id, topset_id):
    exercises = db.get_exercises()
    topset = db.get_topset(person_id, workout_id, topset_id)
    return render_template('partials/topset.html', topset=topset, exercises=exercises)


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset", methods=['POST'])
@ validate_workout
def create_topset(person_id, workout_id):
    exercise_id = request.form.get("exercise_id")
    repetitions = request.form.get("repetitions")
    weight = request.form.get("weight")

    new_top_set_id = db.create_topset(
        workout_id, exercise_id, repetitions, weight)
    exercise = db.get_exercise(exercise_id)

    return f"""
    <tr class="text-gray-500">
        <th class="border-t-0 px-4 align-middle text-l font-normal whitespace-nowrap p-4 text-left">
            { exercise['Name'] }</th>
        </th>
        <td class="border-t-0 px-4 align-middle text-l font-medium text-gray-900 whitespace-nowrap p-4">
            {repetitions} x {weight}kg</td>
        <td class="border-t-0 px-4 align-middle text-xs whitespace-nowrap p-4">
                        <a href="{ url_for('get_topset_edit_form', person_id=person_id, workout_id=workout_id, topset_id=new_top_set_id) }"
                            class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                            Edit
                        </a>
                        <a hx-delete="{ url_for('delete_topset', person_id=person_id, workout_id=workout_id, topset_id=new_top_set_id)}"
                            class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                            Delete
                        </a>
                    </td>
    </tr>
    """


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>", methods=['PUT'])
@ validate_workout
def update_topset(person_id, workout_id, topset_id):
    exercise_id = request.form.get("exercise_id")
    repetitions = request.form.get("repetitions")
    weight = request.form.get("weight")

    db.update_topset(exercise_id, repetitions, weight, topset_id)
    exercise = db.get_exercise(exercise_id)

    return f"""
    <tr class="text-gray-500">
        <th class="border-t-0 px-4 align-middle text-l font-normal whitespace-nowrap p-4 text-left">
            { exercise['Name'] }</th>
        </th>
        <td class="border-t-0 px-4 align-middle text-l font-medium text-gray-900 whitespace-nowrap p-4">
            {repetitions} x {weight}kg</td>
        <td class="border-t-0 px-4 align-middle text-xs whitespace-nowrap p-4">
                        <a hx-get="{ url_for('get_topset_edit_form', person_id=person_id, workout_id=workout_id, topset_id=topset_id) }"
                            class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                            Edit
                        </a>
                        <a hx-delete="{ url_for('delete_topset', person_id=person_id, workout_id=workout_id, topset_id=topset_id)}"
                            class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                            Delete
                        </a>
                    </td>
    </tr>
    """


@ app.route("/person/<int:person_id>/workout/<int:workout_id>/topset/<int:topset_id>/delete", methods=['DELETE'])
@ validate_topset
def delete_topset(person_id, workout_id, topset_id):
    db.delete_topset(topset_id)
    return ""


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
    new_exercise_id = db.create_exercise(name)
    return f"""
    <tr>
        <td class="p-4 whitespace-nowrap text-sm font-semibold text-gray-900">
            {name}
        </td>
        <td class="p-4 whitespace-nowrap text-sm font-semibold text-gray-900">
            <a hx-get="{ url_for('get_exercise_edit_form', exercise_id=new_exercise_id) }" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                Edit
            </a>
            <a hx-delete="{url_for('delete_exercise', exercise_id=new_exercise_id)}" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                Remove
            </a>
        </td>
    </tr>
    """


@ app.route("/exercise/<int:exercise_id>", methods=['GET'])
def get_exercise(exercise_id):
    exercise = db.get_exercise(exercise_id)
    return f"""
    <tr>
        <td class="p-4 whitespace-nowrap text-sm font-semibold text-gray-900">
            {exercise['Name']}
        </td>
        <td class="p-4 whitespace-nowrap text-sm font-semibold text-gray-900">
            <a hx-get="{ url_for('get_exercise_edit_form', exercise_id=exercise['ExerciseId']) }" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                Edit
            </a>
            <a hx-delete="{url_for('delete_exercise', exercise_id=exercise['ExerciseId'])}" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                Remove
            </a>
        </td>
    </tr>
    """


@ app.route("/exercise/<int:exercise_id>/edit_form", methods=['GET'])
def get_exercise_edit_form(exercise_id):
    exercise = db.get_exercise(exercise_id)
    return f"""
    <tr>
        <td class="p-4 whitespace-nowrap text-sm font-semibold text-gray-900">
            <input class="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" type="text" name="name" value="{exercise['Name']}">
        </td>
        <td class="p-4 whitespace-nowrap text-sm font-semibold text-gray-900">
            <a hx-put="{ url_for('update_exercise', exercise_id=exercise['ExerciseId']) }"  hx-include="closest tr" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                Update
            </a>
            <a hx-get="{url_for('get_exercise', exercise_id=exercise['ExerciseId'])}" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                Cancel
            </a>
        </td>
    </tr>
    """


@ app.route("/exercise/<int:exercise_id>/update", methods=['PUT'])
def update_exercise(exercise_id):
    new_name = request.form.get('name')
    db.update_exercise(exercise_id, new_name)
    return f"""
    <tr>
        <td class="p-4 whitespace-nowrap text-sm font-semibold text-gray-900">
            {new_name}
        </td>
        <td class="p-4 whitespace-nowrap text-sm font-semibold text-gray-900">
            <a hx-get="{ url_for('get_exercise_edit_form', exercise_id=exercise_id) }" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                Edit
            </a>
            <a hx-delete="{url_for('delete_exercise', exercise_id=exercise_id)}" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg inline-flex items-center p-2 cursor-pointer">
                Remove
            </a>
        </td>
    </tr>
    """


@ app.route("/exercise/<int:exercise_id>/delete", methods=['DELETE'])
def delete_exercise(exercise_id):
    db.delete_exercise(exercise_id)
    return ""


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
