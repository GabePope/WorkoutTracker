from datetime import datetime


def get_workouts(topsets):
    # Get all unique workout_ids (No duplicates)
    workout_ids = set([t['WorkoutId']
                      for t in topsets if t['WorkoutId'] is not None])

    # Group topsets into workouts
    workouts = []
    for workout_id in workout_ids:
        topsets_in_workout = [
            t for t in topsets if t['WorkoutId'] == workout_id]
        workouts.append({
            'WorkoutId': workout_id,
            'StartDate': topsets_in_workout[0]['StartDate'],
            'TopSets': [{"TopSetId": t['TopSetId'], "ExerciseId": t['ExerciseId'], "ExerciseName": t['ExerciseName'], "Weight": t['Weight'], "Repetitions": t['Repetitions']} for t in topsets_in_workout]
        })
    return workouts


def get_all_exercises_from_topsets(topsets):
    exercise_ids = set([t['ExerciseId']
                       for t in topsets if t['ExerciseId'] is not None])
    exercises = []
    for exercise_id in exercise_ids:
        exercises.append({
            'ExerciseId': exercise_id,
            'ExerciseName': next((t['ExerciseName'] for t in topsets if t['ExerciseId'] == exercise_id), 'Unknown')
        })
    return exercises


def get_rep_maxes_for_person(person_topsets):
    person_exercises = get_all_exercises_from_topsets(person_topsets)

    rep_maxes_in_exercises = []
    for e in person_exercises:
        exercise_topsets = [
            t for t in person_topsets if t['ExerciseId'] == e['ExerciseId']]
        set_reps = set([t['Repetitions'] for t in exercise_topsets])

        topsets_for_exercise = []
        for rep in set_reps:
            reps = [t for t in exercise_topsets if t['Repetitions'] == rep]
            max_weight = max([t['Weight'] for t in reps])
            max_topset_for_rep = [t for t in reps if t['Weight'] == max_weight]
            topsets_for_exercise.append({
                'StartDate': max_topset_for_rep[0]['StartDate'],
                'Repetitions': rep,
                'Weight': max_weight
            })

        # datetime.strptime(x['StartDate'], "%Y-%m-%d")
        topsets_for_exercise.sort(
            key=lambda x: x['Repetitions'], reverse=True)

        rep_maxes_in_exercises.append({
            'ExerciseId': e['ExerciseId'],
            'ExerciseName': e['ExerciseName'],
            'RepMaxes': topsets_for_exercise,
        })
    return rep_maxes_in_exercises


def get_people_and_exercise_rep_maxes(topsets):
    # Get all unique workout_ids (No duplicates)
    people_ids = set([t['PersonId'] for t in topsets])

    # Group topsets into workouts
    people = []
    for person_id in people_ids:
        workouts_for_person = [
            t for t in topsets if t['PersonId'] == person_id]
        people.append({
            'PersonId': person_id,
            'PersonName': workouts_for_person[0]['PersonName'],
            'Exercises': get_rep_maxes_for_person(workouts_for_person)
        })
    return people
