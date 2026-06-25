from flask import Flask, request, jsonify
import random

app = Flask(__name__)

POSITIONS = ["UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB","BB"]

SUITS = ["♠","♥","♦","♣"]
RANKS = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]

# =========================
# 🧠 固定9人桌
# =========================
def create_table():
    return [
        {
            "pos": POSITIONS[i],
            "status": "active",
            "hand": "??",
            "suit": ""
        } for i in range(9)
    ]

# =========================
# 🧠 初始化公共牌
# =========================
def empty_board():
    return []

# =========================
# 🧠 UI牌生成
# =========================
def random_card():
    return random.choice(RANKS) + random.choice(SUITS)

# =========================
# 🧠 设置手牌（用户控制）
# =========================
def set_player_hand(table, card1, card2):
    table[0]["hand"] = card1
    table[1]["hand"] = card2
    return table

# =========================
# 🌐 API（状态）
# =========================
@app.route("/state")
def state():

    return jsonify({
        "table": create_table(),
        "board": empty_board()
    })

# =========================
# 🌐 UI（完全重做）
# =========================
@app.route("/")
def home():
    return """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>

    body{
        background:#111;
        color:white;
        font-family:Arial;
        text-align:center;
        padding:10px;
    }

    .grid{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:10px;
        margin-top:15px;
    }

    .box{
        border:1px solid #444;
        padding:10px;
        border-radius:10px;
        min-height:60px;
    }

    select,button{
        width:90%;
        padding:10px;
        margin:5px;
    }

    .board{
        margin-top:10px;
        font-size:18px;
        color:#00ffcc;
    }

    .btn{
        background:#00c853;
        color:white;
        border:0;
    }

    </style>
    </head>

    <body>

    <h2>🧠 9人德州UI（手动控制版）</h2>

    <div>

    <h3>选择你的手牌</h3>

    <select id="c1"></select>
    <select id="c2"></select>

    <button class="btn" onclick="setHand()">设置手牌</button>

    </div>

    <div class="board" id="board">公共牌: 空</div>

    <button onclick="flop()">发翻牌</button>
    <button onclick="turn()">发转牌</button>
    <button onclick="river()">发河牌</button>

    <div class="grid" id="table"></div>

    <script>

    let deck = [];

    function initCards(){
        let ranks = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"];
        let suits = ["♠","♥","♦","♣"];

        let select1 = document.getElementById("c1");
        let select2 = document.getElementById("c2");

        ranks.forEach(r=>{
            suits.forEach(s=>{
                let opt1 = document.createElement("option");
                opt1.value = r+s;
                opt1.innerText = r+s;

                let opt2 = opt1.cloneNode(true);

                select1.appendChild(opt1);
                select2.appendChild(opt2);
            });
        });
    }

    function setHand(){
        let c1 = document.getElementById("c1").value;
        let c2 = document.getElementById("c2").value;

        renderTable(c1,c2);
    }

    function renderTable(c1="??",c2="??"){

        let html = "";

        let positions = ["UTG","UTG+1","MP","MP+1","HJ","CO","BTN","SB","BB"];

        positions.forEach((p,i)=>{
            let hand = (i==0)? c1 : (i==1)? c2 : "??";

            html += `
            <div class="box">
                <b>${p}</b><br>
                ${hand}
            </div>
            `;
        });

        document.getElementById("table").innerHTML = html;
    }

    let board = [];

    function updateBoard(){
        document.getElementById("board").innerText =
        "公共牌: " + board.join(" ");
    }

    function flop(){
        board = ["A♠","K♥","7♦"];
        updateBoard();
    }

    function turn(){
        board.push("Q♣");
        updateBoard();
    }

    function river(){
        board.push("10♠");
        updateBoard();
    }

    initCards();
    renderTable();

    </script>

    </body>
    </html>
    """

# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
