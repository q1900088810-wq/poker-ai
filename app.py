from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
    <!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>

body{
    margin:0;
    background:#0a3d2e;
    font-family:Arial;
    color:white;
}

/* 🟢 桌面 */
.table{
    width:100%;
    height:65vh;
    position:relative;
    background:radial-gradient(circle,#0f5a43,#06251c);
    border-radius:50% / 40%;
    margin-top:10px;
}

/* 🟡 公共牌区域 */
.board{
    position:absolute;
    top:45%;
    left:50%;
    transform:translate(-50%,-50%);
    display:flex;
    gap:6px;
}

/* 🃏 牌 */
.card{
    width:34px;
    height:48px;
    background:white;
    color:black;
    border-radius:6px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:bold;
}

/* 💰 底池 */
.pot{
    position:absolute;
    top:38%;
    left:50%;
    transform:translateX(-50%);
    font-size:14px;
    background:rgba(0,0,0,0.3);
    padding:4px 10px;
    border-radius:10px;
}

/* 👤 玩家（WePoker风格卡片） */
.player{
    position:absolute;
    width:80px;
    text-align:center;
    font-size:10px;
}

/* 9人环形 */
.p0{bottom:-10px;left:50%;transform:translateX(-50%);}
.p1{left:5%;bottom:15%;}
.p2{left:0%;top:55%;}
.p3{left:10%;top:15%;}
.p4{left:50%;top:5%;transform:translateX(-50%);}
.p5{right:10%;top:15%;}
.p6{right:0%;top:55%;}
.p7{right:5%;bottom:15%;}
.p8{right:25%;bottom:0%;}

/* 🎮 操作栏 */
.actions{
    position:fixed;
    bottom:0;
    width:100%;
    background:#081c15;
    display:flex;
    justify-content:space-around;
    padding:10px 0;
}

button{
    padding:8px;
    border:none;
    border-radius:8px;
    background:#145a43;
    color:white;
    font-size:12px;
}

/* 🃏 手牌 */
.hand{
    position:absolute;
    bottom:90px;
    left:50%;
    transform:translateX(-50%);
    display:flex;
    gap:6px;
}

</style>
</head>

<body>

<div class="table">

    <div class="pot">底池: 400</div>

    <div class="board" id="board"></div>

    <!-- 玩家 -->
    <div class="player p0">你<br>1000</div>
    <div class="player p1">P1<br>800</div>
    <div class="player p2">P2<br>1200</div>
    <div class="player p3">P3<br>500</div>
    <div class="player p4">P4<br>900</div>
    <div class="player p5">P5<br>700</div>
    <div class="player p6">P6<br>600</div>
    <div class="player p7">P7<br>1100</div>
    <div class="player p8">P8<br>950</div>

</div>

<!-- 手牌 -->
<div class="hand" id="hand"></div>

<!-- 操作栏 -->
<div class="actions">
<button>弃牌</button>
<button>跟注</button>
<button>加注</button>
<button>全压</button>
</div>

<script>

let board=["4♣","K♥","5♥"];
let hand=["A♠","Q♠"];

function render(){

document.getElementById("board").innerHTML =
board.map(c=>`<div class="card">${c}</div>`).join("");

document.getElementById("hand").innerHTML =
hand.map(c=>`<div class="card">${c}</div>`).join("");

}

render();

</script>

</body>
</html>
