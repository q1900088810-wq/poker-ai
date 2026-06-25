from flask import Flask, request, jsonify

app = Flask(__name__)

# ================= AI（先基础版，后面升级） =================
def ai(ev_call, ev_raise):
    if ev_raise > ev_call:
        return "RAISE"
    elif ev_call > 0:
        return "CALL"
    return "FOLD"

# ================= 🧠 手机App界面 =================
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
            button { padding:12px 25px; font-size:18px; background:#00c853; color:white; border:none; }
            .res { margin-top:20px; font-size:26px; font-weight:bold; color:#00e676; }
        </style>
    </head>

    <body>
        <h2>🧠 德州AI Level 9</h2>

        <input id="call" placeholder="EV Call">
        <input id="raise" placeholder="EV Raise">

        <br>
        <button onclick="run()">分析</button>

        <div class="res" id="res"></div>

        <script>
            function run(){
                let c = document.getElementById("call").value;
                let r = document.getElementById("raise").value;

                fetch(`/ai?ev_call=${c}&ev_raise=${r}`)
                .then(r=>r.json())
                .then(d=>{
                    document.getElementById("res").innerText =
                    "👉 决策：" + d.action;
                })
            }
        </script>
    </body>
    </html>
    """

@app.route("/ai")
def api():
    ev_call = float(request.args.get("ev_call",0))
    ev_raise = float(request.args.get("ev_raise",0))
    return jsonify({"action": ai(ev_call, ev_raise)})

app.run(host="0.0.0.0", port=10000)
