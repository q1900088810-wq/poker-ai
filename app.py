from flask import Flask, request, jsonify

app = Flask(__name__)

POSITIONS_9MAX = ["UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB","BB"]

# =========================
# 🧠 初始化牌桌
# =========================
def create_table(seats=9):
    table = []

    for i in range(seats):
        table.append({
            "id": i,
            "pos": POSITIONS_9MAX[i],
            "stack": 1000,
            "status": "active",
            "bet": 0
        })

    return table

# =========================
# 🧠 手牌强度（简化）
# =========================
def strength(hand):
    hand = hand.upper()

    if "A" in hand and "K" in hand:
        return 0.85
    if hand[0] == hand[2]:
        return 0.75
    if "A" in hand:
        return 0.6
    return 0.4

# =========================
# 🧠 决策逻辑（核心）
# =========================
def decide(strength, to_call):

    if strength > 0.8:
        return "raise"
    if strength > 0.55 and to_call <= 50:
        return "call"
    return "fold"

# =========================
# 🧠 单个玩家行动
# =========================
def act(player, hand_strength, to_call):

    if player["status"] != "active":
        return player, 0, None

    action = decide(hand_strength, to_call)

    if action == "fold":
        player["status"] = "fold"
        return player, 0, "fold"

    if action == "call":
        pay = min(to_call, player["stack"])
        player["stack"] -= pay
        player["bet"] += pay
        return player, pay, "call"

    if action == "raise":
        raise_amt = 100
        total = to_call + raise_amt
        pay = min(total, player["stack"])
        player["stack"] -= pay
        player["bet"] += pay
        return player, pay, "raise"

# =========================
# 🧠 一轮完整行动（顺序推进）
# =========================
def run_round(table, hand):

    pot = 0
    current_bet = 50

    log = []

    for p in table:

        s = strength(hand)

        to_call = current_bet - p["bet"]

        p, paid, action = act(p, s, to_call)

        pot += paid

        if action == "raise":
            current_bet = p["bet"]

        log.append({
            "位置": p["pos"],
            "动作": action,
            "下注": paid,
            "状态": p["status"]
        })

    return table, pot, current_bet, log

# =========================
# 🧠 AI入口
# =========================
def ai(hand, board, seats):

    table = create_table(seats)

    table, pot, current_bet, log = run_round(table, hand)

    active = len([p for p in table if p["status"] == "active"])
    folded = len([p for p in table if p["status"] == "fold"])

    return {
        "玩家数": seats,
        "公共牌": board,
        "底池": pot,
        "当前下注": current_bet,
        "存活玩家": active,
        "弃牌玩家": folded,
        "行动日志": log,
        "状态": "9人实时位置系统"
    }

# =========================
# 🌐 API
# =========================
@app.route("/ai")
def api():

    hand = request.args.get("hand","A♠ K♠")
    board = request.args.get("board","Q♥ J♦ 10♣")
    seats = int(request.args.get("seats",9))

    return jsonify(ai(hand, board, seats))

# =========================
# 🌐 UI（实时牌桌）
# =========================
@app.route("/")
def home():
    return """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{background:#111;color:#fff;font-family:Arial;text-align:center;padding:20px}
    input{width:90%;padding:12px;margin:6px}
    button{padding:12px;background:#00c853;border:0;color:#fff}
    .log{white-space:pre-line;text-align:left;margin-top:20px}
    </style>
    </head>

    <body>

    <h2>🧠 9人实时位置德州系统</h2>

    <input id="hand" placeholder="手牌（A♠ K♠）">
    <input id="board" placeholder="公共牌">
    <input id="seats" placeholder="人数（2-9）" value="9">

    <button onclick="run()">开始一轮</button>

    <div class="log" id="res"></div>

    <script>

    function run(){
        let h=document.getElementById("hand").value;
        let b=document.getElementById("board").value;
        let s=document.getElementById("seats").value;

        fetch(`/ai?hand=${h}&board=${b}&seats=${s}`)
        .then(r=>r.json())
        .then(d=>{

            let log = "底池: "+d.底池+"\n";
            log += "当前下注: "+d.当前下注+"\n";
            log += "存活: "+d.存活玩家+" / 弃牌: "+d.弃牌玩家+"\n\n";

            log += "行动顺序:\n";

            d.行动日志.forEach(x=>{
                log += x["位置"]+" → "+x["动作"]+" ("+x["下注"]+")\n";
            });

            log += "\n状态: "+d.状态;

            document.getElementById("res").innerText = log;
        })
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
