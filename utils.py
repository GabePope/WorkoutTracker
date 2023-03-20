from datetime import datetime, date, timedelta
import json


def get_workouts(topsets):
    # Get all unique workout_ids (No duplicates)
    workout_ids = list(set([t['WorkoutId']
                            for t in topsets if t['WorkoutId'] is not None]))

    # Group topsets into workouts
    workouts = []
    for workout_id in reversed(workout_ids):
        topsets_in_workout = [
            t for t in topsets if t['WorkoutId'] == workout_id]
        workouts.append({
            'WorkoutId': workout_id,
            'StartDate': topsets_in_workout[0]['StartDate'],
            'TopSets': [{"TopSetId": t['TopSetId'], "ExerciseId": t['ExerciseId'], "ExerciseName": t['ExerciseName'], "Weight": t['Weight'], "Repetitions": t['Repetitions']} for t in topsets_in_workout if t['TopSetId'] is not None]
        })

    workouts.sort(key=lambda x: x['StartDate'], reverse=True)

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
                'StartDate': max_topset_for_rep[0]['StartDate'].strftime("%b %d %Y"),
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
                'StartDates': json.dumps([t['StartDate'].strftime("%Y-%m-%d") for t in exercise_topsets]),
                'TopSets': json.dumps([f"{t['Repetitions']} x {t['Weight']}kg" for t in exercise_topsets]),
                'Estimated1RMs': json.dumps([t['Estimated1RM'] for t in exercise_topsets]),
            }
        })
    return rep_maxes_in_exercises


def get_people_and_exercise_rep_maxes(topsets, selected_person_ids, selected_exercise_ids, min_date, max_date):
    # Get all unique workout_ids (No duplicates)
    people_ids = set([t['PersonId']
                     for t in topsets])
    filtered_people_ids = [p for p in people_ids if p in selected_person_ids]

    # Group topsets into workouts
    people = []
    for person_id in filtered_people_ids:
        workouts_for_person = [
            t for t in topsets if t['PersonId'] == person_id and t['ExerciseId'] in selected_exercise_ids and t['StartDate'] >= min_date and t['StartDate'] <= max_date]
        if workouts_for_person:
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
    workout_start_dates = [t['StartDate']
                           for t in topsets if t['StartDate'] is not None]

    stats = [{"Text": "Total Workouts", "Value": workout_count}]
    if people_count > 1:
        stats.append({"Text": "People tracked", "Value": people_count})
    if workout_count > 0:
        first_workout_date = min(workout_start_dates)
        last_workout_date = max(workout_start_dates)

        stats.append({"Text": "Days Since First Workout", "Value": (
            date.today() - first_workout_date).days})
        if workout_count >= 2:
            stats.append({"Text": "Days Since Last Workout",
                          "Value": (
                              date.today() - last_workout_date).days})

            training_duration = last_workout_date - first_workout_date
            if training_duration > timedelta(days=0):
                average_workouts_per_week = round(
                    workout_count / (training_duration.days / 7), 2)
                stats.append({"Text": "Average Workouts Per Week",
                              "Value": average_workouts_per_week})

    return stats


def convert_str_to_date(date_str, format='%Y-%m-%d'):
    try:
        return datetime.strptime(date_str, format).date()
    except ValueError:
        return None
    except TypeError:
        return None


def get_earliest_and_latest_workout_date(person):
    if len(person['Workouts']) > 0:
        return (min(person['Workouts'], key=lambda x: x['StartDate'])['StartDate'], max(person['Workouts'], key=lambda x: x['StartDate'])['StartDate'])
    return (datetime.now().date(), datetime.now().date())


def filter_workout_topsets(workout, selected_exercise_ids):
    workout['TopSets'] = [topset for topset in workout['TopSets']
                          if topset['ExerciseId'] in selected_exercise_ids]
    return workout


def get_exercise_ids_from_workouts(workouts):
    return list(set(flatten_list(list(map(lambda x: list(
        map(lambda y: y['ExerciseId'], x['TopSets'])), workouts)))))


def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def first_and_last_visible_days_in_month(first_day_of_month, last_day_of_month):
    start = dict([(6, 0), (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)])
    start_date = first_day_of_month - \
        timedelta(days=start[first_day_of_month.weekday()])

    end = dict([(6, 6), (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0)])
    end_date = last_day_of_month + \
        timedelta(days=end[last_day_of_month.weekday()])
    return (start_date, end_date)
