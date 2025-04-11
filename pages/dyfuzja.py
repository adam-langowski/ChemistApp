import streamlit as st

@st.cache_data
def load_data(file):
    import pandas as pd
    import numpy as np

    df = pd.read_csv(file, sep="\t", engine="python", encoding='cp1250')
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.replace(",", ".", regex=False)
    df.columns = [col.strip().lower() for col in df.columns]
    kolumny_liczbowe = ["sigma", "f", "tlife", "temp"]
    for col in kolumny_liczbowe:
        df[col] = df[col].astype(float)
    df["sqrt_tlife"] = np.sqrt(df["tlife"])
    df["inv_tlife"] = 1 / df["tlife"]
    return df

@st.cache_resource(hash_funcs={bytes: lambda _: hash(_)})
def fit_linear_model_cached(x_bytes, y_bytes):
    import numpy as np
    from sklearn.linear_model import LinearRegression

    x = np.frombuffer(x_bytes).reshape(-1, 1)
    y = np.frombuffer(y_bytes)

    model = LinearRegression()
    model.fit(x, y)
    return model

st.title("📉 Analiza kinetyki adsorpcji – wyznaczanie współczynników")

uploaded_file = st.file_uploader("Wczytaj plik z danymi (np. .dat lub .txt)", type=["dat", "txt"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    if "tlife" not in df.columns or "sigma" not in df.columns:
        st.error("Plik musi zawierać kolumny 'Tlife' i 'sigma'")
    else:
        import numpy as np

        st.subheader("📄 Podgląd danych")
        st.dataframe(df[["sigma", "tlife", "sqrt_tlife", "inv_tlife"]].style.format(precision=4))

        st.subheader("⚙️ Wybierz tryb analizy")
        tryb = st.radio("Tryb przekształcenia osi X:", ("Obszar premicelarny (√Tlife)", "Obszar micelarny (1/Tlife)"))

        if tryb == "Obszar premicelarny (√Tlife)":
            x = df["sqrt_tlife"].values.reshape(-1, 1)
            x_label = "√Tlife [√ms]"
        else:
            x = df["inv_tlife"].values.reshape(-1, 1)
            x_label = "1/Tlife [1/ms]"

        y = df["sigma"].values

        # Bufory do hashowania
        x_bytes = x.tobytes()
        y_bytes = y.tobytes()

        model = fit_linear_model_cached(x_bytes, y_bytes)
        y_pred = model.predict(x)
        a = model.coef_[0]
        b = model.intercept_

        st.subheader("📐 Współczynnik kierunkowy (nachylenie)")
        st.write(f"y = **{a:.4f}·x + {b:.4f}**")
        st.write("Ten współczynnik będzie służył do obliczeń dyfuzji i dysocjacji.")

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
        ax.scatter(x, y, color="blue", label="Dane eksperymentalne")
        ax.plot(x, y_pred, color="red", label="Dopasowana prosta")
        ax.set_xlabel(x_label)
        ax.set_ylabel("Sigma [mN/m]")
        ax.legend()
        st.pyplot(fig, use_container_width=False)

        st.subheader("📊 Wyznaczanie współczynnika dyfuzji")

        col1, col2, col3 = st.columns(3)
        with col1:
            n = st.number_input("n (1 = niejonowy, 2 = jonowy)", value=1)
        with col2:
            T_celsius = st.number_input("Temperatura [°C]", value=23.1)
            T = T_celsius + 273.15
        with col3:
            c = st.number_input("Stężenie surfaktantu [mol/L]", value=1e-3, format="%.5f")

        R = 8.314  # J/mol·K

        try:
            D = ((a / (-2 * n * R * T * c)) ** 2) * np.pi
            st.write(f"**Współczynnik dyfuzji D** = {D:.4e} m²/s")
        except Exception as e:
            st.error(f"Nie udało się obliczyć D: {e}")
