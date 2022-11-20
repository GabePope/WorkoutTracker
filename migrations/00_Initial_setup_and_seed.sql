BEGIN;

CREATE TABLE
  IF NOT EXISTS "exercise" (
    "exercise_id" SERIAL PRIMARY KEY,
    "name" TEXT NOT NULL,
    CONSTRAINT min_name_chk CHECK (length (name) >= 2),
    CONSTRAINT max_name_chk CHECK (length (name) <= 100)
  );

INSERT INTO
  "exercise" ("exercise_id", "name")
VALUES
  (1, 'Squat'),
  (2, 'Bench'),
  (3, 'Deadlift'),
  (4, 'Hotep'),
  (5, 'Lat Pulldown'),
  (8, 'DB Seal Row'),
  (9, 'Seated BB Hotep');

CREATE TABLE
  IF NOT EXISTS "person" (
    "person_id" SERIAL PRIMARY KEY,
    "name" TEXT NOT NULL,
    CONSTRAINT min_name_chk CHECK (length (name) >= 2),
    CONSTRAINT max_name_chk CHECK (length (name) <= 100)
  );

INSERT INTO
  "person" ("person_id", "name")
VALUES
  (1, 'Gabe'),
  (2, 'Michael');

CREATE TABLE
  IF NOT EXISTS "workout" (
    "workout_id" SERIAL PRIMARY KEY,
    "person_id" BIGINT NOT NULL,
    "start_date" DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT "workout_person_id_fkey" FOREIGN KEY ("person_id") REFERENCES "person" ("person_id") ON UPDATE NO ACTION ON DELETE CASCADE
  );

INSERT INTO
  "workout" ("workout_id", "person_id", "start_date")
VALUES
  (10, 2, '2022-01-13'),
  (11, 2, '2022-01-18'),
  (12, 2, '2022-01-20'),
  (13, 2, '2022-01-25'),
  (15, 2, '2022-01-27'),
  (16, 2, '2022-02-01'),
  (17, 2, '2022-02-03'),
  (18, 2, '2022-02-08'),
  (19, 2, '2022-02-15'),
  (20, 2, '2022-02-17'),
  (21, 2, '2022-03-01'),
  (22, 2, '2022-03-10'),
  (23, 2, '2022-03-15'),
  (24, 2, '2022-03-22'),
  (25, 2, '2022-04-12'),
  (26, 2, '2022-04-21'),
  (27, 2, '2022-04-26'),
  (28, 2, '2022-04-28'),
  (29, 2, '2022-05-03'),
  (30, 2, '2022-05-05'),
  (31, 2, '2022-05-17'),
  (32, 2, '2022-05-19'),
  (33, 2, '2022-06-07'),
  (34, 2, '2022-06-14'),
  (35, 1, '2022-01-13'),
  (36, 1, '2022-01-18'),
  (37, 1, '2022-02-08'),
  (38, 1, '2022-02-15'),
  (39, 1, '2022-02-17'),
  (40, 1, '2022-03-01'),
  (41, 1, '2022-03-10'),
  (42, 1, '2022-03-15'),
  (43, 1, '2022-03-22'),
  (44, 1, '2022-04-07'),
  (45, 1, '2022-04-21'),
  (46, 1, '2022-04-26'),
  (47, 1, '2022-04-28'),
  (48, 1, '2022-05-03'),
  (49, 1, '2022-05-05'),
  (50, 1, '2022-05-17'),
  (51, 1, '2022-05-19'),
  (52, 1, '2022-06-07'),
  (53, 1, '2022-06-14'),
  (54, 1, '2022-06-29'),
  (55, 1, '2022-07-07'),
  (56, 1, '2022-07-12'),
  (57, 1, '2022-07-15'),
  (65, 1, '2022-11-10'),
  (66, 1, '2022-11-17');

CREATE TABLE
  IF NOT EXISTS "topset" (
    "topset_id" SERIAL PRIMARY KEY,
    "workout_id" BIGINT NOT NULL,
    "exercise_id" BIGINT NOT NULL,
    "repetitions" BIGINT NOT NULL,
    "weight" REAL NOT NULL,
    CONSTRAINT "topset_exercise_id_fkey" FOREIGN KEY ("exercise_id") REFERENCES "exercise" ("exercise_id") ON UPDATE NO ACTION ON DELETE CASCADE,
    CONSTRAINT "topset_workout_id_fkey" FOREIGN KEY ("workout_id") REFERENCES "workout" ("workout_id") ON UPDATE NO ACTION ON DELETE CASCADE
  );

