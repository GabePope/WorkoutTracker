CREATE TABLE IF NOT EXISTS "Person" (
	"PersonId"	INTEGER,
	"Name"	TEXT,
	PRIMARY KEY("PersonId" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "Workout" (
	"WorkoutId"	INTEGER,
	"PersonId"	INTEGER,
	"StartDate"	TEXT NOT NULL,
		
	PRIMARY KEY("WorkoutId" AUTOINCREMENT),
	FOREIGN KEY("PersonId") REFERENCES Person (PersonId)
);

CREATE TABLE IF NOT EXISTS "TopSet" (
	"TopSetId" INTEGER,
	"WorkoutId" INTEGER,
	"ExcerciseId" INTEGER,
	"Repetitions" INTEGER,
	"Weight" INTEGER,
	PRIMARY KEY("TopSetId" AUTOINCREMENT),
	FOREIGN KEY("WorkoutId") REFERENCES Workout (WorkoutId),	
	FOREIGN KEY("ExcerciseId") REFERENCES Excercise (ExcerciseId)
);	
	
CREATE TABLE IF NOT EXISTS "Excercise" (
	"ExcerciseId"	INTEGER,
	"Name"	TEXT,
	PRIMARY KEY("ExcerciseId" AUTOINCREMENT)
);	
	