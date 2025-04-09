import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

st.title("Izoterma napięcia powierzchniowego — Model wygładzania wykładniczego")

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
        y_data = df["napiecie"].values   # N/m

        def izoterma_model(c, a, b, c0):
            return a * np.exp(-b * c) + c0

        # Wybór typu surfaktantu 
        surfactant_type = st.selectbox(
            "Wybierz typ surfaktantu:",
            ["Niejonowy", "Jonowy"],
            index=0
        )
        
        if surfactant_type == "Jonowy":
            alpha = st.number_input(
                "Stopień dysocjacji miceli (α):",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                format="%.2f"
            )

        if "model_fitted" not in st.session_state:
            st.session_state.model_fitted = False

        if st.button("Modeluj"):
            try:
                params, _ = curve_fit(izoterma_model, x_data, y_data, p0=[40, 100, 30], maxfev=10000)
                st.session_state.params = params
                st.session_state.model_fitted = True
            except Exception as e:
                st.error(f"Błąd dopasowania: {e}")
                st.session_state.model_fitted = False

        if st.session_state.model_fitted:
            a_fit, b_fit, c0_fit = st.session_state.params

            st.subheader("Dopasowanie modelu wykładniczego")
            st.write(f"Parametry dopasowania: **a = {a_fit:.4f}**, **b = {b_fit:.4f}**, **c₀ = {c0_fit:.4f}**")

            cmc = 1 / b_fit
            gamma_cmc = izoterma_model(cmc, a_fit, b_fit, c0_fit)

            R = 8.314  # J/mol·K
            T = 298    # temperatura w K

            dgamma_dlnc = a_fit * b_fit * cmc * np.exp(-b_fit * cmc) 
            gamma = dgamma_dlnc / (R * T)  # mol/m²

            if surfactant_type == "Jonowy":
                delta_gm = R * T * (1 + alpha) * np.log(cmc) / 1000
            else:
                delta_gm = R * T * np.log(cmc) / 1000

            st.subheader("Parametry izotermy")
            st.write(f"**CMC** (punkt przegięcia): {cmc:.6f} mol/L")
            st.write(f"**Γ** (adsorpcja): {gamma:.6e} mol/m²")

            if surfactant_type == "Jonowy":
                st.markdown(
                    f"ΔGm = RT⋅(1+α)⋅ln(CMC) = {R:.2f} × {T:.2f} × (1 + {alpha:.2f}) × ln({cmc:.6f}) = {delta_gm:.4f} kJ/mol"
                )
            else:
                st.markdown(
                    f"ΔGm = RT⋅ln(CMC) = {R:.2f} × {T:.2f} × ln({cmc:.6f}) = {delta_gm:.4f} kJ/mol"
                )

            residuals = y_data - izoterma_model(x_data, *st.session_state.params)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_data - np.mean(y_data))**2)
            r_squared = 1 - (ss_res / ss_tot)
            st.write(f"R² = {r_squared:.4f}")

            if r_squared < 0.9:
                st.warning("Model może nie być dobrze dopasowany do danych (R² < 0.9).")

            mode = st.radio("Wybierz sposób dostosowania parametrów:", ["Suwaki", "Wpisz wartości"])

            if mode == "Suwaki":
                a_manual = st.slider("Parametr a", min_value=0.0, max_value=100.0, value=float(a_fit), step=0.1)
                b_manual = st.slider("Parametr b", min_value=0.0, max_value=5000.0, value=float(b_fit), step=0.1)
                c0_manual = st.slider("Parametr c₀", min_value=0.0, max_value=100.0, value=float(c0_fit), step=0.1)
            else:
                a_manual = st.number_input("Parametr a", value=float(a_fit), step=0.1, format="%.4f")
                b_manual = st.number_input("Parametr b", value=float(b_fit), step=1.0, format="%.4f")
                c0_manual = st.number_input("Parametr c₀", value=float(c0_fit), step=0.1, format="%.4f")

            x_range = np.linspace(min(x_data), max(x_data), 300)
            y_fit = izoterma_model(x_range, a_fit, b_fit, c0_fit)
            y_manual = izoterma_model(x_range, a_manual, b_manual, c0_manual)

            fig, ax = plt.subplots(figsize=(8, 5))
            ax.grid(True)
            ax.scatter(x_data, y_data, label="Dane eksperymentalne", color="blue")
            ax.plot(x_range, y_fit, label="Krzywa dopasowana", color="red", linewidth=2)
            ax.plot(x_range, y_manual, label="Krzywa ręczna", color="green", linestyle="--")

            equation = f"$y = {a_fit:.2f} \cdot e^{{-{b_fit:.2f} \cdot x}} + {c0_fit:.2f}$"
            fig.text(0.5, 0.95, equation, ha='center', va='top', fontsize=11,
                     bbox=dict(boxstyle="round", facecolor="white", alpha=0.7))

            ax.axvline(cmc, color="purple", linestyle="--", label=f"CMC ≈ {cmc:.4f} mol/L")
            ax.scatter([cmc], [gamma_cmc], color="purple", zorder=5)

            ax.set_xlabel("Stężenie [mol/L]")
            ax.set_ylabel("Napięcie powierzchniowe [mN/m]")
            ax.legend()
            st.pyplot(fig)

            # Eksport wyników
            results = pd.DataFrame({
                "Parametr": ["a", "b", "c₀", "CMC", "Γ", "ΔGm", "R²"],
                "Wartosc": [a_fit, b_fit, c0_fit, cmc, gamma, delta_gm, r_squared]
            })

            csv = results.to_csv(index=False, sep=";").encode('utf-8')
            st.download_button("Pobierz wyniki jako CSV", csv, "wyniki_izotermy.csv", "text/csv")