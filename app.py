from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["YOU","UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB"]

# =========================
# 🧠 多桌系统
# =========================
TABLES = {}

# =========================
# 🧠 创建单桌
# =========================
def create_table(seats):

    return {
        "seats": seats,
        "board": ["","","","",""],
        "players": [
            {
                "id": i,
                "pos": POSITIONS[i],
                "status": "active",
                "hand": ""
            }
            for i in range(seats)
        ]
    }

# =========================
# 🧠 初始化 N 张桌子（关键）
# =========================
@app.route("/init_tables")
def init_tables():

    n = int(request.args.get("n",2))

    TABLES.clear()

    for i in range(n):
        TABLES[i] = create_table(9)  # 每桌默认9人

    return jsonify({
        "tables": len(TABLES)
    })

# =========================
# 🧠 获取所有桌子
# =========================
@app.route("/get_tables")
def get_tables():

    return jsonify(TABLES)

# =========================
# 🧠 操作某一桌
# =========================
@app.route("/action")
def action():

    tid = int(request.args.get("table"))
    pid = int(request.args.get("id"))
    act = request.args.get("act")

    table = TABLES.get(tid)

    if not table:
        return jsonify({"error":"no table"})

    player = table["players"][pid]

    if act == "fold":
        player["status"] = "fold"

    elif act == "call":
        player["status"] = "active"

    elif act == "raise":
        player["status"] = "active"

    return jsonify(table)

# =========================
# 🌐 UI（多桌）
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

    input,button{
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
        padding:5px;
        font-size:12px;
    }

    </style>
    </head>

    <body>

    <h2>🧠 多桌德州系统</h2>

    <!-- 🟣 创建桌子数量 -->
    <input id="n" type="number" value="2" min="1" max="10">
    <button onclick="init()">创建桌子</button>

    <div id="root"></div>

    <script>

    function init(){

        let n=document.getElementById("n").value;

        fetch(`/init_tables?n=${n}`)
        .then(r=>r.json())
        .then(()=>load());
    }

    function load(){

        fetch("/get_tables")
        .then(r=>r.json())
        .then(data=>render(data));
    }

    function act(tid,pid,act){

        fetch(`/action?table=${tid}&id=${pid}&act=${act}`)
        .then(r=>r.json())
        .then(()=>load());
    }

    function render(data){

        let html="";

        Object.keys(data).forEach(tid=>{

            let t=data[tid];

            html+=`<div class='table'>
                <h3>🟣 桌子 ${tid}（${t.seats}人）</h3>

                <div class='grid'>`;

            t.players.forEach(p=>{

                html+=`
                <div class='box'>
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
