from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

RANKS = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]
SUITS = ["♠","♥","♦","♣"]

# =========================
# 🧠 多桌系统
# =========================
TABLES = {}

# =========================
# 🧠 UI状态（关键补回）
# =========================
MY_HAND = ""
BOARD = ["","","","",""]

# =========================
# 🧠 创建桌子
# =========================
def create_table():

    return {
        "players": [
            {
                "id": i,
                "pos": POSITIONS[i],
                "status": "active",
                "hand": ""
            }
            for i in range(9)
        ]
    }

# =========================
# 🧠 初始化桌子
# =========================
@app.route("/init_tables")
def init_tables():

    n = int(request.args.get("n",2))

    TABLES.clear()

    for i in range(n):
        TABLES[i] = create_table()

    return jsonify({"tables": len(TABLES)})

# =========================
# 🧠 设置手牌（重新补回UI）
# =========================
@app.route("/set_hand")
def set_hand():

    global MY_HAND

    MY_HAND = request.args.get("hand","")

    return jsonify({"hand": MY_HAND})

# =========================
# 🧠 设置公共牌（重新补回UI）
# =========================
@app.route("/set_board")
def set_board():

    global BOARD

    cards = request.args.get("board","").split()

    BOARD = (cards + ["","","","",""])[:5]

    return jsonify({"board": BOARD})

# =========================
# 🧠 操作某桌
# =========================
@app.route("/action")
def action():

    tid = int(request.args.get("table"))
    pid = int(request.args.get("id"))
    act = request.args.get("act")

    table = TABLES.get(tid)

    if table:

        p = table["players"][pid]

        if act == "fold":
            p["status"] = "fold"

        elif act == "call":
            p["status"] = "active"

        elif act == "raise":
            p["status"] = "active"

    return jsonify({
        "tables": TABLES,
        "my_hand": MY_HAND,
        "board": BOARD
    })

# =========================
# 🌐 UI（最终融合版）
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
    }

    .table{
        border:1px solid #444;
        margin:10px;
        padding:10px;
        border-radius:10px;
    }

    .grid{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:10px;
    }

    .box{
        border:1px solid #333;
        padding:6px;
        font-size:12px;
    }

    .board{
        color:#00ffcc;
        margin:10px;
    }

    .me{
        color:#ffd700;
        margin:10px;
    }

    </style>
    </head>

    <body>

    <h2>🧠 德州系统（UI+多桌完整修复版）</h2>

    <!-- 🟡 人数 -->
    <input id="n" type="number" value="2" min="1" max="10">
    <button onclick="init()">创建桌子</button>

    <!-- 🎴 手牌选择 -->
    <h3>我的手牌</h3>
    <select id="h1"></select>
    <select id="h2"></select>
    <button onclick="setHand()">设置手牌</button>

    <!-- 🌍 公共牌 -->
    <h3>公共牌</h3>
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

    function init(){

        let n=document.getElementById("n").value;

        fetch("/init_tables?n="+n)
        .then(r=>r.json())
        .then(()=>load());
    }

    function act(tid,pid,a){

        fetch(`/action?table=${tid}&id=${pid}&act=${a}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function render(d){

        document.getElementById("me").innerText =
        "手牌："+d.my_hand;

        document.getElementById("board").innerText =
        "公共牌："+d.board.join(" ");

        let html="";

        Object.keys(d.tables).forEach(tid=>{

            let t=d.tables[tid];

            html+=`<div class="table">
            <h3>桌子 ${tid}</h3>
            <div class="grid">`;

            t.players.forEach(p=>{

                html+=`
                <div class="box">
                    <b>${p.pos}</b><br>
                    ${p.hand||"空"}<br>
                    ${p.status}<br>

                    <button onclick="act(${tid},${p.id},'fold')">弃牌</button>
                    <button onclick="act(${tid},${p.id},'call')">跟注</button>
                    <button onclick="act(${tid},${p.id},'raise')">加注</button>
                </div>`;
            });

            html+=`</div></div>`;
        });

        document.getElementById("root").innerHTML=html;
    }

    function load(){

        fetch("/action?table=0&id=0&act=none")
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
