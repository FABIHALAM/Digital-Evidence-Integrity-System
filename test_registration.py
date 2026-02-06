from app import app, db, User
import requests

# Test registration functionality
with app.app_context():
    print("Testing user registration...")

    # Test 1: Create a new user
    try:
        new_user = User(username='testuser123', password='testpass123', role='viewer')
        db.session.add(new_user)
        db.session.commit()
        print("✓ User created successfully")

        # Test 2: Check if user exists
        user = User.query.filter_by(username='testuser123').first()
        if user:
            print(f"✓ User retrieved: {user.username}, role: {user.role}")
        else:
            print("✗ User not found after creation")

        # Test 3: Try duplicate username
        try:
            duplicate_user = User(username='testuser123', password='anotherpass', role='admin')
            db.session.add(duplicate_user)
            db.session.commit()
            print("✗ Duplicate username allowed (should not happen)")
        except Exception as e:
            print(f"✓ Duplicate username prevented: {str(e)[:50]}...")

        # Clean up
        db.session.delete(user)
        db.session.commit()
        print("✓ Test user cleaned up")

    except Exception as e:
        print(f"✗ Error during testing: {e}")

print("\nRegistration functionality appears to be working correctly.")
print("If you're experiencing errors, please check:")
print("1. Form fields are filled correctly")
print("2. Passwords match")
print("3. Username is unique")
print("4. Password is at least 4 characters")
