from app import app, db, User

with app.app_context():
    users = User.query.all()
    for user in users:
        if user.username != user.username.lower():
            user.username = user.username.lower()
            db.session.commit()
            print(f"Updated {user.username}")
    print("Done")
