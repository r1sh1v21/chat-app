from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase


app = Flask(__name__)
app.config["SECRET_KEY"] = "fsdfsdfgwook"
socketio = SocketIO(app)

rooms = {}

def generate_code(l):
    while True:
        code=""
        for _ in range(l):
            code+=random.choice(ascii_uppercase)
        if code not in rooms:
            breakfrom flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "fsdfsdfgwook"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    room_code = db.Column(db.String(10), db.ForeignKey('room.code'), nullable=False)


active_members = {}


def generate_code(length):
    while True:
        code = ''.join(random.choices(ascii_uppercase, k=length))
        if not Room.query.filter_by(code=code).first():
            break
    return code


@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name", code=code, name=name)

        if join and not code:
            return render_template("home.html", error="Please enter a room code", code=code, name=name)

        room = code
        if create:
            room = generate_code(4)
            new_room = Room(code=room)
            db.session.add(new_room)
            db.session.commit()
        elif not Room.query.filter_by(code=code).first():
            return render_template("home.html", error="Room does not exist", code=code, name=name)

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None:
        return redirect(url_for("home"))

    messages = Message.query.filter_by(room_code=room).order_by(Message.timestamp).all()
    return render_template("room.html", code=room, messages=messages)

@socketio.on("message")
def handle_message(data):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return

    msg = Message(name=name, content=data["data"], room_code=room)
    db.session.add(msg)
    db.session.commit()

    content = {"name": name, "message": data["data"]}
    send(content, to=room)
    print(f"{name} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    active_members[room] = active_members.get(room, 0) + 1
    print(f"{name} joined {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in active_members:
        active_members[room] -= 1
        if active_members[room] <= 0:
            active_members.pop(room, None)

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} left {room}")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)

    return code



@app.route("/",methods=["POST","GET"])
def home():
    session.clear()
    if request.method=="POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="please enter a name ligma", code=code, name=name)
        if join != False and not code:
            return render_template("home.html", error="please enter a room code",code=code, name=name)
        room = code
        if create != False:
            room = generate_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="room does not exist")

        session["room"] = room
        session["name"] = name

        return redirect(url_for("room"))


    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name":session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name":name, "message":"has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -=1
        if rooms[room]["members"] <=0:
            del rooms[room]

    send({"name":name, "message":"has left the room"}, to=room)
    print(f"{name} left {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)
