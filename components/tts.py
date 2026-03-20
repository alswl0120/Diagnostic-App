import streamlit.components.v1 as components


def tts_button(text: str, color: str = "#4F46E5", bg: str = "#EEF2FF", border: str = "#C7D2FE", lang: str = "en-US"):
    safe = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ").replace("\r", "")
    components.html(f"""
<div style="display:flex;align-items:center;gap:0.5rem;margin:0.4rem 0 0.75rem 0;">
  <button id="tts-btn" onclick="(function(){{
    var btn=document.getElementById('tts-btn');
    if(window._tts_speaking){{
      window.speechSynthesis.cancel();
      window._tts_speaking=false;
      btn.innerHTML='🔊 Read aloud';
      btn.style.background='{bg}';
      return;
    }}
    if(!('speechSynthesis' in window)){{alert('Audio not supported in this browser.');return;}}
    var u=new SpeechSynthesisUtterance('{safe}');
    u.lang='{lang}';u.rate=0.88;
    u.onend=function(){{window._tts_speaking=false;btn.innerHTML='🔊 Read aloud';btn.style.background='{bg}';}};
    window._tts_speaking=true;
    btn.innerHTML='⏹ Stop';
    btn.style.background='{border}';
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  }})()"
  style="background:{bg};border:2px solid {border};border-radius:20px;padding:0.3rem 1rem;font-size:0.82rem;font-weight:700;color:{color};cursor:pointer;font-family:sans-serif;transition:all 0.15s;">
    🔊 Read aloud
  </button>
  <span style="font-size:0.72rem;color:#9CA3AF;font-weight:600;">Works offline · Browser audio</span>
</div>
""", height=48)
