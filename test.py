import sqlite3

connection = sqlite3.connect('workout.db')

cur = connection.cursor()

cur.execute("""SELECT P.Name, W.WorkoutId, W.StartDate, E.Name, T.Repetitions, T.Weight
FROM Workout W, Person P, Excercise E, TopSet T
WHERE W.PersonId=P.PersonId AND W.WorkoutId=T.WorkoutId AND E.ExcerciseId=T.ExcerciseId""")

rows = cur.fetchall(); 

print(rows);

def get_name_from_rows(rows):
    (name, workout_id, start_date, exercise, reps, weight) = rows[0];
    return name;

def get_workout_ids(rows):
    workout_ids = []
    for r in rows:
        (name, workout_id, start_date, exercise, reps, weight) = r;
        if workout_id not in workout_ids:
            workout_ids.append(workout_id);
    return workout_ids

def get_workouts_from_rows(rows):
    workout_ids = get_workout_ids(rows);
    workouts = [];
    for workout_id in workout_ids:
        workouts.append(get_top_sets_from_rows_with_workout_id(rows, workout_id));
    return workouts

def get_top_sets_from_rows_with_workout_id(rows, workout_id):
    topset_id = get_workouts_from_rows(rows);
    topsets = [];
    for topset_id in topsets:
        topsets.append(get_reps_and_weight_from_topset_id(reps, weight));
    return topsets

#def get_reps_and_weight_from_topset_id(reps, weight):
    

def transform_data(rows):
    res = {
        "name": get_name_from_rows(rows),
        "workouts": [
            {
                "StartDate": get_workouts_from_rows(rows),
                "TopSets": [
                    {
                        "ExerciseName": "Squat",
                        "Weight": get_reps_and_weight_from_topset_id(1),
                        "Repetitions": get_reps_and_weight_from_topset_id(0)
                    },
                    {
                        "ExerciseName": "Bench",
                        "Weight": 60,
                        "Repetitions": 4
                    }
                ]
            },
            {
                "StartDate": "bkah",
                "TopSets": [
                    {
                        "ExerciseName": "Squat",
                        "Weight": 60,
                        "Repetitions": 4
                    },
                    {
                        "ExerciseName": "Bench",
                        "Weight": 60,
                        "Repetitions": 4
                    }
                ]
            }
        ]
    };
    return res;

print(transform_data(rows));

print(get_workouts_from_rows(rows));

