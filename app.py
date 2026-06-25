from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB","BB"]

# =========================
# 🧠 状态（全局稳定）
# =========================
TABLE = [
    {"id": i, "pos": POSITIONS[i], "status": "active", "hand": ""}
    for i in range(9)
]

BOARD = ""
MY_HAND = ""

# =========================
# 🧠 设置你的手牌（不会丢）
# =========================
@app.route("/set_hand")
def set_hand():

    global MY_HAND
    MY_HAND = request.args.get("hand","")

    return jsonify({"hand": MY_HAND})

# =========================
# 🧠 设置公共牌（不会丢）
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
# 🌐 UI（完全稳定版）
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

    input{
        width:90%;
        padding:10px;
        margin:5px;
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

    button{
        margin:3px;
        padding:6px;
        font-size:12px;
        background:#00c853;
        border:0;
        color:white;
    }

    .board{
        margin-top:10px;
        color:#00ffcc;
        font-size:16px;
    }

    .me{
        color:#ffd700;
        font-size:18px;
        margin-top:10px;
    }

    </style>
    </head>

    <body>

    <h2>🧠 9人德州交互牌桌（稳定版）</h2>

    <!-- 🟡 永远存在：你的手牌 -->
    <input id="hand" placeholder="我的手牌（如 A♠ K♠）">
    <button onclick="setHand()">设置我的手牌</button>

    <!-- 🟡 永远存在：公共牌 -->
    <input id="board" placeholder="公共牌（如 Q♥ J♦ 10♣）">
    <button onclick="setBoard()">设置公共牌</button>

    <div class="me" id="me">我的手牌：未设置</div>
    <div class="board" id="boardView">公共牌：未设置</div>

    <div class="grid" id="table"></div>

    <script>

    function render(d){

        document.getElementById("boardView").innerText =
        "公共牌：" + d.board;

        document.getElementById("me").innerText =
        "我的手牌：" + d.my_hand;

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

    function setHand(){

        let h = document.getElementById("hand").value;

        fetch(`/set_hand?hand=${h}`)
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function setBoard(){

        let b = document.getElementById("board").value;

        fetch(`/set_board?board=${b}`)
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function act(id,act){

        fetch(`/action?id=${id}&act=${act}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function refresh(){

        fetch(`/action?id=0&act=none`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

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
