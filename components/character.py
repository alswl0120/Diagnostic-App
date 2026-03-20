import streamlit as st

_BUBBLE_CSS = """
<style>
.char-wrap { display:flex; flex-direction:column; align-items:center; }
.speech-bubble {
    position:relative; background:white;
    border:2.5px solid #C7D2FE; border-radius:18px;
    padding:0.65rem 0.9rem; font-size:0.82rem; font-weight:700;
    color:#374151; text-align:center; line-height:1.5;
    box-shadow:0 4px 14px rgba(99,102,241,0.12);
    margin-bottom:0.5rem; max-width:160px;
}
.speech-bubble::after {
    content:''; position:absolute; bottom:-13px; left:50%;
    transform:translateX(-50%);
    border:7px solid transparent; border-top-color:#C7D2FE;
}
.speech-bubble::before {
    content:''; position:absolute; bottom:-10px; left:50%;
    transform:translateX(-50%);
    border:6px solid transparent; border-top-color:white; z-index:1;
}
.sb-green { border-color:#A7F3D0; }
.sb-green::after { border-top-color:#A7F3D0; }
.sb-orange { border-color:#FED7AA; }
.sb-orange::after { border-top-color:#FED7AA; }
.sb-pink { border-color:#FBCFE8; }
.sb-pink::after { border-top-color:#FBCFE8; }
.sb-yellow { border-color:#FDE68A; }
.sb-yellow::after { border-top-color:#FDE68A; }
</style>
"""

# ── LEO  (Yellow · Purple) ─────────────────────────────────────────────────────
_LEO_WAVE = """<svg width="130" height="175" viewBox="0 0 130 175" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="65" cy="171" rx="30" ry="6" fill="rgba(99,102,241,0.15)"/>
<rect x="32" y="112" width="66" height="55" rx="20" fill="#6366F1"/>
<path d="M34 122 Q16 102 20 80" stroke="#6366F1" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="19" cy="76" r="9" fill="#FCD34D"/>
<path d="M96 130 Q112 142 110 158" stroke="#6366F1" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="110" cy="162" r="9" fill="#FCD34D"/>
<rect x="53" y="102" width="24" height="13" fill="#FCD34D"/>
<circle cx="65" cy="70" r="42" fill="#FCD34D"/>
<circle cx="25" cy="60" r="10" fill="#FCD34D"/>
<circle cx="105" cy="60" r="10" fill="#FCD34D"/>
<circle cx="50" cy="65" r="10" fill="white"/><circle cx="80" cy="65" r="10" fill="white"/>
<circle cx="52" cy="67" r="6" fill="#1F2937"/><circle cx="82" cy="67" r="6" fill="#1F2937"/>
<circle cx="54" cy="65" r="2.5" fill="white"/><circle cx="84" cy="65" r="2.5" fill="white"/>
<path d="M46 82 Q65 97 84 82" stroke="#92400E" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<circle cx="38" cy="78" r="8" fill="#FCA5A5" opacity="0.55"/>
<circle cx="92" cy="78" r="8" fill="#FCA5A5" opacity="0.55"/>
<rect x="30" y="30" width="70" height="11" rx="3" fill="#312E81"/>
<polygon points="65,13 28,32 102,32" fill="#1E1B4B"/>
<line x1="98" y1="32" x2="107" y2="50" stroke="#FCD34D" stroke-width="3.5" stroke-linecap="round"/>
<circle cx="107" cy="54" r="5.5" fill="#FCD34D"/>
</svg>"""

_LEO_THINK = """<svg width="110" height="148" viewBox="0 0 110 148" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="55" cy="144" rx="26" ry="6" fill="rgba(99,102,241,0.12)"/>
<rect x="22" y="96" width="66" height="46" rx="18" fill="#6366F1"/>
<path d="M24 108 Q6 113 8 126" stroke="#6366F1" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="9" cy="130" r="9" fill="#FCD34D"/>
<path d="M86 108 Q100 114 98 128" stroke="#6366F1" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="98" cy="132" r="9" fill="#FCD34D"/>
<rect x="44" y="87" width="22" height="12" fill="#FCD34D"/>
<circle cx="55" cy="58" r="38" fill="#FCD34D"/>
<circle cx="19" cy="51" r="9" fill="#FCD34D"/><circle cx="91" cy="51" r="9" fill="#FCD34D"/>
<circle cx="41" cy="55" r="9" fill="white"/><circle cx="69" cy="55" r="9" fill="white"/>
<circle cx="43" cy="57" r="5" fill="#1F2937"/><circle cx="71" cy="57" r="5" fill="#1F2937"/>
<circle cx="44" cy="55" r="2" fill="white"/><circle cx="72" cy="55" r="2" fill="white"/>
<path d="M33 44 Q41 40 49 44" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<path d="M59 42 Q67 39 75 43" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<path d="M40 71 Q55 79 70 71" stroke="#92400E" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="30" cy="66" r="7" fill="#FCA5A5" opacity="0.45"/>
<circle cx="80" cy="66" r="7" fill="#FCA5A5" opacity="0.45"/>
<rect x="25" y="24" width="60" height="9" rx="2.5" fill="#312E81"/>
<polygon points="55,11 25,25 85,25" fill="#1E1B4B"/>
<line x1="82" y1="25" x2="89" y2="40" stroke="#FCD34D" stroke-width="3" stroke-linecap="round"/>
<circle cx="89" cy="43" r="4.5" fill="#FCD34D"/>
<circle cx="95" cy="20" r="8" fill="white" stroke="#C7D2FE" stroke-width="2"/>
<circle cx="104" cy="9" r="5.5" fill="white" stroke="#C7D2FE" stroke-width="2"/>
<circle cx="110" cy="1" r="3.5" fill="white" stroke="#C7D2FE" stroke-width="1.5"/>
</svg>"""

