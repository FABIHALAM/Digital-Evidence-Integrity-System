from flask import Flask, render_template, request, redirect, send_file, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
import pyotp
# import redis  # Commented out for Vercel deployment
import os, datetime, json
import sys
sys.path.insert(0, os.path.dirname(__file__))
import engine
# from celery import Celery  # Commented out for Vercel deployment

app = Flask(__name__, template_folder='api/templates', static_folder='api/static')
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/deis.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
db = SQLAlchemy(app)

# Security enhancements
# talisman = Talisman(app, content_security_policy=None)  # Enable HTTPS and security headers  # Commented out for Vercel compatibility
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)
mail = Mail(app)

# Redis for caching - commented out for Vercel deployment
# redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Celery for async tasks - commented out for executable compatibility
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
# celery = Celery(app.import_name)
# celery.conf.update(app.config)

# @celery.task
# def process_file_async(file_path, file_name):
#     # Async file processing
#     block = engine.build_block(file_path, None)
#     metadata = engine.extract_metadata(file_path)
#     deep_analysis = engine.analyze_file_content(file_path)
#     anomaly_detected = engine.detect_anomaly(file_path)
#     virustotal_result = engine.check_virustotal(block["hash"])
#     qr = engine.generate_qr(block)

#     # Use file_name for logging or future use
#     print(f"Processing file: {file_name}")

#     return {
#         "block": block,
#         "metadata": metadata,
#         "deep_analysis": deep_analysis,
#         "anomaly_detected": anomaly_detected,
#         "virustotal": virustotal_result,
#         "qr": qr
#     }

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    join_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    location = db.Column(db.String(200), nullable=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), nullable=True)

