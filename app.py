from flask import Flask, request, jsonify
import random

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

SUITS = ["♠","♥","♦","♣"]
RANKS = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]

DECK = []
PLAYERS = []
BOARD = ["","","","",""]
PLAYER_COUNT = 2

# =========================
# 🧠 牌库
# =========================
def new_deck():
    deck = [r+s for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

def deal():
    return DECK.pop() if DECK else ""

# =========================
# 🧠 初始化
# =========================
def create_players(n):

    return [
        {
            "id": i,
            "pos": POSITIONS[i],
            "status": "active",
            "hand": [deal(), deal()]
        }
        for i in range(n)
    ]

# =========================
# 🧠 开局
# =========================
def start_game(n):

    global DECK, PLAYERS, BOARD, PLAYER_COUNT

    PLAYER_COUNT = n
    DECK = new_deck()
    BOARD = ["","","","",""]
    PLAYERS = create_players(n)

start_game(2)

# =========================
# 🔄 重开局（核心）
# =========================
@app.route("/reset")
def reset():

    start_game(PLAYER_COUNT)

    return jsonify({
        "msg":"reset ok"
    })

# =========================
# 👥 设置人数
# =========================
@app.route("/set_players")
def set_players():

    n = int(request.args.get("n",2))
    n = max(2, min(9, n))

    start_game(n)

    return jsonify({"players": PLAYER_COUNT})

# =========================
# 🌍 发公共牌
# =========================
@app.route("/deal_board")
def deal_board():

    global BOARD

    BOARD = [deal(),deal(),deal(),deal(),deal()]

    return jsonify({"board": BOARD})

# =========================
# 🎮 操作
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
        "board": BOARD
    })

# =========================
# 🌐 UI（手机优化版）
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
        padding:10px;
    }

    button,input{
        width:100%;
        padding:10px;
        margin:5px 0;
    }

    .board{
        color:#00ffcc;
        margin:10px 0;
        font-size:14px;
    }

    /* 🟣 手机卡片（重点优化） */
    .card{
        background:#1c1c1c;
        border-radius:10px;
        margin:10px 0;
        padding:10px;
    }

    .hidden{
        display:none;
    }

    .title{
        display:flex;
        justify-content:space-between;
        cursor:pointer;
    }

    .btnrow button{
        width:32%;
        font-size:12px;
    }

    </style>
    </head>

    <body>

    <h3>🧠 德州（移动优化版）</h3>

    <!-- 👥 玩家 -->
    <input id="n" type="number" value="2" min="2" max="9">
    <button onclick="setPlayers()">设置人数 & 重开局</button>

    <!-- 🔄 重开局 -->
    <button onclick="resetGame()">🔄 重开局</button>

    <!-- 🌍 公共牌 -->
    <button onclick="dealBoard()">发公共牌</button>

    <div class="board" id="board"></div>

    <div id="root"></div>

    <script>

    function toggle(id){

        let el=document.getElementById(id);

        if(el.classList.contains("hidden")){
            el.classList.remove("hidden");
        }else{
            el.classList.add("hidden");
        }
    }

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
        "公共牌: " + d.board.join(" ");

        let html="";

        d.players.forEach(p=>{

            let id="p"+p.id;

            html+=`
            <div class="card">

                <div class="title" onclick="toggle('${id}')">
                    <b>${p.pos}</b>
                    <span>${p.status}</span>
                </div>

                <div id="${id}" class="hidden">

                    <div>手牌：${p.hand.join(" ")}</div>

                    <div class="btnrow">
                        <button onclick="act(${p.id},'fold')">弃牌</button>
                        <button onclick="act(${p.id},'call')">跟注</button>
                        <button onclick="act(${p.id},'raise')">加注</button>
                    </div>

                </div>
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
