from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
dbname = 'db/MerchDB.db'
app.secret_key = "Group11"


@app.route("/")
def index():
    video_data = get_videos()
    music_data = get_music()
    if 'username' in session:
        user_info = get_user_info(session['username'])
        if user_info:
            full_name = f"{user_info['first_name']} {user_info['last_name']}"
            return render_template("index.html", user_full_name=full_name,
                                   videos=video_data, music=music_data)
        else:
            return "No account found."
    else:
        return render_template("index.html", videos=video_data, music=music_data)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        save_user_to_db(username, first_name, last_name, email, password)
        return redirect(url_for("signin"))
    return render_template("signup.html")


def save_user_to_db(username, email, password, first_name, last_name):
    try:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute("INSERT INTO Customers (username, email, password, firstname, lastname)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (username, first_name, last_name, email, password,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("Error saving user to SQLite:", e)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if check_user_credentials(username, password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return "Wrong."
    return render_template("signin.html")


def check_user_credentials(username, password):
    try:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Customers WHERE username = ? AND password = ?",
                    (username, password))
        result = cur.fetchone()[0]
        conn.close()
        return result > 0
    except sqlite3.Error as e:
        print("Error checking user credentials:", e)
        return False


# Account
@app.route("/account")
def account():
    if 'username' in session:
        user_info = get_user_info(session['username'])
        if user_info:
            return render_template("account.html", user_info=user_info)
        else:
            return "No account found."
    else:
        return redirect(url_for('signin'))


def get_user_info(username):
    try:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute("SELECT id, firstname, lastname, email FROM Customers WHERE username = ?",
                    (username,))
        user_info = cur.fetchone()
        conn.close()
        if user_info:
            user_id, first_name, last_name, email = user_info
            return {
                'user_id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
        else:
            return None
    except sqlite3.Error as e:
        print("Error fetching user info from SQLite:", e)
        return None


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


def get_videos():
    try:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute('SELECT * FROM Videos ORDER BY created_time DESC LIMIT 6')
        videos = cur.fetchall()
        video_list = []
        for video in videos:
            video_dict = {
                'id': video[0],
                'title': video[1],
                'image_url': video[2],
                'created_time': video[3]
            }
            video_list.append(video_dict)
        return video_list
    except sqlite3.Error as e:
        print("Error reading data from SQLite:", e)
        return []


def get_music():
    try:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute('SELECT * FROM Music ORDER BY created_time DESC LIMIT 5')
        music = cur.fetchall()
        music_list = []
        for music_item in music:
            music_dict = {
                'id': music_item[0],
                'type': music_item[1],
                'title': music_item[2],
                'image_url': music_item[3],
                'created_time': music_item[4]
            }
            music_list.append(music_dict)
        return music_list
    except sqlite3.Error as e:
        print("Error reading data from SQLite:", e)
        return []


@app.route("/store", methods=['GET', 'POST'])
def store():
    if request.method == 'POST':
        search_text = request.form['searchInput']
        products = load_data(search_text)
        return render_template('store.html', merch=products, search_text=search_text)
    else:
        merch_data = get_merch()
        return render_template('store.html', merch=merch_data)


def load_data(search_text):
    max_price = {}
    if search_text != "":
        try:
            max_price = float(search_text)
        except ValueError:
            max_price = 0
    if search_text:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        command = "SELECT * FROM Merchandise WHERE name LIKE ? OR price <= ?"
        cur.execute(command, ('%' + search_text + '%', max_price))
        merch = cur.fetchall()
        merch_list = []
        for merch_item in merch:
            merch_dict = {
                'id': merch_item[0],
                'name': merch_item[1],
                'image_main_url': merch_item[2],
                'image_hover_url': merch_item[3],
                'price': merch_item[4],
                'created_time': merch_item[5]
            }
            merch_list.append(merch_dict)
        return merch_list
    else:
        return []


def get_merch():
    try:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute('SELECT * FROM Merchandise')
        merch = cur.fetchall()
        merch_list = []
        for merch_item in merch:
            merch_dict = {
                'id': merch_item[0],
                'name': merch_item[1],
                'image_main_url': merch_item[2],
                'image_hover_url': merch_item[3],
                'price': merch_item[4],
                'created_time': merch_item[5]
            }
            merch_list.append(merch_dict)
        return merch_list
    except sqlite3.Error as e:
        print("Error reading data from SQLite:", e)
        return []


@app.route("/item/<int:item_id>")
def item(item_id):
    item_slides = get_item_slides(item_id)
    item_details = get_item_details(item_id)
    if item_details:
        item_details['des'] = add_line_breaks(item_details['des'])
        return render_template('item.html', item_slides=item_slides, item_details=item_details)


def add_line_breaks(text):
    return text.replace('\n', '<br>')


def get_item_slides(item_id):
    try:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute('SELECT image_url FROM ItemSlideImages m WHERE m.item_id = ?'
                    'ORDER BY num ASC', (item_id,))
        item_details = cur.fetchall()
        if item_details:
            slides = [{'item_id': item_id, 'image_url': row[0]} for row in item_details]
            return slides
        else:
            return None
    except sqlite3.Error as e:
        print("Error reading data from SQLite:", e)
        return None


def get_item_details(item_id):
    try:
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        cur.execute('''SELECT m.name, m.price, md.des, md.note, md.copyright 
                       FROM Merchandise m 
                       JOIN MerchDetails md ON m.id = md.item_id 
                       WHERE m.id = ?''', (item_id,))
        item_details = cur.fetchone()
        if item_details:
            item_dict = {
                'item_id': item_id,
                'name': item_details[0],
                'price': item_details[1],
                'des': item_details[2],
                'note': item_details[3],
                'copyright': item_details[4]
            }
            return item_dict
        else:
            return None
    except sqlite3.Error as e:
        print("Error reading data from SQLite:", e)
        return None


@app.route("/store/add", methods=["POST"])
def add_to_cart():
    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])

    connection = sqlite3.connect(dbname)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Merchandise WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    connection.close()
    product_dict = {
        "id": product[0],
        "name": product[1],
        "image": product[2],
        "price": product[4],
        "quantity": quantity
    }
    cart = session.get("cart", [])
    found = False
    for cart_item in cart:
        if cart_item["id"] == product_id:
            cart_item["quantity"] += quantity
            found = True
            break
    if not found:
        cart.append(product_dict)
    session["cart"] = cart
    return redirect(url_for("store"))


