import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import math

st.title("Wyznaczanie kąta zwilżania")

st.markdown("#### Parametry fizykochemiczne")
col1, col2 = st.columns(2)
with col1:
    eta_mPa_s = st.number_input("Lepkość cieczy η [mPa·s]", value=1.0, step=0.1)
    rho = st.number_input("Gęstość cieczy ρ [g/cm³]", value=1.0, step=0.1)

with col2:
    gamma_mN_m = st.number_input("Napięcie powierzchniowe γ [mN/m]", value=72.8, step=0.1)
    B = st.number_input("Stała materiałowa B", value=1e8, step=1e6, format="%.0f")

eta = eta_mPa_s / 1000 
gamma = gamma_mN_m / 1000

st.markdown("---")
uploaded_file = st.file_uploader("📂 Wczytaj plik CSV z kolumnami: `czas`, `masa`")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if not {'czas', 'masa'}.issubset(df.columns):
        st.error("Plik musi zawierać kolumny: 'czas' oraz 'masa'")
    else:
        df['masa^2'] = df['masa'] ** 2

        # wybór zakresu danych na osi X
        time_min = float(df['czas'].min())
        time_max = float(df['czas'].max())
        zakres = st.slider("Zakres czasu do regresji [s]", min_value=time_min, max_value=time_max,
                           value=(time_min, time_min + (time_max - time_min) / 2), step=0.1)

        mask = (df['czas'] >= zakres[0]) & (df['czas'] <= zakres[1])
        df_reg = df[mask]

        # regresja liniowa
        slope, intercept, r_value, _, _ = linregress(df_reg['czas'], df_reg['masa^2'])
        A = 1 / slope if slope != 0 else np.nan

        # kąt zwilżania
        try:
            cos_theta = eta / (B * (rho**2) * gamma * A)
            cos_theta = np.clip(cos_theta, -1, 1)
            theta = math.degrees(math.acos(cos_theta))
        except Exception as e:
            cos_theta = None
            theta = None
            st.error(f"Błąd podczas obliczania kąta: {e}")

        # wykres
        fig, ax = plt.subplots()
        ax.scatter(df['czas'], df['masa^2'], label='Dane eksperymentalne', color='blue')
        ax.plot(df_reg['czas'], slope * df_reg['czas'] + intercept, color='red', label='Regresja liniowa')
        ax.set_xlabel("Czas [s]")
        ax.set_ylabel("m² [g²]")
        ax.legend()
        ax.axvline(zakres[0], color='green', linestyle='--', label='Początek zakresu')
        ax.axvline(zakres[1], color='orange', linestyle='--', label='Koniec zakresu')
        ax.axvspan(zakres[0], zakres[1], color='yellow', alpha=0.2, label='Zakres regresji')
        st.pyplot(fig)

        # wyniki
        st.markdown("### Wyniki")
        st.write(f"Współczynnik kierunkowy (slope): **{slope:.5f}**")
        st.write(f"Stała A: **{A:.3e}**")
        st.write(f"cos(θ): **{cos_theta:.4f}**")
        st.write(f"Kąt zwilżania θ: **{theta:.2f}°**")