_LEO_CELEBRATE = """<svg width="148" height="188" viewBox="0 0 148 188" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="74" cy="184" rx="33" ry="7" fill="rgba(16,185,129,0.15)"/>
<rect x="38" y="120" width="70" height="60" rx="22" fill="#10B981"/>
<path d="M40 128 Q18 108 16 83" stroke="#10B981" stroke-width="15" fill="none" stroke-linecap="round"/>
<circle cx="15" cy="78" r="11" fill="#FCD34D"/>
<text x="2" y="70" font-size="18">🏆</text>
<path d="M108 128 Q128 108 128 83" stroke="#10B981" stroke-width="15" fill="none" stroke-linecap="round"/>
<circle cx="129" cy="78" r="11" fill="#FCD34D"/>
<text x="118" y="70" font-size="18">⭐</text>
<rect x="62" y="110" width="24" height="13" fill="#FCD34D"/>
<circle cx="74" cy="76" r="46" fill="#FCD34D"/>
<circle cx="30" cy="66" r="12" fill="#FCD34D"/><circle cx="118" cy="66" r="12" fill="#FCD34D"/>
<path d="M54 70 Q62 62 70 70" stroke="#1F2937" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<path d="M78 70 Q86 62 94 70" stroke="#1F2937" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<path d="M50 88 Q74 110 98 88" stroke="#92400E" stroke-width="4" fill="none" stroke-linecap="round"/>
<circle cx="43" cy="84" r="11" fill="#FCA5A5" opacity="0.6"/>
<circle cx="105" cy="84" r="11" fill="#FCA5A5" opacity="0.6"/>
<rect x="34" y="32" width="80" height="12" rx="3.5" fill="#312E81"/>
<polygon points="74,14 32,34 116,34" fill="#1E1B4B"/>
<line x1="112" y1="34" x2="121" y2="54" stroke="#FCD34D" stroke-width="4" stroke-linecap="round"/>
<circle cx="121" cy="58" r="6" fill="#FCD34D"/>
<rect x="8" y="18" width="8" height="8" rx="2" fill="#F59E0B" transform="rotate(20 12 22)"/>
<rect x="126" y="13" width="7" height="7" rx="2" fill="#6366F1" transform="rotate(-15 129 16)"/>
<rect x="18" y="48" width="6" height="6" rx="1.5" fill="#EF4444" transform="rotate(35 21 51)"/>
<rect x="133" y="43" width="8" height="8" rx="2" fill="#10B981" transform="rotate(-25 137 47)"/>
<circle cx="13" cy="88" r="5" fill="#F59E0B" opacity="0.7"/>
<circle cx="136" cy="98" r="4" fill="#6366F1" opacity="0.7"/>
</svg>"""

# ── NOVA  (Lavender skin · Teal body · Star clip) ─────────────────────────────
_NOVA_WAVE = """<svg width="130" height="175" viewBox="0 0 130 175" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="65" cy="171" rx="30" ry="6" fill="rgba(20,184,166,0.15)"/>
<rect x="32" y="112" width="66" height="55" rx="20" fill="#14B8A6"/>
<path d="M34 122 Q16 102 20 80" stroke="#14B8A6" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="19" cy="76" r="9" fill="#E879F9"/>
<path d="M96 130 Q112 142 110 158" stroke="#14B8A6" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="110" cy="162" r="9" fill="#E879F9"/>
<rect x="53" y="102" width="24" height="13" fill="#E879F9"/>
<circle cx="65" cy="70" r="42" fill="#E879F9"/>
<circle cx="25" cy="60" r="10" fill="#E879F9"/><circle cx="105" cy="60" r="10" fill="#E879F9"/>
<!-- Hair buns -->
<circle cx="40" cy="30" r="14" fill="#A855F7"/>
<circle cx="90" cy="30" r="14" fill="#A855F7"/>
<!-- Hair band -->
<path d="M28 58 Q65 42 102 58" stroke="#A855F7" stroke-width="8" fill="none"/>
<!-- Star clip -->
<text x="86" y="24" font-size="16">⭐</text>
<circle cx="50" cy="65" r="10" fill="white"/><circle cx="80" cy="65" r="10" fill="white"/>
<circle cx="52" cy="67" r="6" fill="#1F2937"/><circle cx="82" cy="67" r="6" fill="#1F2937"/>
<circle cx="54" cy="65" r="2.5" fill="white"/><circle cx="84" cy="65" r="2.5" fill="white"/>
<!-- Wink left eye -->
<path d="M42 65 Q50 60 58 65" stroke="#1F2937" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<path d="M46 82 Q65 97 84 82" stroke="#92400E" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<circle cx="38" cy="78" r="8" fill="#FCA5A5" opacity="0.6"/>
<circle cx="92" cy="78" r="8" fill="#FCA5A5" opacity="0.6"/>
<!-- Bow on head -->
<path d="M52 44 Q65 38 78 44" stroke="#F472B6" stroke-width="5" fill="none" stroke-linecap="round"/>
</svg>"""

