from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# =========================
# 🧠 对手模型（2-9人桌通用）
# =========================
class Opponent:
    def __init__(self, players=6):
        self.players = players
        self.aggression = random.uniform(0.4, 0.9)
        self.bluff_rate = random.uniform(0.1, 0.5)
        self.fold_rate = random.uniform(0.3, 0.8)

# =========================
# 🃏 手牌强度评分（核心升级）
# =========================
def hand_strength(hand):
    hand = hand.upper()

    if "AA" in hand:
        return 0.95
    if "KK" in hand:
        return 0.9
    if "QQ" in hand:
        return 0.85
    if "AK" in hand:
        return 0.8
    if "AQ" in hand:
        return 0.75
    if "JJ" in hand:
        return 0.7
    if "TT" in hand:
        return 0.65

    if "A" in hand:
        return 0.55

    return 0.35

# =========================
# 🎯 EV简化模型
# =========================
def calc_ev(strength, opp):
    win_rate = strength

    win_rate += opp.bluff_rate * 0.2
    win_rate -= opp.aggression * 0.15
    win_rate = max(0.05, min(0.95, win_rate))

    ev_call = win_rate * 100
    ev_raise = win_rate * 130 - (1 - win_rate) * 80

    return ev_call, ev_raise, win_rate

# =========================
# 🎯 GTO基础决策
# =========================
def gto(ev_call, ev_raise):
    if ev_raise > ev_call:
        return "RAISE"
    elif ev_call > 40:
        return "CALL"
    return "FOLD"

# =========================
# 🔍 exploit检测
# =========================
def detect_exploit(opp):
    signals = []

    if opp.fold_rate > 0.65:
        signals.append("对手容易弃牌")

    if opp.bluff_rate > 0.35:
        signals.append("对手喜欢诈唬")

    if opp.aggression > 0.75:
        signals.append("对手很激进")

    return signals

# =========================
# ⚡ exploit策略
# =========================
def exploit_strategy(base, signals):
    if "对手容易弃牌" in signals:
        return "加注（轻压制）"
    if "对手喜欢诈唬" in signals:
        return "跟注（抓诈唬）"
    if "对手很激进" in signals:
        return "慢打强牌"
    return base

# =========================
# 🧠 主AI（完整版）
# =========================
def ai_engine(hand, players):
    opp = Opponent(players)

    strength = hand_strength(hand)

    ev_call, ev_raise, win_rate = calc_ev(strength, opp)

    base = gto(ev_call, ev_raise)

    signals = detect_exploit(opp)

    final = exploit_strategy(base, signals)

    return {
        "手牌强度": round(strength, 2),
        "胜率": round(win_rate, 2),
        "GTO决策": base,
        "对手特征": signals,
        "最终建议": final,
        "桌人数": players
    }

# =========================
# 🌐 首页（手机App界面）
# =========================
@app.route("/")
def home():
    return """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>德州AI</title>
        <style>
            body { font-family: Arial; text-align:center; padding:20px; background:#111; color:white; }
            input { width:90%; padding:12px; margin:10px; font-size:18px; }
            button { padding:12px 20px; font-size:18px; background:#00c853; color:white; border:none; }
            .res { margin-top:20px; font-size:20px; white-space:pre-line; }
        </style>
    </head>

    <body>
        <h2>🧠 德州AI（中文版 Level 9）</h2>

        <input id="hand" placeholder="输入手牌（如 A K / AA / QJ）">
        <input id="players" placeholder="人数（2-9人）">

        <br>
        <button onclick="run()">分析</button>

        <div class="res" id="res"></div>

        <script>
            function run(){
                let h = document.getElementById('hand').value;
                let p = document.getElementById('players').value || 6;

                fetch(`/ai?hand=${h}&players=${p}`)
                .then(r=>r.json())
                .then(d=>{
                    document.getElementById('res').innerText =
                    "手牌强度: " + d["手牌强度"] + "\\n" +
                    "胜率: " + d["胜率"] + "\\n" +
                    "GTO: " + d["GTO决策"] + "\\n" +
                    "对手: " + d["对手特征"] + "\\n" +
                    "最终建议: " + d["最终建议"];
                })
            }
        </script>
    </body>
    </html>
    """

# =========================
# 🌐 API接口
# =========================
@app.route("/ai")
def ai():
    hand = request.args.get("hand", "A K")
    players = int(request.args.get("players", 6))

    return jsonify(ai_engine(hand, players))

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
