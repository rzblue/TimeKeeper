# TimeKeeper

TimeKeeper is a timeclock system for robotics teams to track student hours.

## System requirements:

- Python 3.8 or later
- pipenv

## To run:

```bash
pipenv install
pipenv run start
```

The database file will be in the working directory as `database.sqlite`, or you can select another file with the `DATABSE_FILE` environment variable.

To seed the database with some starter data:

***This will delete all data in the database!***

```python reset_db_development.py```