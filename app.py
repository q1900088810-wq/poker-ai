from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 🧠 9人桌：YOU + 8 AI
# =========================
POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

RANKS = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]
SUITS = ["♠","♥","♦","♣"]

TABLE = [
    {"id": i, "pos": POSITIONS[i], "status": "active", "hand": ""}
    for i in range(9)
]

BOARD = ""
MY_HAND = ""

# =========================
# 🧠 设置手牌（你）
# =========================
@app.route("/set_hand")
def set_hand():
    global MY_HAND
    MY_HAND = request.args.get("hand","")
    return jsonify({"hand": MY_HAND})

# =========================
# 🧠 设置公共牌
# =========================
@app.route("/set_board")
def set_board():
    global BOARD
    BOARD = request.args.get("board","")
    return jsonify({"board": BOARD})

# =========================
# 🧠 玩家动作（包含你）
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
# 🌐 UI（彻底清理版）
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
    }

    .me{
        color:#ffd700;
        margin:10px;
    }

    .btn-fold{background:#ff4444;color:white;border:0}
    .btn-call{background:#2196f3;color:white;border:0}
    .btn-raise{background:#00c853;color:white;border:0}

    </style>
    </head>

    <body>

    <!-- 🧠 手牌选择 -->
    <select id="h1"></select>
    <select id="h2"></select>
    <button onclick="setHand()">设置手牌</button>

    <!-- 🌍 公共牌 -->
    <select id="b1"></select>
    <select id="b2"></select>
    <select id="b3"></select>
    <button onclick="setBoard()">设置公共牌</button>

    <div class="me" id="me"></div>
    <div class="board" id="board"></div>

    <!-- 🟣 9人桌 -->
    <div class="grid" id="table"></div>

    <script>

    let RANKS=["A","K","Q","J","10","9","8","7","6","5","4","3","2"];
    let SUITS=["♠","♥","♦","♣"];

    function build(id){
        let el=document.getElementById(id);

        RANKS.forEach(r=>{
            SUITS.forEach(s=>{
                let o=document.createElement("option");
                o.value=r+s;
                o.innerText=r+s;
                el.appendChild(o);
            });
        });
    }

    function init(){
        build("h1");
        build("h2");
        build("b1");
        build("b2");
        build("b3");
    }

    function setHand(){
        let h=document.getElementById("h1").value+" "+document.getElementById("h2").value;

        fetch("/set_hand?hand="+h)
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function setBoard(){
        let b=document.getElementById("b1").value+" "+document.getElementById("b2").value+" "+document.getElementById("b3").value;

        fetch("/set_board?board="+b)
        .then(r=>r.json())
        .then(()=>refresh());
    }

    function act(id,a){
        fetch(`/action?id=${id}&act=${a}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function render(d){

        document.getElementById("me").innerText =
        "我的手牌："+d.my_hand;

        document.getElementById("board").innerText =
        "公共牌："+d.board;

        let html="";

        d.table.forEach(p=>{

            let buttons="";

            // 🧠 你自己 + AI都可以操作
            buttons += `<button class='btn-fold' onclick="act(${p.id},'fold')">弃牌</button>`;
            buttons += `<button class='btn-call' onclick="act(${p.id},'call')">跟注</button>`;
            buttons += `<button class='btn-raise' onclick="act(${p.id},'raise')">加注</button>`;

            html+=`
            <div class="box ${p.status=='fold'?'fold':''}">
                <b>${p.pos}</b><br>
                ${p.hand||"空"}<br>
                状态:${p.status}<br>
                ${buttons}
            </div>`;
        });

        document.getElementById("table").innerHTML=html;
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
if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
