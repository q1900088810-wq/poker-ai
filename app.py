from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "🧠 Poker AI Running"

@app.route("/ai")
def ai():
    ev_call = float(request.args.get("ev_call",0))
    ev_raise = float(request.args.get("ev_raise",0))

    if ev_raise > ev_call:
        return jsonify({"action":"RAISE"})
    elif ev_call > 0:
        return jsonify({"action":"CALL"})
    else:
        return jsonify({"action":"FOLD"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
