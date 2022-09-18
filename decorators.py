from functools import wraps

from flask import render_template, url_for


def validate_person(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        person_id = kwargs.get('person_id')
        from app import db
        person = db.get_person(person_id)
        if person is None:
            return render_template('error.html', error='404', message=f'Unable to find Person({person_id})', url='/')
        return func(*args, **kwargs)
    return wrapper


def validate_workout(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        person_id = kwargs.get('person_id')
        workout_id = kwargs.get('workout_id')
        from app import db
        workout = db.get_workout(person_id, workout_id)
        if workout is None:
            return render_template('error.html', error='404', message=f'Unable to find Workout({workout_id}) completed by Person({person_id})', url=url_for('get_person', person_id=person_id))
        return func(*args, **kwargs)
    return wrapper


def validate_topset(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        person_id = kwargs.get('person_id')
        workout_id = kwargs.get('workout_id')
        topset_id = kwargs.get('topset_id')
        from app import db
        topset = db.get_topset(person_id, workout_id, topset_id)
        if topset is None:
            return render_template('error.html', error='404', message=f'Unable to find TopSet({topset_id}) in Workout({workout_id}) completed by Person({person_id})', url=url_for('get_workout', person_id=person_id, workout_id=workout_id))
        return func(*args, **kwargs)
    return wrapper