_NOVA_THINK = """<svg width="110" height="148" viewBox="0 0 110 148" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="55" cy="144" rx="26" ry="6" fill="rgba(20,184,166,0.12)"/>
<rect x="22" y="96" width="66" height="46" rx="18" fill="#14B8A6"/>
<path d="M24 108 Q6 113 8 126" stroke="#14B8A6" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="9" cy="130" r="9" fill="#E879F9"/>
<path d="M86 108 Q100 114 98 128" stroke="#14B8A6" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="98" cy="132" r="9" fill="#E879F9"/>
<rect x="44" y="87" width="22" height="12" fill="#E879F9"/>
<circle cx="55" cy="58" r="38" fill="#E879F9"/>
<circle cx="19" cy="51" r="9" fill="#E879F9"/><circle cx="91" cy="51" r="9" fill="#E879F9"/>
<!-- Hair -->
<circle cx="30" cy="22" r="12" fill="#A855F7"/>
<circle cx="80" cy="22" r="12" fill="#A855F7"/>
<path d="M20 50 Q55 35 90 50" stroke="#A855F7" stroke-width="7" fill="none"/>
<text x="74" y="18" font-size="13">⭐</text>
<circle cx="41" cy="55" r="9" fill="white"/><circle cx="69" cy="55" r="9" fill="white"/>
<circle cx="43" cy="57" r="5" fill="#1F2937"/><circle cx="71" cy="57" r="5" fill="#1F2937"/>
<circle cx="44" cy="55" r="2" fill="white"/><circle cx="72" cy="55" r="2" fill="white"/>
<path d="M40 71 Q55 79 70 71" stroke="#92400E" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="30" cy="66" r="7" fill="#FCA5A5" opacity="0.5"/>
<circle cx="80" cy="66" r="7" fill="#FCA5A5" opacity="0.5"/>
<circle cx="95" cy="20" r="8" fill="white" stroke="#FBCFE8" stroke-width="2"/>
<circle cx="104" cy="9" r="5.5" fill="white" stroke="#FBCFE8" stroke-width="2"/>
<circle cx="110" cy="1" r="3.5" fill="white" stroke="#FBCFE8" stroke-width="1.5"/>
</svg>"""

# ── ROBO  (Silver · Blue body · Antenna) ─────────────────────────────────────
_ROBO_WAVE = """<svg width="130" height="175" viewBox="0 0 130 175" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="65" cy="171" rx="30" ry="6" fill="rgba(59,130,246,0.15)"/>
<!-- Body (rectangular) -->
<rect x="28" y="108" width="74" height="60" rx="12" fill="#3B82F6"/>
<rect x="36" y="116" width="58" height="8" rx="3" fill="#1D4ED8" opacity="0.4"/>
<!-- Chest panel -->
<rect x="44" y="128" width="42" height="28" rx="6" fill="#1D4ED8" opacity="0.3"/>
<circle cx="52" cy="138" r="5" fill="#60A5FA"/>
<circle cx="65" cy="138" r="5" fill="#34D399"/>
<circle cx="78" cy="138" r="5" fill="#F87171"/>
<!-- Arms -->
<rect x="8" y="112" width="22" height="10" rx="5" fill="#3B82F6"/>
<circle cx="8" cy="117" r="9" fill="#93C5FD"/>
<rect x="100" y="118" width="22" height="10" rx="5" fill="#3B82F6"/>
<circle cx="122" cy="123" r="9" fill="#93C5FD"/>
<!-- Neck -->
<rect x="55" y="100" width="20" height="12" rx="3" fill="#93C5FD"/>
<!-- Head (square) -->
<rect x="20" y="42" width="90" height="62" rx="18" fill="#BFDBFE"/>
<rect x="22" y="44" width="86" height="58" rx="16" fill="#DBEAFE"/>
<!-- Antenna -->
<line x1="65" y1="42" x2="65" y2="22" stroke="#93C5FD" stroke-width="4" stroke-linecap="round"/>
<circle cx="65" cy="18" r="8" fill="#F59E0B"/>
<circle cx="65" cy="18" r="4" fill="#FCD34D"/>
<!-- Eyes (LED screens) -->
<rect x="32" y="58" width="26" height="20" rx="6" fill="#1E40AF"/>
<rect x="72" y="58" width="26" height="20" rx="6" fill="#1E40AF"/>
<rect x="35" y="61" width="20" height="14" rx="4" fill="#60A5FA"/>
<rect x="75" y="61" width="20" height="14" rx="4" fill="#60A5FA"/>
<!-- Pupils (dots) -->
<circle cx="45" cy="68" r="5" fill="#1E3A8A"/>
<circle cx="85" cy="68" r="5" fill="#1E3A8A"/>
<circle cx="47" cy="66" r="2" fill="white"/>
<circle cx="87" cy="66" r="2" fill="white"/>
<!-- Mouth (line) -->
<rect x="40" y="88" width="50" height="8" rx="4" fill="#93C5FD"/>
<rect x="50" y="90" width="10" height="4" rx="2" fill="#3B82F6"/>
<rect x="70" y="90" width="10" height="4" rx="2" fill="#3B82F6"/>
</svg>"""

