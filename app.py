from flask import Flask, request, jsonify
import random

app = Flask(__name__)

POSITIONS = ["BTN","SB","BB","UTG","UTG+1","MP","MP+1","CO","HJ"]

# =========================
# 🧠 初始化牌桌
# =========================
def create_table():
    table = []

    for i in range(9):
        table.append({
            "seat": i,
            "pos": POSITIONS[i],
            "stack": 1000,
            "status": "active",
            "hand": random.choice(["A K","Q Q","J J","9 9","7 2"]),
            "bet": 0
        })

    return table

# =========================
# 🧠 简单手牌强度
# =========================
def strength(hand):
    if "A" in hand and "K" in hand:
        return 0.85
    if hand[0] == hand[2]:
        return 0.75
    return 0.4

# =========================
# 🎯 决策系统
# =========================
def decide(strength, to_call):
    if strength > 0.8:
        return "raise"
    if strength > 0.5 and to_call <= 50:
        return "call"
    return "fold"

# =========================
# 🧠 一轮下注逻辑
# =========================
def betting_round(table, pot, current_bet):

    for p in table:

        if p["status"] != "active":
            continue

        s = strength(p["hand"])

        to_call = current_bet - p["bet"]

        action = decide(s, to_call)

        if action == "fold":
            p["status"] = "fold"

        elif action == "call":
            pay = min(to_call, p["stack"])
            p["stack"] -= pay
            p["bet"] += pay
            pot += pay

        elif action == "raise":
            raise_amt = 100
            total = to_call + raise_amt

            pay = min(total, p["stack"])
            p["stack"] -= pay
            p["bet"] += pay
            pot += pay

            current_bet = p["bet"]

    return table, pot, current_bet

# =========================
# 🧠 游戏一手（preflop）
# =========================
def play_hand():

    table = create_table()

    pot = 0
    current_bet = 50  # SB/BB简化

    # 小盲大盲强制下注
    table[1]["stack"] -= 25
    table[1]["bet"] = 25
    table[2]["stack"] -= 50
    table[2]["bet"] = 50

    pot += 75
    current_bet = 50

    # 一轮下注
    table, pot, current_bet = betting_round(table, pot, current_bet)

    return {
        "table": table,
        "pot": pot,
        "current_bet": current_bet
    }

# =========================
# 🌐 API
# =========================
@app.route("/ai")
def ai():
    return jsonify(play_hand())

# =========================
# 🌐 UI（真实牌桌）
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

    <h2>🧠 9人桌下注系统（筹码版）</h2>

    <button onclick="run()">下一手</button>

    <div id="pot"></div>
    <div class="table" id="table"></div>

    <script>

    function run(){
        fetch('/ai')
        .then(r=>r.json())
        .then(d=>{

            document.getElementById("pot").innerHTML =
            "<h3>底池: " + d.pot + "</h3>";

            let html = "";

            d.table.forEach(p=>{
                html += `
                <div class="player ${p.status}">
                    <b>${p.pos}</b><br>
                    ${p.hand}<br>
                    筹码: ${p.stack}<br>
                    状态: ${p.status}<br>
                    已下注: ${p.bet}
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
