/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */
;

/*!40101 SET NAMES  */
;

/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */
;

/*!40103 SET TIME_ZONE='+00:00' */
;

/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */
;

/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */
;

/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */
;

-- Dumping structure for table public.exercise
CREATE TABLE
  IF NOT EXISTS "exercise" (
    "exerciseid" BIGINT NOT NULL DEFAULT 'nextval(''exercise_exerciseid_seq''::regclass)',
    "name" TEXT NULL DEFAULT NULL,
    PRIMARY KEY ("exerciseid")
  );

-- Dumping data for table public.exercise: 5 rows
/*!40000 ALTER TABLE "exercise" DISABLE KEYS */
;

INSERT INTO
  "exercise" ("exerciseid", "name")
VALUES
  (1, 'Squat'),
  (2, 'Bench'),
  (3, 'Deadlift'),
  (4, 'Hotep'),
  (5, 'Lat Pulldown');

/*!40000 ALTER TABLE "exercise" ENABLE KEYS */
;

-- Dumping structure for table public.person
CREATE TABLE
  IF NOT EXISTS "person" (
    "personid" BIGINT NOT NULL DEFAULT 'nextval(''person_personid_seq''::regclass)',
    "name" TEXT NULL DEFAULT NULL,
    PRIMARY KEY ("personid")
  );

-- Dumping data for table public.person: 2 rows
/*!40000 ALTER TABLE "person" DISABLE KEYS */
;

INSERT INTO
  "person" ("personid", "name")
VALUES
  (1, 'Gabe'),
  (2, 'Michael');

/*!40000 ALTER TABLE "person" ENABLE KEYS */
;

-- Dumping structure for table public.topset
CREATE TABLE
  IF NOT EXISTS "topset" (
    "topsetid" BIGINT NOT NULL DEFAULT 'nextval(''topset_topsetid_seq''::regclass)',
    "workoutid" BIGINT NULL DEFAULT NULL,
    "exerciseid" BIGINT NULL DEFAULT NULL,
    "repetitions" BIGINT NULL DEFAULT NULL,
    "weight" BIGINT NULL DEFAULT NULL,
    PRIMARY KEY ("topsetid"),
    CONSTRAINT "topset_exerciseid_fkey" FOREIGN KEY ("exerciseid") REFERENCES "exercise" ("exerciseid") ON UPDATE NO ACTION ON DELETE CASCADE,
    CONSTRAINT "topset_workoutid_fkey" FOREIGN KEY ("workoutid") REFERENCES "workout" ("workoutid") ON UPDATE NO ACTION ON DELETE CASCADE
  );

-- Dumping data for table public.topset: 90 rows
/*!40000 ALTER TABLE "topset" DISABLE KEYS */
;

INSERT INTO
  "topset" (
    "topsetid",
    "workoutid",
    "exerciseid",
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
  (102, 57, 4, 3, 35);

/*!40000 ALTER TABLE "topset" ENABLE KEYS */
;

-- Dumping structure for table public.workout
CREATE TABLE
  IF NOT EXISTS "workout" (
    "workoutid" BIGINT NOT NULL DEFAULT 'nextval(''workout_workoutid_seq''::regclass)',
    "personid" BIGINT NULL DEFAULT NULL,
    "startdate" TEXT NULL DEFAULT NULL,
    PRIMARY KEY ("workoutid"),
    CONSTRAINT "workout_personid_fkey" FOREIGN KEY ("personid") REFERENCES "person" ("personid") ON UPDATE NO ACTION ON DELETE CASCADE
  );

-- Dumping data for table public.workout: 47 rows
/*!40000 ALTER TABLE "workout" DISABLE KEYS */
;

INSERT INTO
  "workout" ("workoutid", "personid", "startdate")
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
  (57, 1, '2022-07-15');

/*!40000 ALTER TABLE "workout" ENABLE KEYS */
;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */
;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */
;

/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */
;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */
;

/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */
;