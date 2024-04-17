from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
dbname = 'db/MerchDB.db'


@app.route("/")
def index():
    video_data = get_videos()
    music_data = get_music()
    return render_template("index.html", videos=video_data, music=music_data)


@app.route("/acc")
def acc():
    return render_template("acc.html")


@app.route("/item")
def item():
    return render_template("item.html")


@app.route("/store", methods=['POST'])
def store():
    merch_data = get_merch()
    my_search_text = request.form['searchInput']
    products = load_data(my_search_text)
    return render_template('store.html', merch=merch_data, search_text=my_search_text)


def load_data(search_text):
    if search_text != "":
        conn = sqlite3.connect(dbname)
        cursor = conn.cursor()
        command = ("select * from Merchandise where name like '%" + search_text + "%' or price like '%" + search_text + "%'")
        cursor.execute(command)
        data = cursor.fetchall()
        conn.close()
        return data


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


if __name__ == '__main__':
    app.run()
