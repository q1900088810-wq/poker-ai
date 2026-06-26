from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 🧠 游戏状态（单局）
game = {
    "pot": 0,
    "players": {}
}

@app.route("/")
def index():
    return render_template("table.html")

# 🟢 玩家加入
@socketio.on("join")
def join(data):
    game["players"][data["id"]] = {
        "name": data["name"],
        "stack": 1000,
        "bet": 0
    }
    emit("state", game, broadcast=True)

# 💰 下注
@socketio.on("bet")
def bet(data):
    pid = data["id"]
    amount = data["amount"]

    game["players"][pid]["bet"] += amount
    game["players"][pid]["stack"] -= amount
    game["pot"] += amount

    emit("state", game, broadcast=True)

# 🟢 弃牌
@socketio.on("fold")
def fold(data):
    pid = data["id"]
    game["players"][pid]["fold"] = True
    emit("state", game, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
