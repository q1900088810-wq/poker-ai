from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

# =========================
# 🧠 状态
# =========================
PLAYERS = []
PLAYER_COUNT = 2

MY_HAND = ["",""]

BOARD = ["","","","",""]  # flop 0-2, turn 3, river 4

BET = {}  # 每个玩家下注

STREET = "preflop"

# =========================
# 🧠 创建玩家
# =========================
def create_players(n):

    players = []

    for i in range(n):

        players.append({
            "id": i,
            "pos": POSITIONS[i],
            "status": "active",
            "bet": 0
        })

    return players

PLAYERS = create_players(PLAYER_COUNT)

# =========================
# 🧠 设置玩家数量
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
# 🧠 手牌（你选）
# =========================
@app.route("/set_hand")
def set_hand():

    global MY_HAND

    MY_HAND = request.args.get("hand","").split()

    return jsonify({"hand": MY_HAND})

# =========================
# 🧠 Flop（3张）
# =========================
@app.route("/set_flop")
def set_flop():

    global BOARD, STREET

    cards = request.args.get("cards","").split()

    BOARD[0:3] = (cards + ["","",""])[:3]

    STREET = "flop"

    return jsonify({"board": BOARD[:3], "street": STREET})

# =========================
# 🧠 Turn
# =========================
@app.route("/set_turn")
def set_turn():

    global BOARD, STREET

    card = request.args.get("card","")

    BOARD[3] = card
    STREET = "turn"

    return jsonify({"board": BOARD[:4], "street": STREET})

# =========================
# 🧠 River
# =========================
@app.route("/set_river")
def set_river():

    global BOARD, STREET

    card = request.args.get("card","")

    BOARD[4] = card
    STREET = "river"

    return jsonify({"board": BOARD, "street": STREET})

# =========================
# 🧠 下注系统（核心）
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
            BET[pid] = amount
            p["status"] = "call"

        elif act == "raise":
            BET[pid] = amount
            p["status"] = "raise"

    return jsonify({
        "players": PLAYERS,
        "bets": BET,
        "board": BOARD,
        "hand": MY_HAND,
        "street": STREET
    })

# =========================
# 🌐 UI（简洁不炸屏）
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

    <h3>🧠 德州手动模拟系统（完整规则版）</h3>

    <!-- 👥 玩家 -->
    <input id="n" type="number" value="2" min="2" max="9">
    <button onclick="setPlayers()">设置玩家</button>

    <!-- 🎴 手牌 -->
    <h3>我的手牌</h3>
    <input id="h1">
    <input id="h2">
    <button onclick="setHand()">设置手牌</button>

    <!-- 🌍 Flop -->
    <h3>Flop（3张）</h3>
    <input id="f">
    <button onclick="setFlop()">设置Flop</button>

    <!-- Turn -->
    <h3>Turn</h3>
    <input id="t">
    <button onclick="setTurn()">设置Turn</button>

    <!-- River -->
    <h3>River</h3>
    <input id="r">
    <button onclick="setRiver()">设置River</button>

    <!-- 💰 下注 -->
    <h3>下注</h3>
    <input id="pid" placeholder="玩家ID">
    <input id="amt" placeholder="金额">

    <button onclick="call()">跟注</button>
    <button onclick="raise()">加注</button>
    <button onclick="fold()">弃牌</button>

    <div class="board" id="board"></div>
    <div class="me" id="me"></div>
    <div id="root"></div>

    <script>

    function setPlayers(){
        fetch("/set_players?n="+document.getElementById("n").value);
    }

    function setHand(){
        let h=document.getElementById("h1").value+" "+document.getElementById("h2").value;
        fetch("/set_hand?hand="+h);
    }

    function setFlop(){
        fetch("/set_flop?cards="+document.getElementById("f").value);
    }

    function setTurn(){
        fetch("/set_turn?card="+document.getElementById("t").value);
    }

    function setRiver(){
        fetch("/set_river?card="+document.getElementById("r").value);
    }

    function call(){
        fetch(`/bet?id=${pid().id}&amount=${amt()}&act=call`);
    }

    function raise(){
        fetch(`/bet?id=${pid().id}&amount=${amt()}&act=raise`);
    }

    function fold(){
        fetch(`/bet?id=${pid().id}&amount=0&act=fold`);
    }

    function pid(){
        return {id:document.getElementById("pid").value};
    }

    function amt(){
        return document.getElementById("amt").value;
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
