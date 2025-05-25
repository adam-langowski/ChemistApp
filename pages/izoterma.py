import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

st.title("Izoterma napięcia powierzchniowego — Model Szyszkowskiego")

# Stałe fizyczne
FIXED_Y0 = 72.0   # Napięcie powierzchniowe wody w 20°C [mN/m]
R = 8.314         # Stała gazowa [J/mol·K]
T = 298           # Temperatura [K]

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

        x_data = df["stezenie"].values.astype(float)
        y_data = df["napiecie"].values.astype(float)  # mN/m

        def szyszkowski_model(c, B_sz, A_sz):
            """Model Szyszkowskiego ze stałym γ₀=72 mN/m"""
            safe_c = np.maximum(c, 1e-12)
            return FIXED_Y0 * (1 - B_sz * np.log(safe_c/A_sz + 1))

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
                # Ograniczenia parametrów
                bounds = (
                    [0.001, 1e-7],  # Dolne granice [B_sz, A_sz]
                    [1.0,   1.0]    # Górne granice
                )
                
                # Parametry początkowe
                initial_guess = [0.2, 0.01]  # [B_sz, A_sz]
                
                params, _ = curve_fit(szyszkowski_model, x_data, y_data, 
                                    p0=initial_guess,
                                    bounds=bounds,
                                    maxfev=10000)
                
                st.session_state.params = params
                st.session_state.model_fitted = True

            except Exception as e:
                st.error(f"Błąd dopasowania: {e}")
                st.session_state.model_fitted = False

        if st.session_state.model_fitted:
            B_sz_fit, A_sz_fit = st.session_state.params

            st.subheader("Dopasowanie modelu Szyszkowskiego")
            st.write(f"**Ustalony parametr:**")
            st.write(f"- γ₀ (napięcie powierzchniowe wody) = {FIXED_Y0} mN/m")
            st.write(f"**Parametry dopasowania:**")
            st.write(f"- B_sz = {B_sz_fit:.4f}")
            st.write(f"- A_sz = {A_sz_fit * 1e6:.6f} µmol/L")

            # Obliczenie CMC
            cmc = A_sz_fit * (np.exp(1/B_sz_fit) - 1) *0.001  # mmol/L
            gamma_cmc = szyszkowski_model(cmc, B_sz_fit, A_sz_fit)

            # Obliczenia adsorpcji
            gamma = (FIXED_Y0 * B_sz_fit * cmc) / (R * T * (A_sz_fit + cmc))  # mol/m²
            gamma_max = (FIXED_Y0 * B_sz_fit) / (R * T)  # mol/m²

            # Obliczenia energii micelizacji
            if surfactant_type == "Jonowy":
                delta_gm = R * T * (1 + alpha) * np.log(cmc) / 1000
            else:
                delta_gm = R * T * np.log(cmc) / 1000

            # Wyświetlanie wyników
            st.subheader("Parametry izotermy")
            st.write(f"**CMC** (krytyczne stężenie micelarne): {cmc:.6f} mol/L")
            st.write(f"**Γ** (nadmiar powierzchniowy przy CMC): {gamma:.6e} mol/m²")
            st.write(f"**Γ_max** (maksymalna adsorpcja): {gamma_max:.6e} mol/m²")

            # Wyświetlanie równania termodynamicznego
            st.markdown(
                f"ΔGm = RT⋅{'('+str(1+alpha)+')' if surfactant_type == 'Jonowy' else ''}⋅ln(CMC) = "
                f"{delta_gm:.4f} kJ/mol"
            )

            # Analiza jakości dopasowania
            residuals = y_data - szyszkowski_model(x_data, B_sz_fit, A_sz_fit)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_data - np.mean(y_data))**2)
            r_squared = 1 - (ss_res / ss_tot)
            st.write(f"**Współczynnik determinacji R²** = {r_squared:.4f}")

            if r_squared < 0.9:
                st.warning("Uwaga: Model może nie być dobrze dopasowany do danych (R² < 0.9).")

            # Interaktywna modyfikacja parametrów
            st.subheader("Modyfikacja parametrów modelu")
            mode = st.radio("Tryb edycji:", ["Suwaki", "Wprowadź ręcznie"])
            
            if mode == "Suwaki":
                col1, col2 = st.columns(2)
                with col1:
                    B_sz_manual = st.slider("B", 0.0001, 1.0, float(B_sz_fit), 0.0001, format="%.4f")
                with col2:
                    A_sz_manual_umol = st.slider("A", 0.0001, 100.0, float(A_sz_fit * 1e6), 0.0001, format="%.4f")
                    A_sz_manual = A_sz_manual_umol / 1e6  # Konwersja z µmol/L na mol/L
            else:
                B_sz_manual = st.number_input("B", value=float(B_sz_fit), step=0.0001, format="%.4f")
                A_sz_manual_umol = st.number_input("A", value=float(A_sz_fit * 1e6), step=0.0001, format="%.4f")
                A_sz_manual = A_sz_manual_umol / 1e6  # µmol/L → mol/L

            # Generowanie wykresu
            x_range = np.linspace(min(x_data), max(x_data)*1.1, 300)
            y_fit = szyszkowski_model(x_range, B_sz_fit, A_sz_fit)
            y_manual = szyszkowski_model(x_range, B_sz_manual, A_sz_manual)

            # Obliczenia dla parametrów ręcznych
            cmc_manual = A_sz_manual * (np.exp(1/B_sz_manual) - 1) * 0.001
            gamma_cmc_manual = szyszkowski_model(cmc_manual, B_sz_manual, A_sz_manual)

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x_range, y_fit, 'r-', label='Dopasowanie automatyczne', linewidth=2)
            ax.plot(x_range, y_manual, 'g--', label='Parametry ręczne', linewidth=2)
            ax.scatter(x_data, y_data, label='Dane eksperymentalne', color='blue', zorder=5)

            # Zaznaczenie CMC
            ax.axvline(cmc, color='purple', linestyle=':', label=f'CMC = {cmc:.6f} mol/L')
            ax.scatter([cmc], [gamma_cmc], color='purple', s=100, zorder=6)
            ax.axvline(cmc_manual, color='orange', linestyle=':', label=f'CMC (ręczne) = {cmc_manual:.6f} mol/L')
            ax.scatter([cmc_manual], [gamma_cmc_manual], color='orange', s=100, zorder=6)

            # Formatowanie wykresu
            ax.set_xlabel('Stężenie [mol/L]', fontsize=12)
            ax.set_ylabel('Napięcie powierzchniowe [mN/m]', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Wyświetlanie równania
            equation_text = (
                f"$\gamma = {FIXED_Y0} \cdot (1 - {B_sz_fit:.6f} \cdot "
                f"\ln(\\frac{{c}}{{{A_sz_fit * 1e6:.6f}}} + 1))$"            )
            plt.title(equation_text, fontsize=12, pad=20)
            
            st.pyplot(fig)
            
            plt.tight_layout()

            # Eksport wyników
            results = pd.DataFrame({
                "Parametr": ["γ₀ (ustalone)", "B_sz", "A_sz", "CMC", "Γ (CMC)", "Γ_max", "ΔGm", "R²"],
                "Wartość": [FIXED_Y0, B_sz_fit, A_sz_fit, cmc, gamma, gamma_max, delta_gm, r_squared],
                "Jednostka": ["mN/m", "-", "mol/L", "mol/L", "mol/m²", "mol/m²", "kJ/mol", "-"]
            })
            
            csv = results.to_csv(index=False, sep=";").encode('utf-8')
            st.download_button(
                label="Pobierz wyniki jako CSV",
                data=csv,
                file_name="wyniki_izotermy.csv",
                mime="text/csv"
            )