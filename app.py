from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 🃏 手牌强度（真实玩家模型）
# =========================
def hand_strength(hand, board):
    hand = hand.upper()

    base = 0.4

    # 高牌
    if "A" in hand and "K" in hand:
        base = 0.85
    elif "A" in hand:
        base = 0.6
    elif hand[0] == hand[2]:  # pocket pair
        base = 0.7
    elif "Q" in hand or "J" in hand:
        base = 0.5

    # 公共牌影响
    board = board.upper()

    if len(board.split()) >= 3:
        base += 0.05

    if "A" in board:
        base -= 0.05  # 公共A降低相对强度

    return max(0.05, min(0.95, base))

# =========================
# 🧠 对手行为影响（不读牌，只看行为）
# =========================
def opponent_pressure(action):
    if action == "raise":
        return 0.8
    if action == "call":
        return 0.5
    if action == "fold":
        return 0.2
    return 0.5

# =========================
# 🎯 EV模型（核心）
# =========================
def ev_model(strength, pressure):

    winrate = strength - pressure * 0.2
    winrate = max(0.05, min(0.95, winrate))

    ev_call = winrate * 100
    ev_raise = winrate * 140 - (1 - winrate) * 80

    return winrate, ev_call, ev_raise

# =========================
# 🎯 GTO决策
# =========================
def gto(ev_call, ev_raise):
    if ev_raise > ev_call:
        return "RAISE"
    if ev_call > 45:
        return "CALL"
    return "FOLD"

# =========================
# 🧠 exploit修正（行为博弈）
# =========================
def adjust(base, action):

    if action == "raise" and base == "CALL":
        return "CALL（防诈唬）"

    if action == "raise" and base == "FOLD":
        return "FOLD"

    if action == "call" and base == "RAISE":
        return "价值加注"

    return base

# =========================
# 🧠 AI核心（真实玩家版）
# =========================
def ai(hand, board, opp_action):

    strength = hand_strength(hand, board)

    pressure = opponent_pressure(opp_action)

    winrate, ev_call, ev_raise = ev_model(strength, pressure)

    base = gto(ev_call, ev_raise)

    final = adjust(base, opp_action)

    return {
        "手牌": hand,
        "公共牌": board,
        "手牌强度": round(strength,2),
        "胜率": round(winrate,2),
        "EV跟注": round(ev_call,2),
        "EV加注": round(ev_raise,2),
        "对手动作": opp_action,
        "GTO决策": base,
        "最终建议": final
    }

# =========================
# 🌐 API
# =========================
@app.route("/ai")
def api():

    hand = request.args.get("hand","A♠ K♠")
    board = request.args.get("board","Q♥ J♦ 10♣")
    opp_action = request.args.get("action","call")

    return jsonify(ai(hand, board, opp_action))

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
    body{background:#111;color:#fff;font-family:Arial;text-align:center;padding:20px}
    input,select{width:90%;padding:12px;margin:8px}
    button{padding:12px;background:#00c853;border:0;color:#fff}
    .r{white-space:pre-line;margin-top:20px}
    </style>
    </head>

    <body>

    <h2>🧠 德州真实玩家AI</h2>

    <input id="hand" placeholder="手牌（A♠ K♠）">
    <input id="board" placeholder="公共牌（Q♥ J♦ 10♣）">

    <select id="action">
        <option value="raise">对手加注</option>
        <option value="call">对手跟注</option>
        <option value="fold">对手弃牌</option>
    </select>

    <button onclick="run()">分析</button>

    <div class="r" id="res"></div>

    <script>
    function run(){
        let h=document.getElementById("hand").value;
        let b=document.getElementById("board").value;
        let a=document.getElementById("action").value;

        fetch(`/ai?hand=${h}&board=${b}&action=${a}`)
        .then(r=>r.json())
        .then(d=>{
            document.getElementById("res").innerText =
            "手牌: "+d["手牌"]+"\n"+
            "公共牌: "+d["公共牌"]+"\n"+
            "手牌强度: "+d["手牌强度"]+"\n"+
            "胜率: "+d["胜率"]+"\n"+
            "EV跟注: "+d["EV跟注"]+"\n"+
            "EV加注: "+d["EV加注"]+"\n"+
            "对手动作: "+d["对手动作"]+"\n"+
            "GTO: "+d["GTO决策"]+"\n"+
            "最终: "+d["最终建议"];
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
