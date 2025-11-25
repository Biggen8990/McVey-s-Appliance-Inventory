from app_web import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        username="admin",
        password_hash=generate_password_hash("main", method="pbkdf2:sha256"),
        role="admin",
        store=None
    )
    db.session.add(admin)
    db.session.commit()
print("Admin user added!")