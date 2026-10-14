
import hashlib
import sqlite3
import time
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Risk Arena — Bireysel",
    page_icon="🎯",
    layout="centered",
)

DB_PATH = "risk_arena_v5.db"

# =========================================================
# GÖRSEL TASARIM
# =========================================================
st.markdown(
    """
    <style>
      .block-container {
        max-width: 960px;
        padding-top: 1.1rem;
        padding-bottom: 2.5rem;
      }

      .arena-hero {
        border: 1px solid #dbeafe;
        border-radius: 22px;
        padding: 1.35rem 1.5rem;
        background:
          radial-gradient(circle at top right, rgba(59,130,246,.13), transparent 32%),
          linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%);
        margin-bottom: 1rem;
      }
      .arena-hero h1 {
        margin: 0;
        font-size: 2.25rem;
        line-height: 1.05;
      }
      .arena-hero p {
        margin: .45rem 0 0 0;
        color: #475569;
        font-size: 1.03rem;
      }

      .player-strip {
        display:flex;
        flex-wrap:wrap;
        gap:.6rem;
        align-items:center;
        padding:.8rem 1rem;
        border-radius:16px;
        border:1px solid #e2e8f0;
        background:#f8fafc;
        margin-bottom:1rem;
      }
      .chip {
        display:inline-flex;
        align-items:center;
        gap:.35rem;
        padding:.35rem .65rem;
        border-radius:999px;
        background:#fff;
        border:1px solid #e2e8f0;
        font-size:.92rem;
        font-weight:700;
      }

      .mission-card {
        border:1px solid #e2e8f0;
        border-radius:18px;
        background:#fff;
        padding:1rem 1.1rem;
        margin:.75rem 0 1rem 0;
      }
      .mission-kicker {
        font-size:.82rem;
        font-weight:800;
        letter-spacing:.08em;
        text-transform:uppercase;
        color:#64748b;
      }
      .mission-card h3 {
        margin:.2rem 0 .35rem 0;
      }

      .power-card {
        border:1px solid #fde68a;
        background:linear-gradient(135deg,#fffbea,#fff7d6);
        border-radius:16px;
        padding:.9rem 1rem;
        margin:.75rem 0;
      }

      .success-box {
        border-left:5px solid #16a34a;
        background:#f0fdf4;
        padding:.85rem 1rem;
        border-radius:12px;
      }
      .warning-box {
        border-left:5px solid #f59e0b;
        background:#fffbeb;
        padding:.85rem 1rem;
        border-radius:12px;
      }
      .danger-box {
        border-left:5px solid #dc2626;
        background:#fef2f2;
        padding:.85rem 1rem;
        border-radius:12px;
      }

      .badge-grid {
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(145px,1fr));
        gap:.65rem;
        margin:.8rem 0;
      }
      .badge-card {
        border:1px solid #e2e8f0;
        border-radius:14px;
        padding:.75rem;
        background:#fff;
        text-align:center;
      }
      .badge-card.locked {
        opacity:.45;
        filter:grayscale(1);
      }
      .badge-icon {font-size:1.6rem;}
      .badge-name {font-weight:800;font-size:.9rem;margin-top:.2rem;}

      .boss {
        border:1px solid #fecaca;
        border-radius:18px;
        padding:1rem 1.1rem;
        background:linear-gradient(135deg,#fff7f7,#fff);
        margin:.8rem 0;
      }
      .boss-title {
        font-size:1.2rem;
        font-weight:900;
        margin-bottom:.3rem;
      }

      .rank-card {
        border:1px solid #dbeafe;
        border-radius:20px;
        padding:1rem 1.15rem;
        background:linear-gradient(135deg,#f8fbff,#ffffff);
        text-align:center;
      }
      .rank-medal {font-size:3rem;line-height:1;}
      .rank-title {font-size:1.25rem;font-weight:900;margin:.35rem 0;}
      .rank-sub {color:#64748b;font-size:.93rem;}

      .small-muted {font-size:.9rem;color:#64748b;}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# VERİTABANI — sadece öğretmen alanı için
# =========================================================
def db_conn():
    c = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    c.execute("PRAGMA journal_mode=WAL;")
    return c


def init_db():
    with db_conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS results(
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                avatar TEXT NOT NULL,
                role TEXT NOT NULL,
                base_score INTEGER NOT NULL,
                bonus_score INTEGER NOT NULL,
                crisis_score INTEGER NOT NULL,
                total_score INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                finished_at TEXT NOT NULL
            )
            """
        )
        c.commit()


