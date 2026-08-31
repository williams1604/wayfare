from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import timedelta
import csv
import os

app = Flask(__name__)
app.secret_key = "wayfare_secret_key"
app.permanent_session_lifetime = timedelta(days=30)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users table with role and password hash
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT DEFAULT 'user'
    )""")

    # Bookings table
    cur.execute("""CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        travelers TEXT,
        special_requests TEXT,
        destination TEXT,
        date TEXT,
        end_date TEXT,
        status TEXT DEFAULT 'Confirmed',
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    # Migrate existing DB: add new columns if missing
    existing_cols = [r[1] for r in cur.execute("PRAGMA table_info(bookings)").fetchall()]
    for col, col_type in [("first_name","TEXT"),("last_name","TEXT"),("phone","TEXT"),("travelers","TEXT"),("special_requests","TEXT"),("end_date","TEXT"),("payment_method","TEXT"),("transaction_id","TEXT")]:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE bookings ADD COLUMN {col} {col_type}")

    # Destinations table
    cur.execute("""CREATE TABLE IF NOT EXISTS destinations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        image_url TEXT,
        tour_count INTEGER
    )""")

    # Packages table
    cur.execute("""CREATE TABLE IF NOT EXISTS packages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        duration TEXT,
        rating Real,
        description TEXT,
        price INTEGER,
        image_url TEXT,
        is_bestseller BOOLEAN DEFAULT 0,
        is_premium BOOLEAN DEFAULT 0
    )""")

    # Enquiries table
    cur.execute("""CREATE TABLE IF NOT EXISTS enquiries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        email TEXT,
        subject TEXT,
        message TEXT,
        response TEXT,
        status TEXT DEFAULT 'Pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    # Reviews table with approval status
    cur.execute("""CREATE TABLE IF NOT EXISTS reviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        package_id INTEGER,
        rating INTEGER,
        comment TEXT,
        is_approved INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(package_id) REFERENCES packages(id)
    )""")

    # Migrate reviews table: add is_approved column if missing
    existing_review_cols = [r[1] for r in cur.execute("PRAGMA table_info(reviews)").fetchall()]
    if "is_approved" not in existing_review_cols:
        cur.execute("ALTER TABLE reviews ADD COLUMN is_approved INTEGER DEFAULT 0")

    conn.commit()
    conn.close()

# ---------------- ROUTES ----------------

@app.context_processor
def inject_user():
    def get_package_rating(package_id):
        conn = get_db()
        cur = conn.cursor()
        res = cur.execute("SELECT AVG(rating), COUNT(id) FROM reviews WHERE package_id=? AND is_approved=1", (package_id,)).fetchone()
        conn.close()
        avg = round(res[0], 1) if res[0] else 0
        count = res[1]
        return {"avg": avg, "count": count}
    
    def get_pending_reviews_count():
        if session.get("role") != "admin":
            return 0
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) FROM reviews WHERE is_approved=0").fetchone()[0]
        conn.close()
        return count
    
    return dict(user_role=session.get("role"), user_name=session.get("name"), get_package_rating=get_package_rating, get_pending_reviews_count=get_pending_reviews_count)

@app.route("/")
def home():
    conn = get_db()
    cur = conn.cursor()
    destinations = cur.execute("SELECT * FROM destinations ORDER BY tour_count DESC LIMIT 8").fetchall()
    featured_packages = cur.execute("SELECT * FROM packages WHERE is_bestseller=1 LIMIT 12").fetchall()
    all_packages = cur.execute("SELECT * FROM packages ORDER BY name").fetchall()
    conn.close()
    return render_template("index.html", destinations=destinations, packages=featured_packages, all_packages=all_packages)

@app.route("/destinations")
def destinations():
    conn = get_db()
    cur = conn.cursor()
    destinations = cur.execute("SELECT * FROM destinations").fetchall()
    # Fetch all packages to filter client-side or simple matching
    packages = cur.execute("SELECT * FROM packages").fetchall()
    conn.close()
    return render_template("destinations.html", destinations=destinations, packages=packages)

@app.route("/packages")
def packages():
    conn = get_db()
    cur = conn.cursor()
    packages = cur.execute("SELECT * FROM packages").fetchall()
    conn.close()
    return render_template("packages.html", packages=packages)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        if "user_id" not in session:
            flash("Please login to submit an enquiry.", "error")
            return redirect("/#signin")
            
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        whatsapp = request.form.get("whatsapp", "")
        message = request.form["message"]
        
        # Prepend whatsapp number to message string to keep database unchanged for now
        full_message = f"WhatsApp: {whatsapp}\n\n{message}" if whatsapp else message
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO enquiries(user_id, name, email, subject, message) VALUES(?, ?, ?, ?, ?)",
                    (session["user_id"], name, email, subject, full_message))
        conn.commit()
        conn.close()
        
        flash("Enquiry submitted successfully! detailed will be showed in dashboard", "success")
        return redirect("/dashboard")
        
    return render_template("contact.html")

import datetime

def check_expired_bookings(cur):
    today = datetime.date.today().isoformat()
    # Update bookings where the end_date has passed
    cur.execute("UPDATE bookings SET status='Expired' WHERE (status='Confirmed' OR status='Pending') AND end_date < ? AND end_date IS NOT NULL AND end_date != ''", (today,))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    
    conn = get_db()
    cur = conn.cursor()
    
    check_expired_bookings(cur)
    conn.commit()
    
    bookings = cur.execute("""
        SELECT b.*, p.id as package_id, r.rating as user_rating, r.comment as user_comment
        FROM bookings b 
        LEFT JOIN packages p ON b.destination = p.name 
        LEFT JOIN reviews r ON b.user_id = r.user_id AND p.id = r.package_id
        WHERE b.user_id=? 
        ORDER BY b.id DESC
    """, (session["user_id"],)).fetchall()
    enquiries = cur.execute("SELECT * FROM enquiries WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    conn.close()
    
    return render_template("dashboard.html", bookings=bookings, enquiries=enquiries)

@app.route("/add_review", methods=["POST"])
def add_review():
    if "user_id" not in session:
        flash("Please login to post a review.", "error")
        return redirect("/#signin")
    
    package_id = request.form.get("package_id")
    rating = request.form.get("rating")
    comment = request.form.get("comment")
    
    if not rating or not package_id:
        flash("Rating and Package ID are required.", "error")
        return redirect("/dashboard")
        
    conn = get_db()
    cur = conn.cursor()
    
    # Check if user has a confirmed or expired booking for this package
    # First, find the package name to match with booking destination
    package = cur.execute("SELECT name FROM packages WHERE id=?", (package_id,)).fetchone()
    if not package:
        conn.close()
        flash("Invalid package.", "error")
        return redirect("/dashboard")
        
    booking = cur.execute("SELECT id FROM bookings WHERE user_id=? AND destination=? AND (status='Confirmed' OR status='Expired')", 
                          (session["user_id"], package["name"])).fetchone()
    
    if not booking:
        conn.close()
        flash("You can only review packages you have booked and confirmed.", "error")
        return redirect("/dashboard")
        
    # Check if user already reviewed this package
    existing_review = cur.execute("SELECT id FROM reviews WHERE user_id=? AND package_id=?", 
                                (session["user_id"], package_id)).fetchone()
    
    if existing_review:
        cur.execute("UPDATE reviews SET rating=?, comment=? WHERE id=?", (rating, comment, existing_review["id"]))
        flash("Your review has been updated.", "success")
    else:
        cur.execute("INSERT INTO reviews(user_id, package_id, rating, comment) VALUES(?, ?, ?, ?)",
                    (session["user_id"], package_id, rating, comment))
        flash("Thank you for your review!", "success")
        
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# ---------------- AUTH ----------------

@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"].lower().strip()
    password = request.form["password"]
    hashed_password = generate_password_hash(password)

    with open("login_debug.log", "a") as f:
        f.write(f"\n--- Registration Attempt for '{email}' ---\n")
        try:
            conn = get_db()
            cur = conn.cursor()
            
            # Check if email exists (case insensitive)
            existing = cur.execute("SELECT id FROM users WHERE LOWER(email)=?", (email,)).fetchone()
            if existing:
                f.write("Email already exists (Checked via SELECT).\n")
                flash("Email already exists. Please use a different email.", "signup-error")
                return redirect("/#signup")
                
            cur.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                        (name, email, hashed_password))
            conn.commit()
            f.write("User inserted successfully.\n")
            conn.close()
            flash("Registration successful! Please sign in.", "signup-success")
            return redirect("/#signin")
        except sqlite3.IntegrityError as e:
            f.write(f"IntegrityError: {str(e)}\n")
            flash("Email already exists. Please use a different email.", "signup-error")
            return redirect("/#signup")
        except Exception as e:
            f.write(f"Registration Error: {str(e)}\n")
            return f"Error: {str(e)}"

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    remember = request.form.get("remember")

    # Admin check
    if email.lower() == "admin@gmail.com" and password == "admin@wayfare":
        session.clear()
        session["user_id"] = "admin"
        session["name"] = "Administrator"
        session["role"] = "admin"
        if remember:
            session.permanent = True
        else:
            session.permanent = False
        flash("Welcome back, Admin!", "success")
        return redirect("/admin")

    conn = get_db()
    cur = conn.cursor()
    # Case insensitive lookup
    user = cur.execute("SELECT * FROM users WHERE LOWER(email)=?", (email,)).fetchone()
    conn.close()

    with open("login_debug.log", "a") as f:
        f.write(f"\n--- Login Attempt for '{email}' ---\n")
        if user:
            f.write(f"User found in DB: ID={user['id']}, Name='{user['name']}', Email='{user['email']}'\n")
            f.write(f"Stored Hash: {user['password_hash'][:20]}...\n")
            try:
                is_valid = check_password_hash(user["password_hash"], password)
                f.write(f"Password Check Result: {is_valid}\n")
            except Exception as e:
                f.write(f"Password Check Validation Error: {str(e)}\n")
                is_valid = False
            
            if is_valid:
                session.clear()
                session["user_id"] = user["id"]
                session["name"] = user["name"]
                session["role"] = user["role"]
                if remember:
                    session.permanent = True
                else:
                    session.permanent = False
                
                f.write("Login Successful. Redirecting...\n")
                flash(f"Welcome back, {user['name']}!", "success")
                if user["role"] == "admin":
                     return redirect("/admin")
                return redirect("/")
            else:
                 f.write("Password Mismatch.\n")
        else:
            f.write("User NOT found in DB.\n")
            # Debug: check if it exists with exact match or similar
            conn = get_db()
            cur = conn.cursor()
            all_emails = cur.execute("SELECT email FROM users").fetchall()
            conn.close()
            f.write(f"Existing emails in DB: {[r[0] for r in all_emails]}\n")
    
    flash("Invalid email or password. Please try again.", "signin-error")
    return redirect("/#signin")

@app.route("/reset_password", methods=["POST"])
def reset_password():
    email = request.form.get("email", "").strip()
    new_password = request.form.get("new_password", "").strip()

    conn = get_db()
    cur = conn.cursor()
    
    # Check if user exists
    user = cur.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    
    if user:
        if user["email"].lower() == "admin@wayfare.com":
             flash("Cannot reset admin password from here.", "reset-error")
        else:
            cur.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
            conn.commit()
            flash("Password updated successfully! You can now log in.", "signin-success")
            conn.close()
            return redirect("/#signin")
    else:
        # Don't reveal if email exists or not usually, but for simplicity here we can.
        flash("If an account exists with this email, the password has been updated.", "reset-success")
        
    conn.close()
    return redirect("/#reset-password")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/login/<provider>")
def mock_oauth_login(provider):
    # This is a mock implementation since no Client IDs/Secrets were provided.
    # It simulates a successful OAuth flow by logging in a dummy user based on the provider.
    if provider not in ["google", "facebook"]:
        flash("Invalid login provider.", "error")
        return redirect("/#signin")
    
    email = request.args.get("email", f"mockuser@{provider}.com").strip().lower()
    
    # We generate a generic name if a custom email is provided
    if f"mockuser@{provider}.com" in email:
        name = f"{provider.capitalize()} User"
    else:
        name = email.split('@')[0].capitalize()
    
    conn = get_db()
    cur = conn.cursor()
    # Check if this mock user already exists
    user = cur.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    
    if not user:
        # Create the mock user
        # We use a dummy password hash since they authenticate via the mock OAuth
        dummy_hash = generate_password_hash("dummy_oauth_password")
        cur.execute("INSERT INTO users(name, email, password_hash) VALUES(?, ?, ?)",
                    (name, email, dummy_hash))
        conn.commit()
        user = cur.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        
    session.clear()
    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    session.permanent = True
    
    conn.close()
    
    flash(f"Successfully logged in with {provider.capitalize()}!", "success")
    return redirect("/")

@app.route("/login/google/consent")
def google_consent():
    conn = get_db()
    cur = conn.cursor()
    # Fetch recent users that look like Google/Gmail accounts, limit to 3
    recent_users = cur.execute("SELECT name, email FROM users WHERE email LIKE '%@google.com' OR email LIKE '%@gmail.com' ORDER BY id DESC LIMIT 3").fetchall()
    conn.close()
    return render_template("google_consent.html", recent_users=recent_users)

@app.route("/login/facebook/consent")
def facebook_consent():
    conn = get_db()
    cur = conn.cursor()
    # Fetch recent users that look like Facebook accounts, limit to 3
    recent_users = cur.execute("SELECT name, email FROM users WHERE email LIKE '%@facebook.com' ORDER BY id DESC LIMIT 3").fetchall()
    conn.close()
    return render_template("facebook_consent.html", recent_users=recent_users)

# ---------------- ADMIN ----------------

@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db()
    cur = conn.cursor()
    # Get stats
    bookings_count = cur.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    users_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    packages_count = cur.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
    enquiries_count = cur.execute("SELECT COUNT(*) FROM enquiries").fetchone()[0]
    
    # recent bookings
    recent_bookings = cur.execute("""
        SELECT b.id, u.name, b.destination, b.date, b.status 
        FROM bookings b 
        JOIN users u ON b.user_id = u.id 
        ORDER BY b.id DESC LIMIT 5
    """).fetchall()

    # recent enquiries
    recent_enquiries = cur.execute("SELECT * FROM enquiries ORDER BY id DESC LIMIT 5").fetchall()
    
    # pending reviews count
    pending_reviews_count = cur.execute("SELECT COUNT(*) FROM reviews WHERE is_approved=0").fetchone()[0]
    
    conn.close()
    return render_template("admin/dashboard.html", 
                           bookings_count=bookings_count, 
                           users_count=users_count, 
                           packages_count=packages_count,
                           enquiries_count=enquiries_count,
                           pending_reviews_count=pending_reviews_count,
                           recent_bookings=recent_bookings,
                           recent_enquiries=recent_enquiries)

@app.route("/admin/reviews")
@admin_required
def admin_reviews():
    conn = get_db()
    cur = conn.cursor()
    reviews = cur.execute("""
        SELECT r.*, u.name as user_name, u.email as user_email, p.name as package_name 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        JOIN packages p ON r.package_id = p.id 
        ORDER BY r.is_approved ASC, r.created_at DESC
    """).fetchall()
    conn.close()
    return render_template("admin/reviews.html", reviews=reviews)

@app.route("/admin/reviews/toggle/<int:id>", methods=["POST"])
@admin_required
def toggle_review_approval(id):
    conn = get_db()
    cur = conn.cursor()
    review = cur.execute("SELECT is_approved FROM reviews WHERE id=?", (id,)).fetchone()
    if review:
        new_status = 1 if review["is_approved"] == 0 else 0
        cur.execute("UPDATE reviews SET is_approved=? WHERE id=?", (new_status, id))
        conn.commit()
        status_text = "approved" if new_status == 1 else "hidden"
        flash(f"Review has been {status_text}.", "success")
    conn.close()
    return redirect(url_for("admin_reviews"))

@app.route("/admin/reviews/delete/<int:id>", methods=["POST"])
@admin_required
def delete_review(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM reviews WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Review deleted successfully.", "success")
    return redirect(url_for("admin_reviews"))

@app.route("/admin/enquiry/respond/<int:id>", methods=["POST"])
@admin_required
def respond_enquiry(id):
    response = request.form["response"]
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE enquiries SET response=?, status='Responded' WHERE id=?", (response, id))
    conn.commit()
    conn.close()
    flash("Response sent successfully!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/packages/add", methods=["GET", "POST"])
@admin_required
def add_package():
    if request.method == "POST":
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""INSERT INTO packages(name, duration, rating, description, price, image_url, is_bestseller, is_premium)
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                    (request.form["name"], request.form["duration"], request.form["rating"],
                     request.form["description"], request.form["price"], request.form["image_url"],
                     1 if "is_bestseller" in request.form else 0,
                     1 if "is_premium" in request.form else 0))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/add_package.html")

@app.route("/admin/packages/delete/<int:id>")
@admin_required
def delete_package(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM packages WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/bookings/delete/<int:booking_id>", methods=["POST"])
@admin_required
def delete_booking(booking_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
    conn.commit()
    conn.close()
    flash(f"Booking #{booking_id} deleted successfully.", "success")
    return redirect(url_for("admin_bookings"))

@app.route("/admin/enquiry/delete/<int:enquiry_id>", methods=["POST"])
@admin_required
def delete_enquiry(enquiry_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM enquiries WHERE id=?", (enquiry_id,))
    conn.commit()
    conn.close()
    flash("Enquiry deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    conn = get_db()
    cur = conn.cursor()
    
    check_expired_bookings(cur)
    conn.commit()
    
    status_filter = request.args.get("status", "")
    search = request.args.get("search", "").strip()

    query = """
        SELECT b.id, u.name, u.email,
               b.first_name, b.last_name, b.phone, b.travelers, b.special_requests,
               b.destination, b.date, b.end_date, b.status, b.payment_method, b.transaction_id
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        WHERE 1=1
    """
    params = []
    if status_filter:
        query += " AND b.status = ?"
        params.append(status_filter)
    if search:
        query += " AND (u.name LIKE ? OR b.destination LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY b.id DESC"

    bookings = cur.execute(query, params).fetchall()

    # Stats
    total      = cur.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    confirmed  = cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'").fetchone()[0]
    pending    = cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'").fetchone()[0]
    cancelled  = cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'").fetchone()[0]
    conn.close()
    return render_template("admin/bookings.html", bookings=bookings,
                           total=total, confirmed=confirmed,
                           pending=pending, cancelled=cancelled,
                           status_filter=status_filter, search=search)

@app.route("/admin/bookings/update_status/<int:booking_id>", methods=["POST"])
@admin_required
def update_booking_status(booking_id):
    new_status = request.form.get("status")
    allowed = ["Confirmed", "Validation Pending", "Pending", "Cancelled"]
    if new_status not in allowed:
        flash("Invalid status.", "error")
        return redirect(url_for("admin_bookings"))
    conn = get_db()
    cur = conn.cursor()
    # If customer already cancelled, do not allow admin to override
    current = cur.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
    if not current:
        flash(f"Booking #{booking_id} not found.", "error")
        conn.close()
        return redirect(url_for("admin_bookings"))
    if current["status"] == "Cancelled":
        flash(f"Booking #{booking_id} was cancelled by the customer and cannot be modified.", "error")
        conn.close()
        return redirect(url_for("admin_bookings"))
    
    cur.execute("UPDATE bookings SET status=? WHERE id=?", (new_status, booking_id))
    conn.commit()
    
    if new_status == "Confirmed" and current["status"] != "Confirmed":
        package = cur.execute("SELECT price FROM packages WHERE name=?", (current["destination"],)).fetchone()
        price = package["price"] if package else 5000000
        try:
            start_date = datetime.datetime.strptime(current["date"], "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(current["end_date"], "%Y-%m-%d").date()
            days_diff = (end_date - start_date).days
            num_days = days_diff + 1 if days_diff >= 0 else 1
        except (ValueError, TypeError):
            num_days = 1
        try:
            num_travelers = int(''.join(c for c in str(current["travelers"]) if c.isdigit()) or 1)
        except:
            num_travelers = 1
        amount = price * num_travelers * num_days
        
        user = cur.execute("SELECT name, email FROM users WHERE id=?", (current["user_id"],)).fetchone()
        csv_path = "payments.csv"
        file_exists = os.path.exists(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Booking ID", "Customer Name", "Customer Email", "Payment Method", "Transaction ID", "Amount Collected", "Date"])
            writer.writerow([current["id"], user["name"], user["email"], current["payment_method"], current["transaction_id"], amount, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            
    conn.close()
    flash(f"Booking #{booking_id} status updated to {new_status}.", "success")
    return redirect(url_for("admin_bookings"))

# ---------------- BOOKING ----------------

@app.route("/book", methods=["POST"])
def book():
    if "user_id" not in session:
        flash("Please login to book your ticket.", "signin-error")
        return redirect("/#signin")

    first_name       = request.form.get("first_name", "").strip()
    last_name        = request.form.get("last_name", "").strip()
    phone            = request.form.get("phone", "").strip()
    travelers        = request.form.get("travelers", "1")
    special_requests = request.form.get("special_requests", "").strip()
    destination      = request.form.get("destination", "")
    date             = request.form.get("date", "")
    end_date         = request.form.get("end_date", "")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO bookings(user_id, first_name, last_name, phone, travelers, special_requests, destination, date, end_date, status)
           VALUES(?,?,?,?,?,?,?,?,?, 'Pending')""",
        (session["user_id"], first_name, last_name, phone, travelers, special_requests, destination, date, end_date)
    )
    booking_id = cur.lastrowid
    conn.commit()
    conn.close()

    flash("Redirecting to payment portal...", "info")
    return redirect(url_for("payment", booking_id=booking_id))

