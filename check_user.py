from app import app, db, User

with app.app_context():
    user = User.query.filter_by(username='FabihAlam').first()
    if user:
        print(f"Username: {user.username}")
        print(f"Role: {user.role}")
        print(f"2FA Enabled: {user.two_factor_enabled}")
        print(f"2FA Secret: {user.two_factor_secret}")
    else:
        print("User not found")
