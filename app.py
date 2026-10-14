
import random
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

DB_PATH = "risk_arena_results.db"

# -----------------------------
# Görünüm
# -----------------------------
st.markdown(
    """
    <style>
      .block-container {max-width: 900px; padding-top: 1.2rem; padding-bottom: 2rem;}
      .hero {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(135deg,#f8fbff,#eef6ff);
        border: 1px solid #dbeafe;
        margin-bottom: 1rem;
      }
      .hero h1 {margin:0; font-size:2.1rem;}
      .hero p {margin:.35rem 0 0 0; font-size:1.03rem;}
      .me {
        padding:.8rem 1rem;
        border-radius:14px;
        background:#f8fafc;
        border:1px solid #e2e8f0;
        margin-bottom:1rem;
      }
      .good {padding:.8rem 1rem; border-left:5px solid #16a34a; background:#f0fdf4; border-radius:10px;}
      .warn {padding:.8rem 1rem; border-left:5px solid #f59e0b; background:#fffbeb; border-radius:10px;}
      .danger {padding:.8rem 1rem; border-left:5px solid #dc2626; background:#fef2f2; border-radius:10px;}
      .small {font-size:.9rem;color:#64748b;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Ortak sonuç veritabanı
# Öğrenci ana ekranında ASLA gösterilmez.
# Sadece öğretmen alanında.
# -----------------------------
def conn():
    c = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    c.execute("PRAGMA journal_mode=WAL;")
    return c

def init_db():
    with conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS results(
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            knowledge INTEGER NOT NULL,
            crisis INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            finished_at TEXT NOT NULL
        )
        """)
        c.commit()