@app.route("/payment/<int:booking_id>")
def payment(booking_id):
    if "user_id" not in session:
        return redirect("/#signin")
        
    conn = get_db()
    cur = conn.cursor()
    
    check_expired_bookings(cur)
    conn.commit()
    
    booking = cur.execute("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='Pending'", (booking_id, session["user_id"])).fetchone()
    
    if not booking:
        conn.close()
        flash("Invalid booking or payment already processed.", "error")
        return redirect("/dashboard")
        
    # Attempt to get package price based on destination (simple matching)
    package = cur.execute("SELECT price FROM packages WHERE name=?", (booking["destination"],)).fetchone()
    price = package["price"] if package else 5000000 # Default 50k if custom destination
    
    try:
        start_date = datetime.datetime.strptime(booking["date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(booking["end_date"], "%Y-%m-%d").date()
        days_diff = (end_date - start_date).days
        num_days = days_diff + 1 if days_diff >= 0 else 1
    except (ValueError, TypeError):
        num_days = 1
        
    try:
        num_travelers = int(''.join(c for c in str(booking["travelers"]) if c.isdigit()) or 1)
    except:
        num_travelers = 1
        
    total_amount = price * num_travelers * num_days
    
    conn.close()
    return render_template("payment.html", booking=booking, total_amount=total_amount, price=price, num_days=num_days, num_travelers=num_travelers)

@app.route("/process_payment/<int:booking_id>", methods=["POST"])
def process_payment(booking_id):
    if "user_id" not in session:
        return redirect("/#signin")
        
    conn = get_db()
    cur = conn.cursor()
    
    check_expired_bookings(cur)
    conn.commit()
    
    booking = cur.execute("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='Pending'", (booking_id, session["user_id"])).fetchone()
    
    payment_method = request.form.get("payment_method", "Unknown")
    transaction_id = request.form.get("transaction_id", "")
    
    if booking:
        cur.execute("UPDATE bookings SET status='Validation Pending', payment_method=?, transaction_id=? WHERE id=?", (payment_method, transaction_id, booking_id))
        conn.commit()
        flash("Payment details submitted successfully! Awaiting Admin verification.", "success")
        conn.close()
        return redirect("/dashboard")
    else:
        flash("Invalid booking or payment already processed.", "error")
        
    conn.close()
    return redirect("/dashboard")

@app.route("/receipt/<int:booking_id>")
def receipt(booking_id):
    if "user_id" not in session:
        return redirect("/#signin")
        
    conn = get_db()
    cur = conn.cursor()
    booking = cur.execute("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='Confirmed'", (booking_id, session["user_id"])).fetchone()
    
    if not booking:
        conn.close()
        flash("Receipt not found or booking not confirmed.", "error")
        return redirect("/dashboard")
        
    package = cur.execute("SELECT price FROM packages WHERE name=?", (booking["destination"],)).fetchone()
    price = package["price"] if package else 5000000
    
    try:
        start_date = datetime.datetime.strptime(booking["date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(booking["end_date"], "%Y-%m-%d").date()
        days_diff = (end_date - start_date).days
        num_days = days_diff + 1 if days_diff >= 0 else 1
    except (ValueError, TypeError):
        num_days = 1
        
    try:
        num_travelers = int(''.join(c for c in str(booking["travelers"]) if c.isdigit()) or 1)
    except:
        num_travelers = 1
        
    total_amount = price * num_travelers * num_days
    
    today_date = datetime.date.today().strftime("%B %d, %Y")
    
    conn.close()
    return render_template("receipt.html", booking=booking, total_amount=total_amount, today=today_date, price=price, num_days=num_days, num_travelers=num_travelers)

@app.route("/cancel_booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        return redirect("/")
    
    conn = get_db()
    cur = conn.cursor()
    
    # Verify booking belongs to user
    booking = cur.execute("SELECT * FROM bookings WHERE id=? AND user_id=?", (booking_id, session["user_id"])).fetchone()
    
    if booking:
        if booking["status"] != "Cancelled":
            cur.execute("UPDATE bookings SET status='Cancelled' WHERE id=?", (booking_id,))
            conn.commit()
            flash("Booking cancelled successfully.", "success")
        else:
             flash("Booking is already cancelled.", "info")
    else:
        flash("Booking not found or access denied.", "error")
        
    conn.close()
    return redirect("/dashboard")

@app.route("/index.html")
def index_html_alias():
    return home()

@app.route("/destinations.html")
def destinations_html_alias():
    return destinations()

@app.route("/packages.html")
def packages_html_alias():
    return packages()

@app.route("/about.html")
def about_html_alias():
    return about()

@app.route("/contact.html")
def contact_html_alias():
    return contact()

@app.route("/dashboard.html")
def dashboard_html_alias():
    return dashboard()

@app.route("/admin.html")
def admin_html_alias():
    if session.get("role") != "admin":
        return redirect("/#signin")
    return admin_dashboard()

@app.route("/payment.html")
def payment_html_alias():
    booking_id = request.args.get("id")
    if booking_id:
        return redirect(url_for("payment", booking_id=booking_id))
    return redirect("/dashboard")

@app.route("/receipt.html")
def receipt_html_alias():
    booking_id = request.args.get("id")
    if booking_id:
        return redirect(url_for("receipt", booking_id=booking_id))
    return redirect("/dashboard")

# ---------------- RUN ----------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", debug=True)

