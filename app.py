from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS = ["UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB","BB"]

# =========================
# 🧠 初始化9人桌
# =========================
def create_table():
    return [
        {
            "id": i,
            "pos": POSITIONS[i],
            "status": "active",
            "hand": "A♠ K♠" if i == 0 else "??",
        }
        for i in range(9)
    ]

# 全局桌面状态（模拟）
TABLE = create_table()

# =========================
# 🧠 操作玩家状态
# =========================
def update_player(pid, action):

    player = TABLE[int(pid)]

    if action == "fold":
        player["status"] = "fold"

    elif action == "call":
        player["status"] = "active"

    elif action == "raise":
        player["status"] = "active"

    return TABLE

# =========================
# 🌐 API：操作
# =========================
@app.route("/action")
def action():

    pid = request.args.get("id")
    act = request.args.get("act")

    update_player(pid, act)

    return jsonify(TABLE)

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

    .fold{
        color:red;
    }

    button{
        margin:3px;
        padding:6px;
        font-size:12px;
        background:#00c853;
        border:0;
        color:white;
    }

    .foldbtn{background:#ff4444;}

    </style>
    </head>

    <body>

    <h2>🧠 9人交互德州牌桌</h2>

    <div class="grid" id="table"></div>

    <script>

    function load(){

        fetch('/action?id=0&act=none')
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function act(id, action){

        fetch(`/action?id=${id}&act=${action}`)
        .then(r=>r.json())
        .then(d=>render(d));
    }

    function render(data){

        let html = "";

        data.forEach(p=>{

            html += `
            <div class="box ${p.status=='fold'?'fold':''}">
                <b>${p.pos}</b><br>
                ${p.hand}<br>
                状态: ${p.status}<br>

                <button onclick="act(${p.id},'fold')" class="foldbtn">弃牌</button>
                <button onclick="act(${p.id},'call')">跟注</button>
                <button onclick="act(${p.id},'raise')">加注</button>
            </div>
            `;
        });

        document.getElementById("table").innerHTML = html;
    }

    load();

    </script>

    </body>
    </html>
    """

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
