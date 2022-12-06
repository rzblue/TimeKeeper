import sqlite3
from datetime import datetime

from models import User, NullableUser, TimeSession, NullableTimeSession

import logging

logger = logging.getLogger(__name__)


class StorageAPI:
    def __init__(self, file: str):
        """Open the database connection and initialize tables."""
        self.__db = sqlite3.connect(
            file, detect_types=sqlite3.PARSE_COLNAMES | sqlite3.PARSE_DECLTYPES
        )
        self.initialize_tables()

    @property
    def connection(self):
        """get the opened database connection."""
        return self.__db

    # USERS #

    def get_all_users(self) -> list[User]:
        """get a list of all users."""
        cursor = self.connection.cursor()
        results = self.connection.cursor().execute("""SELECT * FROM users""")
        users: list[User] = []
        for record in results:
            users.append(User.from_tuple(record))
        return users

    def get_user_by_id_string(self, id_string: str) -> NullableUser:
        """get a single user by their unique ID string.

        Returns None if the given id string is not found

        """
        result = self.connection.cursor().execute(
            "SELECT * FROM users WHERE id_string = ?", (id_string,)
        )
        data = result.fetchone()
        if data is None:
            return None
        return User.from_tuple(data)

    def get_user_by_id(self, id_: int) -> User | None:
        """get a single user by their database id.

        Returns None if the given id is not found

        """
        result = self.connection.cursor().execute(
            "SELECT * FROM users WHERE id = ?", (id_,)
        )
        data = result.fetchone()
        if data is None:
            return None
        return User.from_tuple(data)

    def create_user(self, user: User) -> NullableUser:
        """adds a user to the database and returns the user.

        Returns None if the provided User's id string matches another in the database or
        is otherwise unsuccessful

        """
        cur = self.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO users VALUES (null, ?, ?)", (user.name, user.id_string)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            logger.warning(
                "Could not create user! User already exists with id_string: %s", user
            )
            return None
        user.id = cur.lastrowid
        return user

    def update_user(self, user: User) -> NullableUser:
        """Updates a user.

        Returns the same user if the update is successful, or None if unsuccessful.

        """
        if not user.id:
            return None
        cur = self.connection.cursor()
        try:
            cur.execute(
                "UPDATE users SET name = ?, id_string = ? WHERE id = ?",
                (user.name, user.id_string, user.id),
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            logger.warning(
                "Could not update user! User already exists with id_string %s",
                user.id_string,
            )
            return None
        return user

    # SESSIONS #
    def start_time_session(
        self, user: User, start_time: datetime = None
    ) -> TimeSession:
        """Creates a new time session in the database with the given user and
        start_time. If start_time is not provided, the current time will be used.

        Returns a TimeSession object.

        """
        if start_time is None:
            start_time = datetime.now()
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO time_sessions VALUES (null, ?, ?, null)", (user.id, start_time)
        )
        self.connection.commit()
        return TimeSession(user.id, start_time, None, cur.lastrowid)

    def end_time_session(
        self, time_session: TimeSession, end_time: datetime = None
    ) -> NullableTimeSession:
        """Ends the given TimeSession with end_time and updates the database entry.

        If end_time is not provided, the current time will be used. Returns the ended
        TimeSession, or None if unsuccessful

        """
        time_session = self.get_time_session_by_id(time_session.id)
        if time_session is None:
            return None
        # Bail if start_time isn't set - you can't finish an unstarted session
        if not time_session.start_time:
            return None
        if end_time is None:
            end_time = datetime.now()
        time_session.end_time = end_time
        # Delegate to update
        return self.update_time_session(time_session)

    def end_time_session_by_id(self, session_id: int, end_time: datetime = None) -> NullableTimeSession:
        """Ends the time session with the given id.

        Returns the ended TimeSession, or None if unsuccessful

        """
        time_session = self.get_time_session_by_id(session_id)
        if time_session is None:
            logger.warning("Tried to end non-existent time session: ID %s", session_id)
            return None
        if time_session.has_ended:
            logger.warning("Tried to end already ended time session: ID %s", session_id)
            return None
        if end_time is None:
            end_time = datetime.now()
        time_session.end_time = end_time
        return self.update_time_session(time_session)

    def update_time_session(self, time_session: TimeSession) -> NullableTimeSession:
        """Updates the TimeSession in the database.

        This uses time_session.id to perform the update. Returns the updated
        TimeSession, or None if unsuccessful

        """
        if not time_session.id:
            return None
        cur = self.connection.cursor()
        try:
            cur.execute(
                "UPDATE time_sessions SET user_id = ?, start_time = ?, end_time = ? WHERE id = ?",
                (
                    time_session.user_id,
                    time_session.start_time,
                    time_session.end_time,
                    time_session.id,
                ),
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            logger.warning("Could not update time session!")
            return None
        if cur.rowcount <= 0:
            logger.warning("Did not update time session!")
            return None
        return time_session

    def get_time_session_by_id(self, session_id: int) -> NullableTimeSession:
        """Gets a single time session by its database ID.

        Returns Null if the session ID does not exist in the database

        """
        cur = self.connection.cursor()
        results = cur.execute("SELECT * FROM time_sessions WHERE id = ?", (session_id,))
        if results.arraysize <= 0:
            return None
        session_tuple = results.fetchone()
        return TimeSession.from_tuple(session_tuple)

    def get_active_sessions(self) -> list[TimeSession]:
        """Get a list of all active sessions (sessions without an end_time)."""
        cur = self.connection.cursor()
        results = cur.execute(
            "SELECT * FROM time_sessions WHERE end_time IS NULL",
        )
        sessions: list[TimeSession] = []
        for record in results:
            sessions.append(TimeSession.from_tuple(record))
        return sessions

    def get_time_sessions_for_user(self, user: User):
        """Get a list of all time sessions associated with user."""
        cur = self.connection.cursor()
        results = cur.execute(
            "SELECT * FROM time_sessions WHERE user_id = ?", (user.id,)
        )
        sessions: list[TimeSession] = []
        for record in results:
            sessions.append(TimeSession.from_tuple(record))
        return sessions

    def get_all_active_time_sessions_for_user(self, user: User):
        """Get a list of all active time sessions (sessions without an end_time)
        associated with user, sorted by start_time."""
        cur = self.connection.cursor()
        results = cur.execute(
            """SELECT * from time_sessions WHERE user_id = ? 
            AND start_time IS NOT NULL
            AND end_time IS NULL
            ORDER BY start_time DESC""",
            (user.id,),
        )
        sessions: list[TimeSession] = []
        for record in results:
            sessions.append(TimeSession.from_tuple(record))
        return sessions

    def get_latest_active_time_session_for_user(self, user: User):
        """Get the most recently started active time session for the user."""
        sessions = self.get_all_active_time_sessions_for_user(user)
        if len(sessions) <= 0:
            return None
        return sessions[0]

    def get_completed_time_sessions_for_user(self, user: User):
        """Get a list of all completed (start and end times exist) sessions for user."""
        cur = self.connection.cursor()
        results = cur.execute(
            "SELECT * from time_sessions WHERE user_id = ? AND end_time IS NOT NULL",
            (user.id,),
        )
        sessions: list[TimeSession] = []
        for record in results:
            sessions.append(TimeSession.from_tuple(record))
        return sessions

    def end_all_sessions(self, end_time: datetime = None):
        """End all active sessions with end_time.

        If end_time is not provided, the current time will be used.

        """
        if end_time is None:
            end_time = datetime.now()
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE time_sessions SET end_time = ? WHERE end_time IS NULL AND start_time IS NOT NULL",
            (end_time,),
        )
        self.connection.commit()

    def cleanup_sessions(self):
        """Deletes any time sessions where start time or user id are null."""
        cur = self.connection.cursor()
        cur.execute(
            "DELETE FROM time_sessions WHERE start_time IS NULL OR user_id IS NULL"
        )
        self.connection.commit()

    def reset_all_dangerous(self):
        """DELETES ALL TABLES, FOR DEVELOPMENT ONLY."""
        cur = self.connection.cursor()
        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("DROP TABLE IF EXISTS time_sessions")
        self.connection.commit()

    def initialize_tables(self):
        """Creates the necessary tables if they don't exist."""
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                name VARCHAR(20),
                id_string VARCHAR(20) UNIQUE
            )"""
        )

        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS time_sessions(
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                start_time timestamp,
                end_time timestamp
            )"""
        )

        self.connection.commit()