_ROBO_THINK = """<svg width="110" height="148" viewBox="0 0 110 148" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="55" cy="144" rx="26" ry="6" fill="rgba(59,130,246,0.12)"/>
<rect x="20" y="96" width="70" height="46" rx="12" fill="#3B82F6"/>
<rect x="26" y="104" width="58" height="6" rx="3" fill="#1D4ED8" opacity="0.35"/>
<!-- Chest -->
<rect x="36" y="114" width="38" height="20" rx="5" fill="#1D4ED8" opacity="0.3"/>
<circle cx="44" cy="124" r="4" fill="#60A5FA"/>
<circle cx="55" cy="124" r="4" fill="#34D399"/>
<circle cx="66" cy="124" r="4" fill="#F87171"/>
<!-- Arms -->
<rect x="4" y="100" width="18" height="9" rx="4.5" fill="#3B82F6"/>
<circle cx="4" cy="104" r="8" fill="#93C5FD"/>
<rect x="88" y="106" width="18" height="9" rx="4.5" fill="#3B82F6"/>
<circle cx="106" cy="110" r="8" fill="#93C5FD"/>
<!-- Neck -->
<rect x="45" y="88" width="20" height="11" rx="3" fill="#93C5FD"/>
<!-- Head -->
<rect x="12" y="36" width="86" height="56" rx="16" fill="#BFDBFE"/>
<rect x="14" y="38" width="82" height="52" rx="14" fill="#DBEAFE"/>
<!-- Antenna -->
<line x1="55" y1="36" x2="55" y2="20" stroke="#93C5FD" stroke-width="3.5" stroke-linecap="round"/>
<circle cx="55" cy="16" r="7" fill="#F59E0B"/>
<circle cx="55" cy="16" r="3.5" fill="#FCD34D"/>
<!-- Eyes (thinking — one squinted) -->
<rect x="20" y="50" width="24" height="18" rx="5" fill="#1E40AF"/>
<rect x="66" y="50" width="24" height="18" rx="5" fill="#1E40AF"/>
<rect x="23" y="53" width="18" height="12" rx="3.5" fill="#60A5FA"/>
<rect x="69" y="53" width="18" height="12" rx="3.5" fill="#60A5FA"/>
<circle cx="32" cy="59" r="5" fill="#1E3A8A"/><circle cx="78" cy="59" r="5" fill="#1E3A8A"/>
<circle cx="34" cy="57" r="2" fill="white"/><circle cx="80" cy="57" r="2" fill="white"/>
<!-- Processing dots -->
<rect x="30" y="78" width="50" height="7" rx="3.5" fill="#93C5FD"/>
<!-- Thought circles (gears) -->
<circle cx="94" cy="22" r="8" fill="white" stroke="#BFDBFE" stroke-width="2"/>
<text x="89" y="27" font-size="11">⚙️</text>
<circle cx="103" cy="10" r="5.5" fill="white" stroke="#BFDBFE" stroke-width="2"/>
<circle cx="109" cy="2" r="3.5" fill="white" stroke="#BFDBFE" stroke-width="1.5"/>
</svg>"""

