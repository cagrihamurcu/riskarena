
import random
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Risk Arena | SİGO451",
    page_icon="🎯",
    layout="wide",
)

# -----------------------------
# Görsel düzen
# -----------------------------
st.markdown(
    """
    <style>
      .block-container {padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1200px;}
      .hero {
        padding: 1.2rem 1.4rem;
        border: 1px solid #d9e3ef;
        border-radius: 18px;
        background: linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%);
        margin-bottom: 1rem;
      }
      .hero h1 {margin: 0 0 .25rem 0; font-size: 2.15rem;}
      .hero p {margin: 0; font-size: 1.05rem;}
      .round-card {
        padding: 1rem 1.15rem;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        background: #ffffff;
        margin: .6rem 0 1rem 0;
      }
      .team-badge {
        display: inline-block;
        padding: .28rem .65rem;
        border-radius: 999px;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        font-weight: 700;
        margin-bottom: .5rem;
      }
      .tiny {font-size: .9rem; color: #5b6470;}
      .big-number {font-size: 1.7rem; font-weight: 800;}
      .good {
        border-left: 5px solid #16a34a;
        background: #f0fdf4;
        padding: .75rem 1rem;
        border-radius: 10px;
      }
      .warn {
        border-left: 5px solid #f59e0b;
        background: #fffbeb;
        padding: .75rem 1rem;
        border-radius: 10px;
      }
      .danger {
        border-left: 5px solid #dc2626;
        background: #fef2f2;
        padding: .75rem 1rem;
        border-radius: 10px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Oyun içeriği
# -----------------------------
ROUNDS = [
    {
        "title": "1. Tur — ERM Radarı",
        "subtitle": "Tek tek risk mi, toplam risk profili mi?",
        "type": "single",
        "max_points": 20,
        "question": "Hangisi Kurumsal Risk Yönetimi (ERM) yaklaşımını en iyi gösterir?",
        "options": [
            "A) BT biriminin yalnızca siber riskleri değerlendirmesi",
            "B) Finans biriminin yalnızca faiz riskine bakması",
            "C) Deprem senaryosunun hasar, yatırım, likidite, operasyon ve reasürans etkilerini birlikte değerlendirmek",
            "D) Yıllık sigorta poliçelerini yenilemek",
        ],
        "correct": "C) Deprem senaryosunun hasar, yatırım, likidite, operasyon ve reasürans etkilerini birlikte değerlendirmek",
        "explanation": (
            "ERM, riskleri ayrı kutular halinde değil; birbirleriyle bağlantılı bir portföy olarak ele alır. "
            "Tek bir olay birden fazla birimi ve finansal kapasiteyi aynı anda etkileyebilir."
        ),
    },
    {
        "title": "2. Tur — Kim Ne Yapar?",
        "subtitle": "Risk yönetişimi ve Üç Hat Modeli",
        "type": "matching",
        "max_points": 20,
        "points_each": 5,
        "options": ["Yönetim Kurulu", "İş Birimi", "Risk Yönetimi / CRO", "İç Denetim"],
        "items": [
            ("Günlük faaliyette riski üstlenir ve kontrolleri uygular.", "İş Birimi"),
            ("Kurumun genel risk iştahını ve risk çerçevesini onaylar.", "Yönetim Kurulu"),
            ("Riskleri ölçer, izler; limitleri takip eder ve sorgular.", "Risk Yönetimi / CRO"),
            ("Sistemin ve kontrollerin etkinliği hakkında bağımsız güvence verir.", "İç Denetim"),
        ],
        "explanation": (
            "İş birimi riski yönetir; risk yönetimi/CRO izler ve sorgular; iç denetim bağımsız güvence verir. "
            "Yönetim kurulu ise genel yönü ve risk sınırlarını belirler."
        ),
    },
    {
        "title": "3. Tur — Kontrol Laboratuvarı",
        "subtitle": "Hangi uygulama hangi risk kontrol tekniği?",
        "type": "matching",
        "max_points": 30,
        "points_each": 5,
        "options": [
            "Riskten Kaçınma",
            "Kayıp Önleme",
            "Kayıp Azaltma",
            "Ayırma",
            "Çoğaltma",
            "Çeşitlendirme",
        ],
        "items": [
            ("Taşkın riski çok yüksek bölgede yeni fabrika kurmaktan vazgeçmek", "Riskten Kaçınma"),
            ("Elektrik sistemine periyodik bakım yaptırmak", "Kayıp Önleme"),
            ("Sprinkler sistemi kurmak", "Kayıp Azaltma"),
            ("Kritik stokları iki farklı depoda tutmak", "Ayırma"),
            ("Yedek veri merkezi kurmak", "Çoğaltma"),
            ("Tek tedarikçi yerine farklı tedarikçilerle çalışmak", "Çeşitlendirme"),
        ],
        "explanation": (
            "Kaçınma maruziyeti kaldırır; önleme sıklığı azaltır; azaltma şiddeti sınırlar; "
            "ayırma böler; çoğaltma yedekler; çeşitlendirme bağımlılığı azaltır."
        ),
    },
    {
        "title": "4. Tur — Zihin Tuzakları",
        "subtitle": "Risk kararı teknik ölçümden neden sapabilir?",
        "type": "matching",
        "max_points": 20,
        "points_each": 4,
        "options": [
            "Erişilebilirlik",
            "Aşırı Güven",
            "Kontrol Yanılsaması",
            "Normalleşme",
            "Çerçeveleme",
        ],
        "items": [
            (
                "Yakındaki fabrikada dün yangın çıktı. Kendi risk verimiz değişmediği halde yönetim yangın riskini birden çok daha yüksek görüyor.",
                "Erişilebilirlik",
            ),
            (
                "“Tahminlerimiz hep tutuyor; bu yıl da rezerv kesin yeter.”",
                "Aşırı Güven",
            ),
            (
                "“Bizim ekip çok iyi; siber saldırı olursa zaten kontrol ederiz.”",
                "Kontrol Yanılsaması",
            ),
            (
                "“On yıldır büyük kaza olmadı; bundan sonra da olmaz.”",
                "Normalleşme",
            ),
            (
                "Aynı risk, “%90 güvenli” denince daha kabul edilebilir; “%10 kayıp ihtimali” denince daha tehlikeli algılanıyor.",
                "Çerçeveleme",
            ),
        ],
        "explanation": (
            "Teknik risk düzeyi değişmese bile yakın deneyimler, güven duygusu, kontrol hissi ve bilginin sunuluş biçimi "
            "algılanan riski değiştirebilir."
        ),
    },
    {
        "title": "5. Tur — Hangi Riskte Hangi Yöntem?",
        "subtitle": "Sıklık + şiddet + taşıma kapasitesi",
        "type": "matching",
        "max_points": 20,
        "points_each": 5,
        "options": [
            "Tutma",
            "Önleme + Tutma",
            "Azaltma + Sigorta / Transfer",
            "Kaçınma / Süreci Yeniden Tasarlama",
        ],
        "items": [
            ("Nadiren oluşan ve küçük kalan ekipman hasarları", "Tutma"),
            ("Sık tekrarlanan fakat tek tek küçük iş kazaları", "Önleme + Tutma"),
            ("Nadiren gerçekleşen fakat çok büyük kayıp yaratabilecek fabrika yangını", "Azaltma + Sigorta / Transfer"),
            ("Sık gerçekleşen ve her seferinde çok büyük kayıp yaratan tehlikeli süreç", "Kaçınma / Süreci Yeniden Tasarlama"),
        ],
        "explanation": (
            "Sıklık ve şiddet iyi bir başlangıçtır; ancak karar verirken likidite, finansal kapasite, maliyet, "
            "sigortalanabilirlik ve hukuki/itibari etkiler de dikkate alınır."
        ),
    },
    {
        "title": "6. Tur — Kriz Odası",
        "subtitle": "10 bütçe puanınız var. Kriz açıklanmadan önce hazırlık yapın.",
        "type": "strategy",
        "max_points": 40,
    },
]

MEASURES = {
    "maintenance": {
        "label": "Bakım ve fiziksel risk azaltma programı",
        "cost": 2,
        "layer": "control",
    },
    "bcp": {
        "label": "Acil durum + iş sürekliliği planı",
        "cost": 2,
        "layer": "control",
    },
    "it": {
        "label": "Yedek veri merkezi + MFA",
        "cost": 4,
        "layer": "control",
    },
    "reinsurance": {
        "label": "Reasürans korumasını güçlendir",
        "cost": 4,
        "layer": "financing",
    },
    "liquidity": {
        "label": "Likidite tamponu oluştur",
        "cost": 3,
        "layer": "financing",
    },
    "supplier": {
        "label": "Kritik tedarikçileri çeşitlendir",
        "cost": 2,
        "layer": "control",
    },
    "claims": {
        "label": "Hasar operasyonunda yedek kapasite kur",
        "cost": 2,
        "layer": "control",
    },
    "insurance": {
        "label": "Operasyonel riskler için ticari sigorta al",
        "cost": 3,
        "layer": "financing",
    },
}

EVENTS = [
    {
        "name": "🌍 Büyük Deprem",
        "base_loss": 40,
        "story": (
            "Hasar ihbarları patladı; bazı şubeler çalışamıyor; likidite ihtiyacı arttı; "
            "reasürans tahsilatı kritik hale geldi."
        ),
        "protection": {
            "maintenance": 5,
            "bcp": 7,
            "it": 7,
            "reinsurance": 12,
            "liquidity": 8,
            "supplier": 3,
            "claims": 6,
            "insurance": 5,
        },
    },
    {
        "name": "🛡️ Siber Saldırı",
        "base_loss": 35,
        "story": (
            "Poliçe ve hasar sistemleri kesintiye uğradı; müşteri hizmetleri yavaşladı; "
            "itibar ve iş sürekliliği riski yükseldi."
        ),
        "protection": {
            "maintenance": 0,
            "bcp": 5,
            "it": 14,
            "reinsurance": 1,
            "liquidity": 4,
            "supplier": 3,
            "claims": 5,
            "insurance": 8,
        },
    },
    {
        "name": "🌊 Büyük Hasar Dalgası",
        "base_loss": 40,
        "story": (
            "Kısa sürede çok sayıda yüksek tutarlı hasar geldi. Hasar operasyonu zorlanıyor; "
            "nakit çıkışı hızlandı; sermaye ve reasürans koruması öne çıktı."
        ),
        "protection": {
            "maintenance": 2,
            "bcp": 4,
            "it": 3,
            "reinsurance": 14,
            "liquidity": 10,
            "supplier": 1,
            "claims": 8,
            "insurance": 2,
        },
    },
    {
        "name": "🚚 Kritik Tedarikçi Kesintisi",
        "base_loss": 32,
        "story": (
            "Teknoloji ve hizmet tedarikçilerinden biri devre dışı kaldı. Operasyon yavaşladı; "
            "müşteri hizmetleri ve iş sürekliliği baskı altında."
        ),
        "protection": {
            "maintenance": 1,
            "bcp": 6,
            "it": 3,
            "reinsurance": 0,
            "liquidity": 4,
            "supplier": 14,
            "claims": 4,
            "insurance": 1,
        },
    },
]


# -----------------------------
# Yardımcı fonksiyonlar
# -----------------------------
def reset_game():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]


def init_game(team_names):
    st.session_state.game_started = True
    st.session_state.teams = [
        {
            "name": name,
            "knowledge": 0,
            "crisis": 0,
            "joker_used": False,
            "round_points": {},
        }
        for name in team_names
    ]
    st.session_state.current_round = 0
    st.session_state.current_team = 0
    st.session_state.answers = {i: {} for i in range(len(ROUNDS))}
    st.session_state.scored_rounds = set()
    st.session_state.event = None
    st.session_state.crisis_details = {}
    st.session_state.started_at = datetime.now().strftime("%H:%M")


def total_score(team):
    return team["knowledge"] + team["crisis"]


def ranking_df():
    rows = []
    for team in st.session_state.teams:
        rows.append(
            {
                "Takım": team["name"],
                "Bilgi Puanı": team["knowledge"],
                "Kriz Puanı": team["crisis"],
                "Toplam": total_score(team),
                "Risk Jokeri": "Kullanıldı" if team["joker_used"] else "Hazır",
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["Toplam", "Kriz Puanı", "Bilgi Puanı"],
        ascending=False,
    ).reset_index(drop=True)


def score_normal_round(round_idx):
    r = ROUNDS[round_idx]

    for team_idx, team in enumerate(st.session_state.teams):
        record = st.session_state.answers[round_idx][team_idx]
        response = record["response"]

        if r["type"] == "single":
            raw = r["max_points"] if response == r["correct"] else 0

        elif r["type"] == "matching":
            raw = 0
            for prompt, correct in r["items"]:
                if response.get(prompt) == correct:
                    raw += r["points_each"]
        else:
            raw = 0

        if record.get("joker"):
            raw *= 2

        team["knowledge"] += raw
        team["round_points"][round_idx] = raw


def score_crisis_round(round_idx):
    if st.session_state.event is None:
        # Aynı kriz tüm takımlar için geçerli: adalet + karşılaştırma.
        st.session_state.event = random.choice(EVENTS)

    event = st.session_state.event

    for team_idx, team in enumerate(st.session_state.teams):
        record = st.session_state.answers[round_idx][team_idx]
        selected = record["response"]
        cost = sum(MEASURES[m]["cost"] for m in selected)
        protection = sum(event["protection"].get(m, 0) for m in selected)

        layers = {MEASURES[m]["layer"] for m in selected}
        layer_bonus = 5 if {"control", "financing"}.issubset(layers) else 0

        residual = max(0, event["base_loss"] - protection)
        points = min(40, max(0, 40 - residual + layer_bonus))

        team["crisis"] += points
        team["round_points"][round_idx] = points

        st.session_state.crisis_details[team_idx] = {
            "selected": selected,
            "cost": cost,
            "protection": protection,
            "layer_bonus": layer_bonus,
            "residual": residual,
            "points": points,
        }


def finalize_round(round_idx):
    if round_idx in st.session_state.scored_rounds:
        return

    if ROUNDS[round_idx]["type"] == "strategy":
        score_crisis_round(round_idx)
    else:
        score_normal_round(round_idx)

    st.session_state.scored_rounds.add(round_idx)


def all_submitted(round_idx):
    return len(st.session_state.answers[round_idx]) == len(st.session_state.teams)


def submit_answer(round_idx, team_idx, response, joker=False):
    st.session_state.answers[round_idx][team_idx] = {
        "response": response,
        "joker": joker,
    }

    if joker:
        st.session_state.teams[team_idx]["joker_used"] = True

    st.session_state.current_team += 1


def render_score_strip():
    df = ranking_df()
    cols = st.columns(min(4, len(df)))
    for i, row in df.head(len(cols)).iterrows():
        with cols[i]:
            st.metric(row["Takım"], int(row["Toplam"]))


def render_standard_result(round_idx):
    r = ROUNDS[round_idx]
    st.success("🔒 Tüm takımlar cevaplarını kilitledi. Sonuçlar açılıyor!")

    if r["type"] == "single":
        st.markdown(f"**Doğru cevap:** {r['correct']}")
    else:
        st.markdown("**Doğru eşleştirmeler:**")
        for prompt, correct in r["items"]:
            st.markdown(f"- **{prompt}** → {correct}")

    st.info(r["explanation"])

    rows = []
    for team in st.session_state.teams:
        rows.append(
            {
                "Takım": team["name"],
                "Bu Tur": team["round_points"].get(round_idx, 0),
                "Toplam": total_score(team),
            }
        )
    st.dataframe(pd.DataFrame(rows).sort_values("Bu Tur", ascending=False), hide_index=True, use_container_width=True)


def render_crisis_result(round_idx):
    event = st.session_state.event
    st.markdown(f"## Kriz zarfı açıldı: {event['name']}")
    st.markdown(f"<div class='danger'>{event['story']}</div>", unsafe_allow_html=True)
    st.caption(
        "Kriz puanı; seçilen önlemlerin bu olaya karşı koruması, kalan risk ve "
        "kontrol + finansman katmanlarının birlikte kullanılmasına göre hesaplandı."
    )

    rows = []
    for team_idx, team in enumerate(st.session_state.teams):
        d = st.session_state.crisis_details[team_idx]
        selected_labels = ", ".join(MEASURES[m]["label"] for m in d["selected"]) or "Hiçbiri"
        rows.append(
            {
                "Takım": team["name"],
                "Bütçe Kullanımı": f"{d['cost']}/10",
                "Koruma": d["protection"],
                "Katman Bonusu": d["layer_bonus"],
                "Kalan Risk": d["residual"],
                "Kriz Puanı": d["points"],
                "Seçimler": selected_labels,
            }
        )

    st.dataframe(
        pd.DataFrame(rows).sort_values(["Kriz Puanı", "Kalan Risk"], ascending=[False, True]),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown(
        "<div class='good'><b>Ders bağlantısı:</b> Tek bir teknik çoğu zaman yeterli değildir. "
        "Kontrol + finansman + likidite/sermaye birlikte düşünülür; yine de kalan risk tamamen yok olmaz.</div>",
        unsafe_allow_html=True,
    )


def render_final():
    st.markdown(
        """
        <div class="hero">
          <h1>🏆 Risk Arena Tamamlandı</h1>
          <p>Şimdi hangi takımın en güçlü risk komitesi olduğuna bakalım.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = ranking_df()
    winner = df.iloc[0]["Takım"]
    st.success(f"🥇 Şampiyon: **{winner}**")

    podium = ["🥇", "🥈", "🥉"]
    cols = st.columns(min(3, len(df)))
    for i, col in enumerate(cols):
        with col:
            row = df.iloc[i]
            st.markdown(f"### {podium[i]} {row['Takım']}")
            st.metric("Toplam Puan", int(row["Toplam"]))
            st.caption(f"Bilgi: {int(row['Bilgi Puanı'])} • Kriz: {int(row['Kriz Puanı'])}")

    st.dataframe(df, hide_index=True, use_container_width=True)

    chart_df = df.set_index("Takım")[["Bilgi Puanı", "Kriz Puanı"]]
    st.bar_chart(chart_df)

    st.markdown("### 🎓 Kapanış Tartışması")
    st.markdown(
        """
        1. En yüksek puanı getiren kararlar neden güçlüydü?
        2. Hangi turda ekipler en çok ayrıştı?
        3. Kriz turunda yalnız risk kontrolüne veya yalnız finansmana güvenen ekipler ne kaybetti?
        4. Gerçek bir sigorta şirketinde aynı kararları verir miydiniz? Neyi değiştirirdiniz?
        """
    )

    st.markdown(
        "<div class='warn'><b>Öğretim mesajı:</b> İyi risk yönetimi tek doğru şıkkı ezberlemek değil; "
        "riskleri birlikte görmek, rol ve sorumlulukları ayırmak, uygun kontrol ve finansman araçlarını "
        "birlikte kullanmak ve kalan riski taşıyabilir düzeyde tutmaktır.</div>",
        unsafe_allow_html=True,
    )


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("🎯 Risk Arena")
    st.caption("SİGO451 • Risk Yönetimi")

    if st.session_state.get("game_started"):
        current = st.session_state.get("current_round", 0)
        if current < len(ROUNDS):
            st.progress((current + 1) / len(ROUNDS))
            st.write(f"**Tur:** {current + 1} / {len(ROUNDS)}")
        st.divider()
        st.dataframe(ranking_df()[["Takım", "Toplam"]], hide_index=True, use_container_width=True)

    st.divider()
    st.markdown(
        """
        **Önerilen kullanım**
        - 2–6 takım
        - 35–50 dakika
        - Tek bilgisayar + projeksiyon
        - Her takım cevabını sırayla kilitler
        - Son takım cevaplamadan doğru cevap görünmez
        """
    )

    if st.button("🔄 Oyunu sıfırla", use_container_width=True):
        reset_game()
        st.rerun()


# -----------------------------
# Giriş ekranı
# -----------------------------
if not st.session_state.get("game_started"):
    st.markdown(
        """
        <div class="hero">
          <h1>🎯 Risk Arena</h1>
          <p>ERM, risk yönetişimi, risk kontrolü ve risk finansmanını sınıf içi rekabete dönüştüren takım simülasyonu.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Tur", "6")
    with c2:
        st.metric("Takım", "2–6")
    with c3:
        st.metric("Önerilen Süre", "35–50 dk")

    st.markdown(
        """
        ### Oyun nasıl ilerler?
        - Her takım bir **Risk Komitesi** olur.
        - İlk 5 turda bilgi ve karar puanı toplanır.
        - Her takımın **1 Risk Jokeri** vardır: seçtiği bir turdaki puanını ikiye katlar.
        - Son turda takımlar **10 bütçe puanı** ile kriz öncesi yatırım yapar.
        - Kriz zarfı, bütün takımlar kararlarını kilitledikten sonra açılır.
        - En yüksek toplam puanı alan takım **Risk Arena Şampiyonu** olur.
        """
    )

    team_count = st.number_input("Takım sayısı", min_value=2, max_value=6, value=4, step=1)

    team_names = []
    cols = st.columns(2)
    for i in range(int(team_count)):
        with cols[i % 2]:
            name = st.text_input(f"{i+1}. takım adı", value=f"Takım {i+1}", key=f"team_name_{i}")
            team_names.append(name.strip())

    if st.button("🚀 Simülasyonu Başlat", type="primary", use_container_width=True):
        cleaned = [n for n in team_names if n]
        if len(cleaned) != int(team_count):
            st.error("Her takım için bir ad yazın.")
        elif len({n.casefold() for n in cleaned}) != len(cleaned):
            st.error("Takım adları birbirinden farklı olmalı.")
        else:
            init_game(cleaned)
            st.rerun()

    st.stop()


# -----------------------------
# Final ekranı
# -----------------------------
if st.session_state.current_round >= len(ROUNDS):
    render_final()
    st.stop()


# -----------------------------
# Tur ekranı
# -----------------------------
round_idx = st.session_state.current_round
r = ROUNDS[round_idx]

st.markdown(
    f"""
    <div class="hero">
      <h1>{r['title']}</h1>
      <p>{r['subtitle']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

render_score_strip()

if all_submitted(round_idx):
    finalize_round(round_idx)

    st.divider()
    if r["type"] == "strategy":
        render_crisis_result(round_idx)
    else:
        render_standard_result(round_idx)

    button_text = "🏁 Finale Geç" if round_idx == len(ROUNDS) - 1 else "➡️ Sonraki Tura Geç"
    if st.button(button_text, type="primary", use_container_width=True):
        st.session_state.current_round += 1
        st.session_state.current_team = 0
        st.rerun()

    st.stop()


team_idx = st.session_state.current_team
team = st.session_state.teams[team_idx]

st.markdown(f"<span class='team-badge'>Sıradaki: {team['name']}</span>", unsafe_allow_html=True)
st.caption("Diğer takımlar cevap vermeden sonuç açılmaz. Takım kararını verince cevabı kilitleyin.")

# -----------------------------
# Standart turlar
# -----------------------------
if r["type"] == "single":
    with st.form(f"form_r{round_idx}_t{team_idx}", clear_on_submit=False):
        st.markdown(f"### {r['question']}")
        answer = st.radio("Cevabınız", r["options"], index=None)

        joker = False
        if not team["joker_used"]:
            joker = st.checkbox("🎲 Risk Jokerimi bu turda kullan — kazandığım puan 2 kat olsun")

        submitted = st.form_submit_button("🔒 Cevabı Kilitle", type="primary", use_container_width=True)

    if submitted:
        if answer is None:
            st.error("Önce bir cevap seçin.")
        else:
            submit_answer(round_idx, team_idx, answer, joker)
            st.rerun()


elif r["type"] == "matching":
    with st.form(f"form_r{round_idx}_t{team_idx}", clear_on_submit=False):
        st.markdown("### Görev")
        st.write("Her ifadeyi en uygun seçenekle eşleştirin.")

        responses = {}
        for i, (prompt, _) in enumerate(r["items"], start=1):
            st.markdown(f"**{i}. {prompt}**")
            choice = st.selectbox(
                f"{i}. seçim",
                ["— Seçiniz —"] + r["options"],
                key=f"match_{round_idx}_{team_idx}_{i}",
                label_visibility="collapsed",
            )
            responses[prompt] = choice

        joker = False
        if not team["joker_used"]:
            joker = st.checkbox("🎲 Risk Jokerimi bu turda kullan — kazandığım puan 2 kat olsun")

        submitted = st.form_submit_button("🔒 Cevapları Kilitle", type="primary", use_container_width=True)

    if submitted:
        if any(v == "— Seçiniz —" for v in responses.values()):
            st.error("Tüm eşleştirmeleri tamamlayın.")
        else:
            submit_answer(round_idx, team_idx, responses, joker)
            st.rerun()


# -----------------------------
# Kriz turu
# -----------------------------
elif r["type"] == "strategy":
    st.markdown(
        """
        <div class="round-card">
        <b>Senaryo:</b> Siz bir sigorta şirketinin risk komitesisiniz. Hangi krizin geleceğini bilmiyorsunuz.
        Elinizde <b>10 bütçe puanı</b> var. Aşağıdaki hazırlıklardan istediklerinizi seçin.
        Kriz, bütün takımlar kararını kilitledikten sonra açıklanacak.
        </div>
        """,
        unsafe_allow_html=True,
    )

    display_to_id = {
        f"{data['label']}  •  Maliyet: {data['cost']}": key
        for key, data in MEASURES.items()
    }

    with st.form(f"crisis_r{round_idx}_t{team_idx}", clear_on_submit=False):
        selections_display = st.multiselect(
            "Yatırımlarınızı seçin",
            options=list(display_to_id.keys()),
        )
        submitted = st.form_submit_button("🔒 Stratejiyi Kilitle", type="primary", use_container_width=True)

    if submitted:
        selected_ids = [display_to_id[x] for x in selections_display]
        cost = sum(MEASURES[m]["cost"] for m in selected_ids)

        if cost > 10:
            st.error(f"Bütçe aşıldı: {cost}/10. Bazı seçimleri çıkarın.")
        else:
            submit_answer(round_idx, team_idx, selected_ids, joker=False)
            st.rerun()
