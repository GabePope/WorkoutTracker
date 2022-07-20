CREATE TABLE
  IF NOT EXISTS "Person" (
    "PersonId" INTEGER,
    "Name" TEXT,
    PRIMARY KEY("PersonId" AUTOINCREMENT)
  );

CREATE TABLE
  IF NOT EXISTS "Workout" (
    "WorkoutId" INTEGER,
    "PersonId" INTEGER,
    "StartDate" TEXT NOT NULL,
    PRIMARY KEY("WorkoutId" AUTOINCREMENT),
    FOREIGN KEY("PersonId") REFERENCES Person (PersonId) ON DELETE CASCADE
  );

CREATE TABLE
  IF NOT EXISTS "TopSet" (
    "TopSetId" INTEGER,
    "WorkoutId" INTEGER,
    "ExerciseId" INTEGER,
    "Repetitions" INTEGER,
    "Weight" INTEGER,
    PRIMARY KEY("TopSetId" AUTOINCREMENT),
    FOREIGN KEY("WorkoutId") REFERENCES Workout (WorkoutId) ON DELETE CASCADE,
    FOREIGN KEY("ExerciseId") REFERENCES Exercise (ExerciseId) ON DELETE CASCADE
  );

CREATE TABLE
  IF NOT EXISTS "Exercise" (
    "ExerciseId" INTEGER,
    "Name" TEXT,
    PRIMARY KEY("ExerciseId" AUTOINCREMENT)
  );