# ── KIMI  (Orange · Cat ears · Whiskers) ─────────────────────────────────────
_KIMI_WAVE = """<svg width="130" height="175" viewBox="0 0 130 175" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="65" cy="171" rx="30" ry="6" fill="rgba(249,115,22,0.15)"/>
<rect x="32" y="112" width="66" height="55" rx="20" fill="#F97316"/>
<path d="M34 122 Q16 102 20 80" stroke="#F97316" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="19" cy="76" r="9" fill="#FED7AA"/>
<path d="M96 130 Q112 142 110 158" stroke="#F97316" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="110" cy="162" r="9" fill="#FED7AA"/>
<rect x="53" y="102" width="24" height="13" fill="#FED7AA"/>
<circle cx="65" cy="70" r="42" fill="#FED7AA"/>
<!-- Cat ears -->
<polygon points="30,38 18,12 46,30" fill="#FED7AA"/>
<polygon points="34,36 24,16 46,30" fill="#FBBF24"/>
<polygon points="100,38 112,12 84,30" fill="#FED7AA"/>
<polygon points="96,36 106,16 84,30" fill="#FBBF24"/>
<!-- Inner face -->
<ellipse cx="65" cy="78" rx="28" ry="22" fill="#FBBF24" opacity="0.4"/>
<!-- Eyes (cat slits) -->
<ellipse cx="50" cy="65" rx="10" ry="10" fill="white"/>
<ellipse cx="80" cy="65" rx="10" ry="10" fill="white"/>
<ellipse cx="50" cy="67" rx="4" ry="6" fill="#1F2937"/>
<ellipse cx="80" cy="67" rx="4" ry="6" fill="#1F2937"/>
<circle cx="51" cy="65" r="2" fill="white"/>
<circle cx="81" cy="65" r="2" fill="white"/>
<!-- Nose -->
<polygon points="65,76 62,80 68,80" fill="#F472B6"/>
<!-- Mouth -->
<path d="M62 80 Q65 84 68 80" stroke="#92400E" stroke-width="2" fill="none"/>
<path d="M46 82 Q55 88 62 82" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<path d="M68 82 Q75 88 84 82" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<!-- Whiskers -->
<line x1="18" y1="78" x2="48" y2="78" stroke="#92400E" stroke-width="1.5" opacity="0.6"/>
<line x1="18" y1="83" x2="48" y2="81" stroke="#92400E" stroke-width="1.5" opacity="0.6"/>
<line x1="82" y1="78" x2="112" y2="78" stroke="#92400E" stroke-width="1.5" opacity="0.6"/>
<line x1="82" y1="81" x2="112" y2="83" stroke="#92400E" stroke-width="1.5" opacity="0.6"/>
<!-- Collar -->
<rect x="44" y="108" width="42" height="10" rx="5" fill="#F472B6"/>
<circle cx="65" cy="113" r="4" fill="#FCD34D"/>
</svg>"""

_KIMI_THINK = """<svg width="110" height="148" viewBox="0 0 110 148" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="55" cy="144" rx="26" ry="6" fill="rgba(249,115,22,0.12)"/>
<rect x="22" y="96" width="66" height="46" rx="18" fill="#F97316"/>
<path d="M24 108 Q6 113 8 126" stroke="#F97316" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="9" cy="130" r="9" fill="#FED7AA"/>
<path d="M86 108 Q100 114 98 128" stroke="#F97316" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="98" cy="132" r="9" fill="#FED7AA"/>
<rect x="44" y="87" width="22" height="12" fill="#FED7AA"/>
<circle cx="55" cy="58" r="38" fill="#FED7AA"/>
<!-- Cat ears -->
<polygon points="24,32 14,10 38,26" fill="#FED7AA"/>
<polygon points="27,30 19,13 38,26" fill="#FBBF24"/>
<polygon points="86,32 96,10 72,26" fill="#FED7AA"/>
<polygon points="83,30 91,13 72,26" fill="#FBBF24"/>
<circle cx="19" cy="51" r="9" fill="#FED7AA"/><circle cx="91" cy="51" r="9" fill="#FED7AA"/>
<ellipse cx="41" cy="56" rx="9" ry="9" fill="white"/>
<ellipse cx="69" cy="56" rx="9" ry="9" fill="white"/>
<ellipse cx="41" cy="58" rx="3.5" ry="5.5" fill="#1F2937"/>
<ellipse cx="69" cy="58" rx="3.5" ry="5.5" fill="#1F2937"/>
<circle cx="42" cy="56" r="1.8" fill="white"/><circle cx="70" cy="56" r="1.8" fill="white"/>
<polygon points="55,69 52,73 58,73" fill="#F472B6"/>
<path d="M52 73 Q55 77 58 73" stroke="#92400E" stroke-width="2" fill="none"/>
<line x1="14" y1="67" x2="40" y2="68" stroke="#92400E" stroke-width="1.5" opacity="0.5"/>
<line x1="70" y1="68" x2="96" y2="67" stroke="#92400E" stroke-width="1.5" opacity="0.5"/>
<rect x="38" y="88" width="34" height="8" rx="4" fill="#F472B6"/>
<circle cx="55" cy="92" r="3" fill="#FCD34D"/>
<circle cx="95" cy="18" r="8" fill="white" stroke="#FED7AA" stroke-width="2"/>
<text x="90" y="24" font-size="12">🐾</text>
<circle cx="103" cy="8" r="5" fill="white" stroke="#FED7AA" stroke-width="1.5"/>
<circle cx="109" cy="1" r="3" fill="white" stroke="#FED7AA" stroke-width="1.5"/>
</svg>"""

