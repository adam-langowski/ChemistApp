import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

st.title("Izoterma napięcia powierzchniowego — Wygładzanie wykładnicze")

uploaded_file = st.file_uploader("Wczytaj plik CSV z danymi (z separatorem ';')", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=";")

    df.columns = [col.strip().lower() for col in df.columns]
    if "stezenie" not in df.columns or "napiecie" not in df.columns:
        st.error("Plik musi zawierać kolumny 'stezenie' i 'napiecie'")
    else:
        pd.options.display.float_format = '{:.10f}'.format
        st.subheader("Podgląd danych")
        st.dataframe(df.style.format(precision=8))

        x_data = df["stezenie"].values
        y_data = df["napiecie"].values

        def izoterma_model(c, a, b, c0):
            return a * np.exp(-b * c) + c0

        try:
            params, _ = curve_fit(izoterma_model, x_data, y_data, p0=[40, 100, 30], maxfev=10000)
            a_fit, b_fit, c0_fit = params

            st.subheader("Dopasowanie modelu wykładniczego")
            st.write(f"Parametry dopasowania: **a = {a_fit:.4f}**, **b = {b_fit:.4f}**, **c₀ = {c0_fit:.4f}**")

            # CMC, gamma_CMC
            cmc = 1 / b_fit
            gamma_cmc = izoterma_model(cmc, a_fit, b_fit, c0_fit)

            # Wyznaczanie Γ i ΔGm
            R = 8.314  # J/mol·K
            T = 298.15  # temperatura w K
            dgamma_dlnc = -a_fit * b_fit * cmc * np.exp(-b_fit * cmc)  # pochodna po ln(c)
            gamma = dgamma_dlnc / (R * T)  # mol/m²
            delta_gm = R * T * np.log(cmc) / 1000  # kJ/mol

            st.subheader("Parametry izotermy")
            st.write(f"**CMC** (punkt przegięcia): {cmc:.6f} mol/L")
            st.write(f"**Γ** (adsorpcja): {gamma:.6e} mol/m²")
            st.write(f"**ΔGm** (energia swobodna): {delta_gm:.4f} kJ/mol")

            st.subheader("Sterowanie ręczne (na tym samym wykresie)")
            a_manual = st.slider("Parametr a", min_value=0.0, max_value=100.0, value=float(a_fit), step=0.1)
            b_manual = st.slider("Parametr b", min_value=0.0, max_value=5000.0, value=float(b_fit), step=0.1)
            c0_manual = st.slider("Parametr c₀", min_value=0.0, max_value=100.0, value=float(c0_fit), step=0.1)

            x_range = np.linspace(min(x_data), max(x_data), 300)
            y_fit = izoterma_model(x_range, a_fit, b_fit, c0_fit)
            y_manual = izoterma_model(x_range, a_manual, b_manual, c0_manual)

            fig, ax = plt.subplots()
            ax.scatter(x_data, y_data, label="Dane eksperymentalne", color="blue")
            ax.plot(x_range, y_fit, label="Krzywa dopasowana", color="red", linewidth=2)
            ax.plot(x_range, y_manual, label="Krzywa ręczna", color="green", linestyle="--")

            # równanie krzywej
            equation = f"$y = {a_fit:.2f} \cdot e^{{-{b_fit:.2f} \cdot x}} + {c0_fit:.2f}$"
            fig.text(0.5, 0.95, equation, ha='center', va='top', fontsize=11, bbox=dict(boxstyle="round", facecolor="white", alpha=0.7))

            # punkt CMC
            ax.axvline(cmc, color="purple", linestyle="--", label=f"CMC ≈ {cmc:.4f}")
            ax.scatter([cmc], [gamma_cmc], color="purple", zorder=5)

            ax.set_xlabel("Stężenie [mol/L]")
            ax.set_ylabel("Napięcie powierzchniowe [mN/m]")
            ax.legend()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Błąd dopasowania: {e}")
