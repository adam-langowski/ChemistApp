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
    B = st.number_input("Stała materiałowa B", value=0.000001, step=0.000001, format="%.8f")

eta = eta_mPa_s / 1000 
gamma = gamma_mN_m / 1000

st.markdown("---")
uploaded_file = st.file_uploader("📂 Wczytaj plik CSV lub XLS")

if uploaded_file:
    try:
        if uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            st.error("Nieobsługiwany format pliku. Proszę załadować plik CSV lub XLS.")
            st.stop()

        df.columns = [col.strip() for col in df.columns]
        col_map = {
            'Time [s]': 'time',
            'Mass [g]': 'mass',
            'Mass² [g²]': 'masa^2'
        }
        df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)

        if 'time' not in df.columns:
            st.error("Brak kolumny 'time' lub jej odpowiednika.")
            st.stop()

        if 'masa^2' not in df.columns:
            if 'mass' in df.columns:
                df['mass'] = pd.to_numeric(df['mass'].astype(str).str.replace(',', '.'), errors='coerce')
                df['masa^2'] = df['mass'] ** 2
            else:
                st.error("Brak kolumny 'masa^2' lub 'mass'.")
                st.stop()


        df['time'] = pd.to_numeric(df['time'].astype(str).str.replace(',', '.'), errors='coerce')
        df.dropna(subset=['time', 'masa^2'], inplace=True)

        if 'masa^2' in df.columns:
            df['masa^2'] = pd.to_numeric(df['masa^2'].astype(str).str.replace(',', '.'), errors='coerce')

        # wybór zakresu danych na osi X
        time_min = float(df['time'].min())
        time_max = float(df['time'].max())
        zakres = st.slider("Zakres czasu do regresji [s]", min_value=time_min, max_value=time_max,
                           value=(time_min, time_min + (time_max - time_min) / 2), step=0.1)

        mask = (df['time'] >= zakres[0]) & (df['time'] <= zakres[1])
        df_reg = df[mask]

        if len(df_reg) < 2:
            st.error("Za mało punktów w wybranym zakresie do regresji.")
            st.stop()

        # regresja liniowa
        slope, intercept, r_value, _, _ = linregress(df_reg['time'], df_reg['masa^2'])
        A = 1 / slope if slope != 0 else np.nan

        try:
            denominator = B * (rho**2) * gamma * A
            cos_theta = eta / denominator if denominator != 0 else np.nan
            cos_theta = np.clip(cos_theta, -1, 1)
            theta = math.degrees(math.acos(cos_theta))

        except Exception as e:
            cos_theta = None
            theta = None
            st.error(f"Błąd podczas obliczania kąta: {e}")


        # wykres
        fig, ax = plt.subplots()
        ax.scatter(df['time'], df['masa^2'], label='Dane eksperymentalne', color='blue')
        ax.plot(df_reg['time'], slope * df_reg['time'] + intercept, color='red', label='Regresja liniowa')
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
        st.write(f"cos(θ): **{cos_theta:.6f}**")
        st.write(f"Kąt zwilżania θ: **{theta:.6f}°**")

    except Exception as e:
        st.error(f"Błąd podczas przetwarzania pliku: {e}")
