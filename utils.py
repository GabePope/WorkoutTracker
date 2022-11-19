from datetime import datetime
import json


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
            'StartDate': datetime.strptime(topsets_in_workout[0]['StartDate'], "%Y-%m-%d").strftime("%b %d %Y"),
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
                'StartDate': datetime.strptime(max_topset_for_rep[0]['StartDate'], "%Y-%m-%d").strftime("%b %d %Y"),
                'Repetitions': rep,
                'Weight': max_weight,
                'Estimated1RM': max_topset_for_rep[0]['Estimated1RM'],
            })

        # datetime.strptime(x['StartDate'], "%Y-%m-%d")
        topsets_for_exercise.sort(
            key=lambda x: x['Repetitions'], reverse=True)

        rep_maxes_in_exercises.append({
            'ExerciseId': e['ExerciseId'],
            'ExerciseName': e['ExerciseName'],
            'RepMaxes': topsets_for_exercise,
            'EstimatedOneRepMaxProgressions': {
                'StartDates': json.dumps([t['StartDate'] for t in exercise_topsets]),
                'TopSets': json.dumps([f"{t['Repetitions']} x {t['Weight']}kg" for t in exercise_topsets]),
                'Estimated1RMs': json.dumps([t['Estimated1RM'] for t in exercise_topsets]),
            }
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
            'NumberOfWorkouts': len(list(set([t['WorkoutId'] for t in workouts_for_person if t['WorkoutId'] is not None]))),
            'Exercises': get_rep_maxes_for_person(workouts_for_person)
        })
    return {"People": people, "Stats": get_stats_from_topsets(topsets)}


def get_stats_from_topsets(topsets):
    workout_count = len(set([t['WorkoutId']
                             for t in topsets if t['WorkoutId'] is not None]))
    people_count = len(set([t['PersonId']
                            for t in topsets if t['PersonId'] is not None]))
    workout_start_dates = [datetime.strptime(
        t['StartDate'], '%Y-%m-%d') for t in topsets if t['StartDate'] is not None]

    stats = [{"Text": "Total Workouts", "Value": workout_count}]
    if people_count > 1:
        stats.append({"Text": "Number of People", "Value": people_count})
    if workout_count > 0:
        first_workout_date = min(workout_start_dates)
        last_workout_date = max(workout_start_dates)
        training_duration = last_workout_date - first_workout_date
        average_workouts_per_week = round(
            workout_count / (training_duration.days / 7), 2)
        stats.append({"Text": "Days Since First Workout", "Value": (
            datetime.now() - first_workout_date).days})
        stats.append({"Text": "Days Since Last Workout",
                     "Value": (
                         datetime.now() - last_workout_date).days})
        stats.append({"Text": "Average Workouts Per Week",
                     "Value": average_workouts_per_week})

    return stats
