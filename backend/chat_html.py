CHAT_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Support Assistant</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:linear-gradient(160deg,#f0edf8 0%,#e2daf2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:16px}

/* Launcher */
.launcher{position:fixed;bottom:28px;right:28px;width:54px;height:54px;border-radius:50%;background:linear-gradient(135deg,#7c5cbf,#9b7fd4);border:none;cursor:pointer;box-shadow:0 6px 24px rgba(124,92,191,.45);display:flex;align-items:center;justify-content:center;transition:transform .2s,box-shadow .2s;z-index:999}
.launcher:hover{transform:scale(1.08);box-shadow:0 8px 28px rgba(124,92,191,.55)}
.launcher svg{width:24px;height:24px;stroke:#fff;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.launcher .icon-open{display:block}
.launcher .icon-close{display:none}
.launcher.open .icon-open{display:none}
.launcher.open .icon-close{display:block}

/* Popup */
.chat-popup{position:fixed;bottom:94px;right:28px;width:370px;height:580px;display:flex;flex-direction:column;border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(109,86,179,.22);transform:scale(.93) translateY(14px);opacity:0;pointer-events:none;transition:transform .25s cubic-bezier(.34,1.56,.64,1),opacity .2s ease;z-index:998}
.chat-popup.visible{transform:scale(1) translateY(0);opacity:1;pointer-events:all}

/* Demo page */
.demo-page{text-align:center;color:#4c1d95}
.demo-page h1{font-size:26px;font-weight:700;margin-bottom:8px}
.demo-page p{font-size:14px;color:#7c5cbf;opacity:.8}

/* Chat window */
.chat-window{width:100%;height:100%;background:#fff;display:flex;flex-direction:column;overflow:hidden}

/* Header */
.chat-header{background:linear-gradient(135deg,#7c5cbf 0%,#9b7fd4 100%);padding:14px 18px;display:flex;align-items:center;gap:10px;flex-shrink:0}
.avatar{width:38px;height:38px;background:rgba(255,255,255,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.avatar svg{width:20px;height:20px;stroke:#fff;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.header-info{flex:1}
.header-info h2{color:#fff;font-size:14px;font-weight:600}
.header-info p{color:rgba(255,255,255,.75);font-size:11px;margin-top:2px;display:flex;align-items:center;gap:4px}
.status-dot{width:6px;height:6px;background:#a3e635;border-radius:50%;display:inline-block;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.clear-btn{background:rgba(255,255,255,.15);border:none;color:#fff;padding:5px 11px;border-radius:20px;font-size:11px;cursor:pointer;transition:background .2s}
.clear-btn:hover{background:rgba(255,255,255,.25)}

/* Messages */
.chat-messages{flex:1;overflow-y:auto;padding:16px 14px 10px;display:flex;flex-direction:column;gap:10px;scroll-behavior:smooth;background:#faf9ff}
.chat-messages::-webkit-scrollbar{width:3px}
.chat-messages::-webkit-scrollbar-thumb{background:#ddd6fe;border-radius:4px}
.msg-row{display:flex;align-items:flex-end;gap:7px;animation:fadeUp .2s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
.msg-row.user{flex-direction:row-reverse}
.msg-avatar{width:28px;height:28px;border-radius:9px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.msg-row.bot .msg-avatar{background:#ede9fe}
.msg-row.bot .msg-avatar svg{width:14px;height:14px;stroke:#7c5cbf;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.msg-row.user .msg-avatar{background:#7c5cbf}
.msg-row.user .msg-avatar svg{width:14px;height:14px;stroke:#fff;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.msg-content{max-width:78%;display:flex;flex-direction:column;gap:2px}
.msg-row.user .msg-content{align-items:flex-end}
.bubble{padding:9px 13px;border-radius:15px;font-size:13px;line-height:1.55;word-break:break-word}
.msg-row.bot .bubble{background:#fff;color:#2d2040;border:1px solid #ede9fe;border-bottom-left-radius:3px;box-shadow:0 1px 3px rgba(109,86,179,.07)}
.msg-row.user .bubble{background:linear-gradient(135deg,#7c5cbf,#9b7fd4);color:#fff;border-bottom-right-radius:3px}
.msg-time{font-size:9.5px;color:#b0a8c8;padding:0 3px}

/* Typing */
.typing-indicator{display:flex;align-items:center;gap:4px;padding:10px 14px;background:#fff;border:1px solid #ede9fe;border-radius:15px;border-bottom-left-radius:3px;width:fit-content}
.typing-indicator span{width:6px;height:6px;background:#c4b5fd;border-radius:50%;animation:bounce 1.2s infinite}
.typing-indicator span:nth-child(2){animation-delay:.2s}
.typing-indicator span:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-5px)}}

/* Suggestions */
.suggestions-area{padding:7px 14px 5px;display:flex;flex-wrap:wrap;gap:5px;flex-shrink:0;border-top:1px solid #f0ecfa;background:#fff}
.suggestions-label{width:100%;font-size:10.5px;color:#b0a8c8;margin-bottom:1px}
.chip{background:#f3f0fb;color:#7c5cbf;border:1px solid #ddd6fe;padding:4px 11px;border-radius:20px;font-size:11.5px;cursor:pointer;transition:all .2s;white-space:nowrap}
.chip:hover{background:#ede9fe;border-color:#c4b5fd}

/* Input */
.chat-input-area{padding:9px 14px 12px;border-top:1px solid #f0ecfa;flex-shrink:0;background:#fff}
.input-row{display:flex;align-items:center;gap:7px;background:#f8f6ff;border:1.5px solid #ddd6fe;border-radius:26px;padding:5px 5px 5px 14px;transition:border-color .2s,box-shadow .2s}
.input-row:focus-within{border-color:#9b7fd4;background:#fff;box-shadow:0 0 0 3px rgba(155,127,212,.1)}
#userInput{flex:1;border:none;background:transparent;outline:none;font-size:13px;color:#2d2040;min-width:0}
#userInput::placeholder{color:#c4b5fd}
#sendBtn{width:32px;height:32px;background:linear-gradient(135deg,#7c5cbf,#9b7fd4);border:none;border-radius:50%;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:opacity .2s;flex-shrink:0}
#sendBtn:hover{opacity:.88}
#sendBtn:disabled{opacity:.35;cursor:not-allowed}
.char-count{font-size:9.5px;color:#c4b5fd;text-align:right;margin-top:2px;padding-right:3px}
.char-count.warn{color:#f59e0b}
.char-count.over{color:#ef4444}

/* Welcome card */
.welcome-card{background:linear-gradient(135deg,#f3f0fb,#ede9fe);border-radius:12px;padding:12px 14px;font-size:12.5px;color:#4c1d95;line-height:1.6;border:1px solid #ddd6fe}
.welcome-card strong{display:block;margin-bottom:4px;font-size:13px;color:#5b21b6}

@media(max-width:480px){
  .chat-popup{right:0;bottom:0;width:100vw;height:100vh;border-radius:0}
  .launcher{bottom:20px;right:20px}
}
</style>
</head>
<body>

<div class="demo-page">
  <h1>Support Portal</h1>
  <p>Click the button in the bottom-right corner to chat with us.</p>
</div>

<div class="chat-popup" id="chatPopup">
  <div class="chat-window">
    <div class="chat-header">
      <div class="avatar">
        <svg viewBox="0 0 24 24"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>
      </div>
      <div class="header-info">
        <h2>Support Assistant</h2>
        <p><span class="status-dot"></span>Online &mdash; here to help</p>
      </div>
      <button class="clear-btn" onclick="clearChat()">Clear</button>
    </div>

    <div class="chat-messages" id="messages">
      <div class="msg-row bot">
        <div class="msg-avatar">
          <svg viewBox="0 0 24 24"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>
        </div>
        <div class="msg-content">
          <div class="bubble welcome-card">
            <strong>Welcome to Support</strong>
            I can help you with courses, certificates, payments, account issues, and more.
            Type your question below or pick a suggestion.
          </div>
          <span class="msg-time" id="welcomeTime"></span>
        </div>
      </div>
    </div>

    <div class="suggestions-area" id="suggestionsArea">
      <span class="suggestions-label">Try asking:</span>
      <div id="chips" style="display:flex;flex-wrap:wrap;gap:5px;"></div>
    </div>

    <div class="chat-input-area">
      <div class="input-row">
        <input type="text" id="userInput" placeholder="Type your question..." autocomplete="off" maxlength="500"/>
        <button id="sendBtn" onclick="sendMessage()" title="Send">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
      <div class="char-count" id="charCount">0 / 500</div>
    </div>
  </div>
</div>

<button class="launcher" id="launcher" onclick="toggleChat()" title="Chat with us">
  <svg class="icon-open" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
  <svg class="icon-close" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
</button>

<script>
var input    = document.getElementById("userInput");
var messages = document.getElementById("messages");
var sendBtn  = document.getElementById("sendBtn");
var charCount= document.getElementById("charCount");
var chipsEl  = document.getElementById("chips");
var popup    = document.getElementById("chatPopup");
var launcher = document.getElementById("launcher");

var BOT_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="#7c5cbf" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="14" height="14"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>';
var USER_ICON= '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="14" height="14"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';

function now(){return new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});}
document.getElementById("welcomeTime").textContent = now();

function toggleChat(){
  var isOpen = popup.classList.toggle("visible");
  launcher.classList.toggle("open", isOpen);
  if(isOpen) input.focus();
}

input.addEventListener("input", function(){
  var len = input.value.length;
  charCount.textContent = len + " / 500";
  charCount.className = "char-count" + (len > 450 ? (len >= 500 ? " over" : " warn") : "");
});
input.addEventListener("keydown", function(e){
  if(e.key === "Enter" && !e.shiftKey){ e.preventDefault(); sendMessage(); }
});

function appendMessage(text, sender){
  var row = document.createElement("div"); row.className = "msg-row " + sender;
  var av  = document.createElement("div"); av.className  = "msg-avatar";
  av.innerHTML = sender === "bot" ? BOT_ICON : USER_ICON;
  var content = document.createElement("div"); content.className = "msg-content";
  var bubble  = document.createElement("div"); bubble.className  = "bubble"; bubble.textContent = text;
  var time    = document.createElement("span"); time.className   = "msg-time"; time.textContent = now();
  content.appendChild(bubble); content.appendChild(time);
  row.appendChild(av); row.appendChild(content);
  messages.appendChild(row); messages.scrollTop = messages.scrollHeight;
}

function showTyping(){
  var row = document.createElement("div"); row.className = "msg-row bot"; row.id = "typingRow";
  var av  = document.createElement("div"); av.className  = "msg-avatar"; av.innerHTML = BOT_ICON;
  var content = document.createElement("div"); content.className = "msg-content";
  var ind = document.createElement("div"); ind.className = "typing-indicator";
  ind.innerHTML = "<span></span><span></span><span></span>";
  content.appendChild(ind); row.appendChild(av); row.appendChild(content);
  messages.appendChild(row); messages.scrollTop = messages.scrollHeight;
}
function hideTyping(){ var el = document.getElementById("typingRow"); if(el) el.remove(); }

async function sendMessage(){
  var text = input.value.trim(); if(!text || sendBtn.disabled) return;
  appendMessage(text, "user");
  input.value = ""; charCount.textContent = "0 / 500"; charCount.className = "char-count";
  sendBtn.disabled = true; showTyping();
  try{
    var res  = await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})});
    var data = await res.json(); hideTyping();
    appendMessage(data.reply || data.error || "Something went wrong.", "bot");
  }catch(e){ hideTyping(); appendMessage("Connection error. Please try again.", "bot"); }
  finally{ sendBtn.disabled = false; input.focus(); }
}

async function loadSuggestions(){
  try{
    var res  = await fetch("/suggestions"); var data = await res.json();
    chipsEl.innerHTML = "";
    (data.suggestions || []).forEach(function(q){
      var btn = document.createElement("button"); btn.className = "chip"; btn.textContent = q;
      btn.onclick = function(){ input.value = q; sendMessage(); };
      chipsEl.appendChild(btn);
    });
  }catch(e){ document.getElementById("suggestionsArea").style.display = "none"; }
}

function clearChat(){
  messages.innerHTML = "";
  var row = document.createElement("div"); row.className = "msg-row bot";
  var av  = document.createElement("div"); av.className  = "msg-avatar"; av.innerHTML = BOT_ICON;
  var content = document.createElement("div"); content.className = "msg-content";
  var bubble  = document.createElement("div"); bubble.className  = "bubble welcome-card";
  bubble.innerHTML = "<strong>Chat cleared</strong> How can I help you today?";
  var time = document.createElement("span"); time.className = "msg-time"; time.textContent = now();
  content.appendChild(bubble); content.appendChild(time);
  row.appendChild(av); row.appendChild(content);
  messages.appendChild(row); loadSuggestions(); input.focus();
}

loadSuggestions();
</script>
</body>
</html>"""
