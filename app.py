from flask import Flask, request, jsonify
import random

app = Flask(__name__)

POSITIONS = ["BTN","SB","BB","UTG","UTG+1","MP","MP+1","CO","HJ"]

# =========================
# 🧠 初始化9人桌
# =========================
def create_table():
    table = []

    for i in range(9):
        table.append({
            "seat": i,
            "pos": POSITIONS[i],
            "status": "active",   # active / fold / allin
            "hand": random.choice(["A K","Q Q","J T","9 9","7 2"]),
            "action": None
        })

    return table

# =========================
# 🧠 简单AI决策
# =========================
def decide(hand):
    if "A" in hand and "K" in hand:
        return "raise"
    if hand[0] == hand[2]:
        return "call"
    return "fold"

# =========================
# 🧠 模拟一轮行动
# =========================
def run_round(table):
    for p in table:
        if p["status"] == "active":
            action = decide(p["hand"])

            if action == "fold":
                p["status"] = "fold"
            elif action == "raise":
                p["status"] = "active"
            else:
                p["status"] = "active"

            p["action"] = action

    return table

# =========================
# 🧠 状态统计
# =========================
def summary(table):
    active = len([p for p in table if p["status"] == "active"])
    fold = len([p for p in table if p["status"] == "fold"])

    return {
        "active": active,
        "folded": fold
    }

# =========================
# 🌐 API
# =========================
@app.route("/ai")
def ai():
    table = create_table()
    table = run_round(table)

    return jsonify({
        "table": table,
        "summary": summary(table)
    })

# =========================
# 🌐 UI（9人桌可视化）
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
    }

    .table{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:10px;
        margin-top:20px;
    }

    .player{
        padding:10px;
        border:1px solid #444;
        border-radius:10px;
    }

    .active{color:#00ff7f}
    .fold{color:#ff4444}

    button{
        padding:12px;
        margin-top:10px;
        background:#00c853;
        border:0;
        color:white;
    }

    </style>
    </head>

    <body>

    <h2>🧠 9人桌动态扑克UI</h2>

    <button onclick="run()">下一手</button>

    <div class="table" id="table"></div>

    <script>

    function run(){
        fetch('/ai')
        .then(r=>r.json())
        .then(d=>{

            let html = "";

            d.table.forEach(p=>{
                html += `
                <div class="player ${p.status}">
                    <b>${p.pos}</b><br>
                    ${p.hand}<br>
                    状态: ${p.status}<br>
                    动作: ${p.action}
                </div>
                `;
            });

            document.getElementById("table").innerHTML = html;
        });
    }

    run();

    </script>

    </body>
    </html>
    """

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
