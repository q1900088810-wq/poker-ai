from flask import Flask, request, jsonify

app = Flask(__name__)

# ===== AI逻辑 =====
def ai(ev_call, ev_raise):
    if ev_raise > ev_call:
        return "RAISE"
    elif ev_call > 0:
        return "CALL"
    else:
        return "FOLD"

@app.route("/")
def home():
    return """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>德州AI</title>
        <style>
            body { font-family: Arial; text-align:center; padding:20px; }
            input { width:80%; padding:10px; margin:10px; font-size:18px; }
            button { padding:10px 20px; font-size:18px; }
            .res { margin-top:20px; font-size:22px; font-weight:bold; }
        </style>
    </head>

    <body>
        <h2>🧠 德州AI助手</h2>

        <input id="call" placeholder="EV Call">
        <input id="raise" placeholder="EV Raise">

        <br>
        <button onclick="runAI()">分析</button>

        <div class="res" id="res"></div>

        <script>
            function runAI(){
                let call = document.getElementById('call').value;
                let raise = document.getElementById('raise').value;

                fetch(`/ai?ev_call=${call}&ev_raise=${raise}`)
                .then(r=>r.json())
                .then(d=>{
                    document.getElementById('res').innerText =
                    "👉 决策: " + d.action;
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
