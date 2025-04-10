import streamlit as st

st.set_page_config(
    page_title="Aplikacja chemiczna",
    page_icon="🧪",
    layout="wide"
)

# pyright: reportUndefinedVariable=false
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
        text-align: center; /* ← to dodaj */
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
col1, col2, col3= st.columns([1, 1, 1])

with col1:
    st.markdown(
        '<a href="/dyfuzja" target="_self" style="text-decoration: none;"><h2>📉 Kinetyka adsorpcji</h2></a>',
        unsafe_allow_html=True
    )
    st.markdown("Przejdź do strony *Dyfuzja*, gdzie możesz:")
    st.markdown("""
    - Wczytać dane z eksperymentu
    - Dopasować prostą regresji
    - Obliczyć współczynnik dyfuzji
    """)
    st.page_link("pages/dyfuzja.py", label="🔗 Przejdź do analizy dyfuzji")

with col2:
    st.markdown(
            '<a href="/izoterma" target="_self" style="text-decoration: none;"><h2>📈 Izoterma adsorpcji</h2></a>',
            unsafe_allow_html=True
        )    
    st.markdown("Przejdź do strony *Izoterma*, aby:")
    st.markdown("""
    - Dopasować model wykładniczy
    - Wyznaczyć CMC, Γ i ΔGm
    - Zweryfikować jakość dopasowania
    """)
    st.page_link("pages/izoterma.py", label="🔗 Przejdź do analizy izotermy")

with col3:
    st.markdown(
            '<a href="/trzeci" target="_self" style="text-decoration: none;"><h2>📈 Do uzupełnienia</h2></a>',
            unsafe_allow_html=True
        )    
    st.markdown("Do uzupełnienia")
    st.markdown("""
    - Do uzupełnienia
    - Do uzupełnienia
    - Do uzupełnienia
    """)
    st.page_link("pages/trzeci.py", label="🔗 Do uzupełnienia")

# Oddzielenie
st.markdown("---")
st.info("📌 Aby wrócić do strony głównej z podstron, użyj nawigacji po lewej stronie.")

