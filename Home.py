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


row1_col1, row1_col2 = st.columns(2)

with row1_col1:
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

with row1_col2:
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

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown(
        '<a href="/zwilzanie" target="_self" style="text-decoration: none;"><h2>💧 Kąt zwilżania</h2></a>',
        unsafe_allow_html=True
    )
    st.markdown("Przejdź do strony *Zwilżanie*, aby:")
    st.markdown("""
    - Uzupełnić fizykochemiczne parametry wykorzystywanych materiałów
    - Wczytać dane z pomiaru masy zwilżanego materiału w czasie
    - Wyznaczyć kąt zwilżania
    """)
    st.page_link("pages/zwilzanie.py", label="🔗 Przejdź do kąta zwilżania")


with row2_col2:
    st.markdown(
        '<a href="/energia" target="_self" style="text-decoration: none;"><h2>⚡ Energia powierzchniowa</h2></a>',
        unsafe_allow_html=True
    )
    st.markdown("Przejdź do strony *Energia powierzchniowa*, aby:")
    st.markdown("""
    - Wyznaczyć krytyczną energię powierzchniową metodą Zismana
    - Obliczyć składniki energii (dyspersyjny i polarny) metodą OWRK
    """)
    st.page_link("pages/energia.py", label="🔗 Przejdź do obliczeń energii")

# Oddzielenie
st.markdown("---")
st.info("📌 Aby wrócić do strony głównej z podstron, użyj nawigacji po lewej stronie.")

