from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
dbname = 'db/MerchDB.db'


@app.route("/")
def index():
    video_data = get_videos()
    music_data = get_music()
    return render_template("index.html", videos=video_data, music=music_data)


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


@app.route("/acc")
def acc():
    return render_template("acc.html")


if __name__ == '__main__':
    app.run()
