# Workout tracker

Track topsets over time.

### Setup

Install `python>3`

Install dependencies

```
$ pip install -r requirements.txt
```

Enable development mode

```
PS $ENV:FLASK_ENV='development'
```

Set database url, either setup postgres database locally use migration script or expose deployed one

```
$Env:DATABASE_URL = 'postgres://postgres:***@***:***/***'
```

Start application:

```
flask run
```

### Features

- [x] Track topsets for each workout
- [x] Multi user
- [ ] Authentication/Authorisation