# ── SOL  (Warm yellow · Sun · Green body) ─────────────────────────────────────
_SOL_WAVE = """<svg width="130" height="175" viewBox="0 0 130 175" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="65" cy="171" rx="30" ry="6" fill="rgba(234,179,8,0.15)"/>
<rect x="32" y="112" width="66" height="55" rx="20" fill="#EAB308"/>
<path d="M34 122 Q16 102 20 80" stroke="#EAB308" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="19" cy="76" r="9" fill="#FDE68A"/>
<path d="M96 130 Q112 142 110 158" stroke="#EAB308" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="110" cy="162" r="9" fill="#FDE68A"/>
<rect x="53" y="102" width="24" height="13" fill="#FDE68A"/>
<circle cx="65" cy="70" r="42" fill="#FDE68A"/>
<!-- Sun rays as hair spikes -->
<line x1="65" y1="28" x2="65" y2="14" stroke="#F59E0B" stroke-width="5" stroke-linecap="round"/>
<line x1="82" y1="32" x2="92" y2="20" stroke="#F59E0B" stroke-width="5" stroke-linecap="round"/>
<line x1="92" y1="47" x2="106" y2="40" stroke="#F59E0B" stroke-width="5" stroke-linecap="round"/>
<line x1="48" y1="32" x2="38" y2="20" stroke="#F59E0B" stroke-width="5" stroke-linecap="round"/>
<line x1="38" y1="47" x2="24" y2="40" stroke="#F59E0B" stroke-width="5" stroke-linecap="round"/>
<circle cx="22" cy="58" r="10" fill="#FDE68A"/><circle cx="108" cy="58" r="10" fill="#FDE68A"/>
<!-- Sunglasses -->
<rect x="35" y="59" width="26" height="16" rx="8" fill="#1F2937"/>
<rect x="69" y="59" width="26" height="16" rx="8" fill="#1F2937"/>
<rect x="61" y="64" width="8" height="3" rx="1.5" fill="#1F2937"/>
<rect x="37" y="61" width="22" height="12" rx="6" fill="#3B82F6" opacity="0.7"/>
<rect x="71" y="61" width="22" height="12" rx="6" fill="#3B82F6" opacity="0.7"/>
<circle cx="44" cy="66" r="4" fill="white" opacity="0.4"/>
<circle cx="78" cy="66" r="4" fill="white" opacity="0.4"/>
<!-- Big smile -->
<path d="M44 84 Q65 100 86 84" stroke="#92400E" stroke-width="4" fill="none" stroke-linecap="round"/>
<circle cx="36" cy="79" r="8" fill="#FCA5A5" opacity="0.55"/>
<circle cx="94" cy="79" r="8" fill="#FCA5A5" opacity="0.55"/>
</svg>"""

_SOL_THINK = """<svg width="110" height="148" viewBox="0 0 110 148" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="55" cy="144" rx="26" ry="6" fill="rgba(234,179,8,0.12)"/>
<rect x="22" y="96" width="66" height="46" rx="18" fill="#EAB308"/>
<path d="M24 108 Q6 113 8 126" stroke="#EAB308" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="9" cy="130" r="9" fill="#FDE68A"/>
<path d="M86 108 Q100 114 98 128" stroke="#EAB308" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="98" cy="132" r="9" fill="#FDE68A"/>
<rect x="44" y="87" width="22" height="12" fill="#FDE68A"/>
<circle cx="55" cy="58" r="38" fill="#FDE68A"/>
<!-- Sun rays -->
<line x1="55" y1="20" x2="55" y2="9" stroke="#F59E0B" stroke-width="4" stroke-linecap="round"/>
<line x1="69" y1="23" x2="76" y2="14" stroke="#F59E0B" stroke-width="4" stroke-linecap="round"/>
<line x1="79" y1="34" x2="88" y2="28" stroke="#F59E0B" stroke-width="4" stroke-linecap="round"/>
<line x1="41" y1="23" x2="34" y2="14" stroke="#F59E0B" stroke-width="4" stroke-linecap="round"/>
<line x1="31" y1="34" x2="22" y2="28" stroke="#F59E0B" stroke-width="4" stroke-linecap="round"/>
<circle cx="19" cy="51" r="9" fill="#FDE68A"/><circle cx="91" cy="51" r="9" fill="#FDE68A"/>
<!-- Sunglasses (pushed up on forehead for thinking) -->
<rect x="28" y="42" width="22" height="12" rx="6" fill="#1F2937" opacity="0.6"/>
<rect x="60" y="42" width="22" height="12" rx="6" fill="#1F2937" opacity="0.6"/>
<rect x="50" y="46" width="10" height="3" rx="1.5" fill="#1F2937" opacity="0.6"/>
<!-- Regular eyes -->
<circle cx="41" cy="58" r="9" fill="white"/><circle cx="69" cy="58" r="9" fill="white"/>
<circle cx="43" cy="60" r="5" fill="#1F2937"/><circle cx="71" cy="60" r="5" fill="#1F2937"/>
<circle cx="44" cy="58" r="2" fill="white"/><circle cx="72" cy="58" r="2" fill="white"/>
<path d="M40 74 Q55 82 70 74" stroke="#92400E" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="30" cy="68" r="7" fill="#FCA5A5" opacity="0.45"/>
<circle cx="80" cy="68" r="7" fill="#FCA5A5" opacity="0.45"/>
<circle cx="95" cy="20" r="8" fill="white" stroke="#FDE68A" stroke-width="2"/>
<text x="90" y="26" font-size="12">☀️</text>
<circle cx="104" cy="9" r="5.5" fill="white" stroke="#FDE68A" stroke-width="2"/>
<circle cx="110" cy="1" r="3.5" fill="white" stroke="#FDE68A" stroke-width="1.5"/>
</svg>"""

