from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

# =========================
# 🧠 状态
# =========================
PLAYERS = []
PLAYER_COUNT = 2

MY_HAND = ["",""]
BOARD = ["","","","",""]
STREET = "preflop"  # flop / turn / river

# =========================
# 🧠 玩家
# =========================
def create_players(n):

    return [
        {
            "id": i,
            "pos": POSITIONS[i],
            "status": "active"
        }
        for i in range(n)
    ]

PLAYERS = create_players(PLAYER_COUNT)

# =========================
# 🧠 玩家数量
# =========================
@app.route("/set_players")
def set_players():

    global PLAYERS, PLAYER_COUNT

    n = int(request.args.get("n",2))
    n = max(2, min(9, n))

    PLAYER_COUNT = n
    PLAYERS = create_players(n)

    return jsonify({"players": PLAYER_COUNT})

# =========================
# 🧠 设置手牌（你选2张）
# =========================
@app.route("/set_hand")
def set_hand():

    global MY_HAND

    MY_HAND = request.args.get("hand","").split()

    return jsonify({"hand": MY_HAND})

# =========================
# 🧠 设置Flop（3张）
# =========================
@app.route("/set_flop")
def set_flop():

    global BOARD, STREET

    cards = request.args.get("cards","").split()

    BOARD[0:3] = (cards + ["","",""])[:3]
    STREET = "flop"

    return jsonify({"board": BOARD[:3], "street": STREET})

# =========================
# 🧠 Turn（第4张）
# =========================
@app.route("/set_turn")
def set_turn():

    global BOARD, STREET

    card = request.args.get("card","")

    BOARD[3] = card
    STREET = "turn"

    return jsonify({"board": BOARD[:4], "street": STREET})

# =========================
# 🧠 River（第5张）
# =========================
@app.route("/set_river")
def set_river():

    global BOARD, STREET

    card = request.args.get("card","")

    BOARD[4] = card
    STREET = "river"

    return jsonify({"board": BOARD, "street": STREET})

# =========================
# 🌐 UI
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

    input,select,button{
        width:100%;
        padding:10px;
        margin:5px 0;
    }

    .box{
        border:1px solid #444;
        padding:8px;
        margin:5px 0;
    }

    .board{color:#00ffcc;}
    .me{color:#ffd700;}

    </style>
    </head>

    <body>

    <h2>🧠 德州（正确街道版）</h2>

    <!-- 👥 玩家 -->
    <input id="n" type="number" value="2" min="2" max="9">
    <button onclick="setPlayers()">设置玩家</button>

    <!-- 🎴 手牌 -->
    <h3>我的手牌（2张）</h3>
    <input id="h1">
    <input id="h2">
    <button onclick="setHand()">设置手牌</button>

    <!-- 🌍 Flop -->
    <h3>Flop（3张）</h3>
    <input id="f1">
    <input id="f2">
    <input id="f3">
    <button onclick="setFlop()">设置Flop</button>

    <!-- Turn -->
    <h3>Turn（1张）</h3>
    <input id="t">
    <button onclick="setTurn()">设置Turn</button>

    <!-- River -->
    <h3>River（1张）</h3>
    <input id="r">
    <button onclick="setRiver()">设置River</button>

    <div class="board" id="board"></div>
    <div class="me" id="me"></div>

    <script>

    function setPlayers(){

        let n=document.getElementById("n").value;

        fetch("/set_players?n="+n).then(r=>r.json());
    }

    function setHand(){

        let h=
        document.getElementById("h1").value+" "+
        document.getElementById("h2").value;

        fetch("/set_hand?hand="+h).then(r=>r.json());
    }

    function setFlop(){

        let c=
        document.getElementById("f1").value+" "+
        document.getElementById("f2").value+" "+
        document.getElementById("f3").value;

        fetch("/set_flop?cards="+c).then(r=>r.json());
    }

    function setTurn(){

        let c=document.getElementById("t").value;

        fetch("/set_turn?card="+c).then(r=>r.json());
    }

    function setRiver(){

        let c=document.getElementById("r").value;

        fetch("/set_river?card="+c).then(r=>r.json());
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
