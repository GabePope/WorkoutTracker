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
            'TopSets': [{"TopSetId": t['TopSetId'], "ExcerciseId": t['ExcerciseId'], "ExerciseName": t['ExerciseName'], "Weight": t['Weight'], "Repetitions": t['Repetitions']} for t in topsets_in_workout]
        })
    return workouts


def get_all_exercises_from_topsets(topsets):
    exercise_ids = set([t['ExcerciseId']
                       for t in topsets if t['ExcerciseId'] is not None])
    exercises = []
    for exercise_id in exercise_ids:
        exercises.append({
            'ExcerciseId': exercise_id,
            'ExerciseName': next((t['ExerciseName'] for t in topsets if t['ExcerciseId'] == exercise_id), 'Unknown')
        })
    return exercises