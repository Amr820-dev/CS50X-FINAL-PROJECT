# app.py


import os
import sqlite3
from pathlib import Path
from datetime import datetime
from flask import (
    Flask, g, render_template, request, redirect, url_for,
    session, flash, send_from_directory, abort
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# --------------------------
# CONFIG (no .env required)
# --------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = str(DB_DIR / "auto_market.db")

UPLOAD_FOLDER = str(BASE_DIR / "static" / "images" / "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SECRET_KEY = "change_this_to_a_long_secret_in_production"

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# --------------------------
# APP INIT
# --------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# --------------------------
# DB HELPERS
# --------------------------
def get_db_connection():
    db = getattr(g, "_database", None)
    if db is None:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        g._database = db
    return db

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    conn.commit()
    lastrowid = cur.lastrowid
    cur.close()
    return lastrowid

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# --------------------------
# INIT DB
# --------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        brand TEXT,
        year INTEGER,
        price REAL,
        km INTEGER DEFAULT 0,
        image TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        brand TEXT,
        model TEXT,
        year INTEGER,
        mileage INTEGER,
        price REAL,
        image TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        car_id INTEGER,
        payment_type TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(car_id) REFERENCES cars(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        phone TEXT,
        service_type TEXT,
        car_model TEXT,
        preferred_date TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

# --------------------------
# HELPERS (uploads, allowed)
# --------------------------
def allowed_image(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS

def save_uploaded_image(file_storage):
    if not file_storage:
        return None
    filename = secure_filename(file_storage.filename)
    if filename == "":
        return None
    if not allowed_image(filename):
        return None
    dest = Path(app.config["UPLOAD_FOLDER"]) / filename
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        filename = f"{stem}_{int(datetime.utcnow().timestamp())}{suffix}"
        dest = Path(app.config["UPLOAD_FOLDER"]) / filename
    file_storage.save(dest)
    return filename

# --------------------------
# CONTEXT PROCESSOR
# --------------------------
@app.context_processor
def inject_globals():
    return {"current_year": datetime.utcnow().year, "session": session}

# --------------------------
# BASIC ROUTES
# --------------------------
@app.route("/ping")
def ping():
    return "pong"

@app.route("/")
@app.route("/index")
def index():
    try:
        cars = query_db("SELECT id, title, brand, year, price, image FROM cars ORDER BY created_at DESC LIMIT 6;")
    except Exception:
        cars = []
    return render_template("index.html", new_cars=cars)

# --------------------------
# AUTH: register / login / logout
# --------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # basic validation
        if not username or not email or not password:
            flash("please fill the required fields", "danger")
            return render_template("registration.html")

        if password != confirm:
            flash("password do not match", "danger")
            return render_template("registration.html")

        # check existing email
        existing = query_db("SELECT id FROM users WHERE email = ?;", (email,), one=True)
        if existing:
            flash("this e-mail already exists,try another one", "warning")
            return render_template("registration.html")

        password_hash = generate_password_hash(password)
        user_id = execute_db(
            "INSERT INTO users (username, email, password_hash) VALUES (?,?,?);",
            (username, email, password_hash)
        )
        session["user_id"] = user_id
        session["username"] = username
        flash("تم التسجيل بنجاح. مرحباً بك!", "success")
        return redirect(url_for("index"))
    return render_template("registration.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = query_db("SELECT id, username, password_hash FROM users WHERE email = ?;", (email,), one=True)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("wrong e-mail or password", "danger")
            return render_template("login.html")
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("you have successfully logged in", "success")
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("logged out", "info")
    return redirect(url_for("index"))

# --------------------------
# New cars & details & buying flow
# --------------------------
@app.route("/new_cars")
def new_cars():
    cars = query_db("SELECT id, title, brand, year, price, image FROM cars ORDER BY created_at DESC;")
    return render_template("new_cars.html", cars=cars)

@app.route("/new_cars/<int:car_id>")
def new_car_details(car_id):
    car = query_db("SELECT * FROM cars WHERE id = ?;", (car_id,), one=True)
    if not car:
        abort(404)
    car = dict(car)  # مهم لتحويل Row → dict
    return render_template("new_car_details.html", car=car)



@app.route("/new_cars/<int:car_id>/buy")
def application_buying_new_car(car_id):
    car = query_db("SELECT * FROM cars WHERE id = ?;", (car_id,), one=True)
    if not car:
        abort(404)
    try:
        car = dict(car)
    except Exception:
        pass
    return render_template("application_buying_new_car.html", car=car)


@app.route("/new_cars/<int:car_id>/buy/cash", methods=["GET", "POST"])
def buy_cash(car_id):
    car = query_db("SELECT * FROM cars WHERE id = ?;", (car_id,), one=True)
    if not car:
        abort(404)
    try:
        car = dict(car)
    except Exception:
        pass

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        details = f"Cash purchase by {name}, email:{email}, phone:{phone}, address:{address}"
        user_id = session.get("user_id")
        execute_db("INSERT INTO orders (user_id, car_id, payment_type, details) VALUES (?,?,?,?);",
                   (user_id, car_id, "cash", details))
        flash("تم تأكيد طلب الشراء كاش. شكراً لك!", "success")
        return redirect(url_for("thank_you_new_car"))
    return render_template("buy_cash.html", car=car)

@app.route("/new_cars/<int:car_id>/buy/installment", methods=["GET", "POST"])
def buy_installment(car_id):
    car = query_db("SELECT * FROM cars WHERE id = ?;", (car_id,), one=True)
    if not car:
        abort(404)
    try:
        car = dict(car)
    except Exception:
        pass

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        down = request.form.get("down_payment", "0").strip()
        period = request.form.get("installment_period", "").strip()
        details = f"Installment purchase by {name}, down:{down}, period:{period}, email:{email}, phone:{phone}"
        user_id = session.get("user_id")
        execute_db("INSERT INTO orders (user_id, car_id, payment_type, details) VALUES (?,?,?,?);",
                   (user_id, car_id, "installment", details))
        flash("تم إرسال طلب التقسيط. سنقوم بالتواصل معك.", "success")
        return redirect(url_for("thank_you_new_car"))
    return render_template("buy_installment.html", car=car)

@app.route("/thank_you_new_car")
def thank_you_new_car():
    return render_template("thank_you_new_car.html")

# --------------------------
# Used cars prices
# --------------------------
@app.route("/used_cars_prices", methods=["GET", "POST"])
def used_cars_prices():
    results = []
    if request.method == "POST":
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        year = request.form.get("year", "").strip()
        # for now just mock a response or simple DB query if listings exist
        q = "SELECT brand, model, year, price FROM listings WHERE 1=1"
        params = []
        if brand:
            q += " AND brand LIKE ?"
            params.append(f"%{brand}%")
        if model:
            q += " AND model LIKE ?"
            params.append(f"%{model}%")
        if year:
            q += " AND year = ?"
            params.append(year)
        results = query_db(q, params)
    return render_template("used_cars_prices.html", results=results)

# --------------------------
# Sell your car (listing)
# --------------------------
@app.route("/sell_your_car", methods=["GET", "POST"])
def sell_your_car():
    if request.method == "POST":
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        year = request.form.get("year", "").strip()
        mileage = request.form.get("mileage", "").strip()
        price = request.form.get("price", "").strip()
        image_file = request.files.get("image")
        filename = save_uploaded_image(image_file) if image_file else None

        user_id = session.get("user_id")
        listing_id = execute_db(
            "INSERT INTO listings (user_id, brand, model, year, mileage, price, image) VALUES (?,?,?,?,?,?,?);",
            (user_id, brand, model or None, year or None, mileage or None, price or None, filename)
        )
        flash("your post have been published", "success")
        return redirect(url_for("your_car_selling_post", listing_id=listing_id))
    return render_template("sell_your_car.html")

@app.route("/your_car_selling_post")
def your_car_selling_post():
    listing_id = request.args.get("listing_id") or request.args.get("id")
    if not listing_id:
        # show generic page or error
        return render_template("your_car_selling_post.html", brand=None, model=None, year=None, mileage=None, price=None, image_url=None)
    listing = query_db("SELECT * FROM listings WHERE id = ?;", (listing_id,), one=True)
    image_url = None
    if listing and listing["image"]:
        image_url = url_for("static", filename=f"images/uploads/{listing['image']}")
    return render_template("your_car_selling_post.html",
                           brand=listing["brand"] if listing else None,
                           model=listing["model"] if listing else None,
                           year=listing["year"] if listing else None,
                           mileage=listing["mileage"] if listing else None,
                           price=listing["price"] if listing else None,
                           image_url=image_url)

# --------------------------
# Service maintenance
# --------------------------
@app.route("/service_maintenance", methods=["GET", "POST"])
def service_maintenance():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        car_model = request.form.get("car_model", "").strip()
        current_km = request.form.get("current_km", "").strip()
        service_type = request.form.get("service_type", "").strip()
        preferred_date = request.form.get("preferred_date", "").strip()
        notes = request.form.get("notes", "").strip()

        # basic save
        execute_db("""
            INSERT INTO bookings (name, phone, service_type, car_model, preferred_date, notes)
            VALUES (?,?,?,?,?,?);
        """, (name, phone, service_type, car_model, preferred_date, notes))
        flash("your service booking request has been received, we will contact you shortly", "success")
        # redirect to thank you with summary params (GET)
        return redirect(url_for("thank_you_service", name=name, car_model=car_model, service_type=service_type, preferred_date=preferred_date, phone=phone))
    return render_template("service_maintenance.html")

@app.route("/thank_you_service")
def thank_you_service():
    # read params from query string if provided
    name = request.args.get("name")
    car_model = request.args.get("car_model")
    service_type = request.args.get("service_type")
    preferred_date = request.args.get("preferred_date")
    phone = request.args.get("phone")
    return render_template("thank_you_service.html",
                           name=name, car_model=car_model,
                           service_type=service_type, preferred_date=preferred_date, phone=phone)

# --------------------------
# Branches & dealers
# --------------------------
@app.route("/branches_of_dealerships_and_distributers", methods=["GET"])
def branches_of_dealerships_and_distributers():
    # For now static/example list (could be loaded from DB)
    branches = [
        {"name": "cairo branch-authorized distributer", "brand": "toyota", "city": "cairo", "address": "15 شارع النادي، مدينة نصر", "phone": "0223456789", "schedule": "السبت-الخميس 9:00-18:00"},
        {"name": "Alexandria branch-authorized dealership", "brand": "hyundai", "city": "alexandria", "address": "شارع البحر، الإسكندرية", "phone": "034567890", "schedule": "السبت-الخميس 9:00-17:00"}
    ]
    return render_template("branches_of_dealerships_and_distributers.html", branches=branches)

# --------------------------
# Driving lessons & licenses
# --------------------------
@app.route("/driving_lessons_and_licenses", methods=["GET", "POST"])
def driving_lessons_and_licenses():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        service = request.form.get("service", "").strip()
        preferred_date = request.form.get("preferred_date", "").strip()
        location = request.form.get("location", "").strip()
        notes = request.form.get("notes", "").strip()

        execute_db("""
            INSERT INTO bookings (name, phone, service_type, preferred_date, notes, car_model)
            VALUES (?,?,?,?,?,?);
        """, (name, phone, service, preferred_date, notes, location))
        flash("your request has been submitted, we will contact you to confirm details", "success")
        return redirect(url_for("thank_you_driving", name=name, service_label=service, preferred_date=preferred_date, location=location, phone=phone))
    return render_template("driving_lessons_and_licenses.html")

@app.route("/thank_you_driving")
def thank_you_driving():
    name = request.args.get("name")
    service_label = request.args.get("service_label") or request.args.get("service")
    preferred_date = request.args.get("preferred_date")
    location = request.args.get("location")
    phone = request.args.get("phone")
    return render_template("thank_you_driving.html", name=name, service_label=service_label, preferred_date=preferred_date, location=location, phone=phone)

# --------------------------
# Static uploaded files route (optional)
# --------------------------
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# --------------------------
# ERROR HANDLERS
# --------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("layout.html", content="<h2>404 - unavailable page</h2>"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("layout.html", content="<h2>500 - خطأ في السيرفر</h2>"), 500

# --------------------------
# RUN
# --------------------------
if __name__ == "__main__":
    init_db()  # ensure DB exists with tables
    app.run(host="0.0.0.0", port=5000, debug=True)
