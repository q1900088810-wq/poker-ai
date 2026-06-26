from flask import Flask, request, jsonify
import random

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

# =========================
# 🧠 真实牌库（52张）
# =========================
SUITS = ["♠","♥","♦","♣"]
RANKS = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]

DECK = []
PLAYERS = []
BOARD = ["","","","",""]
PLAYER_COUNT = 2

# =========================
# 🧠 生成牌库 + 洗牌
# =========================
def new_deck():
    deck = [r+s for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

DECK = new_deck()

# =========================
# 🧠 发牌（从真实牌库抽）
# =========================
def deal_card():
    return DECK.pop() if DECK else ""

# =========================
# 🧠 创建玩家（自动发两张手牌）
# =========================
def create_players(n):

    global DECK

    players = []

    for i in range(n):

        players.append({
            "id": i,
            "pos": POSITIONS[i],
            "status": "active",
            "hand": [deal_card(), deal_card()]
        })

    return players

PLAYERS = create_players(PLAYER_COUNT)

# =========================
# 🧠 重开局（核心功能）
# =========================
@app.route("/reset")
def reset():

    global DECK, PLAYERS, BOARD

    DECK = new_deck()
    BOARD = ["","","","",""]

    PLAYERS = create_players(PLAYER_COUNT)

    return jsonify({
        "msg":"new game",
        "deck_left": len(DECK)
    })

# =========================
# 🧠 设置玩家数量
# =========================
@app.route("/set_players")
def set_players():

    global PLAYERS, PLAYER_COUNT

    n = int(request.args.get("n",2))
    n = max(2, min(9, n))

    PLAYER_COUNT = n

    DECK = new_deck()
    PLAYERS = create_players(n)

    return jsonify({"players": PLAYER_COUNT})

# =========================
# 🧠 设置公共牌（从牌库发，不是手动输入）
# =========================
@app.route("/deal_board")
def deal_board():

    global BOARD

    BOARD = [
        deal_card(),
        deal_card(),
        deal_card(),
        deal_card(),
        deal_card()
    ]

    return jsonify({"board": BOARD})

# =========================
# 🧠 玩家操作
# =========================
@app.route("/action")
def action():

    pid = int(request.args.get("id"))
    act = request.args.get("act")

    if pid < len(PLAYERS):

        p = PLAYERS[pid]

        if act == "fold":
            p["status"] = "fold"

        elif act == "call":
            p["status"] = "active"

        elif act == "raise":
            p["status"] = "active"

    return jsonify({
        "players": PLAYERS,
        "board": BOARD,
        "deck_left": len(DECK)
    })

# =========================
# 🌐 UI（真实牌库版）
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

    input,button{
        width:90%;
        padding:10px;
        margin:5px;
    }

    .box{
        border:1px solid #444;
        margin:5px;
        padding:8px;
        border-radius:8px;
    }

    .board{color:#00ffcc;margin:10px;}
    .hand{color:#ffd700;}

    </style>
    </head>

    <body>

    <h2>🧠 德州（真实牌库版）</h2>

    <!-- 👥 玩家 -->
    <input id="n" type="number" value="2" min="2" max="9">
    <button onclick="setPlayers()">设置玩家 + 重发牌</button>

    <!-- 🔄 重开局 -->
    <button onclick="resetGame()">🔄 重开局</button>

    <!-- 🌍 公共牌 -->
    <button onclick="dealBoard()">发公共牌（5张）</button>

    <div class="board" id="board"></div>
    <div id="root"></div>

    <script>

    function setPlayers(){

        let n=document.getElementById("n").value;

        fetch("/set_players?n="+n)
        .then(r=>r.json())
        .then(()=>load());
    }

    function resetGame(){

        fetch("/reset")
        .then(r=>r.json())
        .then(()=>load());
    }

    function dealBoard(){

        fetch("/deal_board")
        .then(r=>r.json())
        .then(()=>load());
    }

    function act(id,a){

        fetch(`/action?id=${id}&act=${a}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function render(d){

        document.getElementById("board").innerText =
        "公共牌：" + d.board.join(" ");

        let html="";

        d.players.forEach(p=>{

            html+=`
            <div class="box">
                <b>${p.pos}</b><br>

                手牌：${p.hand.join(" ")}<br>
                状态：${p.status}<br>

                <button onclick="act(${p.id},'fold')">弃牌</button>
                <button onclick="act(${p.id},'call')">跟注</button>
                <button onclick="act(${p.id},'raise')">加注</button>
            </div>`;
        });

        document.getElementById("root").innerHTML=html;
    }

    function load(){
        fetch("/action?id=0&act=none")
        .then(r=>r.json())
        .then(d=>render(d));
    }

    load();

    </script>

    </body>
    </html>
    """

# =========================
# 🚀 启动
# =========================
if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
