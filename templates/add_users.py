from app_web import db, User, app
from werkzeug.security import generate_password_hash

users_to_add = [
    {"username": "admin", "password": "admin", "role": "admin", "store": None},
    {"username": "main", "password": "main", "role": "store", "store": "Main"},
    {"username": "test", "password": "test", "role": "store", "store": "Test"},
    ]    # Add more users as needed

with app.app_context():
    for u in users_to_add:
        # Only add if username doesn't exist yet
        if not User.query.filter_by(username=u["username"]).first():
            user = User(
                username=u["username"],
                password_hash=generate_password_hash(u["password"], method="pbkdf2:sha256"),
                role=u["role"],
                store=u["store"],
            )
            db.session.add(user)
    db.session.commit()
print("Users added successfully!")