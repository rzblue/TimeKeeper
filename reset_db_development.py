import random
from datetime import datetime, timedelta

import loggers
from app import db
from models import User

loggers.setup_logger()

db.reset_all_dangerous()
db.initialize_tables()

users = [
    User("John Smith", "12345678"),
    User("Tim Cook", "thisismyid"),
    User("Bill Gates", "qwerty"),
    User("Bobby Tables", "987654321"),
]

created_users = []
for user in users:
    created_users.append(db.create_user(user))

now = datetime.now()
for user in created_users:
    for i in range(4):
        session = db.start_time_session(
            user, now - timedelta(seconds=random.randint(7200, 86400), days=2 * i)
        )
        db.end_time_session(
            session, session.start_time + timedelta(seconds=random.randint(1800, 7200))
        )

db.connection.close()
