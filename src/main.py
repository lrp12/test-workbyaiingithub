<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Modern Calculator</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
  --bg:#f5f7fa;
  --key:#ffffff;
  --keyShadow:#d9e2ec;
  --accent:#4a90e2;
  --accentDark:#357abd;
  --text:#2d3748;
  --textLight:#718096;
}
*{
  box-sizing:border-box;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
body{
  margin:0;
  height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  background:var(--bg);
}
.calculator{
  width:320px;
  background:var(--key);
  border-radius:24px;
  box-shadow:0 20px 40px rgba(0,0,0,.1);
  padding:24px;
}
.display{
  background:var(--bg);
  border-radius:16px;
  padding:16px;
  text-align:right;
  font-size:2.2rem;
  color:var(--text);
  margin-bottom:16px;
  min-height:64px;
  word-wrap:break-word;
  overflow:hidden;
}
.keys{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:12px;
}
button{
  border:none;
  border-radius:16px;
  font-size:1.4rem;
  padding:20px 0;
  cursor:pointer;
  background:var(--key);
  box-shadow:0 4px 8px var(--keyShadow);
  color:var(--text);
  transition:transform .1s,box-shadow .1s;
}
button:active{
  transform:translateY(2px);
  box-shadow:0 2px 4px var(--keyShadow);
}
.operator{
  background:var(--accent);
  color:#fff;
}
.operator:active{
  background:var(--accentDark);
}
.zero{
  grid-column:span 2;
}
</style>
</head>
<body>
<div class="calculator">
  <div class="display" id="display">0</div>
  <div class="keys">
    <button onclick="clearDisplay()">C</button>
    <button onclick="appendToDisplay('/')" class="operator">÷</button>
    <button onclick="appendToDisplay('*')" class="operator">×</button>
    <button onclick="deleteLast()">←</button>

    <button onclick="appendToDisplay('7')">7</button>
    <button onclick="appendToDisplay('8')">8</button>
    <button onclick="appendToDisplay('9')">9</button>
    <button onclick="appendToDisplay('-')" class="operator">−</button>

    <button onclick="appendToDisplay('4')">4</button>
    <button onclick="appendToDisplay('5')">5</button>
    <button onclick="appendToDisplay('6')">6</button>
    <button onclick="appendToDisplay('+')" class="operator">+</button>

    <button onclick="appendToDisplay('1')">1</button>
    <button onclick="appendToDisplay('2')">2</button>
    <button onclick="appendToDisplay('3')">3</button>
    <button onclick="calculate()" class="operator" style="grid-row:span 2;">=</button>

    <button onclick="appendToDisplay('0')" class="zero">0</button>
    <button onclick="appendToDisplay('.')">.</button>
  </div>
</div>
<script>
let display=document.getElementById('display');
function appendToDisplay(val){
  if(display.textContent==='0' && val!=='.') display.textContent='';
  display.textContent+=val;
}
function clearDisplay(){
  display.textContent='0';
}
function deleteLast(){
  display.textContent=display.textContent.slice(0,-1)||'0';
}
function calculate(){
  try{
    display.textContent=eval(display.textContent.replace(/×/g,'*').replace(/÷/g,'/').replace(/−/g,'-'));
  }catch{
    display.textContent='Error';
  }
}
</script>
</body>
</html>
