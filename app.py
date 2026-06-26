from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 🧠 9人桌：1个你 + 8个AI
# =========================
POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

# =========================
# 🧠 52张标准牌
# =========================
RANKS = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]
SUITS = ["♠","♥","♦","♣"]

def deck():
    return [r+s for r in RANKS for s in SUITS]

# =========================
# 🧠 状态
# =========================
TABLE = [
    {"id": i, "pos": POSITIONS[i], "status": "active", "hand": ""}
    for i in range(9)
]

BOARD = ""
MY_HAND = ""

# =========================
# 🧠 设置你的手牌（下拉选牌）
# =========================
@app.route("/set_hand")
def set_hand():

    global MY_HAND
    MY_HAND = request.args.get("hand","")

    return jsonify({"hand": MY_HAND})

# =========================
# 🧠 设置公共牌（下拉选牌）
# =========================
@app.route("/set_board")
def set_board():

    global BOARD
    BOARD = request.args.get("board","")

    return jsonify({"board": BOARD})

# =========================
# 🧠 玩家操作
# =========================
@app.route("/action")
def action():

    pid = int(request.args.get("id"))
    act = request.args.get("act")

    if act == "fold":
        TABLE[pid]["status"] = "fold"

    elif act == "call":
        TABLE[pid]["status"] = "active"

    elif act == "raise":
        TABLE[pid]["status"] = "active"

    return jsonify({
        "table": TABLE,
        "board": BOARD,
        "my_hand": MY_HAND
    })

# =========================
# 🌐 UI（最终修复版）
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

    select,button{
        width:90%;
        padding:10px;
        margin:5px;
        font-size:14px;
    }

    .grid{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:10px;
        margin-top:15px;
    }

    .box{
        border:1px solid #444;
        padding:10px;
        border-radius:10px;
    }

    .fold{color:red}

    .board{
        margin-top:10px;
        color:#00ffcc;
    }

    .me{
        color:#ffd700;
        margin-top:10px;
    }

    </style>
    </head>

    <body>

    <h2>🧠 9人德州桌（最终稳定版）</h2>

    <!-- 🟡 你的手牌（必须选牌） -->
    <h3>🎴 我的手牌</h3>
    <select id="h1"></select>
    <select id="h2"></select>
    <button onclick="setHand()">确认手牌</button>

    <!-- 🟡 公共牌 -->
    <h3>🌍 公共牌</h3>
    <select id="b1"></select>
    <select id="b2"></select>
    <select id="b3"></select>
    <button onclick="setBoard()">确认公共牌</button>

    <div class="me" id="me">我的手牌：未设置</div>
    <div class="board" id="boardView">公共牌：未设置</div>

    <!-- 🟣 9人桌 -->
    <div class="grid" id="table"></div>

    <script>

    let RANKS = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"];
    let SUITS = ["♠","♥","♦","♣"];

    function makeDeck(selectId){

        let el = document.getElementById(selectId);

        RANKS.forEach(r=>{
            SUITS.forEach(s=>{
                let opt = document.createElement("option");
                opt.value = r+s;
                opt.innerText = r+s;
                el.appendChild(opt);
            });
        });
    }

    function init(){

        makeDeck("h1");
        makeDeck("h2");

        makeDeck("b1");
        makeDeck("b2");
        makeDeck("b3");
    }

    function setHand(){

        let h = document.getElementById("h1").value + " " +
                document.getElementById("h2").value;

        fetch(`/set_hand?hand=${h}`)
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function setBoard(){

        let b = document.getElementById("b1").value + " " +
                document.getElementById("b2").value + " " +
                document.getElementById("b3").value;

        fetch(`/set_board?board=${b}`)
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function act(id,act){

        fetch(`/action?id=${id}&act=${act}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function render(d){

        document.getElementById("me").innerText =
        "我的手牌：" + d.my_hand;

        document.getElementById("boardView").innerText =
        "公共牌：" + d.board;

        let html = "";

        d.table.forEach(p=>{

            html += `
            <div class="box ${p.status=='fold'?'fold':''}">
                <b>${p.pos}</b><br>
                ${p.hand || "空"}<br>
                状态: ${p.status}<br>

                <button onclick="act(${p.id},'fold')">弃牌</button>
                <button onclick="act(${p.id},'call')">跟注</button>
                <button onclick="act(${p.id},'raise')">加注</button>
            </div>
            `;
        });

        document.getElementById("table").innerHTML = html;
    }

    function refresh(){
        fetch("/action?id=0&act=none")
        .then(r=>r.json())
        .then(d=>render(d));
    }

    init();
    refresh();

    </script>

    </body>
    </html>
    """

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
