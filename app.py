from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# 🃏 解析牌（带花色）
# =========================
def parse(cards):
    return [c.strip().upper() for c in cards.split() if c.strip()]

# =========================
# 🧠 手牌强度（含花色思维）
# =========================
def hand_strength(hand, board):
    h = parse(hand)
    b = parse(board)

    all_cards = h + b

    base = 0.4

    # 高牌
    if any(c[0] == "A" for c in h):
        base += 0.1

    if "A" in hand and "K" in hand:
        base += 0.2

    # 对子
    if len(set([c[0] for c in h])) < len(h):
        base += 0.2

    # 公共牌增强
    if len(b) >= 3:
        base += 0.1

    return min(0.95, base)

# =========================
# 🧠 根据下注行为推 range（核心）
# =========================
def estimate_range(action, street, board_texture):

    if action == "raise":

        if "A" in board_texture:
            return "强牌范围（顶对+ / AK / AA）"
        else:
            return "宽加注范围（诈唬 + 强牌混合）"

    if action == "call":
        return "中等范围（对子 / 听牌 / 弱顶对）"

    if action == "fold":
        return "弱范围（空气牌 / 无连接）"

    return "未知范围"

# =========================
# 🧠 GTO + exploit决策
# =========================
def decision(strength, opp_action):

    if opp_action == "raise":
        if strength > 0.7:
            return "跟注（抓范围）"
        return "弃牌"

    if opp_action == "call":
        if strength > 0.6:
            return "价值加注"
        return "过牌"

    return "过牌"

# =========================
# 🧠 AI核心（真正局面版）
# =========================
def ai(hand, board, opp_action):

    strength = hand_strength(hand, board)

    board_cards = parse(board)

    range_read = estimate_range(
        opp_action,
        "flop",
        "".join(board_cards)
    )

    action = decision(strength, opp_action)

    return {
        "手牌": hand,
        "公共牌": board,
        "手牌强度": round(strength, 2),
        "对手动作": opp_action,
        "推测对手范围": range_read,
        "建议动作": action
    }

# =========================
# 🌐 API
# =========================
@app.route("/ai")
def api():

    hand = request.args.get("hand","A♠ K♠")
    board = request.args.get("board","Q♥ J♦ 10♣")
    opp_action = request.args.get("action","raise")

    return jsonify(ai(hand, board, opp_action))

# =========================
# 🌐 UI（重点：真实牌桌信息）
# =========================
@app.route("/")
def home():
    return """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{background:#111;color:#fff;font-family:Arial;text-align:center;padding:20px}
    input{width:90%;padding:12px;margin:8px}
    button{padding:12px;background:#00c853;border:0;color:#fff}
    .r{white-space:pre-line;margin-top:20px}
    </style>
    </head>

    <body>

    <h2>🧠 德州局面分析AI（范围推理版）</h2>

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
            "强度: "+d["手牌强度"]+"\n"+
            "对手动作: "+d["对手动作"]+"\n"+
            "推测范围: "+d["推测对手范围"]+"\n"+
            "建议: "+d["建议动作"];
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