# ── BISCUIT  (Brown dog · Floppy ears · Collar) ───────────────────────────────
_BISCUIT_WAVE = """<svg width="130" height="175" viewBox="0 0 130 175" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="65" cy="171" rx="30" ry="6" fill="rgba(180,83,9,0.15)"/>
<rect x="32" y="112" width="66" height="55" rx="20" fill="#B45309"/>
<path d="M34 122 Q16 102 20 80" stroke="#B45309" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="19" cy="76" r="9" fill="#FDE68A"/>
<path d="M96 130 Q112 142 110 158" stroke="#B45309" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="110" cy="162" r="9" fill="#FDE68A"/>
<rect x="53" y="102" width="24" height="13" fill="#FDE68A"/>
<circle cx="65" cy="68" r="42" fill="#D97706"/>
<ellipse cx="65" cy="74" rx="26" ry="20" fill="#FDE68A"/>
<ellipse cx="28" cy="68" rx="14" ry="24" fill="#92400E" transform="rotate(-15 28 68)"/>
<ellipse cx="102" cy="68" rx="14" ry="24" fill="#92400E" transform="rotate(15 102 68)"/>
<ellipse cx="28" cy="72" rx="9" ry="18" fill="#B45309" opacity="0.5" transform="rotate(-15 28 72)"/>
<ellipse cx="102" cy="72" rx="9" ry="18" fill="#B45309" opacity="0.5" transform="rotate(15 102 72)"/>
<circle cx="50" cy="63" r="10" fill="white"/><circle cx="80" cy="63" r="10" fill="white"/>
<circle cx="52" cy="65" r="6" fill="#1F2937"/><circle cx="82" cy="65" r="6" fill="#1F2937"/>
<circle cx="54" cy="63" r="2.5" fill="white"/><circle cx="84" cy="63" r="2.5" fill="white"/>
<ellipse cx="65" cy="79" rx="10" ry="7" fill="#92400E"/>
<circle cx="65" cy="76" r="6" fill="#F472B6"/>
<path d="M55 81 Q65 92 75 81" stroke="#92400E" stroke-width="3" fill="none" stroke-linecap="round"/>
<path d="M52 82 Q48 90 44 82" stroke="#D97706" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<path d="M78 82 Q82 90 86 82" stroke="#D97706" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<circle cx="37" cy="76" r="8" fill="#FCA5A5" opacity="0.45"/>
<circle cx="93" cy="76" r="8" fill="#FCA5A5" opacity="0.45"/>
<rect x="44" y="107" width="42" height="10" rx="5" fill="#DC2626"/>
<circle cx="65" cy="112" r="5" fill="#FCD34D"/>
<ellipse cx="105" cy="100" rx="7" ry="5" fill="#92400E" transform="rotate(30 105 100)"/>
</svg>"""

