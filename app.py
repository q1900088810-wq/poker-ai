from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# =========================
# 🧠 牌库
# =========================
RANKS = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]
SUITS = ["♠","♥","♦","♣"]

def new_deck():
    deck = [r+s for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

# =========================
# 🧠 游戏状态
# =========================
state = {
    "deck": [],
    "players": [],
    "board": [],
    "street": "preflop"
}

# =========================
# 🧠 开始新牌局
# =========================
@app.route("/start")
def start():

    n = int(request.args.get("n",2))
    n = max(2, min(9, n))

    deck = new_deck()

    players = []
    for i in range(n):
        players.append({
            "id": i,
            "hand": [deck.pop(), deck.pop()]
        })

    state["deck"] = deck
    state["players"] = players
    state["board"] = []
    state["street"] = "preflop"

    return jsonify(state)

# =========================
# 🧠 下一步（自动推进）
# =========================
@app.route("/next")
def next_step():

    deck = state["deck"]

    if state["street"] == "preflop":
        state["board"] = [deck.pop(), deck.pop(), deck.pop()]
        state["street"] = "flop"

    elif state["street"] == "flop":
        state["board"].append(deck.pop())
        state["street"] = "turn"

    elif state["street"] == "turn":
        state["board"].append(deck.pop())
        state["street"] = "river"

    return jsonify(state)

# =========================
# 🌐 UI（极简不卡）
# =========================
@app.route("/")
def home():
    return """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>

    body{
        background:#111;
        color:white;
        font-family:Arial;
        text-align:center;
        padding:10px;
    }

    button{
        width:90%;
        padding:12px;
        margin:5px;
    }

    .box{
        border:1px solid #444;
        margin:8px;
        padding:8px;
    }

    .board{color:#00ffcc;margin:10px;}

    </style>
    </head>

    <body>

    <h3>🧠 德州模拟器（正常版）</h3>

    <button onclick="start()">开始一局</button>
    <button onclick="next()">下一街</button>

    <div class="board" id="board"></div>
    <div id="players"></div>

    <script>

    function start(){
        let n=prompt("玩家人数 2-9");
        fetch("/start?n="+n).then(r=>r.json()).then(d=>render(d));
    }

    function next(){
        fetch("/next").then(r=>r.json()).then(d=>render(d));
    }

    function render(d){

        document.getElementById("board").innerText =
        "街道：" + d.street + " | 公共牌：" + d.board.join(" ");

        let html="";

        d.players.forEach(p=>{
            html+=`
            <div class="box">
                玩家 ${p.id}<br>
                手牌：${p.hand.join(" ")}
            </div>`;
        });

        document.getElementById("players").innerHTML=html;
    }

    </script>

    </body>
    </html>
    """

# =========================
# 🚀 启动
# =========================
if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
