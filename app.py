from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB","BB"]

# =========================
# 🧠 初始化牌桌
# =========================
TABLE = [
    {
        "id": i,
        "pos": POSITIONS[i],
        "status": "active",
        "hand": "",
        "note": ""
    }
    for i in range(9)
]

BOARD = ""

# =========================
# 🧠 设置手牌（用户输入）
# =========================
@app.route("/set_hand")
def set_hand():

    pid = int(request.args.get("id"))
    hand = request.args.get("hand","")

    TABLE[pid]["hand"] = hand

    return jsonify(TABLE)

# =========================
# 🧠 设置公共牌
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
        TABLE[pid]["note"] = "弃牌"

    elif act == "call":
        TABLE[pid]["status"] = "active"
        TABLE[pid]["note"] = "跟注"

    elif act == "raise":
        TABLE[pid]["status"] = "active"
        TABLE[pid]["note"] = "加注"

    return jsonify({
        "table": TABLE,
        "board": BOARD
    })

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
        font-size:14px;
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

    .foldbtn{background:#ff4444;}

    .board{
        margin-top:10px;
        color:#00ffcc;
        font-size:16px;
    }

    </style>
    </head>

    <body>

    <h2>🧠 9人德州交互牌桌（手动版）</h2>

    <h3>设置手牌</h3>

    <input id="hand0" placeholder="UTG 手牌">
    <button onclick="setHand(0)">设置UTG</button>

    <input id="hand1" placeholder="UTG+1 手牌">
    <button onclick="setHand(1)">设置UTG+1</button>

    <hr>

    <h3>公共牌</h3>
    <input id="board" placeholder="例如：A♠ K♥ Q♦">
    <button onclick="setBoard()">设置公共牌</button>

    <div class="board" id="boardView">公共牌：空</div>

    <div class="grid" id="table"></div>

    <script>

    function render(d){

        document.getElementById("boardView").innerText =
        "公共牌: " + d.board;

        let html = "";

        d.table.forEach(p=>{

            html += `
            <div class="box ${p.status=='fold'?'fold':''}">
                <b>${p.pos}</b><br>
                ${p.hand || "空"}<br>
                状态: ${p.status}<br>
                ${p.note}<br>

                <button onclick="act(${p.id},'fold')">弃牌</button>
                <button onclick="act(${p.id},'call')">跟注</button>
                <button onclick="act(${p.id},'raise')">加注</button>
            </div>
            `;
        });

        document.getElementById("table").innerHTML = html;
    }

    function setHand(id){

        let val = document.getElementById("hand"+id).value;

        fetch(`/set_hand?id=${id}&hand=${val}`)
        .then(r=>r.json())
        .then(d=>render({table:d,board:""}));
    }

    function setBoard(){

        let val = document.getElementById("board").value;

        fetch(`/set_board?board=${val}`)
        .then(r=>r.json())
        .then(d=>{

            fetch("/action?id=0&act=none")
            .then(r=>r.json())
            .then(x=>render(x));

        });
    }

    function act(id,act){

        fetch(`/action?id=${id}&act=${act}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    </script>

    </body>
    </html>
    """

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