_BISCUIT_THINK = """<svg width="110" height="148" viewBox="0 0 110 148" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="55" cy="144" rx="26" ry="6" fill="rgba(180,83,9,0.12)"/>
<rect x="22" y="96" width="66" height="46" rx="18" fill="#B45309"/>
<path d="M24 108 Q6 113 8 126" stroke="#B45309" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="9" cy="130" r="9" fill="#FDE68A"/>
<path d="M86 108 Q100 114 98 128" stroke="#B45309" stroke-width="13" fill="none" stroke-linecap="round"/>
<circle cx="98" cy="132" r="9" fill="#FDE68A"/>
<rect x="44" y="87" width="22" height="12" fill="#FDE68A"/>
<circle cx="55" cy="56" r="38" fill="#D97706"/>
<ellipse cx="55" cy="62" rx="22" ry="17" fill="#FDE68A"/>
<ellipse cx="22" cy="58" rx="12" ry="20" fill="#92400E" transform="rotate(-15 22 58)"/>
<ellipse cx="88" cy="58" rx="12" ry="20" fill="#92400E" transform="rotate(15 88 58)"/>
<ellipse cx="22" cy="62" rx="7.5" ry="15" fill="#B45309" opacity="0.5" transform="rotate(-15 22 62)"/>
<ellipse cx="88" cy="62" rx="7.5" ry="15" fill="#B45309" opacity="0.5" transform="rotate(15 88 62)"/>
<circle cx="41" cy="53" r="9" fill="white"/><circle cx="69" cy="53" r="9" fill="white"/>
<circle cx="43" cy="55" r="5" fill="#1F2937"/><circle cx="71" cy="55" r="5" fill="#1F2937"/>
<circle cx="44" cy="53" r="2" fill="white"/><circle cx="72" cy="53" r="2" fill="white"/>
<path d="M32 43 Q41 39 49 43" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<path d="M59 41 Q67 37 75 41" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<ellipse cx="55" cy="67" rx="8" ry="6" fill="#92400E"/>
<circle cx="55" cy="65" r="5" fill="#F472B6"/>
<path d="M46 69 Q55 78 64 69" stroke="#92400E" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<circle cx="30" cy="65" r="7" fill="#FCA5A5" opacity="0.4"/>
<circle cx="80" cy="65" r="7" fill="#FCA5A5" opacity="0.4"/>
<rect x="36" y="88" width="38" height="8" rx="4" fill="#DC2626"/>
<circle cx="55" cy="92" r="4" fill="#FCD34D"/>
<circle cx="95" cy="20" r="8" fill="white" stroke="#FDE68A" stroke-width="2"/>
<text x="90" y="26" font-size="12">🐾</text>
<circle cx="103" cy="9" r="5.5" fill="white" stroke="#FDE68A" stroke-width="2"/>
<circle cx="109" cy="1" r="3.5" fill="white" stroke="#FDE68A" stroke-width="1.5"/>
</svg>"""

# ── Character pools ────────────────────────────────────────────────────────────
_WAVE_CHARS = [
    (_LEO_WAVE, ""),
    (_NOVA_WAVE, "sb-pink"),
    (_KIMI_WAVE, "sb-orange"),
    (_SOL_WAVE, "sb-yellow"),
    (_BISCUIT_WAVE, "sb-orange"),
]

_THINK_CHARS = [
    (_LEO_THINK, ""),
    (_NOVA_THINK, "sb-pink"),
    (_ROBO_THINK, ""),
    (_KIMI_THINK, "sb-orange"),
    (_SOL_THINK, "sb-yellow"),
    (_BISCUIT_THINK, "sb-orange"),
]

_CELEBRATE_CHARS = [
    (_LEO_CELEBRATE, "sb-yellow"),
]

_WAVE_MSGS = [
    "Hi! Ready to discover your learning level? 🚀",
    "Hello! Let's see what you know! ✨",
    "Welcome! Time to shine! 🌟",
    "Hey there! Let's get started! 💪",
]

_THINK_MSGS = [
    "Think carefully! 🤔", "You've got this! 💪",
    "Take your time! ⏳", "Almost there! 🌟",
    "You know this! 💡", "Great question! 🔬",
    "Keep it up! 🎯", "Stay focused! 👀",
]

_CELEBRATE_MSGS = {
    1: "Keep going! Every step counts! 💪",
    2: "Good effort! You're improving! 📈",
    3: "Well done! You're on track! ⭐",
    4: "Outstanding! You're a star! 🏆",
}


def _render(svg: str, bubble_class: str, message: str):
    st.markdown(_BUBBLE_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<div class="char-wrap"><div class="speech-bubble {bubble_class}">{message}</div>{svg}</div>',
        unsafe_allow_html=True,
    )


def character_wave(message: str | None = None, seed: int = 0):
    svg, cls = _WAVE_CHARS[seed % len(_WAVE_CHARS)]
    msg = message or _WAVE_MSGS[seed % len(_WAVE_MSGS)]
    _render(svg, cls, msg)


def character_think(message: str | None = None, seed: int = 0):
    svg, cls = _THINK_CHARS[seed % len(_THINK_CHARS)]
    msg = message or _THINK_MSGS[seed % len(_THINK_MSGS)]
    _render(svg, cls, msg)


def character_celebrate(message: str | None = None, level: int = 3):
    svg, cls = _CELEBRATE_CHARS[0]
    msg = message or _CELEBRATE_MSGS.get(level, _CELEBRATE_MSGS[3])
    _render(svg, cls, msg)