class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(200), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    prev_hash = db.Column(db.String(64), nullable=True)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(20), unique=True, nullable=False)
    file = db.Column(db.String(200), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    file_metadata = db.Column(db.Text, nullable=False)  # JSON string
    qr = db.Column(db.String(200), nullable=False)

# Initialize database function
def init_db():
    try:
        with app.app_context():
            db.create_all()
            # Add default users if not exist
            if not User.query.filter_by(username='FabihAlam').first():
                db.session.add(User(username='FabihAlam', password=generate_password_hash('Fabih123.'), role='admin', location='Local'))
            if not User.query.filter_by(username='Anyoneiam').first():
                db.session.add(User(username='Anyoneiam', password=generate_password_hash('whoisu.'), role='investigator', location='Local'))
            if not User.query.filter_by(username='viewer').first():
                db.session.add(User(username='viewer', password=generate_password_hash('Viewer123!'), role='viewer', location='Local'))
            db.session.commit()
    except Exception as e:
        print(f"Database initialization error: {e}")
        # Continue without failing

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    result = None
    if request.method == "POST":
        f = request.files["file"]
        path = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(path)

        # Get previous hash from database
        last_block = Block.query.order_by(Block.id.desc()).first()
        prev_hash = last_block.hash if last_block else None
        block = engine.build_block(path, prev_hash)

        # Get all blocks for integrity check
        all_blocks = Block.query.all()
        chain_data = [{"hash": b.hash, "file": b.file} for b in all_blocks]
        status = engine.verify_integrity(chain_data, path)

        # Generate case ID
        case_count = Case.query.count()
        case_id = f"CASE-{case_count+1:03d}"

        metadata = engine.extract_metadata(path)
        deep_analysis = engine.analyze_file_content(path)
        anomaly_detected = engine.detect_anomaly(path)
        virustotal_result = engine.check_virustotal(block["hash"])

        # Enhanced metadata
        enhanced_metadata = {
            **metadata,
            "deep_analysis": deep_analysis,
            "anomaly_detected": anomaly_detected,
            "virustotal": virustotal_result
        }

        qr = engine.generate_qr(block)

        # Save to database
        new_block = Block(file=f.filename, hash=block["hash"], time=block["time"], prev_hash=prev_hash)
        new_case = Case(case_id=case_id, file=f.filename, hash=block["hash"], time=block["time"],
                       status=status, file_metadata=json.dumps(metadata), qr=qr)
        db.session.add(new_block)
        db.session.add(new_case)
        db.session.commit()

        result = {
            "case_id": case_id,
            "file": f.filename,
            "hash": block["hash"],
            "time": block["time"].isoformat(),
            "status": status,
            "metadata": metadata,
            "qr": qr
        }

    # Get data for template
    all_blocks = Block.query.all()
    all_cases = Case.query.all()

    # Parse metadata for each case
    cases_with_parsed_metadata = []
    for case in all_cases:
        case_dict = {
            "case_id": case.case_id,
            "file": case.file,
            "hash": case.hash,
            "time": case.time,
            "status": case.status,
            "metadata": json.loads(case.file_metadata),
            "qr": case.qr
        }
        cases_with_parsed_metadata.append(case_dict)

    return render_template(
        "dashboard.html",
        result=result,
        chain=all_blocks,
        cases=cases_with_parsed_metadata,
        role=session.get("role")
    )

@app.route("/verify", methods=["GET","POST"])
def verify():
    result=None
    if request.method=="POST":
        f=request.files["file"]
        path=os.path.join(UPLOAD_FOLDER,f.filename)
        f.save(path)

        # Get all blocks for integrity check
        all_blocks = Block.query.all()
        chain_data = [{"hash": b.hash, "file": b.file} for b in all_blocks]
        status = engine.verify_integrity(chain_data, path)

        result={
            "file":f.filename,
            "hash":engine.hash_file(path),
            "status":status,
            "time":datetime.datetime.now().isoformat()
        }
    return render_template("verify.html", result=result)

@app.route("/public_verify", methods=["GET","POST"])
def public_verify():
    result=None
    if request.method=="POST":
        f=request.files["file"]
        path=os.path.join(UPLOAD_FOLDER,f.filename)
        f.save(path)

        # Get all blocks for integrity check
        all_blocks = Block.query.all()
        chain_data = [{"hash": b.hash, "file": b.file} for b in all_blocks]
        status = engine.verify_integrity(chain_data, path)

        result={
            "file":f.filename,
            "hash":engine.hash_file(path),
            "status":status,
            "time":datetime.datetime.now().isoformat()
        }
    return render_template("public_verify.html", result=result)

@app.route("/case/<cid>")
def case_view(cid):
    case = Case.query.filter_by(case_id=cid).first()
    if not case:
        return "Case not found", 404
    # Convert to dict for template compatibility
    case_dict = {
        "case_id": case.case_id,
        "file": case.file,
        "hash": case.hash,
        "time": case.time,
        "status": case.status,
        "metadata": json.loads(case.file_metadata),
        "qr": case.qr
    }
    return render_template("case.html", case=case_dict)

@app.route("/", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    error = None
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        user = User.query.filter_by(username=u).first()
        if user and check_password_hash(user.password, p):
            if user.two_factor_enabled:
                session["temp_user"] = u
                return redirect("/2fa")
            else:
                session["user"] = u
                session["role"] = user.role
                return redirect("/dashboard")
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@app.route("/2fa", methods=["GET", "POST"])
def two_factor():
    if "temp_user" not in session:
        return redirect("/")

    user = User.query.filter_by(username=session["temp_user"]).first()
    if not user or not user.two_factor_enabled:
        return redirect("/")

    if request.method == "POST":
        token = request.form["token"]
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(token):
            session["user"] = session["temp_user"]
            session["role"] = user.role
            session.pop("temp_user", None)
            return redirect("/dashboard")
        else:
            flash("Invalid 2FA token")

    return render_template("2fa.html")

@app.route("/setup_2fa", methods=["GET", "POST"])
def setup_2fa():
    if "user" not in session:
        return redirect("/")

    user = User.query.filter_by(username=session["user"]).first()
    if request.method == "POST":
        token = request.form["token"]
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(token):
            user.two_factor_enabled = True
            db.session.commit()
            flash("2FA enabled successfully")
            return redirect("/dashboard")
        else:
            flash("Invalid token")

    if not user.two_factor_secret:
        user.two_factor_secret = pyotp.random_base32()
        db.session.commit()

    totp = pyotp.TOTP(user.two_factor_secret)
    qr_uri = totp.provisioning_uri(name=user.username, issuer_name="DEIS")
    return render_template("setup_2fa.html", qr_uri=qr_uri)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate reset token (simplified)
            reset_token = pyotp.random_base32()
            # In production, store token securely
            msg = Message("Password Reset", sender="noreply@deis.com", recipients=[email])
            msg.body = f"Reset token: {reset_token}"
            mail.send(msg)
            flash("Reset email sent")
        else:
            flash("Email not found")

    return render_template("reset_password.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        u = request.form["username"].lower()
        p = request.form["password"]
        cp = request.form["confirm_password"]
        r = request.form.get("role", "viewer")  # Default to viewer if not provided

        if User.query.filter_by(username=u).first():
            error = "Username already exists"
        elif p != cp:
            error = "Passwords do not match"
        elif len(p) < 4:
            error = "Password must be at least 4 characters"
        else:
            ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
            location = engine.get_location_from_ip(ip)
            new_user = User(username=u, password=generate_password_hash(p), role=r, location=location)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/")

    return render_template("register.html", error=error)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("role") != "admin":
        return redirect("/dashboard")

    error = None
    success = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_user":
            u = request.form["username"].lower()
            p = request.form["password"]
            r = request.form["role"]

            if User.query.filter_by(username=u).first():
                error = "Username already exists"
            elif len(p) < 4:
                error = "Password must be at least 4 characters"
            else:
                ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
                location = engine.get_location_from_ip(ip)
                new_user = User(username=u, password=generate_password_hash(p), role=r, location=location)
                db.session.add(new_user)
                db.session.commit()
                success = f"User '{u}' created successfully with role '{r}'"

        elif action == "remove_user":
            user_id = request.form.get("user_id")
            user = User.query.get(user_id)
            if user and user.username != 'admin':  # Prevent removing admin
                db.session.delete(user)
                db.session.commit()
                success = f"User '{user.username}' removed successfully"
            else:
                error = "Cannot remove this user"

    all_blocks = Block.query.all()
    all_cases = Case.query.all()
    all_users = User.query.all()
    return render_template("admin.html", chain=all_blocks, cases=all_cases, users=all_users, error=error, success=success)

@app.route("/export/<case_id>")
def export_case(case_id):
    case = Case.query.filter_by(case_id=case_id).first()
    if not case:
        return "Case not found", 404

    # Convert to dict for PDF generation
    case_dict = {
        "case_id": case.case_id,
        "file": case.file,
        "hash": case.hash,
        "time": case.time,
        "status": case.status,
        "metadata": json.loads(case.file_metadata),
        "qr": case.qr
    }

    os.makedirs("reports", exist_ok=True)
    output = f"reports/{case_id}.pdf"

    engine.generate_forensic_pdf(case_dict, output)
    return send_file(output, as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Vercel deployment handler
def handler(event, context):
    init_db()
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)

if __name__=="__main__":
    app.run(debug=True)
