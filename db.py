import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from urllib.parse import urlparse

from utils import get_all_exercises_from_topsets, get_stats_from_topsets, get_workouts


class DataBase():
    def __init__(self, app):
        db_url = urlparse(os.environ['DATABASE_URL'])

        self.conn = psycopg2.connect(
            database=db_url.path[1:],
            user=db_url.username,
            password=db_url.password,
            host=db_url.hostname,
            port=db_url.port
        )

    def execute(self, query, args=(), one=False, commit=False):
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, args)
        rv = None
        if cur.description is not None:
            rv = cur.fetchall()
        if commit:
            self.conn.commit()
        cur.close()

        return (rv[0] if rv else None) if one else rv

    def get_exercises(self):
        exercises = self.execute(
            'SELECT ExerciseId AS "ExerciseId", Name AS "Name" FROM Exercise')
        return [{"ExerciseId": e['ExerciseId'], "Name": e['Name']} for e in exercises]

    def get_exercise(self, exercise_id):
        exercise = self.execute(
            'SELECT ExerciseId AS "ExerciseId", Name AS "Name" FROM Exercise WHERE ExerciseId=%s LIMIT 1', [exercise_id], one=True)
        return exercise

    def create_exercise(self, name):
        new_exercise = self.execute('INSERT INTO Exercise (Name) VALUES (%s) RETURNING ExerciseId AS "ExerciseId"',
                                    [name], commit=True, one=True)
        return new_exercise['ExerciseId']

    def delete_exercise(self, exercise_id):
        self.execute('DELETE FROM Exercise WHERE ExerciseId=%s', [
            exercise_id], commit=True)

    def update_exercise(self, exercise_id, name):
        self.execute('UPDATE Exercise SET Name=%s WHERE ExerciseId=%s', [
            name, exercise_id], commit=True)

    def get_people(self):
        people = self.execute(
            'SELECT PersonId AS "PersonId", Name AS "Name" FROM Person')
        return people

    def is_valid_person(self, person_id):
        person = self.execute(
            'SELECT PersonId AS "PersonId" FROM Person WHERE PersonId=%s LIMIT 1', [person_id], one=True)
        return person

    def create_person(self, name):
        new_person = self.execute('INSERT INTO Person (Name) VALUES (%s) RETURNING PersonId AS "PersonId"', [
                                  name], commit=True, one=True)
        return new_person['PersonId']

    def delete_person(self, person_id):
        self.execute('DELETE FROM TopSet WHERE WorkoutId IN (SELECT WorkoutId FROM Workout WHERE PersonId=%s)', [
            person_id], commit=True)
        self.execute('DELETE FROM Workout WHERE PersonId=%s',
                     [person_id], commit=True)
        self.execute('DELETE FROM Person WHERE PersonId=%s',
                     [person_id], commit=True)

    def update_person_name(self, person_id, name):
        self.execute('UPDATE Person SET Name=%s WHERE PersonId=%s', [
            name, person_id], commit=True)

    def is_valid_workout(self, person_id, workout_id):
        workout = self.execute('SELECT W.WorkoutId AS "WorkoutId" FROM Person P, Workout W WHERE P.PersonId=W.PersonId AND P.PersonId=%s AND W.WorkoutId=%s LIMIT 1', [
            person_id, workout_id], one=True)
        return workout

    def is_valid_topset(self, person_id, workout_id, topset_id):
        topset = self.execute("""
            SELECT T.TopSetId AS "TopSetId"
            FROM Person P, Workout W, TopSet T
            WHERE W.PersonId=W.PersonId AND W.WorkoutId=T.WorkoutId AND P.PersonId=%s AND W.WorkoutId = %s AND T.TopSetId = %s
            LIMIT 1""", [person_id, workout_id, topset_id], one=True)
        return topset

    def delete_workout(self, workout_id):
        self.execute('DELETE FROM TopSet WHERE WorkoutId=%s',
                     [workout_id], commit=True)
        self.execute('DELETE FROM Workout WHERE WorkoutId=%s',
                     [workout_id], commit=True)

    def update_topset(self, exercise_id, repetitions, weight, topset_id):
        self.execute('UPDATE TopSet SET ExerciseId=%s, Repetitions=%s, Weight=%s WHERE TopSetId=%s', [
            exercise_id, repetitions, weight, topset_id], commit=True)

    def create_topset(self, workout_id, exercise_id, repetitions, weight):
        new_top_set = self.execute('INSERT INTO TopSet (WorkoutId, ExerciseId, Repetitions, Weight) VALUES (%s, %s, %s, %s) RETURNING TopSetId AS "TopSetId"', [
            workout_id, exercise_id, repetitions, weight], commit=True, one=True)
        return new_top_set['TopSetId']

    def delete_topset(self, topset_id):
        self.execute('DELETE FROM TopSet WHERE TopSetId=%s', [
            topset_id], commit=True)

    def create_workout(self, person_id):
        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')
        print(
            f'Creating workout for PersonId {person_id} starting at {date_string}')
        new_workout = self.execute('INSERT INTO Workout (PersonId, StartDate) VALUES (%s, %s) RETURNING WorkoutId AS "WorkoutId"', [
            person_id, date_string], commit=True, one=True)
        return new_workout['WorkoutId']

    def get_people_and_workout_count(self, person_id):
        return self.execute("""
            SELECT
                P.PersonId AS "PersonId",
                P.Name AS "Name",
                COUNT(W.WorkoutId) AS "NumberOfWorkouts",
                CASE P.PersonId
                    WHEN %s
                        THEN 1
                        ELSE 0
                    END "IsActive"
            FROM
                Person P LEFT JOIN Workout W ON P.PersonId = W.PersonId
            GROUP BY
                P.PersonId
            ORDER BY
                P.PersonId""", [person_id])

    def update_workout_start_date(self, workout_id, start_date):
        self.execute('UPDATE Workout SET StartDate=%s WHERE WorkoutId=%s', [
            start_date, workout_id], commit=True)

    def get_person(self, person_id):
        topsets = self.execute("""
            SELECT
                P.PersonId AS "PersonId",
                P.Name AS "PersonName",
                W.WorkoutId AS "WorkoutId",
                W.StartDate AS "StartDate",
                T.TopSetId AS "TopSetId",
                E.ExerciseId AS "ExerciseId",
                E.Name AS "ExerciseName",
                T.Repetitions AS "Repetitions",
                T.Weight AS "Weight"
            FROM Person P
                LEFT JOIN Workout W ON P.PersonId=W.PersonId
                LEFT JOIN TopSet T ON W.WorkoutId=T.WorkoutId
                LEFT JOIN Exercise E ON T.ExerciseId=E.ExerciseId
            WHERE P.PersonId=%s""", [person_id])

        return {
            'PersonId': next((t['PersonId'] for t in topsets), -1),
            'PersonName': next((t['PersonName'] for t in topsets), 'Unknown'),
            'Stats': get_stats_from_topsets(topsets),
            'Exercises': get_all_exercises_from_topsets(topsets),
            'Workouts': get_workouts(topsets)
        }

    def get_workout(self, person_id, workout_id):
        topsets = self.execute("""
            SELECT
                P.PersonId AS "PersonId",
                P.Name AS "PersonName",
                W.WorkoutId AS "WorkoutId",
                W.StartDate AS "StartDate",
                T.TopSetId AS "TopSetId",
                E.ExerciseId AS "ExerciseId",
                E.Name AS "ExerciseName",
                T.Repetitions AS "Repetitions",
                T.Weight AS "Weight"
            FROM Person P
                LEFT JOIN Workout W ON P.PersonId=W.PersonId
                LEFT JOIN TopSet T ON W.WorkoutId=T.WorkoutId
                LEFT JOIN Exercise E ON T.ExerciseId=E.ExerciseId
            WHERE P.PersonId=%s
                AND W.WorkoutId = %s""", [person_id, workout_id])

        return {
            'PersonId': next((t['PersonId'] for t in topsets), -1),
            'PersonName': next((t['PersonName'] for t in topsets), 'Unknown'),
            'WorkoutId': workout_id,
            'StartDate': datetime.strptime(topsets[0]['StartDate'], "%Y-%m-%d").strftime("%Y-%m-%d"),
            'Exercises': self.get_exercises(),
            'TopSets': [{"TopSetId": t['TopSetId'], "ExerciseId": t['ExerciseId'], "ExerciseName": t['ExerciseName'], "Weight": t['Weight'], "Repetitions": t['Repetitions']} for t in topsets if t['TopSetId'] is not None]
        }

    def get_topset(self, person_id, workout_id, topset_id):
        topset = self.execute("""
            SELECT
                P.PersonId AS "PersonId",
                P.Name AS "PersonName",
                W.WorkoutId AS "WorkoutId",
                W.StartDate AS "StartDate",
                T.TopSetId AS "TopSetId",
                E.ExerciseId AS "ExerciseId",
                E.Name AS "ExerciseName",
                T.Repetitions AS "Repetitions",
                T.Weight AS "Weight"
            FROM Person P
                INNER JOIN Workout W ON P.PersonId=W.PersonId
                INNER JOIN TopSet T ON W.WorkoutId=T.WorkoutId
                INNER JOIN Exercise E ON T.ExerciseId=E.ExerciseId
            WHERE P.PersonId=%s
                AND W.WorkoutId = %s
                AND T.TopSetId = %s""", [person_id, workout_id, topset_id], one=True)

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

    def get_all_topsets(self):
        all_topsets = self.execute("""
            SELECT
            P.PersonId AS "PersonId",
            P.Name AS "PersonName",
            W.WorkoutId AS "WorkoutId",
            W.StartDate AS "StartDate",
            T.TopSetId AS "TopSetId",
            E.ExerciseId AS "ExerciseId",
            E.Name AS "ExerciseName",
            T.Repetitions AS "Repetitions",
            T.Weight AS "Weight",
            round((100 * T.Weight)/(101.3-2.67123 * T.Repetitions),0)::numeric::integer AS "Estimated1RM"
        FROM Person P
            LEFT JOIN Workout W ON P.PersonId=W.PersonId
            LEFT JOIN TopSet T ON W.WorkoutId=T.WorkoutId
            LEFT JOIN Exercise E ON T.ExerciseId=E.ExerciseId""")

        return all_topsets