INSERT INTO
  "topset" (
    "topset_id",
    "workout_id",
    "exercise_id",
    "repetitions",
    "weight"
  )
VALUES
  (13, 10, 2, 7, 45),
  (14, 10, 3, 5, 115),
  (15, 11, 1, 10, 55),
  (16, 11, 4, 10, 30),
  (17, 12, 2, 3, 50),
  (18, 12, 3, 10, 115),
  (19, 13, 1, 6, 65),
  (20, 13, 4, 7, 35),
  (21, 15, 2, 1, 55),
  (22, 15, 3, 5, 125),
  (23, 16, 1, 5, 75),
  (24, 16, 4, 5, 40),
  (25, 17, 2, 2, 55),
  (26, 17, 3, 3, 135),
  (27, 18, 1, 2, 80),
  (28, 18, 2, 3, 50),
  (29, 19, 1, 5, 80),
  (30, 19, 4, 3, 45),
  (31, 20, 2, 1, 60),
  (32, 20, 3, 2, 150),
  (33, 21, 1, 7, 75),
  (34, 21, 4, 4, 45),
  (35, 22, 2, 10, 45),
  (36, 22, 3, 10, 100),
  (37, 23, 2, 2, 55),
  (38, 23, 3, 2, 120),
  (39, 24, 1, 5, 60),
  (40, 24, 2, 5, 40),
  (41, 25, 2, 1, 55),
  (42, 25, 3, 1, 130),
  (43, 26, 1, 4, 60),
  (44, 26, 2, 3, 50),
  (45, 27, 2, 2, 55),
  (46, 27, 3, 1, 125),
  (47, 28, 1, 2, 80),
  (48, 28, 4, 2, 42),
  (49, 29, 2, 3, 47),
  (50, 29, 3, 2, 130),
  (51, 30, 1, 5, 80),
  (52, 30, 4, 4, 44),
  (53, 31, 2, 3, 55),
  (54, 31, 3, 2, 140),
  (55, 32, 2, 2, 55),
  (56, 32, 3, 5, 100),
  (57, 33, 1, 3, 85),
  (58, 33, 4, 5, 45),
  (59, 34, 3, 6, 120),
  (60, 34, 4, 5, 45),
  (61, 35, 2, 8, 50),
  (62, 36, 1, 7, 55),
  (63, 36, 4, 4, 25),
  (64, 37, 2, 5, 55),
  (65, 37, 3, 6, 95),
  (66, 38, 1, 3, 65),
  (67, 38, 4, 6, 25),
  (68, 39, 2, 2, 60),
  (69, 39, 3, 8, 105),
  (70, 40, 1, 3, 75),
  (71, 40, 4, 4, 30),
  (72, 41, 2, 11, 50),
  (73, 42, 1, 5, 75),
  (74, 42, 4, 5, 30),
  (75, 43, 2, 4, 60),
  (76, 43, 3, 4, 110),
  (77, 44, 1, 6, 75),
  (78, 44, 4, 2, 35),
  (79, 45, 2, 10, 45),
  (80, 45, 3, 10, 100),
  (81, 46, 1, 3, 80),
  (82, 47, 2, 2, 60),
  (83, 47, 3, 5, 100),
  (84, 48, 2, 4, 55),
  (85, 48, 3, 7, 95),
  (86, 49, 2, 4, 55),
  (87, 49, 3, 7, 110),
  (88, 50, 1, 3, 60),
  (89, 50, 4, 4, 27),
  (90, 51, 2, 1, 65),
  (91, 51, 3, 4, 125),
  (92, 52, 2, 4, 55),
  (93, 52, 3, 5, 100),
  (94, 53, 1, 2, 75),
  (95, 53, 4, 4, 31),
  (96, 54, 2, 11, 40),
  (97, 55, 1, 5, 65),
  (98, 55, 4, 6, 30),
  (99, 56, 2, 4, 60),
  (100, 56, 3, 9, 100),
  (101, 57, 1, 6, 75),
  (102, 57, 4, 3, 35),
  (106, 65, 8, 10, 17.5),
  (107, 65, 2, 6, 45),
  (108, 66, 5, 12, 45),
  (109, 66, 9, 8, 25);

SELECT
  setval ('exercise_exercise_id_seq', 1000, FALSE);

SELECT
  setval ('person_person_id_seq', 1000, FALSE);

SELECT
  setval ('workout_workout_id_seq', 1000, FALSE);

SELECT
  setval ('topset_topset_id_seq', 1000, FALSE);

COMMIT;