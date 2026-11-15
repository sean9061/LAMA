#!/usr/bin/env python3
"""config/LAMA.keymap と config/LAMA.json から doc/keymap.html（キー配置図）を生成する。

使い方: python3 doc/keymap_gen.py
keymapを変えたら実行し直すこと。ZMK Studioで変えた内容は反映されない。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYMAP = ROOT / "config" / "LAMA.keymap"
LAYOUT = ROOT / "config" / "LAMA.json"
OUT = ROOT / "doc" / "keymap.html"

LAYER_NAMES = {0: "BASE", 1: "FUNCTION", 2: "NUM", 3: "ARROW", 4: "MOUSE", 5: "SCROLL", 6: "SYSTEM"}
ENC_INDEX = 18  # 左手 row1 の Col6（エンコーダ押し込み、未配線）

# ZMKのキー名 -> (表示ラベル, KeyboardEvent.code, 暗黙のShift)
# code は HID usage に対応するので、MacのJIS/US配列設定に関係なく一致する
SHIFTED = {
    "COLON": (":", "Semicolon"), "PLUS": ("+", "Equal"), "ASTERISK": ("*", "Digit8"),
    "CARET": ("^", "Digit6"), "AMPERSAND": ("&", "Digit7"), "TILDE": ("~", "Backquote"),
    "LEFT_PARENTHESIS": ("(", "Digit9"), "RIGHT_PARENTHESIS": (")", "Digit0"),
    "UNDERSCORE": ("_", "Minus"), "EXCLAMATION": ("!", "Digit1"), "AT_SIGN": ("@", "Digit2"),
    "HASH": ("#", "Digit3"), "DOLLAR": ("$", "Digit4"), "PERCENT": ("%", "Digit5"),
    "LEFT_BRACE": ("{", "BracketLeft"), "RIGHT_BRACE": ("}", "BracketRight"), "PIPE": ("|", "Backslash"),
}
PLAIN = {
    "SPACE": ("Space", "Space"), "BACKSPACE": ("BS", "Backspace"), "ENTER": ("Enter", "Enter"),
    "DEL": ("Del", "Delete"), "ESCAPE": ("Esc", "Escape"), "TAB": ("Tab", "Tab"),
    "MINUS": ("-", "Minus"), "SQT": ("'", "Quote"), "SEMICOLON": (";", "Semicolon"),
    "COMMA": (",", "Comma"), "DOT": (".", "Period"), "PERIOD": (".", "Period"), "SLASH": ("/", "Slash"),
    "EQUAL": ("=", "Equal"), "LEFT_BRACKET": ("[", "BracketLeft"), "RIGHT_BRACKET": ("]", "BracketRight"),
    "LBKT": ("[", "BracketLeft"), "RBKT": ("]", "BracketRight"),
    "BACKSLASH": ("\\", "Backslash"), "HOME": ("Home", "Home"), "END": ("End", "End"),
    "UP_ARROW": ("↑", "ArrowUp"), "DOWN_ARROW": ("↓", "ArrowDown"),
    "LEFT_ARROW": ("←", "ArrowLeft"), "RIGHT_ARROW": ("→", "ArrowRight"),
    "LCTRL": ("Ctrl", "ControlLeft"), "LEFT_WIN": ("⌘ / Win", "MetaLeft"), "LEFT_ALT": ("⌥ / Alt", "AltLeft"),
    "LEFT_SHIFT": ("Shift", "ShiftLeft"), "LSHIFT": ("Shift", "ShiftLeft"), "RSHIFT": ("Shift", "ShiftRight"),
    "RGUI": ("右⌘ 音声", "MetaRight"),
    "LANG1": ("かな", "Lang1"), "LANG2": ("英数", "Lang2"),
    "PAGE_UP": ("PgUp", "PageUp"), "PG_UP": ("PgUp", "PageUp"), "PAGE_DOWN": ("PgDn", "PageDown"),
}
# 用途を表示したいキー
LABEL_OVERRIDE = {}
CONSUMER = {
    "C_BRI_DN": "明るさ-", "C_BRI_UP": "明るさ+", "C_PREV": "前の曲", "C_PP": "再生/停止",
    "C_NEXT": "次の曲", "C_MUTE": "ミュート", "C_VOL_DN": "音量-", "C_VOL_UP": "音量+",
}
# 用途がわかりにくい組み合わせキーには説明を添える
COMBO_NOTE = {"LG(LBKT)": "戻る", "LG(RBKT)": "進む"}
MODS = {"LC": ("⌃", "ctrl"), "LS": ("⇧", "shift"), "LG": ("⌘", "meta"), "LA": ("⌥", "alt")}


def key(k):
    """ZMKのキー表記 -> {'label', 'code', 'mods'}"""
    m = re.match(r"(L[CSGA])\((.*)\)$", k)
    if m:
        sym, mod = MODS[m.group(1)]
        inner = key(m.group(2))
        note = " " + COMBO_NOTE[k] if k in COMBO_NOTE else ""
        return {"label": sym + inner["label"] + note, "code": inner["code"], "mods": sorted(set(inner["mods"] + [mod]))}
    if re.fullmatch(r"[A-Z]", k):
        return {"label": k, "code": "Key" + k, "mods": []}
    m = re.fullmatch(r"KP_NUMBER_(\d)", k)
    if m:
        return {"label": m.group(1), "code": "Numpad" + m.group(1), "mods": []}
    m = re.fullmatch(r"(?:NUMBER_|N)(\d)", k)
    if m:
        return {"label": m.group(1), "code": "Digit" + m.group(1), "mods": []}
    if re.fullmatch(r"F\d+", k):
        return {"label": LABEL_OVERRIDE.get(k, k), "code": k, "mods": []}
    if k in CONSUMER:
        # メディアキーはブラウザにキーイベントとして届かないことが多いので code は付けない
        return {"label": CONSUMER[k], "code": None, "mods": []}
    if k in SHIFTED:
        label, code = SHIFTED[k]
        return {"label": label, "code": code, "mods": ["shift"]}
    if k in PLAIN:
        label, code = PLAIN[k]
        return {"label": label, "code": code, "mods": []}
    return {"label": k, "code": None, "mods": []}


def binding(b):
    p = b.split()
    t = p[0]
    if t == "&kp":
        k = key(p[1])
        return {"tap": k["label"], "code": k["code"], "mods": k["mods"]}
    if t == "&trans":
        return {"trans": True}
    if t == "&none":
        return {"none": True}
    if t == "&mt":
        tap, hold = key(p[2]), key(p[1])
        return {"tap": tap["label"], "code": tap["code"], "mods": tap["mods"], "hold": hold["label"], "holdCode": hold["code"]}
    if t in ("&lt", "&lt_to_layer_0"):
        tap = key(p[2])
        n = int(p[1])
        return {"tap": tap["label"], "code": tap["code"], "mods": tap["mods"], "hold": LAYER_NAMES[n], "layer": n}
    if t == "&bt":
        if p[1] == "BT_SEL":
            return {"tap": "BT " + p[2], "kind": "sys"}
        return {"tap": {"BT_CLR": "BT消去", "BT_CLR_ALL": "BT全消去"}[p[1]], "kind": "danger"}
    if t == "&mkp":
        return {"tap": {"MB1": "左クリック", "MB2": "右クリック", "MB3": "中クリック"}[p[1]],
                "mouse": {"MB1": 0, "MB3": 1, "MB2": 2}[p[1]]}
    if t == "&bootloader":
        return {"tap": "Boot", "kind": "danger"}
    if t == "&ind_con":
        return {"tap": "接続表示", "kind": "sys"}
    return {"tap": b}


def build_data():
    km = KEYMAP.read_text()
    layout = json.loads(LAYOUT.read_text())["layouts"]["default_layout"]["layout"]
    body = km[km.index("keymap {"):]
    found = re.findall(r"\n        (\w+) \{\s*(?:display-name = \"[^\"]*\";\s*)?bindings = <(.*?)>;(.*?)\n        \};", body, flags=re.S)
    layers = []
    for i, (_name, b, rest) in enumerate(found):
        bs = [x.strip() for x in re.split(r"(?=&)", b) if x.strip()]
        if len(bs) != len(layout):
            raise SystemExit(f"layer {i}: binding数 {len(bs)} != キー数 {len(layout)}")
        sb = re.search(r"sensor-bindings = <(.*?)>", rest)
        enc = None
        if sb:
            ks = [key(x) for x in sb.group(1).split()[1:]]
            enc = {"label": " / ".join(k["label"] for k in ks), "keys": ks}
        layers.append({"id": LAYER_NAMES[i], "keys": [binding(x) for x in bs], "enc": enc})
    return {"layers": layers, "layout": layout, "encIndex": ENC_INDEX}


TEMPLATE = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LAMA キーマップ</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
:root{
  --bg:#E8ECEA; --surface:#F6F8F7; --ink:#1B2421; --muted:#5F6B66; --line:#C9D1CD;
  --key:#FFFFFF; --keyline:#AEB8B3; --accent:#0B6E4F; --accent-ink:#FFFFFF; --accent-soft:#D3EBE1;
  --hold:#8A5A00; --hold-soft:#F6E7C8; --danger:#A8322A; --danger-soft:#F5DAD6; --sys:#2F5D8A; --sys-soft:#DCE7F2;
  --ghost:#9AA5A0; --press:#E0A100; --press-ink:#1B1400;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --bg:#101513; --surface:#18201D; --ink:#E4EBE8; --muted:#95A29C; --line:#2C3632;
    --key:#212B27; --keyline:#3C4944; --accent:#4CC49A; --accent-ink:#0B1A14; --accent-soft:#1D3A2F;
    --hold:#E0B35C; --hold-soft:#3A2F17; --danger:#F08A80; --danger-soft:#3E2220; --sys:#8DB8E6; --sys-soft:#1F2F40;
    --ghost:#5C6964; --press:#F2C14E; --press-ink:#1B1400;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#101513; --surface:#18201D; --ink:#E4EBE8; --muted:#95A29C; --line:#2C3632;
  --key:#212B27; --keyline:#3C4944; --accent:#4CC49A; --accent-ink:#0B1A14; --accent-soft:#1D3A2F;
  --hold:#E0B35C; --hold-soft:#3A2F17; --danger:#F08A80; --danger-soft:#3E2220; --sys:#8DB8E6; --sys-soft:#1F2F40;
  --ghost:#5C6964; --press:#F2C14E; --press-ink:#1B1400;
}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans JP","Hiragino Sans","Noto Sans JP",system-ui,sans-serif;font-size:15px;line-height:1.6;padding-inline:16px;padding-block:28px 48px}
main{max-width:1080px;margin:0 auto;display:flex;flex-direction:column;gap:18px}
header{display:flex;flex-direction:column;gap:4px}
h1{font-size:26px;margin:0;font-weight:700;letter-spacing:.02em;text-wrap:balance}
.sub{color:var(--muted);margin:0;font-size:13px}
.mono{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace}
.tabs{display:flex;flex-wrap:wrap;gap:6px}
.tab{appearance:none;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:6px 14px;font:inherit;font-size:14px;cursor:pointer;display:flex;gap:8px;align-items:baseline}
.tab .n{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--muted)}
.tab[aria-selected="true"]{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.tab[aria-selected="true"] .n{color:var(--accent-ink);opacity:.8}
.tab:focus-visible,.opt input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.how{margin:0;font-size:14px;color:var(--ink)}
.how b{color:var(--accent)}
.live{display:flex;flex-wrap:wrap;align-items:center;gap:8px 18px;font-size:13px;color:var(--muted);background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:8px 12px}
.live .dot{width:8px;height:8px;border-radius:50%;background:var(--ghost);display:inline-block;margin-right:6px}
.live.focus .dot{background:var(--accent)}
.live .last{font-family:"IBM Plex Mono",monospace;color:var(--ink)}
.opt{display:flex;align-items:center;gap:6px;cursor:pointer;color:var(--ink)}
.board{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px;overflow-x:auto}
.board svg{display:block;width:100%;min-width:720px;height:auto}
svg text{font-family:"IBM Plex Sans JP","Hiragino Sans",system-ui,sans-serif}
.k.on rect.cap{fill:var(--press);stroke:var(--press)}
.k.on text{fill:var(--press-ink)}
.k.on path.band{fill:transparent}
.legend{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:13px;color:var(--muted);margin:0;padding:0;list-style:none}
.legend li{display:flex;align-items:center;gap:8px}
.sw{width:18px;height:14px;border-radius:3px;border:1px solid var(--keyline);background:var(--key);display:inline-block}
.sw.hold{background:linear-gradient(to top,var(--hold-soft) 40%,var(--key) 40%)}
.sw.here{background:var(--accent);border-color:var(--accent)}
.sw.on{background:var(--press);border-color:var(--press)}
.sw.trans{border-style:dashed;background:transparent}
.sw.danger{background:var(--danger-soft);border-color:var(--danger)}
.sw.sys{background:var(--sys-soft);border-color:var(--sys)}
section h2{font-size:16px;margin:0 0 8px}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:520px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:500;color:var(--muted);font-size:12px;letter-spacing:.06em}
td.l{font-family:"IBM Plex Mono",monospace;white-space:nowrap}
.notes{font-size:13px;color:var(--muted);margin:0;padding-left:1.2em;display:flex;flex-direction:column;gap:4px}
</style>
</head>
<body>
<main>
  <header>
    <h1>LAMA キーマップ</h1>
    <p class="sub">config/LAMA.keymap とPCBのスイッチ座標から <span class="mono">doc/keymap_gen.py</span> で生成。ZMK Studioで変更した内容は反映されません。</p>
  </header>
  <div class="tabs" role="tablist" id="tabs"></div>
  <p class="how" id="how"></p>
  <div class="live" id="live">
    <span><span class="dot"></span><span id="focusMsg">このページをクリックしてからキーを押すと、押したキーが光ります</span></span>
    <span>受け取ったキー: <span class="last" id="last">—</span></span>
    <label class="opt"><input type="checkbox" id="mouseSync">マウス・トラックボールにも反応する</label>
  </div>
  <div class="board"><svg id="svg" role="img" aria-label="キー配置図"></svg></div>
  <ul class="legend">
    <li><span class="sw on"></span>今押しているキー</li>
    <li><span class="sw"></span>タップで入力</li>
    <li><span class="sw hold"></span>下段の色帯 = 押し続けたときの動作</li>
    <li><span class="sw here"></span>このレイヤーに入るために押し続けるキー</li>
    <li><span class="sw trans"></span>透過（下のレイヤーのキーがそのまま効く）</li>
    <li><span class="sw sys"></span>Bluetooth・表示</li>
    <li><span class="sw danger"></span>消去・ブートローダー（押す前に確認）</li>
  </ul>
  <section>
    <h2>レイヤー一覧</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>#</th><th>レイヤー</th><th>入り方</th><th>主な中身</th></tr></thead>
      <tbody id="tbl"></tbody>
    </table></div>
  </section>
  <section>
    <h2>メモ</h2>
    <ul class="notes">
      <li>レイヤーはキーボードの中の状態なので、ページからは直接見えません。届いたキーがどのレイヤーにしかないキーかで判断して、表示を切り替えています。レイヤーキーを押し続けただけでは切り替わりません。</li>
      <li>⌘Space（Spotlight）や ⌃↑（Mission Control）など、Macが先に受け取るキーはページに届かないので光りません。</li>
      <li>Bluetoothの操作キーはパソコンに何も送らないので光りません。</li>
      <li>右手の下段の「右⌘」は、VoiceOSの音声入力のトリガーです。</li>
      <li>左手のエンコーダを回すと PgUp / PgDn。ARROWレイヤーでは ⌃PgUp / ⌃PgDn（タブの切り替え）。</li>
      <li>エンコーダの押し込み（左手・中段の一番内側）は、PCB上で配線されていないため押しても反応しません。</li>
    </ul>
  </section>
</main>
<script>
const DATA = __DATA__;
const INFO = [
  {how:'何も押していないときの基本レイヤー。', what:'文字入力、親指で英数/かな・Space・BS・Enter、端の列にEsc・Tab・Shift'},
  {how:'右手の親指 <b>Enter</b> を押し続ける', what:'右手でF1〜F13、左手で音量・再生/停止・曲送り・画面の明るさ・スクショ（T: ⇧⌘4、G: ⇧⌘5）'},
  {how:'左手の親指 <b>Space</b> を押し続ける', what:'テンキー配置の数字、記号'},
  {how:'左手の一番内側の親指 <b>かな</b> を押し続ける', what:'Esc、矢印、Home/End、タブ切り替え'},
  {how:'<b>トラックボールを動かす</b>と自動で入る（止めて0.7秒で戻る）', what:'J / K / L で左・中・右クリック'},
  {how:'右手の <b>I</b> を押し続ける', what:'トラックボールでスクロール'},
  {how:'左手の親指 <b>英数</b> を押し続ける', what:'Bluetoothの切り替え・消去、接続表示、ブートローダー'},
];
const ENC = DATA.encIndex, U = 64, PAD = 16, BACK_MS = 1200;
const svg = document.getElementById('svg');
const lay = DATA.layout;
const maxX = Math.max(...lay.map(k=>k.x))+1, maxY = Math.max(...lay.map(k=>k.y))+1.1;
svg.setAttribute('viewBox', `0 0 ${maxX*U+PAD*2} ${maxY*U+PAD*2}`);
const NS='http://www.w3.org/2000/svg';
function el(n,a,p){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);p&&p.appendChild(e);return e}
const holdKeyIndex = li => DATA.layers[0].keys.findIndex(k=>k.layer===li);
const fit = t => t.length>7 ? 14 : t.length>4 ? 16 : 20;

let cur = 0, keyEls = [];
const pressed = new Map();   // code -> [index...]
let backTimer = null;

function draw(li){
  cur = li; svg.innerHTML=''; keyEls=[];
  const L = DATA.layers[li], base = DATA.layers[0];
  const hk = holdKeyIndex(li);
  lay.forEach((p,i)=>{
    let k = L.keys[i], ghost=false;
    if(k.trans){ k = base.keys[i]; ghost=true; }
    const x=PAD+p.x*U+3, y=PAD+p.y*U+3, w=U-6, h=U-6;
    const g=el('g',{class:'k'},svg); keyEls.push(g);
    if(p.r) g.setAttribute('transform',`rotate(${p.r} ${PAD+p.rx*U} ${PAD+p.ry*U})`);
    const here = li>0 && i===hk;
    let fill='var(--key)', stroke='var(--keyline)', ink='var(--ink)', dash='';
    if(ghost){ fill='transparent'; dash='4 3'; ink='var(--ghost)'; }
    if(k.none){ fill='transparent'; dash='2 4'; }
    if(!ghost && k.kind==='danger'){ fill='var(--danger-soft)'; stroke='var(--danger)'; ink='var(--danger)'; }
    if(!ghost && k.kind==='sys'){ fill='var(--sys-soft)'; stroke='var(--sys)'; ink='var(--sys)'; }
    if(here){ fill='var(--accent)'; stroke='var(--accent)'; ink='var(--accent-ink)'; dash=''; }
    const r=el('rect',{class:'cap',x,y,width:w,height:h,rx:8,fill,stroke,'stroke-width':1.2},g);
    if(dash) r.setAttribute('stroke-dasharray',dash);
    const hasHold = k.hold && !ghost;
    if(hasHold && !here){
      el('path',{class:'band',d:`M${x} ${y+h-18} h${w} v10 a8 8 0 0 1 -8 8 h${-(w-16)} a8 8 0 0 1 -8 -8 z`,fill:'var(--hold-soft)'},g);
    }
    if(!k.none){
      const t = k.tap||'';
      const ty = hasHold||here ? y+h/2-3 : y+h/2+6;
      el('text',{x:x+w/2,y:ty,'text-anchor':'middle','font-size':fit(t),'font-weight':500,fill:ink},g).textContent=t;
      if(hasHold || here){
        el('text',{x:x+w/2,y:y+h-5,'text-anchor':'middle','font-size':10,'font-weight':700,fill:here?'var(--accent-ink)':'var(--hold)','letter-spacing':'.04em'},g).textContent = here ? '押し続ける' : k.hold;
      }
    }
    if(i===ENC){
      el('text',{x:x+w/2,y:y-6,'text-anchor':'middle','font-size':10,fill:'var(--muted)'},g).textContent='エンコーダ（押し込み未配線）';
      const enc = L.enc || base.enc;
      el('text',{x:x+w/2,y:y+h+13,'text-anchor':'middle','font-size':10,fill:L.enc&&li>0?'var(--accent)':'var(--muted)'},g).textContent='回す: '+enc.label;
    }
  });
  if(li===4){
    el('text',{x:PAD+7*U,y:PAD+maxY*U-4,'text-anchor':'middle','font-size':12,fill:'var(--accent)'},svg).textContent='トラックボールを動かすと自動でこのレイヤーに入ります';
  }
  document.getElementById('how').innerHTML = (li===0?'':'入り方: ')+INFO[li].how;
  document.querySelectorAll('.tab').forEach((b,j)=>b.setAttribute('aria-selected',j===li));
  for(const idx of pressed.values()) idx.forEach(i=>keyEls[i]&&keyEls[i].classList.add('on'));
}

// ---- キー入力から位置とレイヤーを推定 ----
const MODKEYS = {ShiftLeft:1,ShiftRight:1,ControlLeft:1,ControlRight:1,MetaLeft:1,MetaRight:1,AltLeft:1,AltRight:1};
function evMods(e){ return {shift:e.shiftKey, ctrl:e.ctrlKey, meta:e.metaKey, alt:e.altKey}; }
function modsOk(req, m){ return req.every(x=>m[x]); }
function exact(req, m, code){
  // 修飾キー自身の押下は数えない
  const own = {ShiftLeft:'shift',ShiftRight:'shift',ControlLeft:'ctrl',MetaLeft:'meta',AltLeft:'alt'}[code];
  return ['shift','ctrl','meta','alt'].every(x=> x===own || (!!m[x]) === req.includes(x));
}
// レイヤー li で見えている(透過を解決した)バインディング
function eff(li,i){ const k=DATA.layers[li].keys[i]; return k.trans ? DATA.layers[0].keys[i] : k; }
function matchesIn(li, code, m){
  const hits=[]; let ex=false;
  lay.forEach((_,i)=>{
    const k=eff(li,i);
    if(k.code===code && modsOk(k.mods||[],m)){ hits.push(i); if(exact(k.mods||[],m,code)) ex=true; }
    else if(k.holdCode===code){ hits.push(i); ex=true; }
  });
  const L=DATA.layers[li].enc || DATA.layers[0].enc;
  if(L && L.keys.some(k=>k.code===code && modsOk(k.mods,m))){ hits.push(ENC); if(L.keys.some(k=>k.code===code && exact(k.mods,m,code))) ex=true; }
  return {hits, ex};
}
function locate(code, m){
  // 優先: 修飾キーまで一致 > 今のレイヤー > BASE > その他
  const order=[cur, 0, ...DATA.layers.map((_,i)=>i).filter(i=>i!==cur && i!==0)];
  let best=null;
  for(const li of order){
    const r=matchesIn(li,code,m);
    if(!r.hits.length) continue;
    if(r.ex) return {li, hits:r.hits};
    if(!best) best={li, hits:r.hits};
  }
  return best;
}
function scheduleBack(){
  clearTimeout(backTimer);
  if(cur!==0 && pressed.size===0) backTimer=setTimeout(()=>{ if(pressed.size===0) draw(0); }, BACK_MS);
}
function press(code, idx){
  pressed.set(code, idx);
  idx.forEach(i=>keyEls[i]&&keyEls[i].classList.add('on'));
}
function release(code){
  const idx=pressed.get(code); pressed.delete(code);
  if(idx) idx.forEach(i=>{
    const still=[...pressed.values()].some(a=>a.includes(i));
    if(!still && keyEls[i]) keyEls[i].classList.remove('on');
  });
  scheduleBack();
}
function showLast(txt){ document.getElementById('last').textContent = txt; }

document.addEventListener('keydown', e=>{
  if(e.repeat){ e.preventDefault(); return; }
  const m=evMods(e);
  showLast(e.code + (e.key && e.key.length===1 ? `  (${e.key})` : e.key && e.key!==e.code ? `  (${e.key})` : ''));
  // ⌘付きのブラウザ操作(⌘R など)は邪魔しない
  if(!m.meta || MODKEYS[e.code]) e.preventDefault();
  const found=locate(e.code, m);
  if(!found) return;
  clearTimeout(backTimer);
  if(found.li!==cur && !MODKEYS[e.code]) draw(found.li);
  press(e.code, found.hits);
});
document.addEventListener('keyup', e=>{ release(e.code); });
window.addEventListener('blur', ()=>{ for(const c of [...pressed.keys()]) release(c); setFocus(false); });
window.addEventListener('focus', ()=>setFocus(true));
function setFocus(f){
  document.getElementById('live').classList.toggle('focus', f);
  document.getElementById('focusMsg').textContent = f ? 'キー入力を受け付けています' : 'このページをクリックしてからキーを押すと、押したキーが光ります';
}
setFocus(document.hasFocus());

// ---- マウス・トラックボール(任意) ----
const mouseSync=document.getElementById('mouseSync');
let moveTimer=null;
function mouseLayer(li){
  if(!mouseSync.checked) return;
  clearTimeout(backTimer); clearTimeout(moveTimer);
  if(cur!==li && pressed.size===0) draw(li);
  moveTimer=setTimeout(()=>{ if(pressed.size===0 && cur===li) draw(0); }, 700);
}
document.addEventListener('mousemove', ()=>{ if(cur===0||cur===4) mouseLayer(4); });
document.addEventListener('wheel', ()=>mouseLayer(5), {passive:true});
document.addEventListener('mousedown', e=>{
  if(!mouseSync.checked || e.target.closest('.tabs, .opt')) return;
  const i=DATA.layers[4].keys.findIndex(k=>k.mouse===e.button);
  if(i<0) return;
  if(cur!==4) draw(4);
  press('mouse'+e.button,[i]);
});
document.addEventListener('mouseup', e=>{ if(pressed.has('mouse'+e.button)) release('mouse'+e.button); });
document.addEventListener('contextmenu', e=>{ if(mouseSync.checked && !e.target.closest('.tabs, .opt')) e.preventDefault(); });

// ---- タブと表 ----
const tabs=document.getElementById('tabs'), tbl=document.getElementById('tbl');
DATA.layers.forEach((L,i)=>{
  const b=document.createElement('button');
  b.className='tab'; b.setAttribute('role','tab'); b.id='tab-'+i;
  b.innerHTML=`<span class="n">${i}</span>${L.id}`;
  b.onclick=()=>{ clearTimeout(backTimer); draw(i); b.blur(); };
  tabs.appendChild(b);
  const tr=document.createElement('tr');
  tr.innerHTML=`<td class="l">${i}</td><td class="l">${L.id}</td><td>${INFO[i].how}</td><td>${INFO[i].what}</td>`;
  tbl.appendChild(tr);
});
draw(0);
</script>
</body>
</html>
'''


def main():
    data = json.dumps(build_data(), ensure_ascii=False)
    OUT.write_text(TEMPLATE.replace("__DATA__", data))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
