from app import app, db, User
with app.app_context():
    try:
        users = User.query.all()
        print(f"Database connection successful. Users in DB: {len(users)}")
        for user in users:
            print(f"- {user.username}: {user.role}")
    except Exception as e:
        print(f"Database error: {e}")
