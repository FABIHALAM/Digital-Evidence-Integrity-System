from app import app, db, User
from werkzeug.security import check_password_hash

with app.app_context():
    user = User.query.filter_by(username='FabihAlam').first()
    if user:
        print(f"User found: {user.username}")
        print(f"Stored hash: {user.password}")
        test_password = 'Fabih123.'
        if check_password_hash(user.password, test_password):
            print("Password matches!")
        else:
            print("Password does not match!")
    else:
        print("User not found")
