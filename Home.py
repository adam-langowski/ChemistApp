import streamlit as st

st.set_page_config(
    page_title="Aplikacja chemiczna",
    page_icon="🧪",
    layout="centered"
)

st.markdown(f"""
    <style>
    .stApp {{
        background-size: cover;
        background-position: center;
    }}

    /* Tytuł strony */
    .big-font {{
        font-size: 36px !important;
        font-weight: 700;
        color: #D4D8DB;
        text-align: center;
    }}

    /* Podtytuł */
    .sub-font {{
        font-size: 15px !important;
        color: #328762;
        text-align: center;
        margin-bottom: 2rem;
    }}

    /* Styl boxów */
    .stContainer > div {{
        background-color: #ffffffdd;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }}

    /* Styl linków */
    a {{
        color: #BBC3CA;
        text-decoration: none;
    }}

    a:hover {{
        text-decoration: underline;
    }}

    /* Przycisk styl */
    button {{
        background-color: #4a6fa5 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Tytuł i opis
st.markdown('<p class="big-font">Obliczanie adsorpcji i napięcia powierzchniowego</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-font">Wybierz analizę, którą chcesz przeprowadzić</p>', unsafe_allow_html=True)

# Układ w dwóch kolumnach
col1, col2 = st.columns(2)

with col1:
    st.header("📉 Kinetyka adsorpcji")
    st.markdown("Przejdź do strony *Dyfuzja*, gdzie możesz:")
    st.markdown("""
    - Wczytać dane z eksperymentu
    - Dopasować prostą regresji
    - Obliczyć współczynnik dyfuzji
    """)
    st.page_link("pages/dyfuzja.py", label="🔗 Przejdź do analizy dyfuzji")

with col2:
    st.header("📈 Izoterma adsorpcji")
    st.markdown("Przejdź do strony *Izoterma*, aby:")
    st.markdown("""
    - Dopasować model wykładniczy
    - Wyznaczyć CMC, Γ i ΔGm
    - Zweryfikować jakość dopasowania
    """)
    st.page_link("pages/izoterma.py", label="🔗 Przejdź do analizy izotermy")

# Oddzielenie
st.markdown("---")
st.info("📌 Aby wrócić do strony głównej z podstron, kliknij logo lub użyj nawigacji po lewej stronie.")

