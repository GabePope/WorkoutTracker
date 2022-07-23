import datetime
import sqlite3

from utils import get_all_exercises_from_topsets, get_workouts


class DataBase():
    def __init__(self, app):
        self.DATABASE_URI = app.config['DATABASE_URI']

    def execute(self, query, args=(), one=False, commit=False):
        conn = sqlite3.connect(self.DATABASE_URI)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        if commit:
            conn.commit()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def get_exercises(self):
        exercises = self.execute('SELECT * FROM Exercise')
        return [{"ExerciseId": e['ExerciseId'], "Name": e['Name']} for e in exercises]

    def get_person(self, person_id):
        person = self.execute(
            'SELECT * FROM Person WHERE PersonId=? LIMIT 1', [person_id], one=True)
        return person

    def get_workout(self, person_id, workout_id):
        workout = self.execute('SELECT W.WorkoutId FROM Person P, Workout W WHERE P.PersonId=W.PersonId AND P.PersonId=? AND W.WorkoutId=? LIMIT 1', [
                               person_id, workout_id], one=True)
        return workout

    def get_topset(self, person_id, workout_id, topset_id):
        topset = self.execute("""
            SELECT T.TopSetId
            FROM Person P, Workout W, TopSet T
            WHERE W.PersonId=W.PersonId AND W.WorkoutId=T.WorkoutId AND P.PersonId=? AND W.WorkoutId = ? AND T.TopSetId = ?
            LIMIT 1""", [person_id, workout_id, topset_id], one=True)
        return topset

    def delete_workout(self, workout_id):
        self.execute('DELETE FROM TopSet WHERE WorkoutId=?',
                     [workout_id], commit=True)
        self.execute('DELETE FROM Workout WHERE WorkoutId=?',
                     [workout_id], commit=True)

    def update_topset(self, exercise_id, repetitions, weight, topset_id):
        self.execute('UPDATE TopSet SET ExerciseId=?, Repetitions=?, Weight=? WHERE TopSetId=?', [
            exercise_id, repetitions, weight, topset_id], commit=True)

    def create_topset(self, workout_id, exercise_id, repetitions, weight):
        self.execute('INSERT INTO TopSet (WorkoutId, ExerciseId, Repetitions, Weight) VALUES (?, ?, ?, ?)', [
            workout_id, exercise_id, repetitions, weight], commit=True)

    def delete_topset(self, topset_id):
        self.execute('DELETE FROM TopSet WHERE TopSetId=?', [
            topset_id], commit=True)

    def create_workout(self, person_id):
        now = datetime.datetime.now()
        date_string = now.strftime('%Y-%m-%d')
        print(f'Creating workout for {person_id} at {date_string}')
        self.execute('INSERT INTO Workout (PersonId, StartDate) VALUES	(?, ?)', [
            person_id, date_string], commit=True)
        w = self.execute('SELECT MAX(WorkoutId) AS WorkoutId FROM Workout WHERE PersonId=?', [
                         person_id], one=True)
        return w['WorkoutId']

    def get_people_and_workout_count(self, person_id):
        return self.execute("""
                    SELECT
                    P.PersonId,
                    P.Name,
                    COUNT(W.WorkoutId) AS NumberOfWorkouts,
                    CASE P.PersonId
                        WHEN ?
                            THEN 1
                            ELSE 0
                    END IsActive
                FROM
                    Person P
                    LEFT JOIN Workout W ON P.PersonId = W.PersonId
                GROUP BY
                    P.PersonId""", [person_id])

    def get_person_final(self, person_id):
        topsets = self.execute("""
            SELECT 
                P.PersonId, 
                P.Name AS PersonName, 
                W.WorkoutId, 
                W.StartDate, 
                T.TopSetId, 
                E.ExerciseId, 
                E.Name AS ExerciseName, 
                T.Repetitions, 
                T.Weight
            FROM Person P
                LEFT JOIN Workout W ON P.PersonId=W.PersonId
                LEFT JOIN TopSet T ON W.WorkoutId=T.WorkoutId
                LEFT JOIN Exercise E ON T.ExerciseId=E.ExerciseId
            WHERE P.PersonId=?""", [person_id])

        return {
            'PersonId': next((t['PersonId'] for t in topsets), -1),
            'PersonName': next((t['PersonName'] for t in topsets), 'Unknown'),
            'Exercises': get_all_exercises_from_topsets(topsets),
            'Workouts': get_workouts(topsets)
        }

    def get_workout_final(self, person_id, workout_id):
        topsets = self.execute("""
            SELECT 
                P.PersonId, 
                P.Name AS PersonName, 
                W.WorkoutId, 
                W.StartDate, 
                T.TopSetId, 
                E.ExerciseId, 
                E.Name AS ExerciseName, 
                T.Repetitions, 
                T.Weight
            FROM Person P
                LEFT JOIN Workout W ON P.PersonId=W.PersonId
                LEFT JOIN TopSet T ON W.WorkoutId=T.WorkoutId
                LEFT JOIN Exercise E ON T.ExerciseId=E.ExerciseId
            WHERE P.PersonId=?
                AND W.WorkoutId = ?""", [person_id, workout_id])

        return {
            'PersonId': next((t['PersonId'] for t in topsets), -1),
            'PersonName': next((t['PersonName'] for t in topsets), 'Unknown'),
            'WorkoutId': workout_id,
            'StartDate': next((t['StartDate'] for t in topsets), 'Unknown'),
            'Exercises': self.get_exercises(),
            'TopSets': [{"TopSetId": t['TopSetId'], "ExerciseId": t['ExerciseId'], "ExerciseName": t['ExerciseName'], "Weight": t['Weight'], "Repetitions": t['Repetitions']} for t in topsets if t['TopSetId'] is not None]
        }

    def get_topset_final(self, person_id, workout_id, topset_id):
        topset = self.execute("""
            SELECT 
                P.PersonId, 
                P.Name AS PersonName, 
                W.WorkoutId, 
                W.StartDate, 
                T.TopSetId, 
                E.ExerciseId, 
                E.Name AS ExerciseName, 
                T.Repetitions, 
                T.Weight
            FROM Person P
                INNER JOIN Workout W ON P.PersonId=W.PersonId
                INNER JOIN TopSet T ON W.WorkoutId=T.WorkoutId
                INNER JOIN Exercise E ON T.ExerciseId=E.ExerciseId
            WHERE P.PersonId=?
                AND W.WorkoutId = ?
                AND T.TopSetId = ?""", [person_id, workout_id, topset_id], one=True)

        return {
            'PersonId': topset['PersonId'],
            'PersonName': topset['PersonName'],
            'WorkoutId': workout_id,
            'StartDate': topset['StartDate'],
            'Exercises': self.get_exercises(),
            "TopSetId": topset['TopSetId'],
            "ExerciseId": topset['ExerciseId'],
            "ExerciseName": topset['ExerciseName'],
            "Weight": topset['Weight'],
            "Repetitions": topset['Repetitions']
        }