@app.route("/cart", methods=["GET", "POST"])
def view_cart():
    current_cart = session.get("cart", [])
    if not current_cart:
        return "No item in the current cart!"
    return render_template("cart.html", cart=current_cart)


@app.route("/cart/delete", methods=["POST"])
def delete_item():
    product_id = int(request.form["product_id"])
    cart = session.get("cart", [])
    for cart_item in cart:
        if cart_item["id"] == product_id:
            cart.remove(cart_item)
            break
    session["cart"] = cart
    return redirect(url_for("view_cart"))


@app.route("/cart/update", methods=["POST"])
def update_item():
    change = int(request.form["quantityChange"])
    product_id = int(request.form["product_id"])
    cart = session.get("cart", [])
    for cart_item in cart:
        if cart_item["id"] == product_id:
            cart_item["quantity"] = change
            break
    session["cart"] = cart
    return redirect(url_for("view_cart"))


@app.route("/cart/proceed", methods=["POST"])
def proceed_cart():
    current_cart = []
    user_info = {}

    if 'cart' in session:
        current_cart = session.get("cart", [])
    if 'username' in session:
        user_info = get_user_info(session["username"])

    connection = sqlite3.connect(dbname)
    cursor = connection.cursor()

    try:
        # Insert order into Orders table
        cursor.execute("INSERT INTO Orders (customerId) VALUES (?)", (user_info["user_id"],))

        # Get the last inserted OrderID
        cursor.execute("SELECT orderId FROM Orders ORDER BY date DESC")
        data = cursor.fetchone()
        orderid = data[0]

        values = ""
        for product in current_cart:
            pid = product["id"]
            quantity = product["quantity"]
            price = product["price"]
            values += f"({orderid}, {pid}, {quantity}, {price}),"

        values = values.rstrip(',')

        cursor.execute("INSERT INTO OrderDetails VALUES " + values)

        cursor.execute(
            "SELECT OrderDetails.orderId, Merchandise.image_main_url, Merchandise.name, Merchandise.price, "
            "OrderDetails.quantity, Merchandise.price * OrderDetails.quantity AS total_price FROM OrderDetails JOIN "
            "Merchandise ON OrderDetails.merchId = Merchandise.id WHERE OrderDetails.orderId = ?",
            (orderid,))
        items = cursor.fetchall()

        connection.commit()
        session.pop('cart')

        return render_template("proceed.html", items=items)

    except sqlite3.Error as e:
        print("SQLite error:", e)
        connection.rollback()

    finally:
        connection.close()


@app.route("/acc")
def acc():
    return render_template("acc.html")


@app.route("/cart")
def my_cart():
    return render_template("cart.html")


if __name__ == '__main__':
    app.run()
