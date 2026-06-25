from flask import Flask, request, jsonify
import random

app = Flask(__name__)

POSITIONS = ["BTN","SB","BB","UTG","UTG+1","MP","MP+1","CO","HJ"]

ACTIONS = ["FOLD", "CALL", "RAISE"]

# =========================
# 🧠 9人桌初始化
# =========================
def create_table():
    table = []
    for i in range(9):
        table.append({
            "seat": i,
            "position": POSITIONS[i],
            "active": True,
            "aggression": random.uniform(0.3, 0.9),
            "bluff": random.uniform(0.1, 0.5)
        })
    return table

# =========================
# 🧠 公共牌解析
# =========================
def parse_cards(text):
    return [c.upper() for c in text.split() if c.strip()]

# =========================
# 🧠 手牌强度（简化）
# =========================
def strength(hand, board):
    cards = parse_cards(hand) + parse_cards(board)

    if len(cards) == 0:
        return 0.3

    score = 0.4

    ranks = "23456789TJQKA"

    for c in cards:
        if c[0] in "AK":
            score += 0.05

    if len(board.split()) >= 3:
        score += 0.1  # flop bonus

    if len(board.split()) >= 4:
        score += 0.05

    return min(0.95, score)

# =========================
# 🧠 9人动态影响
# =========================
def table_pressure(table):
    active = [p for p in table if p["active"]]

    agg = sum(p["aggression"] for p in active) / len(active)

    bluff = sum(p["bluff"] for p in active) / len(active)

    return agg, bluff, len(active)

# =========================
# 🎯 EV模型（动态）
# =========================
def ev_calc(strength, agg, bluff, players):
    win = strength + bluff*0.2 - agg*0.15 - (players-2)*0.02

    win = max(0.05, min(0.95, win))

    return win*100, win*140

# =========================
# 🎯 动态GTO
# =========================
def gto(ev1, ev2):
    if ev2 > ev1:
        return "RAISE"
    if ev1 > 45:
        return "CALL"
    return "FOLD"

# =========================
# 🔍 动态exploit
# =========================
def exploit(agg, bluff):
    s = []

    if agg > 0.65:
        s.append("对手整体激进")

    if bluff > 0.35:
        s.append("桌面诈唬偏高")

    return s

# =========================
# 🧠 AI核心（9人桌动态版）
# =========================
def ai_engine(hand, board):
    table = create_table()

    agg, bluff, players = table_pressure(table)

    s = strength(hand, board)

    ev1, ev2 = ev_calc(s, agg, bluff, players)

    base = gto(ev1, ev2)

    signals = exploit(agg, bluff)

    # 🟣 动态策略修正（关键）
    if "桌面诈唬偏高" in signals and base == "CALL":
        final = "CALL（抓诈唬）"
    elif "对手整体激进" in signals and base == "RAISE":
        final = "SLOW PLAY"
    else:
        final = {
            "RAISE":"加注",
            "CALL":"跟注",
            "FOLD":"弃牌"
        }[base]

    return {
        "桌面人数": players,
        "手牌强度": round(s,2),
        "桌面激进度": round(agg,2),
        "桌面诈唬率": round(bluff,2),
        "EV跟注": round(ev1,2),
        "EV加注": round(ev2,2),
        "GTO": base,
        "最终决策": final,
        "状态": "动态9人桌模型"
    }

# =========================
# 🌐 UI（手机）
# =========================
@app.route("/")
def home():
    return """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{background:#111;color:#fff;text-align:center;font-family:Arial;padding:20px}
    input{width:90%;padding:12px;margin:8px;font-size:16px}
    button{padding:12px 20px;background:#00c853;color:#fff;border:0}
    .r{margin-top:20px;white-space:pre-line}
    </style>
    </head>

    <body>
    <h2>🧠 9人桌动态德州AI</h2>

    <input id="hand" placeholder="手牌（A K / AA / QQ）">
    <input id="board" placeholder="公共牌（Q J 10）">

    <button onclick="run()">分析</button>

    <div class="r" id="res"></div>

    <script>
    function run(){
        let h=document.getElementById("hand").value;
        let b=document.getElementById("board").value;

        fetch(`/ai?hand=${h}&board=${b}`)
        .then(r=>r.json())
        .then(d=>{
            document.getElementById("res").innerText =
            "人数: "+d["桌面人数"]+"\n"+
            "强度: "+d["手牌强度"]+"\n"+
            "EV跟注: "+d["EV跟注"]+"\n"+
            "EV加注: "+d["EV加注"]+"\n"+
            "GTO: "+d["GTO"]+"\n"+
            "最终: "+d["最终决策"]+"\n"+
            "状态: "+d["状态"];
        })
    }
    </script>

    </body>
    </html>
    """

# =========================
# 🌐 API
# =========================
@app.route("/ai")
def api():
    hand = request.args.get("hand","A K")
    board = request.args.get("board","")

    return jsonify(ai_engine(hand, board))

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