def save_result():
    duration = int(time.time() - st.session_state.started_at)
    with db_conn() as c:
        c.execute(
            """
            INSERT OR REPLACE INTO results
            (id,name,avatar,role,base_score,bonus_score,crisis_score,total_score,duration,finished_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                st.session_state.player_id,
                st.session_state.name,
                st.session_state.avatar,
                st.session_state.role,
                int(st.session_state.base_score),
                int(st.session_state.bonus_score),
                int(st.session_state.crisis_score),
                int(total_score()),
                duration,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        c.commit()
    st.session_state.duration = duration


def teacher_results():
    with db_conn() as c:
        return pd.read_sql_query(
            """
            SELECT
              name AS Öğrenci,
              avatar AS Avatar,
              role AS Rol,
              total_score AS Toplam,
              base_score AS Bilgi,
              bonus_score AS Joker,
              crisis_score AS Kriz,
              duration AS Süre_sn,
              finished_at AS Bitiş
            FROM results
            ORDER BY total_score DESC, duration ASC
            """,
            c,
        )


init_db()

# =========================================================
# OYUN İÇERİĞİ
# =========================================================
ROUNDS = [
    {
        "icon": "🌐",
        "title": "1. Görev — ERM Radarı",
        "subtitle": "Riskleri tek tek değil, birlikte gör.",
        "type": "single",
        "base_max": 20,
        "question": "Hangisi Kurumsal Risk Yönetimi (ERM) yaklaşımını en iyi gösterir?",
        "options": [
            "BT biriminin yalnızca siber riskleri değerlendirmesi",
            "Finans biriminin yalnızca faiz riskine bakması",
            "Deprem senaryosunun hasar, yatırım, likidite, operasyon ve reasürans etkilerini birlikte değerlendirmek",
            "Yıllık sigorta poliçelerini yenilemek",
        ],
        "correct": "Deprem senaryosunun hasar, yatırım, likidite, operasyon ve reasürans etkilerini birlikte değerlendirmek",
        "explain": "ERM, riskleri ayrı kutular halinde değil; birbirleriyle bağlantılı bir risk portföyü olarak değerlendirir.",
        "badge": ("🌐", "ERM Kaşifi"),
    },
    {
        "icon": "🧭",
        "title": "2. Görev — Risk Komuta Merkezi",
        "subtitle": "Doğru rolü doğru sorumlulukla eşleştir.",
        "type": "matching",
        "each": 5,
        "base_max": 20,
        "options": ["Yönetim Kurulu", "İş Birimi", "Risk Yönetimi / CRO", "İç Denetim"],
        "items": [
            ("Günlük faaliyette riski üstlenir ve kontrolleri uygular.", "İş Birimi"),
            ("Genel risk iştahını ve risk çerçevesini onaylar.", "Yönetim Kurulu"),
            ("Riskleri ölçer, izler, limitleri takip eder ve sorgular.", "Risk Yönetimi / CRO"),
            ("Sistemin etkinliği hakkında bağımsız güvence verir.", "İç Denetim"),
        ],
        "explain": "İş birimi riski yönetir; CRO izler ve sorgular; iç denetim bağımsız güvence verir.",
        "badge": ("🧭", "Yönetişim Ustası"),
    },
    {
        "icon": "🛠️",
        "title": "3. Görev — Kontrol Laboratuvarı",
        "subtitle": "Risk kontrol araçlarını doğru yere yerleştir.",
        "type": "matching",
        "each": 5,
        "base_max": 30,
        "options": ["Riskten Kaçınma", "Kayıp Önleme", "Kayıp Azaltma", "Ayırma", "Çoğaltma", "Çeşitlendirme"],
        "items": [
            ("Taşkın riski çok yüksek bölgede fabrika kurmaktan vazgeçmek", "Riskten Kaçınma"),
            ("Elektrik sistemine periyodik bakım yaptırmak", "Kayıp Önleme"),
            ("Sprinkler sistemi kurmak", "Kayıp Azaltma"),
            ("Kritik stokları iki farklı depoda tutmak", "Ayırma"),
            ("Yedek veri merkezi kurmak", "Çoğaltma"),
            ("Tek tedarikçi yerine farklı tedarikçilerle çalışmak", "Çeşitlendirme"),
        ],
        "explain": "Kaçınma maruziyeti kaldırır; önleme sıklığı, azaltma şiddeti etkiler; ayırma böler, çoğaltma yedekler, çeşitlendirme bağımlılığı azaltır.",
        "badge": ("🛠️", "Kontrol Mimarı"),
    },
    {
        "icon": "🕵️",
        "title": "4. Görev — Risk Dedektifi",
        "subtitle": "Teknik olarak ölçülen risk mi değişti, algımız mı?",
        "type": "scenario_quiz",
        "each": 4,
        "base_max": 20,
        "scenarios": [
            {
                "title": "🔥 Olay 1 — Komşu Fabrikada Yangın",
                "text": (
                    "Yan fabrikada büyük bir yangın çıktı. Sizin fabrikanızda elektrik sistemi, "
                    "üretim süreci, bakım programı ve geçmiş hasar verileri değişmedi. "
                    "Buna rağmen yönetici “Yangın riskimiz artık çok daha yüksek.” diyor."
                ),
                "options": [
                    "A) Teknik olarak ölçülen risk değişti",
                    "B) Algılanan risk değişti",
                    "C) Her ikisi de değişti",
                    "D) Karar vermek için yeterli bilgi yok",
                ],
                "correct": "B) Algılanan risk değişti",
                "explain": (
                    "Yakındaki olay yöneticinin risk algısını artırmış olabilir. "
                    "Ancak işletmenin kendi teknik risk göstergelerinde yeni bir değişiklik yok."
                ),
            },
            {
                "title": "⚡ Olay 2 — Bakım Raporu Geldi",
                "text": (
                    "Teknik incelemede elektrik tesisatının eskidiği, son altı ayda küçük elektrik "
                    "arızalarının arttığı ve bazı güvenlik kontrollerinin geciktiği belirlendi."
                ),
                "options": [
                    "A) Teknik olarak ölçülen risk değişti",
                    "B) Algılanan risk değişti",
                    "C) Her ikisi de değişti",
                    "D) Karar vermek için yeterli bilgi yok",
                ],
                "correct": "A) Teknik olarak ölçülen risk değişti",
                "explain": (
                    "Burada yalnızca bir his veya endişe yok. Risk değerlendirmesini değiştirecek "
                    "yeni veri ve gözlemler var."
                ),
            },
            {
                "title": "🛡️ Olay 3 — “Biz Hazırız”",
                "text": (
                    "Şirket yeni bir acil durum tatbikatı yaptı. Yönetici “Artık bize hiçbir şey olmaz.” diyor. "
                    "Ancak yangının oluşma olasılığına ilişkin verilerde herhangi bir değişiklik yok."
                ),
                "options": [
                    "A) Teknik olarak ölçülen risk değişti",
                    "B) Algılanan risk değişti",
                    "C) Her ikisi de değişti",
                    "D) Karar vermek için yeterli bilgi yok",
                ],
                "correct": "B) Algılanan risk değişti",
                "explain": (
                    "Hazırlıklı olmak önemlidir; ancak kişinin kendisini daha güvende hissetmesi, "
                    "olayın gerçekleşme olasılığının otomatik olarak azaldığı anlamına gelmez."
                ),
            },
            {
                "title": "🚨 Olay 4 — Hem Veri Hem Algı",
                "text": (
                    "Son bir yılda iş kazalarının sayısı arttı, bakım gecikmeleri çoğaldı ve çalışanlar "
                    "işyerini eskisine göre daha tehlikeli bulmaya başladı."
                ),
                "options": [
                    "A) Teknik olarak ölçülen risk değişti",
                    "B) Algılanan risk değişti",
                    "C) Her ikisi de değişti",
                    "D) Karar vermek için yeterli bilgi yok",
                ],
                "correct": "C) Her ikisi de değişti",
                "explain": (
                    "Yeni veriler teknik risk değerlendirmesini değiştirirken çalışanların risk algısı da yükselmiştir."
                ),
            },
            {
                "title": "🎯 Final Kararı — Risk Yöneticisi Ne Yapmalı?",
                "text": (
                    "Bir yönetici bir riski çok tehlikeli hissediyor; ancak mevcut veriler bu görüşü desteklemiyor. "
                    "En uygun yaklaşım hangisidir?"
                ),
                "options": [
                    "A) Yöneticinin hissine göre hemen karar vermek",
                    "B) Riski tamamen görmezden gelmek",
                    "C) Algıyı dikkate almak, ancak kararı veri ve analizle kontrol etmek",
                    "D) Her durumda sigorta satın almak",
                ],
                "correct": "C) Algıyı dikkate almak, ancak kararı veri ve analizle kontrol etmek",
                "explain": (
                    "Risk yönetimi yalnızca sayılara bakmak değildir; yalnızca hislere dayanmak da değildir. "
                    "Veri değerlendirilir, insanların riski nasıl algıladığı da dikkate alınır."
                ),
            },
        ],
        "explain": (
            "Teknik olarak ölçülen risk; veri, gözlem, olasılık, sıklık ve kayıp şiddetine dayanır. "
            "Algılanan risk ise deneyim, duygu, güven ve kontrol hissinden etkilenebilir."
        ),
        "badge": ("🕵️", "Risk Dedektifi"),
    },
    {
        "icon": "⚖️",
        "title": "5. Görev — Risk Stratejisti",
        "subtitle": "Sıklık, şiddet ve kapasiteyi birlikte düşün.",
        "type": "matching",
        "each": 5,
        "base_max": 20,
        "options": ["Tutma", "Önleme + Tutma", "Azaltma + Sigorta / Transfer", "Kaçınma / Süreci Yeniden Tasarlama"],
        "items": [
            ("Nadiren oluşan ve küçük kalan ekipman hasarları", "Tutma"),
            ("Sık tekrarlanan fakat tek tek küçük iş kazaları", "Önleme + Tutma"),
            ("Nadiren gerçekleşen fakat çok büyük kayıp yaratabilecek fabrika yangını", "Azaltma + Sigorta / Transfer"),
            ("Sık gerçekleşen ve her seferinde çok büyük kayıp yaratan tehlikeli süreç", "Kaçınma / Süreci Yeniden Tasarlama"),
        ],
        "explain": "Sıklık ve şiddet başlangıç noktasıdır; kapasite, likidite, maliyet ve sigortalanabilirlik de kararı etkiler.",
        "badge": ("⚖️", "Risk Stratejisti"),
    },
    {
        "icon": "👾",
        "title": "6. Görev — BOSS: Kriz Odası",
        "subtitle": "10 bütçe puanıyla krize hazırlan.",
        "type": "crisis",
        "base_max": 40,
        "badge": ("👑", "Kriz Komutanı"),
    },
]

MEASURES = {
    "maintenance": {"label": "Bakım ve fiziksel risk azaltma", "cost": 2, "layer": "control", "icon": "🔧"},
    "bcp": {"label": "Acil durum + iş sürekliliği planı", "cost": 2, "layer": "control", "icon": "🗺️"},
    "it": {"label": "Yedek veri merkezi + MFA", "cost": 4, "layer": "control", "icon": "🖥️"},
    "reinsurance": {"label": "Reasürans korumasını güçlendir", "cost": 4, "layer": "finance", "icon": "🤝"},
    "liquidity": {"label": "Likidite tamponu oluştur", "cost": 3, "layer": "finance", "icon": "💰"},
    "supplier": {"label": "Kritik tedarikçileri çeşitlendir", "cost": 2, "layer": "control", "icon": "🚚"},
    "claims": {"label": "Hasar operasyonunda yedek kapasite", "cost": 2, "layer": "control", "icon": "📋"},
    "insurance": {"label": "Operasyonel riskler için ticari sigorta", "cost": 3, "layer": "finance", "icon": "🛡️"},
}

EVENTS = [
    {
        "name": "🌍 Büyük Deprem",
        "base": 40,
        "story": "Hasar ihbarları hızla arttı; bazı şubeler çalışamıyor; likidite ihtiyacı yükseldi; reasürans kritik hale geldi.",
        "p": {"maintenance": 5, "bcp": 7, "it": 7, "reinsurance": 12, "liquidity": 8, "supplier": 3, "claims": 6, "insurance": 5},
    },
    {
        "name": "🛡️ Siber Saldırı",
        "base": 35,
        "story": "Poliçe ve hasar sistemleri kesintiye uğradı; müşteri hizmetleri yavaşladı; iş sürekliliği ve itibar baskı altında.",
        "p": {"maintenance": 0, "bcp": 5, "it": 14, "reinsurance": 1, "liquidity": 4, "supplier": 3, "claims": 5, "insurance": 8},
    },
    {
        "name": "🌊 Büyük Hasar Dalgası",
        "base": 40,
        "story": "Kısa sürede çok sayıda yüksek tutarlı hasar geldi; nakit çıkışı ve hasar operasyonu baskı altında.",
        "p": {"maintenance": 2, "bcp": 4, "it": 3, "reinsurance": 14, "liquidity": 10, "supplier": 1, "claims": 8, "insurance": 2},
    },
    {
        "name": "🚚 Kritik Tedarikçi Kesintisi",
        "base": 32,
        "story": "Kritik bir hizmet tedarikçisi devre dışı kaldı; operasyon ve müşteri hizmetleri aksıyor.",
        "p": {"maintenance": 1, "bcp": 6, "it": 3, "reinsurance": 0, "liquidity": 4, "supplier": 14, "claims": 4, "insurance": 1},
    },
]

AVATARS = ["🛡️", "🧠", "🎯", "📊", "⚡", "🧭"]
ROLES = ["Risk Analisti", "Risk Muhafızı", "Strateji Mimarı", "Kriz Yöneticisi"]

BASE_TOTAL_MAX = sum(r["base_max"] for r in ROUNDS)  # 150

# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================
def daily_event():
    """Aynı gün oynayan herkes için aynı kriz: rekabet daha adil."""
    key = datetime.now().strftime("%Y-%m-%d")
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    idx = int(digest[:8], 16) % len(EVENTS)
    return EVENTS[idx]


def start_player(name, avatar, role):
    st.session_state.player_id = str(uuid.uuid4())
    st.session_state.name = name
    st.session_state.avatar = avatar
    st.session_state.role = role
    st.session_state.started_at = time.time()

    st.session_state.round_idx = 0
    st.session_state.base_score = 0
    st.session_state.bonus_score = 0
    st.session_state.crisis_score = 0

    st.session_state.joker_used = False
    st.session_state.feedback = {}
    st.session_state.badges = []
    st.session_state.perfect_streak = 0
    st.session_state.best_streak = 0
    st.session_state.celebrated_rounds = set()
    st.session_state.finished = False
    st.session_state.event = daily_event()


def ensure_state():
    if "name" not in st.session_state:
        return
    defaults = {
        "avatar": "🛡️",
        "role": "Risk Analisti",
        "base_score": 0,
        "bonus_score": 0,
        "crisis_score": 0,
        "round_idx": 0,
        "joker_used": False,
        "feedback": {},
        "badges": [],
        "perfect_streak": 0,
        "best_streak": 0,
        "celebrated_rounds": set(),
        "finished": False,
        "started_at": time.time(),
        "player_id": str(uuid.uuid4()),
        "event": daily_event(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def total_score():
    ensure_state()
    return int(st.session_state.base_score + st.session_state.bonus_score + st.session_state.crisis_score)


def level_info():
    xp = total_score()
    level = min(6, 1 + xp // 35)
    start_xp = (level - 1) * 35
    next_xp = level * 35
    if level >= 6:
        return level, 1.0, "MAX"
    progress = max(0.0, min(1.0, (xp - start_xp) / 35))
    return level, progress, str(next_xp - xp)


def round_is_perfect(round_idx, base_points):
    return base_points >= ROUNDS[round_idx]["base_max"]


def record_round(round_idx, base_points, joker_used=False, extra=None):
    bonus = base_points if joker_used else 0

    if round_idx < 5:
        st.session_state.base_score += base_points
        st.session_state.bonus_score += bonus
    else:
        st.session_state.crisis_score += base_points

    perfect = round_is_perfect(round_idx, base_points)
    if perfect:
        st.session_state.perfect_streak += 1
        if st.session_state.perfect_streak > st.session_state.best_streak:
            st.session_state.best_streak = st.session_state.perfect_streak
        icon, name = ROUNDS[round_idx]["badge"]
        if name not in [b["name"] for b in st.session_state.badges]:
            st.session_state.badges.append({"icon": icon, "name": name})
    else:
        st.session_state.perfect_streak = 0

    fb = {
        "base_points": base_points,
        "bonus_points": bonus,
        "perfect": perfect,
    }
    if extra:
        fb.update(extra)
    st.session_state.feedback[round_idx] = fb


def reset_session():
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def render_player_strip():
    level, _, _ = level_info()
    st.markdown(
        f"""
        <div class="player-strip">
          <span class="chip">{st.session_state.avatar} {st.session_state.name}</span>
          <span class="chip">🏷️ {st.session_state.role}</span>
          <span class="chip">⭐ XP {total_score()}</span>
          <span class="chip">⬆️ Seviye {level}</span>
          <span class="chip">🔥 Seri {st.session_state.perfect_streak}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_level():
    level, progress, to_next = level_info()
    c1, c2 = st.columns([1, 3])
    with c1:
        st.metric("Seviye", level)
    with c2:
        st.caption("Seviye ilerlemesi")
        st.progress(progress)
        if to_next == "MAX":
            st.caption("Maksimum seviyeye ulaştın.")
        else:
            st.caption(f"Sonraki seviyeye {to_next} XP")


def render_mission_map():
    ri = st.session_state.round_idx
    st.markdown("**Görev Haritası**")
    labels = []
    for i, r in enumerate(ROUNDS):
        if i < ri:
            mark = "✅"
        elif i == ri and not st.session_state.finished:
            mark = "▶️"
        else:
            mark = "🔒"
        labels.append(f"{mark} {r['icon']} {i+1}")
    st.caption("  →  ".join(labels))


def render_badges():
    unlocked = {b["name"] for b in st.session_state.badges}
    cards = []
    for r in ROUNDS:
        icon, name = r["badge"]
        locked = name not in unlocked
        cls = "badge-card locked" if locked else "badge-card"
        cards.append(
            f"<div class='{cls}'><div class='badge-icon'>{'🔒' if locked else icon}</div>"
            f"<div class='badge-name'>{name}</div></div>"
        )
    st.markdown("<div class='badge-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)


def performance_rank():
    performance = (st.session_state.base_score + st.session_state.crisis_score) / BASE_TOTAL_MAX
    if performance >= .90:
        return "🏆", "Risk Arena Eliti", "Kavramları ve karar mantığını çok güçlü biçimde birleştirdin."
    if performance >= .78:
        return "🥇", "Kıdemli Risk Stratejisti", "Güçlü performans. Karmaşık kararları büyük ölçüde doğru kuruyorsun."
    if performance >= .65:
        return "🥈", "Risk Stratejisti", "İyi düzey. Bazı karar alanlarında küçük tekrarlarla daha da güçlenebilirsin."
    if performance >= .50:
        return "🥉", "Risk Analisti", "Temel çerçeve oluşmuş durumda; özellikle kontrol ve finansman ayrımını pekiştir."
    return "🧩", "Risk Çırağı", "Temel kavramları yeniden gözden geçirip simülasyonu tekrar oynaman yararlı olur."


ensure_state()

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("🎯 Risk Arena")
    st.caption("BİREYSEL ÖĞRENCİ MODU")

    if "name" in st.session_state:
        st.markdown(f"### {st.session_state.avatar} {st.session_state.name}")
        st.caption(st.session_state.role)

        st.metric("XP", total_score())
        level, prog, _ = level_info()
        st.progress(prog)
        st.caption(f"Seviye {level} • En iyi seri: {st.session_state.best_streak}")

        if not st.session_state.finished:
            st.progress((st.session_state.round_idx + 1) / len(ROUNDS))
            st.caption(f"Görev {st.session_state.round_idx + 1} / {len(ROUNDS)}")

        st.caption("🎲 Risk Jokeri: " + ("Kullanıldı" if st.session_state.joker_used else "Hazır"))

    st.divider()
    st.caption("Başka öğrencilerin puanı ve cevabı öğrenci ekranında görünmez.")

    with st.expander("🔐 Öğretmen Alanı"):
        code = st.text_input("Öğretmen kodu", type="password", key="teacher_code_v5")
        if code == "sigo451":
            df = teacher_results()
            st.metric("Tamamlayan Öğrenci", len(df))
            if not df.empty:
                c1, c2 = st.columns(2)
                c1.metric("Sınıf Ortalaması", f"{df['Toplam'].mean():.1f}")
                c2.metric("En Yüksek XP", int(df["Toplam"].max()))
                st.dataframe(df, hide_index=True, use_container_width=True)
        elif code:
            st.error("Kod yanlış.")

    if st.button("↩️ Oturumu Sıfırla", use_container_width=True):
        reset_session()
        st.rerun()

# =========================================================
# GİRİŞ
# =========================================================
if "name" not in st.session_state:
    st.markdown(
        """
        <div class="arena-hero">
          <h1>🎯 Risk Arena</h1>
          <p>Bir sınav değil: risk yöneticisi gibi karar vereceğin bireysel görev serisi.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Görev", "6")
    c2.metric("Güç", "1 Risk Jokeri")
    c3.metric("Final", "👾 Kriz Boss'u")

    st.markdown("### Oyuncunu oluştur")

    with st.form("player_setup_v5"):
        name = st.text_input("Ad Soyad", placeholder="Örn. Ayşe Yılmaz")

        avatar = st.radio(
            "Avatarını seç",
            AVATARS,
            horizontal=True,
        )

        role = st.selectbox(
            "Risk rolünü seç",
            ROLES,
        )

        start = st.form_submit_button("🚀 ARENAYA GİR", type="primary", use_container_width=True)

    if start:
        clean = name.strip()
        if len(clean) < 2:
            st.error("Lütfen adını ve soyadını yaz.")
        else:
            start_player(clean, avatar, role)
            st.rerun()

    st.markdown(
        """
        <div class="mission-card">
          <div class="mission-kicker">OYUN MEKANİKLERİ</div>
          <h3>Nasıl puan kazanırsın?</h3>
          <p>
            Doğru kararlarla XP kazanırsın. Kusursuz tamamladığın görevler rozet açar.
            Bir kez kullanabileceğin <b>Risk Jokeri</b>, seçtiğin bilgi görevindeki puanını ikiye katlar.
            Son görevde 10 bütçe puanıyla gerçek bir kriz öncesi yatırım kararı verirsin.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# =========================================================
# FİNAL
# =========================================================
if st.session_state.finished:
    medal, rank_title, rank_text = performance_rank()

    st.markdown(
        f"""
        <div class="arena-hero">
          <h1>🏁 Arena Tamamlandı</h1>
          <p>{st.session_state.avatar} {st.session_state.name} • {st.session_state.role}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.balloons()

    st.markdown(
        f"""
        <div class="rank-card">
          <div class="rank-medal">{medal}</div>
          <div class="rank-title">{rank_title}</div>
          <div class="rank-sub">{rank_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam XP", total_score())
    c2.metric("Bilgi", st.session_state.base_score)
    c3.metric("Joker Bonusu", st.session_state.bonus_score)
    c4.metric("Kriz", st.session_state.crisis_score)

    st.caption(
        f"Tamamlama süresi: {st.session_state.duration // 60} dk {st.session_state.duration % 60} sn "
        f"• En iyi kusursuz görev serisi: {st.session_state.best_streak}"
    )

    st.markdown("### 🏅 Rozet Koleksiyonun")
    render_badges()

    st.markdown("### 🎓 Son Karar")
    st.markdown(
        """
        - ERM'de riskleri neden tek tek değil, birlikte değerlendirmek gerekir?
        - Risk sahibi ile CRO neden aynı rol değildir?
        - Bir riskte yalnız kontrol veya yalnız sigortaya güvenmek neden yetersiz kalabilir?
        - Kriz görevindeki kararını gerçek bir kurumda nasıl geliştirirdin?
        """
    )

    if st.button("🔁 Yeniden Oyna", type="primary", use_container_width=True):
        old_name = st.session_state.name
        old_avatar = st.session_state.avatar
        old_role = st.session_state.role
        reset_session()
        start_player(old_name, old_avatar, old_role)
        st.rerun()
    st.stop()

# =========================================================
# AKTİF GÖREV
# =========================================================
ri = st.session_state.round_idx
r = ROUNDS[ri]

st.markdown(
    f"""
    <div class="arena-hero">
      <h1>{r['icon']} {r['title']}</h1>
      <p>{r['subtitle']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

render_player_strip()
render_mission_map()
render_level()

# Cevaplanmış görev geri bildirimi
if ri in st.session_state.feedback:
    fb = st.session_state.feedback[ri]

    if fb["perfect"] and ri not in st.session_state.celebrated_rounds:
        st.session_state.celebrated_rounds.add(ri)
        st.balloons()

    earned = fb["base_points"] + fb["bonus_points"]
    if earned > 0:
        if fb["bonus_points"] > 0:
            st.success(f"⚡ Görev puanı: {fb['base_points']} + Joker bonusu: {fb['bonus_points']} = **{earned} XP**")
        else:
            st.success(f"⭐ Bu görevden **{earned} XP** kazandın.")
    else:
        st.warning("Bu görevden XP kazanamadın; açıklamayı inceleyip bir sonraki göreve geç.")

    if fb["perfect"]:
        icon, badge_name = r["badge"]
        st.markdown(
            f"<div class='success-box'><b>{icon} Kusursuz görev!</b> "
            f"<b>{badge_name}</b> rozeti açıldı. 🔥 Seri: {st.session_state.perfect_streak}</div>",
            unsafe_allow_html=True,
        )

    if r["type"] == "single":
        st.markdown(f"**Doğru cevap:** {r['correct']}")
        st.info(r["explain"])

    elif r["type"] == "scenario_quiz":
        st.markdown("### 🕵️ Risk Dedektifi — Doğru Kararlar")
        for i, s in enumerate(r["scenarios"], 1):
            st.markdown(f"**{i}. {s['title']}**")
            st.markdown(f"Doğru cevap: **{s['correct']}**")
            st.caption(s["explain"])
        st.info(r["explain"])

    elif r["type"] == "matching":
        st.markdown("**Doğru eşleştirmeler:**")
        for q, a in r["items"]:
            st.markdown(f"- {q} → **{a}**")
        st.info(r["explain"])

    elif r["type"] == "crisis":
        ev = fb["event"]
        st.markdown(
            f"""
            <div class="boss">
              <div class="boss-title">👾 KRİZ BOSS'U: {ev['name']}</div>
              <div>{ev['story']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**Kriz Dayanıklılığı**")
        resilience = max(0.0, min(1.0, 1 - fb["residual"] / max(1, ev["base"])))
        st.progress(resilience)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Bütçe", f"{fb['cost']}/10")
        c2.metric("Koruma", fb["protection"])
        c3.metric("Kalan Risk", fb["residual"])
        c4.metric("Kriz XP", f"{fb['base_points']}/40")

        if fb["layer_bonus"] > 0:
            st.markdown(
                "<div class='success-box'><b>+5 Katman Bonusu:</b> "
                "Risk kontrolü ile risk finansmanını birlikte kullandın.</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div class='warning-box'><b>Ders bağlantısı:</b> "
            "İyi risk yönetimi tek bir teknik seçmek değildir. Kontrol + finansman + likidite/sermaye "
            "birlikte düşünülür; yine de kalan risk tamamen yok olmayabilir.</div>",
            unsafe_allow_html=True,
        )

    button_label = "🏁 ARENAYI BİTİR" if ri == len(ROUNDS) - 1 else "➡️ SONRAKİ GÖREV"
    if st.button(button_label, type="primary", use_container_width=True):
        if ri == len(ROUNDS) - 1:
            save_result()
            st.session_state.finished = True
        else:
            st.session_state.round_idx += 1
        st.rerun()

    st.stop()

# =========================================================
# GÖREV FORMU
# =========================================================
if not st.session_state.joker_used and r["type"] != "crisis":
    st.markdown(
        """
        <div class="power-card">
          <b>🎲 RİSK JOKERİ HAZIR</b><br>
          Bu görevde kullanırsan kazandığın bilgi XP'si ikiye katlanır.
          Yanlış cevapta bonus gelmez.
        </div>
        """,
        unsafe_allow_html=True,
    )

if r["type"] == "single":
    with st.form(f"single_form_{ri}"):
        st.markdown(f"### 🎯 Karar Noktası")
        st.write(r["question"])

        answer = st.radio(
            "Cevabın",
            r["options"],
            index=None,
        )

        use_joker = False
        if not st.session_state.joker_used:
            use_joker = st.checkbox("🎲 Risk Jokerini kullan")

        submit = st.form_submit_button("🔒 KARARI KİLİTLE", type="primary", use_container_width=True)

    if submit:
        if answer is None:
            st.error("Önce bir cevap seç.")
        else:
            base_points = r["base_max"] if answer == r["correct"] else 0
            if use_joker:
                st.session_state.joker_used = True
            record_round(ri, base_points, use_joker)
            st.rerun()

elif r["type"] == "scenario_quiz":
    with st.form(f"scenario_form_{ri}"):
        st.markdown("### 🕵️ Risk Dedektifi Dosyaları")
        st.caption("Her olayda önce şu soruyu sor: Teknik veriler mi değişti, yoksa insanların risk algısı mı?")

        responses = {}
        for i, s in enumerate(r["scenarios"], 1):
            st.markdown(f"#### {s['title']}")
            st.write(s["text"])
            responses[i] = st.radio(
                f"{i}. kararın",
                s["options"],
                index=None,
                key=f"scenario_{ri}_{i}",
            )
            st.divider()

        use_joker = False
        if not st.session_state.joker_used:
            use_joker = st.checkbox("🎲 Risk Jokerini kullan")

        submit = st.form_submit_button("🔒 DOSYAYI KAPAT", type="primary", use_container_width=True)

    if submit:
        if any(v is None for v in responses.values()):
            st.error("Tüm olaylar için bir karar ver.")
        else:
            base_points = 0
            for i, s in enumerate(r["scenarios"], 1):
                if responses[i] == s["correct"]:
                    base_points += r["each"]

            if use_joker:
                st.session_state.joker_used = True

            record_round(ri, base_points, use_joker)
            st.rerun()

elif r["type"] == "matching":
    with st.form(f"matching_form_{ri}"):
        st.markdown("### 🧩 Eşleştirme Görevi")
        responses = {}

        for i, (q, _) in enumerate(r["items"], 1):
            st.markdown(f"**{i}. {q}**")
            responses[q] = st.selectbox(
                f"{i}. seçim",
                ["— Seçiniz —"] + r["options"],
                key=f"match_{ri}_{i}",
                label_visibility="collapsed",
            )

        use_joker = False
        if not st.session_state.joker_used:
            use_joker = st.checkbox("🎲 Risk Jokerini kullan")

        submit = st.form_submit_button("🔒 CEVAPLARI KİLİTLE", type="primary", use_container_width=True)

    if submit:
        if any(v == "— Seçiniz —" for v in responses.values()):
            st.error("Tüm eşleştirmeleri tamamla.")
        else:
            base_points = sum(r["each"] for q, a in r["items"] if responses[q] == a)
            if use_joker:
                st.session_state.joker_used = True
            record_round(ri, base_points, use_joker)
            st.rerun()

else:
    st.markdown(
        """
        <div class="boss">
          <div class="boss-title">👾 BOSS GÖREVİ: KRİZ HENÜZ GİZLİ</div>
          <div>
            Bir sigorta şirketinin risk komitesindesin. Elinde <b>10 bütçe puanı</b> var.
            Hangi krizin geleceğini bilmiyorsun. Yatırımlarını seç, sonra kriz açıklansın.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🛒 Risk Yatırım Pazarı")
    for key, m in MEASURES.items():
        st.markdown(
            f"**{m['icon']} {m['label']}** — Maliyet: **{m['cost']}** "
            f"• {'Kontrol' if m['layer']=='control' else 'Finansman'}"
        )

    display_to_id = {
        f"{m['icon']} {m['label']} • Maliyet {m['cost']}": key
        for key, m in MEASURES.items()
    }

    with st.form("crisis_strategy_form_v5"):
        selected_display = st.multiselect(
            "10 bütçe puanını aşmadan yatırımlarını seç",
            list(display_to_id.keys()),
        )
        submit = st.form_submit_button("⚔️ STRATEJİYİ KİLİTLE VE KRİZİ AÇ", type="primary", use_container_width=True)

    if submit:
        selected = [display_to_id[x] for x in selected_display]
        cost = sum(MEASURES[x]["cost"] for x in selected)

        if cost > 10:
            st.error(f"🚫 Bütçeyi aştın: {cost}/10. Bazı yatırımları çıkar.")
        elif not selected:
            st.error("En az bir yatırım seç.")
        else:
            ev = st.session_state.event
            protection = sum(ev["p"].get(x, 0) for x in selected)
            layers = {MEASURES[x]["layer"] for x in selected}
            layer_bonus = 5 if {"control", "finance"}.issubset(layers) else 0
            residual = max(0, ev["base"] - protection)

            crisis_points = min(40, max(0, 40 - residual + layer_bonus))

            record_round(
                ri,
                crisis_points,
                joker_used=False,
                extra={
                    "event": ev,
                    "cost": cost,
                    "protection": protection,
                    "residual": residual,
                    "layer_bonus": layer_bonus,
                    "selected": selected,
                },
            )
            st.rerun()
