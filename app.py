from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB = Path(__file__).with_name("shop.db")

PRODUCTS = [
    {"id": 1, "name": "ชานมไข่มุกต้นตำรับ", "price": 45, "category": "ชานม", "description": "ชานมหอมละมุน พร้อมไข่มุกหนึบ"},
    {"id": 2, "name": "ชานมบราวน์ชูการ์", "price": 55, "category": "ชานม", "description": "ชานมเข้มข้น หอมบราวน์ชูการ์"},
    {"id": 3, "name": "ชานมเผือก", "price": 50, "category": "ชานม", "description": "กลิ่นเผือกหอมหวาน ดื่มง่าย"},
    {"id": 4, "name": "ชานมมัทฉะ", "price": 55, "category": "ชาเขียว", "description": "มัทฉะหอมเข้ม ผสมนมอย่างลงตัว"},
    {"id": 5, "name": "ชาไทยไข่มุก", "price": 50, "category": "ชาไทย", "description": "ชาไทยหอมเข้ม เสิร์ฟพร้อมไข่มุก"},
    {"id": 6, "name": "โกโก้ไข่มุก", "price": 50, "category": "โกโก้", "description": "โกโก้เข้มข้น หวานมัน"},
    {"id": 7, "name": "ชาพีช", "price": 45, "category": "ชาใส", "description": "ชาหอมพีช สดชื่น"},
    {"id": 8, "name": "ชามะนาว", "price": 40, "category": "ชาใส", "description": "เปรี้ยวหวาน สดชื่น"},
]

TOPPINGS = [
    {"id": 101, "name": "ไข่มุกดำ", "price": 10},
    {"id": 102, "name": "วุ้นมะพร้าว", "price": 10},
    {"id": 103, "name": "พุดดิ้ง", "price": 15},
    {"id": 104, "name": "เยลลี่ผลไม้", "price": 10},
    {"id": 105, "name": "ชีสโฟม", "price": 15},
]

SIZES = {"S": 0, "M": 5, "L": 10}
SWEETNESS = ["0%", "25%", "50%", "75%", "100%"]
ICE = ["ไม่ใส่น้ำแข็ง", "น้อย", "ปกติ", "มาก"]

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total REAL NOT NULL,
        address TEXT NOT NULL,
        note TEXT,
        status TEXT DEFAULT 'รอรับออเดอร์',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        size TEXT NOT NULL,
        sweetness TEXT NOT NULL,
        ice TEXT NOT NULL,
        toppings TEXT,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    );
    """)
    conn.commit()
    conn.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("กรุณาเข้าสู่ระบบก่อนครับ", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def find_product(product_id):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)

def find_topping(topping_id):
    return next((t for t in TOPPINGS if t["id"] == topping_id), None)

@app.context_processor
def inject_globals():
    cart = session.get("cart", [])
    cart_count = sum(item["quantity"] for item in cart)
    return {"cart_count": cart_count}

@app.route("/")
def home():
    return render_template("index.html", products=PRODUCTS)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        full_name = request.form["full_name"].strip()
        phone = request.form.get("phone", "").strip()

        if not username or not password or not full_name:
            flash("กรุณากรอกข้อมูลที่จำเป็นให้ครบ", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("รหัสผ่านควรมีอย่างน้อย 6 ตัวอักษร", "danger")
            return render_template("register.html")

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users(username,password,full_name,phone) VALUES(?,?,?,?)",
                (username, generate_password_hash(password), full_name, phone)
            )
            conn.commit()
            flash("สมัครสมาชิกสำเร็จ! สามารถเข้าสู่ระบบได้เลยครับ", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาใช้ชื่ออื่น", "danger")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            flash("เข้าสู่ระบบสำเร็จครับ", "success")
            return redirect(url_for("home"))

        flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("ออกจากระบบแล้วครับ", "success")
    return redirect(url_for("home"))

@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_detail(product_id):
    product = find_product(product_id)
    if not product:
        return "ไม่พบสินค้า", 404

    if request.method == "POST":
        size = request.form.get("size", "M")
        sweetness = request.form.get("sweetness", "50%")
        ice = request.form.get("ice", "ปกติ")
        quantity = max(1, int(request.form.get("quantity", 1)))
        topping_ids = request.form.getlist("toppings")

        if size not in SIZES or sweetness not in SWEETNESS or ice not in ICE:
            flash("ข้อมูลตัวเลือกไม่ถูกต้อง", "danger")
            return redirect(url_for("product_detail", product_id=product_id))

        selected_toppings = [find_topping(int(tid)) for tid in topping_ids]
        selected_toppings = [t for t in selected_toppings if t]

        unit_price = product["price"] + SIZES[size] + sum(t["price"] for t in selected_toppings)
        item = {
            "product_id": product["id"],
            "product_name": product["name"],
            "size": size,
            "sweetness": sweetness,
            "ice": ice,
            "toppings": selected_toppings,
            "quantity": quantity,
            "unit_price": unit_price
        }

        cart = session.get("cart", [])
        cart.append(item)
        session["cart"] = cart
        flash("เพิ่มสินค้าเข้าตะกร้าแล้วครับ", "success")
        return redirect(url_for("cart"))

    return render_template("product.html", product=product, sizes=SIZES, sweetness=SWEETNESS, ice=ICE, toppings=TOPPINGS)

@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total = sum(item["unit_price"] * item["quantity"] for item in cart_items)
    return render_template("cart.html", cart=cart_items, total=total)

@app.route("/cart/remove/<int:index>")
def remove_cart(index):
    cart = session.get("cart", [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart_items = session.get("cart", [])
    if not cart_items:
        flash("ตะกร้าสินค้ายังว่างครับ", "warning")
        return redirect(url_for("home"))

    total = sum(item["unit_price"] * item["quantity"] for item in cart_items)

    if request.method == "POST":
        address = request.form["address"].strip()
        note = request.form.get("note", "").strip()

        if not address:
            flash("กรุณากรอกที่อยู่จัดส่ง", "danger")
            return render_template("checkout.html", cart=cart_items, total=total)

        conn = get_db()
        cur = conn.execute(
            "INSERT INTO orders(user_id,total,address,note) VALUES(?,?,?,?)",
            (session["user_id"], total, address, note)
        )
        order_id = cur.lastrowid

        for item in cart_items:
            toppings_text = ", ".join(f'{t["name"]} (+{t["price"]}฿)' for t in item["toppings"])
            conn.execute("""
                INSERT INTO order_items(order_id,product_name,size,sweetness,ice,toppings,quantity,price)
                VALUES(?,?,?,?,?,?,?,?)
            """, (
                order_id, item["product_name"], item["size"], item["sweetness"],
                item["ice"], toppings_text, item["quantity"], item["unit_price"]
            ))

        conn.commit()
        conn.close()
        session["cart"] = []
        flash(f"สั่งซื้อสำเร็จ! เลขออเดอร์ #{order_id}", "success")
        return redirect(url_for("orders"))

    return render_template("checkout.html", cart=cart_items, total=total)

@app.route("/orders")
@login_required
def orders():
    conn = get_db()
    orders = conn.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()

    details = {}
    for order in orders:
        details[order["id"]] = conn.execute(
            "SELECT * FROM order_items WHERE order_id=?", (order["id"],)
        ).fetchall()
    conn.close()
    return render_template("orders.html", orders=orders, details=details)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
