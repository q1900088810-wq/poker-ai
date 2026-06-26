from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

# =========================
# 🧠 全局状态
# =========================
SEATS = 9
TABLE = []
BOARD = ["","","","",""]

# =========================
# 🧠 创建桌子（按人数）
# =========================
def create_table(n):
    return [
        {
            "id": i,
            "pos": POSITIONS[i],
            "status": "active",
            "hand": ""
        }
        for i in range(n)
    ]

TABLE = create_table(SEATS)

# =========================
# 🔄 重置开局
# =========================
@app.route("/reset")
def reset():

    global TABLE, BOARD

    TABLE = create_table(SEATS)
    BOARD = ["","","","",""]

    return jsonify({"ok": True})

# =========================
# 👥 设置人数（2-9）
# =========================
@app.route("/set_seats")
def set_seats():

    global SEATS, TABLE

    SEATS = int(request.args.get("n",9))
    SEATS = max(2, min(9, SEATS))

    TABLE = create_table(SEATS)

    return jsonify({"seats": SEATS})

# =========================
# 🌍 设置公共牌（5张）
# =========================
@app.route("/set_board")
def set_board():

    global BOARD

    cards = request.args.get("board","").split()

    BOARD = (cards + ["","","","",""])[:5]

    return jsonify({"board": BOARD})

# =========================
# 🎯 玩家操作
# =========================
@app.route("/action")
def action():

    pid = int(request.args.get("id"))
    act = request.args.get("act")

    if pid < len(TABLE):

        if act == "fold":
            TABLE[pid]["status"] = "fold"

        elif act == "call":
            TABLE[pid]["status"] = "active"

        elif act == "raise":
            TABLE[pid]["status"] = "active"

    return jsonify({
        "table": TABLE,
        "board": BOARD,
        "seats": SEATS
    })

# =========================
# 🌐 UI（干净版）
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

    select,input,button{
        width:90%;
        padding:10px;
        margin:5px;
        font-size:14px;
    }

    .grid{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:10px;
        margin-top:10px;
    }

    .box{
        border:1px solid #444;
        padding:10px;
        border-radius:10px;
    }

    .fold{color:red}

    .board{
        color:#00ffcc;
        margin:10px;
        font-size:16px;
    }

    .btn-red{background:#ff4444;color:white;border:0}
    .btn-blue{background:#2196f3;color:white;border:0}
    .btn-green{background:#00c853;color:white;border:0}

    </style>
    </head>

    <body>

    <h2>🧠 德州牌桌（干净重构版）</h2>

    <!-- 👥 人数 -->
    <input id="seats" type="number" min="2" max="9" value="9">
    <button class="btn-green" onclick="setSeats()">设置人数</button>

    <!-- 🔄 重置 -->
    <button class="btn-red" onclick="reset()">重置开局</button>

    <!-- 🌍 公共牌 -->
    <h3>公共牌（5张）</h3>

    <input id="b1">
    <input id="b2">
    <input id="b3">
    <input id="b4">
    <input id="b5">

    <button class="btn-blue" onclick="setBoard()">设置公共牌</button>

    <div class="board" id="board"></div>

    <!-- 🟣 牌桌 -->
    <div class="grid" id="table"></div>

    <script>

    function render(d){

        document.getElementById("board").innerText =
        "公共牌: " + d.board.join(" ");

        let html="";

        d.table.forEach(p=>{

            html+=`
            <div class="box ${p.status=='fold'?'fold':''}">
                <b>${p.pos}</b><br>
                ${p.hand||"空"}<br>
                状态:${p.status}<br>

                <button onclick="act(${p.id},'fold')">弃牌</button>
                <button onclick="act(${p.id},'call')">跟注</button>
                <button onclick="act(${p.id},'raise')">加注</button>
            </div>`;
        });

        document.getElementById("table").innerHTML=html;
    }

    function setSeats(){

        let n=document.getElementById("seats").value;

        fetch(`/set_seats?n=${n}`)
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function reset(){

        fetch("/reset")
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function setBoard(){

        let b=
        document.getElementById("b1").value+" "+
        document.getElementById("b2").value+" "+
        document.getElementById("b3").value+" "+
        document.getElementById("b4").value+" "+
        document.getElementById("b5").value;

        fetch(`/set_board?board=${b}`)
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function act(id,a){

        fetch(`/action?id=${id}&act=${a}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function refresh(){

        fetch("/action?id=0&act=none")
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
if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
