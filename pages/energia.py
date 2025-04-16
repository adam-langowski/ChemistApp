import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

st.title(" Wyznaczanie energii powierzchniowej – metoda Zismana")

# parametry dla predefiniowanych cieczy
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

# dodawanie nowego punktu
st.subheader("➕ Dodaj nowy punkt pomiarowy")
with st.form("add_point_form", clear_on_submit=True):
    selected_liquid = st.selectbox("Wybierz ciecz pomiarową", list(predef_ciecze.keys()))
    
    if selected_liquid != "Inna":
        gamma = predef_ciecze[selected_liquid]["gamma"]
        gamma_d = predef_ciecze[selected_liquid].get("gamma_d")
        gamma_p = predef_ciecze[selected_liquid].get("gamma_p")

        st.write(f"**Napięcie powierzchniowe γ:** {gamma} mN/m")
        if gamma_d is not None:
            st.write(f"**Składnik dyspersyjny γᵈ:** {gamma_d} mN/m")
        if gamma_p is not None:
            st.write(f"**Składnik polarny γᵖ:** {gamma_p} mN/m")
    else:
        gamma = st.number_input("γ [mN/m]", step=0.1)
        gamma_d = st.number_input("γᵈ (opcjonalnie)", step=0.1)
        gamma_p = st.number_input("γᵖ (opcjonalnie)", step=0.1)
    
    theta = st.number_input("Kąt zwilżania θ [°]", min_value=0.0, max_value=180.0, step=0.1)
    submitted = st.form_submit_button("Dodaj punkt")
    
    if submitted:
        st.session_state.punkty.append({
            "ciecz": selected_liquid,
            "gamma": gamma,
            "gamma_d": gamma_d,
            "gamma_p": gamma_p,
            "theta": theta,
            "cos_theta": np.cos(np.radians(theta))
        })

# tabela dodanych punktów
if st.session_state.punkty:
    st.subheader("Dodane punkty")

    # umożliwia usuwanie punktów
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


df_owrk = pd.DataFrame([p for p in st.session_state.punkty if p["gamma_d"] is not None and p["gamma_p"] is not None])
if len(df_owrk) >= 2:
    y_vals = []
    x_vals = []
    for _, row in df_owrk.iterrows():
        gamma_L = row["gamma"]
        gamma_L_d = row["gamma_d"]
        gamma_L_p = row["gamma_p"]
        cos_theta = row["cos_theta"]

        y = gamma_L * (cos_theta + 1) / (2 * np.sqrt(gamma_L_d))
        x = np.sqrt(gamma_L_p) / np.sqrt(gamma_L_d)
        y_vals.append(y)
        x_vals.append(x)

    slope, intercept, _, _, _ = linregress(x_vals, y_vals)

    gamma_S_p = slope**2
    gamma_S_d = intercept**2
    gamma_S_total = gamma_S_p + gamma_S_d

    st.success("Obliczenia metodą OWRK:")
    st.markdown(f"""
    - Składnik polarny powierzchni: **γˢᵖ = {gamma_S_p:.2f} mN/m**
    - Składnik dyspersyjny powierzchni: **γˢᵈ = {gamma_S_d:.2f} mN/m**
    - Całkowita energia powierzchniowa: **γˢ = {gamma_S_total:.2f} mN/m**
    """)
else:
    st.info("Aby wyznaczyć energię powierzchniową metodą OWRK, podaj przynajmniej dwa punkty z uzupełnionymi wartościami γᵈ i γᵖ.")
