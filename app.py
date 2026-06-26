from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

# =========================
# 🧠 单桌系统
# =========================
PLAYERS = []
PLAYER_COUNT = 2
BOARD = ["","","","",""]
MY_HAND = ""

# =========================
# 🧠 创建玩家（核心）
# =========================
def create_players(n):

    return [
        {
            "id": i,
            "pos": POSITIONS[i],
            "status": "active",
            "hand": ""
        }
        for i in range(n)
    ]

PLAYERS = create_players(PLAYER_COUNT)

# =========================
# 🧠 设置玩家数量（2-9）
# =========================
@app.route("/set_players")
def set_players():

    global PLAYERS, PLAYER_COUNT

    n = int(request.args.get("n",2))
    n = max(2, min(9, n))

    PLAYER_COUNT = n
    PLAYERS = create_players(n)

    return jsonify({
        "players": PLAYER_COUNT
    })

# =========================
# 🧠 设置手牌
# =========================
@app.route("/set_hand")
def set_hand():

    global MY_HAND
    MY_HAND = request.args.get("hand","")

    return jsonify({"hand": MY_HAND})

# =========================
# 🧠 设置公共牌（5张固定）
# =========================
@app.route("/set_board")
def set_board():

    global BOARD

    cards = request.args.get("board","").split()
    BOARD = (cards + ["","","","",""])[:5]

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
        "my_hand": MY_HAND
    })

# =========================
# 🌐 UI（单桌版本）
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

    input,select,button{
        width:90%;
        padding:10px;
        margin:5px;
    }

    .grid{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:10px;
    }

    .box{
        border:1px solid #444;
        padding:8px;
        border-radius:8px;
        font-size:12px;
    }

    .board{color:#00ffcc;margin:10px;}
    .me{color:#ffd700;margin:10px;}

    </style>
    </head>

    <body>

    <h2>🧠 单桌德州（玩家可配置版）</h2>

    <!-- 👥 玩家数量 -->
    <h3>玩家数量 (2-9)</h3>
    <input id="n" type="number" value="2" min="2" max="9">
    <button onclick="setPlayers()">设置玩家</button>

    <!-- 🎴 手牌 -->
    <h3>手牌</h3>
    <select id="h1"></select>
    <select id="h2"></select>
    <button onclick="setHand()">设置手牌</button>

    <!-- 🌍 公共牌 -->
    <h3>公共牌（5张）</h3>
    <select id="b1"></select>
    <select id="b2"></select>
    <select id="b3"></select>
    <select id="b4"></select>
    <select id="b5"></select>
    <button onclick="setBoard()">设置公共牌</button>

    <div class="me" id="me"></div>
    <div class="board" id="board"></div>

    <div id="root"></div>

    <script>

    let R=["A","K","Q","J","10","9","8","7","6","5","4","3","2"];
    let S=["♠","♥","♦","♣"];

    function build(id){

        let el=document.getElementById(id);

        R.forEach(r=>{
            S.forEach(s=>{
                let o=document.createElement("option");
                o.value=r+s;
                o.innerText=r+s;
                el.appendChild(o);
            });
        });
    }

    function initUI(){

        build("h1");build("h2");
        build("b1");build("b2");build("b3");build("b4");build("b5");
    }

    function setPlayers(){

        let n=document.getElementById("n").value;

        fetch("/set_players?n="+n)
        .then(r=>r.json())
        .then(()=>load());
    }

    function setHand(){

        let h=document.getElementById("h1").value+" "+document.getElementById("h2").value;

        fetch("/set_hand?hand="+h)
        .then(r=>r.json())
        .then(()=>load());
    }

    function setBoard(){

        let b=
        document.getElementById("b1").value+" "+
        document.getElementById("b2").value+" "+
        document.getElementById("b3").value+" "+
        document.getElementById("b4").value+" "+
        document.getElementById("b5").value;

        fetch("/set_board?board="+b)
        .then(r=>r.json())
        .then(()=>load());
    }

    function act(id,a){

        fetch(`/action?id=${id}&act=${a}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function render(d){

        document.getElementById("me").innerText =
        "我的手牌：" + d.my_hand;

        document.getElementById("board").innerText =
        "公共牌：" + d.board.join(" ");

        let html="";

        d.players.forEach(p=>{

            html+=`
            <div class="box ${p.status=='fold'?'fold':''}">
                ${p.pos}<br>
                ${p.status}<br>

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

    initUI();
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
