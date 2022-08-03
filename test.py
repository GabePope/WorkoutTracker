import sqlite3

DATABASE = 'workout.db'

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

rows = query_db("""
    SELECT 
        P.PersonId, 
        P.Name AS PersonName, 
        W.WorkoutId,
        W.StartDate,
        T.TopSetId,
        E.ExcerciseId,
        E.Name AS ExerciseName,
        T.Repetitions,
        T.Weight
    FROM Person P
         LEFT JOIN Workout W ON P.PersonId=W.PersonId
         LEFT JOIN TopSet T ON W.WorkoutId=T.WorkoutId
         LEFT JOIN Excercise E ON T.ExcerciseId=E.ExcerciseId
    WHERE P.PersonId=?""", [1])

def get_name_from_rows(rows):
    return rows[0]["PersonName"];

def get_workout_ids(rows):
    workout_ids = [];
    for r in rows:
        workout_id = r["WorkoutId"];
        if workout_id not in workout_ids:
            workout_ids.append(workout_id);  
    return workout_ids

def get_workouts_from_rows(rows):
    workout_ids = get_workout_ids(rows);
    workouts = [];
    for workout_id in workout_ids:
        workout = {  
            "WorkoutId": workout_id,
            "StartDate": get_startdate(workout_id, rows),  
            "TopSets": get_topsets(workout_id, rows)
        }
        workouts.append(workout);
    return workouts

def get_topsets(workout_id, rows):
    topsets = [];
    for row in rows:
        if workout_id == row["WorkoutId"]:
            topset = {  
                "TopSetId": row["TopSetId"],
                "ExerciseId": row["ExcerciseId"],
                "ExerciseName": row["ExerciseName"],
                "Weight": row["Weight"],
                "Repetitions": row["Repetitions"],
            }  
            topsets.append(topset)
    return topsets

def get_startdate(workout_id, rows):
    for r in rows:
        if workout_id == r["WorkoutId"]:
            start_date = r["StartDate"]
            return start_date

def get_person(rows, person_id):
    person = {
        "PersonId": get_person_from_id(person_id),
        "PersonName": get_name_from_rows(rows),
        "Workouts": get_workouts_from_rows(rows)
    }
    return person

def get_person_from_id(person_id):
    for r in rows:
        if person_id == r["PersonId"]:
            person_name = r["PersonName"]
            return person_name

def get_person_id_request():
    person_id = input("Which ID would you like to query?");
    print("Results for Person with ID ",person_id,":")
    print(get_person(rows, person_id));

print(get_person_id_request());