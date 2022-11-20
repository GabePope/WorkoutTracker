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
            'SELECT exercise_id AS "ExerciseId", name AS "Name" FROM exercise')
        return [{"ExerciseId": e['ExerciseId'], "Name": e['Name']} for e in exercises]

    def get_exercise(self, exercise_id):
        exercise = self.execute(
            'SELECT exercise_id AS "ExerciseId", name AS "Name" FROM exercise WHERE exercise_id=%s LIMIT 1', [exercise_id], one=True)
        return exercise

    def create_exercise(self, name):
        new_exercise = self.execute('INSERT INTO exercise (name) VALUES (%s) RETURNING exercise_id AS "ExerciseId"',
                                    [name], commit=True, one=True)
        return new_exercise['ExerciseId']

    def delete_exercise(self, exercise_id):
        self.execute('DELETE FROM exercise WHERE exercise_id=%s', [
            exercise_id], commit=True)

    def update_exercise(self, exercise_id, name):
        self.execute('UPDATE Exercise SET Name=%s WHERE exercise_id=%s', [
            name, exercise_id], commit=True)

    def get_people(self):
        people = self.execute(
            'SELECT person_id AS "PersonId", name AS "Name" FROM person')
        return people

    def is_valid_person(self, person_id):
        person = self.execute(
            'SELECT person_id AS "PersonId" FROM person WHERE person_id=%s LIMIT 1', [person_id], one=True)
        return person

    def create_person(self, name):
        new_person = self.execute('INSERT INTO person (name) VALUES (%s) RETURNING person_id AS "PersonId"', [
                                  name], commit=True, one=True)
        return new_person['PersonId']

    def delete_person(self, person_id):
        self.execute('DELETE FROM topset WHERE workout_id IN (SELECT workout_id FROM workout WHERE person_id=%s)', [
            person_id], commit=True)
        self.execute('DELETE FROM workout WHERE person_id=%s',
                     [person_id], commit=True)
        self.execute('DELETE FROM person WHERE person_id=%s',
                     [person_id], commit=True)

    def update_person_name(self, person_id, name):
        self.execute('UPDATE person SET name=%s WHERE person_id=%s', [
            name, person_id], commit=True)

    def is_valid_workout(self, person_id, workout_id):
        workout = self.execute('SELECT W.workout_id AS "WorkoutId" FROM Person P, Workout W WHERE P.person_id=W.person_id AND P.person_id=%s AND W.workout_id=%s LIMIT 1', [
            person_id, workout_id], one=True)
        return workout

    def is_valid_topset(self, person_id, workout_id, topset_id):
        topset = self.execute("""
            SELECT T.topset_id AS "TopSetId"
            FROM Person P, Workout W, TopSet T
            WHERE W.person_id=W.person_id AND W.workout_id=T.workout_id AND P.person_id=%s AND W.workout_id = %s AND T.topset_id = %s
            LIMIT 1""", [person_id, workout_id, topset_id], one=True)
        return topset

    def delete_workout(self, workout_id):
        self.execute('DELETE FROM topset WHERE workout_id=%s',
                     [workout_id], commit=True)
        self.execute('DELETE FROM workout WHERE workout_id=%s',
                     [workout_id], commit=True)

    def update_topset(self, exercise_id, repetitions, weight, topset_id):
        self.execute('UPDATE topset SET exercise_id=%s, repetitions=%s, weight=%s WHERE topSet_id=%s', [
            exercise_id, repetitions, weight, topset_id], commit=True)

    def create_topset(self, workout_id, exercise_id, repetitions, weight):
        new_top_set = self.execute('INSERT INTO topset (workout_id, exercise_id, repetitions, weight) VALUES (%s, %s, %s, %s) RETURNING topset_id AS "TopSetId"', [
            workout_id, exercise_id, repetitions, weight], commit=True, one=True)
        return new_top_set['TopSetId']

    def delete_topset(self, topset_id):
        self.execute('DELETE FROM topset WHERE topset_id=%s', [
            topset_id], commit=True)

    def create_workout(self, person_id):
        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')
        print(
            f'Creating workout for PersonId {person_id} starting at {date_string}')
        new_workout = self.execute('INSERT INTO workout (person_id, start_date) VALUES (%s, %s) RETURNING workout_id AS "WorkoutId"', [
            person_id, date_string], commit=True, one=True)
        return new_workout['WorkoutId']

    def get_people_and_workout_count(self, person_id):
        return self.execute("""
            SELECT
                P.person_id AS "PersonId",
                P.name AS "Name",
                COUNT(W.workout_id) AS "NumberOfWorkouts",
                CASE P.person_id
                    WHEN %s
                        THEN 1
                        ELSE 0
                    END "IsActive"
            FROM
                Person P LEFT JOIN Workout W ON P.person_id = W.person_id
            GROUP BY
                P.person_id
            ORDER BY
                P.person_id""", [person_id])

    def update_workout_start_date(self, workout_id, start_date):
        self.execute('UPDATE workout SET start_date=%s WHERE workout_id=%s', [
            start_date, workout_id], commit=True)

    def get_person(self, person_id):
        topsets = self.execute("""
            SELECT
                P.person_id AS "PersonId",
                P.name AS "PersonName",
                W.workout_id AS "WorkoutId",
                W.start_date AS "StartDate",
                T.topset_id AS "TopSetId",
                E.exercise_id AS "ExerciseId",
                E.name AS "ExerciseName",
                T.repetitions AS "Repetitions",
                T.weight AS "Weight"
            FROM Person P
                LEFT JOIN Workout W ON P.person_id=W.person_id
                LEFT JOIN TopSet T ON W.workout_id=T.workout_id
                LEFT JOIN Exercise E ON T.exercise_id=E.exercise_id
            WHERE P.person_id=%s""", [person_id])

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
                P.person_id AS "PersonId",
                P.name AS "PersonName",
                W.workout_id AS "WorkoutId",
                W.start_date AS "StartDate",
                T.topset_id AS "TopSetId",
                E.exercise_id AS "ExerciseId",
                E.name AS "ExerciseName",
                T.repetitions AS "Repetitions",
                T.weight AS "Weight"
            FROM Person P
                LEFT JOIN Workout W ON P.person_id=W.person_id
                LEFT JOIN TopSet T ON W.workout_id=T.workout_id
                LEFT JOIN Exercise E ON T.exercise_id=E.exercise_id
            WHERE P.person_id=%s
                AND W.workout_id = %s""", [person_id, workout_id])

        return {
            'PersonId': next((t['PersonId'] for t in topsets), -1),
            'PersonName': next((t['PersonName'] for t in topsets), 'Unknown'),
            'WorkoutId': workout_id,
            'StartDate': topsets[0]['StartDate'].strftime("%Y-%m-%d"),
            'Exercises': self.get_exercises(),
            'TopSets': [{"TopSetId": t['TopSetId'], "ExerciseId": t['ExerciseId'], "ExerciseName": t['ExerciseName'], "Weight": t['Weight'], "Repetitions": t['Repetitions']} for t in topsets if t['TopSetId'] is not None]
        }

    def get_topset(self, person_id, workout_id, topset_id):
        topset = self.execute("""
            SELECT
                P.person_id AS "PersonId",
                P.name AS "PersonName",
                W.workout_id AS "WorkoutId",
                W.start_date AS "StartDate",
                T.topset_id AS "TopSetId",
                E.exercise_id AS "ExerciseId",
                E.name AS "ExerciseName",
                T.repetitions AS "Repetitions",
                T.weight AS "Weight"
            FROM Person P
                INNER JOIN Workout W ON P.person_id=W.person_id
                INNER JOIN TopSet T ON W.workout_id=T.workout_id
                INNER JOIN Exercise E ON T.exercise_id=E.exercise_id
            WHERE P.person_id=%s
                AND W.workout_id = %s
                AND T.topset_id = %s""", [person_id, workout_id, topset_id], one=True)

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
            P.person_id AS "PersonId",
            P.name AS "PersonName",
            W.workout_id AS "WorkoutId",
            W.start_date AS "StartDate",
            T.topset_id AS "TopSetId",
            E.exercise_id AS "ExerciseId",
            E.name AS "ExerciseName",
            T.repetitions AS "Repetitions",
            T.weight AS "Weight",
            round((100 * T.Weight::numeric::integer)/(101.3-2.67123 * T.Repetitions),0)::numeric::integer AS "Estimated1RM"
        FROM Person P
            LEFT JOIN Workout W ON P.person_id=W.person_id
            LEFT JOIN TopSet T ON W.workout_id=T.workout_id
            LEFT JOIN Exercise E ON T.exercise_id=E.exercise_id""")

        return all_topsets
