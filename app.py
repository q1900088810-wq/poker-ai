from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# =========================
# 🧠 对手模型（Level 9）
# =========================
class Opponent:
    def __init__(self):
        self.aggression = random.uniform(0.4, 0.9)
        self.bluff_rate = random.uniform(0.1, 0.5)
        self.fold_rate = random.uniform(0.3, 0.8)

# =========================
# 🎯 EV计算
# =========================
def calc_ev(ev_call, ev_raise, opp):
    win_prob = 0.5 + (ev_raise - ev_call) * 0.01

    win_prob += opp.bluff_rate * 0.3
    win_prob -= opp.fold_rate * 0.2

    win_prob = max(0.05, min(0.95, win_prob))

    ev_call_score = win_prob * ev_call
    ev_raise_score = win_prob * ev_raise - (1 - win_prob) * ev_raise

    return ev_call_score, ev_raise_score

# =========================
# 🎯 GTO策略
# =========================
def gto(ev_call, ev_raise):
    if ev_raise > ev_call:
        return "RAISE"
    elif ev_call > 0:
        return "CALL"
    return "FOLD"

# =========================
# 🔍 exploit检测
# =========================
def detect_exploit(opp):
    signals = []

    if opp.fold_rate > 0.65:
        signals.append("EXPLOIT_FOLD")

    if opp.bluff_rate > 0.35:
        signals.append("CALL_MORE")

    if opp.aggression > 0.75:
        signals.append("TRAP_MODE")

    return signals

# =========================
# ⚡ 策略偏移
# =========================
def exploit_strategy(base, signals):
    if "EXPLOIT_FOLD" in signals:
        return "RAISE_LIGHT"
    if "CALL_MORE" in signals:
        return "VALUE_HEAVY_CALL"
    if "TRAP_MODE" in signals:
        return "SLOW_PLAY_STRONG"
    return base

# =========================
# 🧠 AI核心
# =========================
def ai_engine(ev_call, ev_raise):
    opp = Opponent()

    ev_c, ev_r = calc_ev(ev_call, ev_raise, opp)

    base = gto(ev_c, ev_r)

    signals = detect_exploit(opp)

    final = exploit_strategy(base, signals)

    return {
        "gto": base,
        "ev_call": round(ev_c, 2),
        "ev_raise": round(ev_r, 2),
        "signals": signals,
        "final": final
    }

# =========================
# 🌐 网页接口
# =========================
@app.route("/")
def home():
    return """
    <h2>🧠 Level 9 德州AI</h2>
    <p>测试接口：</p>
    <p>/ai?ev_call=10&ev_raise=25</p>
    """

@app.route("/ai")
def ai():
    ev_call = float(request.args.get("ev_call", 0))
    ev_raise = float(request.args.get("ev_raise", 0))

    return jsonify(ai_engine(ev_call, ev_raise))

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
