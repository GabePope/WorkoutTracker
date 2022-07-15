INSERT INTO Person (Name)
	VALUES	("Gabe"),
			("Michael");

INSERT INTO Excercise (Name)
	VALUES	("Squat"),
			("Bench"),
			("Deadlift"),
			("Hotep"),
			("Lat Pulldown");
			
INSERT INTO Workout (PersonId, StartDate)
	VALUES	(1, "2022-06-29 00:00:00.000"),
			(1, "2022-07-07 00:00:00.000"),
			(1, "2022-07-12 00:00:00.000");
			
INSERT INTO TopSet (WorkoutId, ExcerciseId, Repetitions, Weight)
	VALUES	(1, 2, 11, 40),
			(2, 1, 5, 65),
			(2, 4, 6, 30),
			(3, 2, 4, 60),
			(3, 3, 9, 100);