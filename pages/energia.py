import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

st.title("Wyznaczanie energii powierzchniowej – metoda Zismana")

# Predefined liquids
predef_ciecze = {
    "Woda": {"gamma": 72.8, "gamma_d": 21.8, "gamma_p": 51.0},
    "Glicerol": {"gamma": 63.4, "gamma_d": 37.0, "gamma_p": 26.4},
    "Etanodiol": {"gamma": 48.3, "gamma_d": 29.3, "gamma_p": 19.0},
    "Formamid": {"gamma": 58.2, "gamma_d": 39.5, "gamma_p": 18.7},
    "Etanol": {"gamma": 22.4, "gamma_d": 17.0, "gamma_p": 5.4},
    "Dijodometan": {"gamma": 50.8, "gamma_d": 50.8, "gamma_p": 0.0},
    "Inna": None
}

if "punkty" not in st.session_state:
    st.session_state.punkty = []

st.subheader("➕ Dodaj nowy punkt pomiarowy")
selected_liquid_key = st.selectbox("Wybierz ciecz pomiarową", list(predef_ciecze.keys()), key="selected_liquid")

input_data = {}

if selected_liquid_key == "Inna":
    input_data["ciecz"] = st.text_input("Nazwa cieczy", value="Ciecz")
    input_data["gamma"] = st.number_input("γ [mN/m]", step=0.1, min_value=0.0)
    input_data["gamma_d"] = st.number_input("γᵈ (opcjonalnie)", step=0.1, min_value=0.0)
    input_data["gamma_p"] = st.number_input("γᵖ (opcjonalnie)", step=0.1, min_value=0.0)
else:
    ciecz_info = predef_ciecze[selected_liquid_key]
    input_data["ciecz"] = selected_liquid_key
    input_data["gamma"] = ciecz_info["gamma"]
    input_data["gamma_d"] = ciecz_info["gamma_d"]
    input_data["gamma_p"] = ciecz_info["gamma_p"]

    st.markdown(f"**γ:** {input_data['gamma']} mN/m")
    st.markdown(f"**γᵈ:** {input_data['gamma_d']} mN/m")
    st.markdown(f"**γᵖ:** {input_data['gamma_p']} mN/m")

input_data["theta"] = st.number_input("Kąt zwilżania θ [°]", min_value=0.0, max_value=180.0, step=0.1)

if st.button("Dodaj punkt"):
    input_data["cos_theta"] = np.cos(np.radians(input_data["theta"]))
    st.session_state.punkty.append(input_data)
    st.success(f"Punkt dodany: {input_data['ciecz']}")

if st.session_state.punkty:
    st.subheader("Dodane punkty")

    for i, pkt in enumerate(st.session_state.punkty):
        cols = st.columns([4, 2, 2, 2, 1])
        cols[0].markdown(f"**{pkt['ciecz']}**")
        cols[1].write(f"γ = {pkt['gamma']}")
        cols[2].write(f"θ = {pkt['theta']}°")
        cols[3].write(f"cos(θ) = {pkt['cos_theta']:.3f}")
        if cols[4].button("❌", key=f"del_{i}"):
            st.session_state.punkty.pop(i)
            st.rerun()

    st.subheader("Wykres Zismana")
    df = pd.DataFrame(st.session_state.punkty)
    x = df["gamma"].to_numpy()
    y = df["cos_theta"].to_numpy()

    slope, intercept, r_value, _, _ = linregress(x, y)
    gamma_c = (1 - intercept) / slope if slope != 0 else np.nan

    fig, ax = plt.subplots()
    ax.scatter(x, y, color="blue", label="Dane")
    ax.plot(x, slope * x + intercept, color="red", label=f"Regresja: y = {slope:.3f}x + {intercept:.3f}")
    ax.axhline(1, color="green", linestyle="--", label="cos(θ) = 1")
    ax.axvline(gamma_c, color="purple", linestyle="--", label=f"γ_c = {gamma_c:.2f} mN/m")
    ax.set_xlabel("γ cieczy [mN/m]")
    ax.set_ylabel("cos(θ)")
    ax.legend()
    st.pyplot(fig)

    st.markdown(f"Krytyczna energia powierzchniowa = **{gamma_c:.2f} mN/m**")
else:
    st.info("Dodaj przynajmniej jeden punkt, aby zobaczyć wykres Zismana.")





st.title("Wyznaczanie energii powierzchniowej – metoda OWRK")
df_owrk = pd.DataFrame([
    p for p in st.session_state.punkty
    if p["gamma_d"] is not None and p["gamma_p"] is not None
])

if len(df_owrk) < 2:
    st.info("Aby skorzystać z metody OWRK, dodaj przynajmniej dwa punkty z pełnymi danymi (γ, γᵈ, γᵖ).")
else:
    if len(df_owrk) > 2:
        st.subheader("🔢 Wybierz dwa punkty do obliczeń")
        labels = [
            f"{i+1}. {row['ciecz']} – θ={row['theta']}°"
            for i, row in df_owrk.iterrows()
        ]
        selected_labels = st.multiselect("Wybierz dwa punkty:", labels, max_selections=2)

        if len(selected_labels) != 2:
            st.warning("Musisz wybrać dokładnie dwa punkty.")
            st.stop()

        selected_indices = [int(label.split(".")[0]) - 1 for label in selected_labels]
        selected_rows = df_owrk.iloc[selected_indices]
    else:
        selected_rows = df_owrk.iloc[:2]

    y_vals, x_vals = [], []

    for _, row in selected_rows.iterrows():
        gamma_L = row["gamma"]
        gamma_L_d = row["gamma_d"]
        gamma_L_p = row["gamma_p"]
        cos_theta = row["cos_theta"]

        y = gamma_L * (cos_theta + 1) / (2 * np.sqrt(gamma_L_d))
        x = np.sqrt(gamma_L_p) / np.sqrt(gamma_L_d)

        y_vals.append(y)
        x_vals.append(x)

    x1, x2 = x_vals
    y1, y2 = y_vals
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1

    gamma_S_p = a ** 2
    gamma_S_d = b ** 2
    gamma_S_total = gamma_S_p + gamma_S_d

    st.success("Obliczenia metodą OWRK (dla wybranych dwóch cieczy):")
    st.markdown(f"""
    - Składnik polarny powierzchni: **γˢᵖ = {gamma_S_p:.2f} mN/m**  
    - Składnik dyspersyjny powierzchni: **γˢᵈ = {gamma_S_d:.2f} mN/m**  
    - Całkowita energia powierzchniowa: **γˢ = {gamma_S_total:.2f} mN/m**
    """)
