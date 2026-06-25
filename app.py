from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 🧠 对手模型（Level 9核心）
# =========================
class Opponent:
    def __init__(self):
        self.aggression = 0.7
        self.bluff_rate = 0.3
        self.fold_rate = 0.6

def update_opponent(opponent, action):
    if action == "RAISE":
        opponent.aggression += 0.05
    if action == "FOLD":
        opponent.fold_rate += 0.05

# =========================
# 🎯 GTO基础策略
# =========================
def gto(ev_call, ev_raise):
    if ev_raise > ev_call:
        return "RAISE"
    elif ev_call > 0:
        return "CALL"
    return "FOLD"

# =========================
# 🔍 剥削信号检测
# =========================
def detect_exploit(opponent):
    signals = []

    if opponent.fold_rate > 0.65:
        signals.append("EXPLOIT_FOLD_HEAVY")

    if opponent.bluff_rate > 0.35:
        signals.append("CALL_MORE
