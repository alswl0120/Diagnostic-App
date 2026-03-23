import streamlit.components.v1 as components


def tts_button(text: str, color: str = "#4F46E5", bg: str = "#EEF2FF", border: str = "#C7D2FE", lang: str = "en-US"):
    safe = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ").replace("\r", "")
    components.html(f"""
<div style="margin:0.5rem 0 1rem 0;">
  <button id="tts-btn" onclick="(function(){{
    var btn=document.getElementById('tts-btn');
    if(window._tts_speaking){{
      window.speechSynthesis.cancel();
      window._tts_speaking=false;
      btn.innerHTML='&#128266; Read question aloud';
      btn.style.background='{bg}';
      btn.style.transform='scale(1)';
      return;
    }}
    if(!('speechSynthesis' in window)){{alert('Audio not supported in this browser.');return;}}
    var u=new SpeechSynthesisUtterance('{safe}');
    u.lang='{lang}';u.rate=0.85;u.pitch=1.05;
    u.onend=function(){{window._tts_speaking=false;btn.innerHTML='&#128266; Read question aloud';btn.style.background='{bg}';btn.style.transform='scale(1)';}};
    window._tts_speaking=true;
    btn.innerHTML='&#9646;&#9646; Stop reading';
    btn.style.background='{border}';
    btn.style.transform='scale(0.97)';
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  }})()"
  style="background:{bg};border:2.5px solid {border};border-radius:24px;padding:0.5rem 1.25rem;font-size:0.88rem;font-weight:800;color:{color};cursor:pointer;font-family:sans-serif;transition:all 0.15s;display:inline-flex;align-items:center;gap:0.4rem;box-shadow:0 2px 8px {border}55;">
    &#128266; Read question aloud
  </button>
  <span style="font-size:0.7rem;color:#9CA3AF;font-weight:600;margin-left:0.6rem;">Works offline &middot; Browser audio</span>
</div>
""", height=56)
