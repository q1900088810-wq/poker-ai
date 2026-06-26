from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

PLAYERS = []
PLAYER_COUNT = 2

MY_HAND = ["",""]
BOARD = ["","","","",""]
BET = {}

# =========================
# 🧠 玩家
# =========================
def create_players(n):

    return [
        {
            "id": i,
            "pos": POSITIONS[i],
            "status": "active",
            "bet": 0
        }
        for i in range(n)
    ]

PLAYERS = create_players(PLAYER_COUNT)

# =========================
# 🧠 玩家数量
# =========================
@app.route("/set_players")
def set_players():

    global PLAYERS, PLAYER_COUNT, BET

    n = int(request.args.get("n",2))
    n = max(2, min(9, n))

    PLAYER_COUNT = n
    PLAYERS = create_players(n)
    BET = {i:0 for i in range(n)}

    return jsonify({"players": PLAYER_COUNT})

# =========================
# 🧠 手牌（手动输入）
# =========================
@app.route("/set_hand")
def set_hand():

    global MY_HAND

    MY_HAND = request.args.get("hand","").split()

    return jsonify({"hand": MY_HAND})

# =========================
# 🧠 公共牌（完全手动，无发牌）
# =========================
@app.route("/set_board")
def set_board():

    global BOARD

    BOARD = request.args.get("board","").split()

    return jsonify({"board": BOARD})

# =========================
# 🧠 下注系统
# =========================
@app.route("/bet")
def bet():

    pid = int(request.args.get("id"))
    amount = int(request.args.get("amount",0))
    act = request.args.get("act")

    if pid < len(PLAYERS):

        p = PLAYERS[pid]

        if act == "fold":
            p["status"] = "fold"

        elif act == "call":
            p["status"] = "call"
            p["bet"] = amount

        elif act == "raise":
            p["status"] = "raise"
            p["bet"] = amount

    return jsonify({
        "players": PLAYERS,
        "bets": BET,
        "board": BOARD,
        "hand": MY_HAND
    })

# =========================
# 🌐 UI（已去标题 + 极简）
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

    input,button{
        width:100%;
        padding:10px;
        margin:5px 0;
    }

    .card{
        border:1px solid #444;
        padding:8px;
        margin:5px 0;
        border-radius:8px;
    }

    .board{color:#00ffcc;margin:10px;}
    .me{color:#ffd700;}

    </style>
    </head>

    <body>

    <!-- 👥 玩家 -->
    <input id="n" type="number" value="2" min="2" max="9">
    <button onclick="setPlayers()">玩家数量</button>

    <!-- 🎴 手牌 -->
    <input id="h1" placeholder="手牌1">
    <input id="h2" placeholder="手牌2">
    <button onclick="setHand()">设置手牌</button>

    <!-- 🌍 公共牌 -->
    <input id="board" placeholder="公共牌（空格分隔）">
    <button onclick="setBoard()">设置公共牌</button>

    <!-- 💰 下注 -->
    <input id="pid" placeholder="玩家ID">
    <input id="amt" placeholder="金额">

    <button onclick="call()">跟注</button>
    <button onclick="raise()">加注</button>
    <button onclick="fold()">弃牌</button>

    <div class="board" id="boardView"></div>
    <div class="me" id="me"></div>
    <div id="root"></div>

    <script>

    function setPlayers(){
        fetch("/set_players?n="+n().value);
    }

    function setHand(){
        fetch("/set_hand?hand="+h1().value+" "+h2().value);
    }

    function setBoard(){
        fetch("/set_board?board="+b().value);
    }

    function call(){
        fetch(`/bet?id=${pid().value}&amount=${amt().value}&act=call`);
    }

    function raise(){
        fetch(`/bet?id=${pid().value}&amount=${amt().value}&act=raise`);
    }

    function fold(){
        fetch(`/bet?id=${pid().value}&amount=0&act=fold`);
    }

    function n(){return document.getElementById("n");}
    function h1(){return document.getElementById("h1");}
    function h2(){return document.getElementById("h2");}
    function b(){return document.getElementById("board");}
    function pid(){return document.getElementById("pid");}
    function amt(){return document.getElementById("amt");}

    </script>

    </body>
    </html>
    """

# =========================
# 🚀 启动
# =========================
if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