def save_result():
    duration = int(time.time() - st.session_state.started_at)
    with conn() as c:
        c.execute("""
        INSERT OR REPLACE INTO results
        (id,name,score,knowledge,crisis,duration,finished_at)
        VALUES(?,?,?,?,?,?,?)
        """, (
            st.session_state.player_id,
            st.session_state.name,
            st.session_state.knowledge + st.session_state.crisis_score,
            st.session_state.knowledge,
            st.session_state.crisis_score,
            duration,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        c.commit()
    st.session_state.duration = duration

def teacher_results():
    with conn() as c:
        return pd.read_sql_query("""
        SELECT name AS Öğrenci,
               score AS Toplam,
               knowledge AS Bilgi,
               crisis AS Kriz,
               duration AS Süre_sn,
               finished_at AS Bitiş
        FROM results
        ORDER BY score DESC, duration ASC
        """, c)

init_db()

# -----------------------------
# Soru seti
# -----------------------------
ROUNDS = [
    {
        "title":"1. Tur — ERM Radarı",
        "type":"single",
        "points":20,
        "question":"Hangisi Kurumsal Risk Yönetimi (ERM) yaklaşımını en iyi gösterir?",
        "options":[
            "BT biriminin yalnızca siber riskleri değerlendirmesi",
            "Finans biriminin yalnızca faiz riskine bakması",
            "Deprem senaryosunun hasar, yatırım, likidite, operasyon ve reasürans etkilerini birlikte değerlendirmek",
            "Yıllık sigorta poliçelerini yenilemek",
        ],
        "correct":"Deprem senaryosunun hasar, yatırım, likidite, operasyon ve reasürans etkilerini birlikte değerlendirmek",
        "explain":"ERM, riskleri tek tek değil; birbirleriyle bağlantılı bir risk portföyü olarak değerlendirir."
    },
    {
        "title":"2. Tur — Kim Ne Yapar?",
        "type":"matching",
        "each":5,
        "options":["Yönetim Kurulu","İş Birimi","Risk Yönetimi / CRO","İç Denetim"],
        "items":[
            ("Günlük faaliyette riski üstlenir ve kontrolleri uygular.","İş Birimi"),
            ("Genel risk iştahını ve risk çerçevesini onaylar.","Yönetim Kurulu"),
            ("Riskleri ölçer, izler, limitleri takip eder ve sorgular.","Risk Yönetimi / CRO"),
            ("Sistemin etkinliği hakkında bağımsız güvence verir.","İç Denetim"),
        ],
        "explain":"İş birimi riski yönetir; CRO izler ve sorgular; iç denetim bağımsız güvence verir."
    },
    {
        "title":"3. Tur — Kontrol Laboratuvarı",
        "type":"matching",
        "each":5,
        "options":["Riskten Kaçınma","Kayıp Önleme","Kayıp Azaltma","Ayırma","Çoğaltma","Çeşitlendirme"],
        "items":[
            ("Taşkın riski çok yüksek bölgede fabrika kurmaktan vazgeçmek","Riskten Kaçınma"),
            ("Elektrik sistemine periyodik bakım yaptırmak","Kayıp Önleme"),
            ("Sprinkler sistemi kurmak","Kayıp Azaltma"),
            ("Kritik stokları iki farklı depoda tutmak","Ayırma"),
            ("Yedek veri merkezi kurmak","Çoğaltma"),
            ("Tek tedarikçi yerine farklı tedarikçilerle çalışmak","Çeşitlendirme"),
        ],
        "explain":"Kaçınma maruziyeti kaldırır; önleme sıklığı, azaltma şiddeti etkiler; ayırma böler, çoğaltma yedekler, çeşitlendirme bağımlılığı azaltır."
    },
    {
        "title":"4. Tur — Zihin Tuzakları",
        "type":"matching",
        "each":4,
        "options":["Erişilebilirlik","Aşırı Güven","Kontrol Yanılsaması","Normalleşme","Çerçeveleme"],
        "items":[
            ("Yakındaki yangından sonra, kendi verisi değişmediği halde riski birden çok yüksek görmek","Erişilebilirlik"),
            ("“Tahminlerimiz hep tutuyor; bu yıl da rezerv kesin yeter.”","Aşırı Güven"),
            ("“Bizim ekip çok iyi; saldırı olursa zaten kontrol ederiz.”","Kontrol Yanılsaması"),
            ("“On yıldır büyük kaza olmadı; bundan sonra da olmaz.”","Normalleşme"),
            ("Aynı riski “%90 güvenli” ve “%10 kayıp ihtimali” ifadelerinde farklı değerlendirmek","Çerçeveleme"),
        ],
        "explain":"Teknik risk düzeyi aynı kalsa bile deneyim, güven, kontrol hissi ve sunuluş biçimi algılanan riski değiştirebilir."
    },
    {
        "title":"5. Tur — Hangi Riskte Hangi Yöntem?",
        "type":"matching",
        "each":5,
        "options":["Tutma","Önleme + Tutma","Azaltma + Sigorta / Transfer","Kaçınma / Süreci Yeniden Tasarlama"],
        "items":[
            ("Nadiren oluşan ve küçük kalan ekipman hasarları","Tutma"),
            ("Sık tekrarlanan fakat tek tek küçük iş kazaları","Önleme + Tutma"),
            ("Nadiren gerçekleşen fakat çok büyük kayıp yaratabilecek fabrika yangını","Azaltma + Sigorta / Transfer"),
            ("Sık gerçekleşen ve her seferinde çok büyük kayıp yaratan tehlikeli süreç","Kaçınma / Süreci Yeniden Tasarlama"),
        ],
        "explain":"Sıklık ve şiddet başlangıç noktasıdır; kapasite, likidite, maliyet ve sigortalanabilirlik de kararı etkiler."
    },
    {
        "title":"6. Tur — Kriz Odası",
        "type":"crisis",
    },
]

MEASURES = {
    "maintenance":{"label":"Bakım ve fiziksel risk azaltma","cost":2,"layer":"control"},
    "bcp":{"label":"Acil durum + iş sürekliliği planı","cost":2,"layer":"control"},
    "it":{"label":"Yedek veri merkezi + MFA","cost":4,"layer":"control"},
    "reinsurance":{"label":"Reasürans korumasını güçlendir","cost":4,"layer":"finance"},
    "liquidity":{"label":"Likidite tamponu oluştur","cost":3,"layer":"finance"},
    "supplier":{"label":"Kritik tedarikçileri çeşitlendir","cost":2,"layer":"control"},
    "claims":{"label":"Hasar operasyonunda yedek kapasite","cost":2,"layer":"control"},
    "insurance":{"label":"Operasyonel riskler için ticari sigorta","cost":3,"layer":"finance"},
}

EVENTS = [
    {
        "name":"🌍 Büyük Deprem",
        "base":40,
        "story":"Hasar ihbarları hızla arttı; bazı şubeler çalışamıyor; likidite ihtiyacı yükseldi; reasürans kritik hale geldi.",
        "p":{"maintenance":5,"bcp":7,"it":7,"reinsurance":12,"liquidity":8,"supplier":3,"claims":6,"insurance":5}
    },
    {
        "name":"🛡️ Siber Saldırı",
        "base":35,
        "story":"Poliçe ve hasar sistemleri kesintiye uğradı; müşteri hizmetleri yavaşladı; iş sürekliliği ve itibar baskı altında.",
        "p":{"maintenance":0,"bcp":5,"it":14,"reinsurance":1,"liquidity":4,"supplier":3,"claims":5,"insurance":8}
    },
    {
        "name":"🌊 Büyük Hasar Dalgası",
        "base":40,
        "story":"Kısa sürede çok sayıda yüksek tutarlı hasar geldi; nakit çıkışı ve hasar operasyonu baskı altında.",
        "p":{"maintenance":2,"bcp":4,"it":3,"reinsurance":14,"liquidity":10,"supplier":1,"claims":8,"insurance":2}
    },
    {
        "name":"🚚 Kritik Tedarikçi Kesintisi",
        "base":32,
        "story":"Kritik bir hizmet tedarikçisi devre dışı kaldı; operasyon ve müşteri hizmetleri aksıyor.",
        "p":{"maintenance":1,"bcp":6,"it":3,"reinsurance":0,"liquidity":4,"supplier":14,"claims":4,"insurance":1}
    },
]

# -----------------------------
# Session
# -----------------------------
def start_player(name):
    st.session_state.player_id = str(uuid.uuid4())
    st.session_state.name = name
    st.session_state.started_at = time.time()
    st.session_state.round = 0
    st.session_state.knowledge = 0
    st.session_state.crisis_score = 0
    st.session_state.joker_used = False
    st.session_state.feedback = {}
    st.session_state.finished = False
    rng = random.Random(st.session_state.player_id)
    st.session_state.event = rng.choice(EVENTS)

def ensure_player_state():
    """Eski uygulama sürümünden kalan tarayıcı oturumlarında eksik anahtarları güvenle tamamlar."""
    if "name" not in st.session_state:
        return

    if "knowledge" not in st.session_state:
        st.session_state.knowledge = 0

    if "crisis_score" not in st.session_state:
        # Eski sürümde "crisis" adı kullanılmış olabilir.
        legacy_value = st.session_state.get("crisis", 0)
        if isinstance(legacy_value, (int, float)):
            st.session_state.crisis_score = int(legacy_value)
        else:
            st.session_state.crisis_score = 0

    if "round" not in st.session_state:
        st.session_state.round = 0
    if "joker_used" not in st.session_state:
        st.session_state.joker_used = False
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "finished" not in st.session_state:
        st.session_state.finished = False
    if "started_at" not in st.session_state:
        st.session_state.started_at = time.time()
    if "player_id" not in st.session_state:
        st.session_state.player_id = str(uuid.uuid4())
    if "event" not in st.session_state:
        rng = random.Random(st.session_state.player_id)
        st.session_state.event = rng.choice(EVENTS)


def total():
    ensure_player_state()
    return st.session_state.knowledge + st.session_state.crisis_score

def clear_session_only():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

# Eski/hot-reload edilmiş oturumlarda state uyumluluğunu sağla.
ensure_player_state()

# -----------------------------
# Sidebar — SADECE KENDİ BİLGİSİ
# -----------------------------
with st.sidebar:
    st.title("🎯 Risk Arena")
    st.caption("BİREYSEL ÖĞRENCİ MODU")

    if "name" in st.session_state:
        st.markdown(f"**{st.session_state.name}**")
        st.metric("Puanım", total())
        if not st.session_state.finished:
            st.progress((st.session_state.round + 1) / len(ROUNDS))
            st.caption(f"Tur {st.session_state.round + 1} / {len(ROUNDS)}")
        st.caption("Risk Jokeri: " + ("Kullanıldı" if st.session_state.joker_used else "Hazır"))

    st.divider()
    st.markdown("**Bu ekranda başka öğrenci görünmez.**")
    st.caption("Her öğrenci kendi cihazında yalnızca kendi sorularını ve puanını görür.")

    with st.expander("🔐 Öğretmen alanı"):
        code = st.text_input("Öğretmen kodu", type="password")
        if code == "sigo451":
            df = teacher_results()
            st.write(f"Tamamlayan: **{len(df)}**")
            if not df.empty:
                st.dataframe(df, hide_index=True, use_container_width=True)
        elif code:
            st.error("Kod yanlış.")

    if st.button("↩️ Oturumu sıfırla", use_container_width=True):
        clear_session_only()
        st.rerun()

# -----------------------------
# Ana ekran
# -----------------------------
if "name" not in st.session_state:
    st.markdown(
        """
        <div class="hero">
          <h1>🎯 Risk Arena — Bireysel</h1>
          <p>Takım yok. Her öğrenci kendi kararlarını verir, kendi puanını toplar.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        ### Nasıl oynanır?
        - **Bireysel** oynarsın.
        - Başka öğrencilerin cevaplarını veya puanlarını göremezsin.
        - 5 bilgi/karar turu + 1 kriz turu vardır.
        - Bir kez **Risk Jokeri** kullanabilirsin.
        - Oyun sonunda yalnızca **kendi performans özetini** görürsün.
        """
    )

    with st.form("start"):
        name = st.text_input("Ad Soyad", placeholder="Örn. Ayşe Yılmaz")
        go = st.form_submit_button("🚀 Başla", type="primary", use_container_width=True)

    if go:
        name = name.strip()
        if len(name) < 2:
            st.error("Lütfen adınızı ve soyadınızı yazın.")
        else:
            start_player(name)
            st.rerun()
    st.stop()

# -----------------------------
# Final — SADECE KENDİ SONUCU
# -----------------------------
if st.session_state.finished:
    st.markdown(
        """
        <div class="hero">
          <h1>🏁 Simülasyon Tamamlandı</h1>
          <p>Aşağıda yalnızca senin bireysel performansın var.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1,c2,c3 = st.columns(3)
    c1.metric("Toplam Puanım", total())
    c2.metric("Bilgi Puanım", st.session_state.knowledge)
    c3.metric("Kriz Puanım", st.session_state.crisis_score)

    st.caption(f"Süre: {st.session_state.duration // 60} dk {st.session_state.duration % 60} sn")

    max_score = 20 + 20 + 30 + 20 + 20 + 40
    pct = round(100 * total() / max_score)

    if pct >= 85:
        msg = "Çok güçlü. Kavramlar ve uygulama kararları birlikte oturmuş görünüyor."
    elif pct >= 70:
        msg = "İyi düzey. Birkaç karar alanında tekrar faydalı olabilir."
    elif pct >= 55:
        msg = "Temel çerçeve var; özellikle risk kontrolü–finansmanı ayrımını tekrar et."
    else:
        msg = "Temel kavramları yeniden gözden geçirip simülasyonu bir kez daha oynaman yararlı olur."

    st.info(f"**Bireysel başarı oranı: %{pct}**\n\n{msg}")

    st.markdown(
        """
        ### Kısa düşünme soruları
        - ERM'de riskleri birlikte değerlendirmek neden önemlidir?
        - Risk sahibi ile CRO neden aynı şey değildir?
        - Bir riskte yalnız kontrol veya yalnız sigorta neden yeterli olmayabilir?
        - Kriz turunda hangi kararını değiştirirdin?
        """
    )

    if st.button("🔁 Yeniden Oyna", type="primary", use_container_width=True):
        old_name = st.session_state.name
        clear_session_only()
        start_player(old_name)
        st.rerun()
    st.stop()

# -----------------------------
# Tur ekranı
# -----------------------------
ri = st.session_state.round
r = ROUNDS[ri]

st.markdown(
    f"""
    <div class="hero">
      <h1>{r['title']}</h1>
      <p>{st.session_state.name} • Bireysel Tur {ri+1}/6</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"<div class='me'><b>Puanım:</b> {total()} &nbsp;&nbsp; | &nbsp;&nbsp; "
    f"<b>Risk Jokeri:</b> {'Kullanıldı' if st.session_state.joker_used else 'Hazır'}</div>",
    unsafe_allow_html=True
)

# Geri bildirim
if ri in st.session_state.feedback:
    fb = st.session_state.feedback[ri]
    if fb["points"] > 0:
        st.success(f"+{fb['points']} puan")
    else:
        st.warning("Bu tur puan kazanamadın.")

    if r["type"] == "single":
        st.markdown(f"**Doğru cevap:** {r['correct']}")
        st.info(r["explain"])
    elif r["type"] == "matching":
        st.markdown("**Doğru eşleştirmeler:**")
        for q,a in r["items"]:
            st.markdown(f"- {q} → **{a}**")
        st.info(r["explain"])
    else:
        ev = fb["event"]
        st.markdown(f"## Kriz: {ev['name']}")
        st.markdown(f"<div class='danger'>{ev['story']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            **Bütçe kullanımı:** {fb['cost']}/10  
            **Koruma puanı:** {fb['protection']}  
            **Katman bonusu:** {fb['bonus']}  
            **Kalan risk:** {fb['residual']}  
            **Kriz puanı:** {fb['points']}/40
            """
        )
        st.markdown(
            "<div class='good'><b>Ders bağlantısı:</b> Kontrol, finansman ve likidite/sermaye "
            "birlikte düşünüldüğünde risk daha iyi yönetilir; yine de kalan risk tamamen yok olmaz.</div>",
            unsafe_allow_html=True
        )

    label = "🏁 Bitir" if ri == len(ROUNDS)-1 else "➡️ Sonraki Tur"
    if st.button(label, type="primary", use_container_width=True):
        if ri == len(ROUNDS)-1:
            save_result()
            st.session_state.finished = True
        else:
            st.session_state.round += 1
        st.rerun()
    st.stop()

# Soru
if r["type"] == "single":
    with st.form(f"f{ri}"):
        st.markdown(f"### {r['question']}")
        ans = st.radio("Cevabın", r["options"], index=None)

        joker = False
        if not st.session_state.joker_used:
            joker = st.checkbox("🎲 Risk Jokerimi bu turda kullan — puanım 2 kat olsun")

        ok = st.form_submit_button("🔒 Cevabı Kilitle", type="primary", use_container_width=True)

    if ok:
        if ans is None:
            st.error("Önce bir cevap seç.")
        else:
            pts = r["points"] if ans == r["correct"] else 0
            if joker:
                pts *= 2
                st.session_state.joker_used = True
            st.session_state.knowledge += pts
            st.session_state.feedback[ri] = {"points":pts}
            st.rerun()

elif r["type"] == "matching":
    with st.form(f"f{ri}"):
        responses = {}
        for i,(q,a) in enumerate(r["items"],1):
            st.markdown(f"**{i}. {q}**")
            responses[q] = st.selectbox(
                f"{i}. seçim",
                ["— Seçiniz —"] + r["options"],
                key=f"m_{ri}_{i}",
                label_visibility="collapsed"
            )

        joker = False
        if not st.session_state.joker_used:
            joker = st.checkbox("🎲 Risk Jokerimi bu turda kullan — puanım 2 kat olsun")

        ok = st.form_submit_button("🔒 Cevapları Kilitle", type="primary", use_container_width=True)

    if ok:
        if any(v == "— Seçiniz —" for v in responses.values()):
            st.error("Tüm eşleştirmeleri tamamla.")
        else:
            pts = sum(r["each"] for q,a in r["items"] if responses[q] == a)
            if joker:
                pts *= 2
                st.session_state.joker_used = True
            st.session_state.knowledge += pts
            st.session_state.feedback[ri] = {"points":pts}
            st.rerun()

else:
    st.markdown(
        """
        <div class="warn">
        <b>Kriz henüz açıklanmadı.</b><br>
        Bir sigorta şirketinin risk komitesindesin. 10 bütçe puanın var.
        Kriz gelmeden önce hazırlıklarını seç.
        </div>
        """,
        unsafe_allow_html=True
    )

    display_to_id = {
        f"{v['label']} • Maliyet: {v['cost']}": k
        for k,v in MEASURES.items()
    }

    with st.form("crisis_strategy_form"):
        chosen_display = st.multiselect("Hazırlıklarını seç", list(display_to_id.keys()))
        ok = st.form_submit_button("🔒 Stratejiyi Kilitle", type="primary", use_container_width=True)

    if ok:
        chosen = [display_to_id[x] for x in chosen_display]
        cost = sum(MEASURES[x]["cost"] for x in chosen)

        if cost > 10:
            st.error(f"Bütçe aşıldı: {cost}/10")
        else:
            ev = st.session_state.event
            protection = sum(ev["p"].get(x,0) for x in chosen)
            layers = {MEASURES[x]["layer"] for x in chosen}
            bonus = 5 if {"control","finance"}.issubset(layers) else 0
            residual = max(0, ev["base"] - protection)
            pts = min(40, max(0, 40 - residual + bonus))

            st.session_state.crisis_score += pts
            st.session_state.feedback[ri] = {
                "points":pts, "event":ev, "cost":cost,
                "protection":protection, "bonus":bonus, "residual":residual
            }
            st.rerun()

