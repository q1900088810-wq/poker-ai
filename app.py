from flask import Flask, request, jsonify
import random
import numpy as np

app = Flask(__name__)

# =========================
# 🧠 神经网络（极简版）
# =========================
class SimpleNN:
    def __init__(self):
        self.weights = np.random.randn(3, 3) * 0.1

    def forward(self, x):
        return np.dot(x, self.weights)

    def train(self, x, y, lr=0.01):
        pred = self.forward(x)
        grad = (pred - y)
        self.weights -= lr * np.outer(x, grad)

# =========================
# 🧠 CFR记忆库
# =========================
regret_memory = []
strategy_memory = []

regret_net = SimpleNN()
strategy_net = SimpleNN()

ACTIONS = ["FOLD", "CALL", "RAISE"]

# =========================
# 🃏 手牌特征
# =========================
def hand_features(hand):
    hand = hand.upper()

    f1 = 1 if "A" in hand else 0
    f2 = 1 if "K" in hand else 0
    f3 = 1 if hand.count(hand[0]) > 1 else 0

    return np.array([f1, f2, f3])

# =========================
# 🎯 策略输出
# =========================
def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()

# =========================
# 🧠 CFR训练样本生成
# =========================
def generate_cfr_sample(x):
    base = regret_net.forward(x)

    probs = softmax(base)

    return probs

# =========================
# 🧠 self-play训练
# =========================
def train_step(x):
    probs = generate_cfr_sample(x)

    # 假设 reward（简化）
    reward = np.array([
        -0.2,
        0.5,
        1.0
    ])

    target = probs + 0.1 * reward

    regret_net.train(x, target)
    strategy_net.train(x, probs)

    return probs

# =========================
# 🧠 AI决策
# =========================
def ai_engine(hand):
    x = hand_features(hand)

    probs = train_step(x)

    action = ACTIONS[np.argmax(probs)]

    translate = {
        "FOLD": "弃牌",
        "CALL": "跟注",
        "RAISE": "加注"
    }

    return {
        "输入特征": x.tolist(),
        "弃牌概率": round(float(probs[0]), 3),
        "跟注概率": round(float(probs[1]), 3),
        "加注概率": round(float(probs[2]), 3),
        "最终决策": translate[action]
    }

# =========================
# 🌐 UI
# =========================
@app.route("/")
def home():
    return """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Deep CFR AI</title>
        <style>
            body{font-family:Arial;text-align:center;padding:20px;background:#111;color:#fff}
            input{width:90%;padding:12px;margin:8px;font-size:16px}
            button{padding:12px 20px;font-size:18px;background:#00c853;color:#fff;border:0}
            .r{margin-top:20px;white-space:pre-line}
        </style>
    </head>

    <body>
        <h2>🧠 Deep CFR 德州AI</h2>

        <input id="hand" placeholder="手牌（如 AA / AK / QQ）">

        <button onclick="run()">训练 + 决策</button>

        <div class="r" id="res"></div>

        <script>
        function run(){
            let h=document.getElementById('hand').value;

            fetch(`/ai?hand=${h}`)
            .then(r=>r.json())
            .then(d=>{
                document.getElementById('res').innerText =
                "弃牌概率: "+d["弃牌概率"]+"\n"+
                "跟注概率: "+d["跟注概率"]+"\n"+
                "加注概率: "+d["加注概率"]+"\n"+
                "最终决策: "+d["最终决策"];
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
def ai():
    hand = request.args.get("hand","A K")
    return jsonify(ai_engine(hand))

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
