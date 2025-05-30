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

def analiza_i_wykres(df, tryb_label, x_column, x_label):
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd

    # Przygotuj dataframe do edycji
    df_editable = df[["sigma", "tlife", "sqrt_tlife", "inv_tlife"]].copy()
    df_editable["Użyj"] = True  # domyślnie zaznaczone wszystkie

    st.markdown(f"### 📄 Podgląd i wybór punktów ({tryb_label})")
    edited_df = st.data_editor(
        df_editable,
        column_config={"Użyj": st.column_config.CheckboxColumn("Użyj punktu")},
        disabled=["sigma", "tlife", "sqrt_tlife", "inv_tlife"],
        use_container_width=True,
        key=tryb_label
    )

    # Filtrowanie tylko zaznaczonych punktów
    df_filtered = df.copy()
    df_filtered["Użyj"] = edited_df["Użyj"]
    df_filtered = df_filtered[df_filtered["Użyj"] == True]

    if df_filtered.empty:
        st.warning("❗ Zaznacz przynajmniej jeden punkt do analizy.")
        return None

    x = df_filtered[x_column].values.reshape(-1, 1)
    y = df_filtered["sigma"].values

    x_bytes = x.tobytes()
    y_bytes = y.tobytes()
    model = fit_linear_model_cached(x_bytes, y_bytes)
    y_pred = model.predict(x)
    a, b = model.coef_[0], model.intercept_

    st.markdown(f"### 📐 Współczynnik kierunkowy ({tryb_label})")
    st.write(f"y = **{a:.4f}·x + {b:.4f}**")

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    ax.set_title(f"{tryb_label}", fontsize=10, fontweight='bold')
    ax.tick_params(axis='both', labelsize=10)
    ax.scatter(x, y, color="#1f77b4", s=30, label="Wybrane punkty")
    ax.plot(x, y_pred, color="#d62728", linewidth=2, label="Dopasowana prosta")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlabel(x_label, fontsize=8)
    ax.set_ylabel("Sigma [mN/m]", fontsize=8)
    ax.legend(loc="best", fontsize=8, frameon=True)
    st.pyplot(fig, use_container_width=False)

    return a


st.title("📉 Analiza kinetyki adsorpcji – tryb podwójny")

col1, col2 = st.columns(2)
with col1:
    premicel_file = st.file_uploader("📁 Wczytaj plik *premicelarny*", type=["txt", "dat"], key="premicel")
with col2:
    micel_file = st.file_uploader("📁 Wczytaj plik *micelarny*", type=["txt", "dat"], key="micel")

a_premi = None
a_mice = None

if premicel_file:
    df_premi = load_data(premicel_file)
    a_premi = analiza_i_wykres(df_premi, "premicelarny", "sqrt_tlife", "√Tlife [√ms]")

if micel_file:
    df_mice = load_data(micel_file)
    a_mice = analiza_i_wykres(df_mice, "micelarny", "inv_tlife", "1/Tlife [1/ms]")

if a_premi or a_mice:
    st.subheader("📊 Wyznaczanie współczynnika dyfuzji")
    import numpy as np

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        temp_scale = st.selectbox("Skala temperatury", ["Celsjusz", "Farenheit", "Kelvin"])
    with col2:
        temp_input = st.number_input("Temperatura", value=23.1)
        if temp_scale == "Celsjusz":
            T = temp_input + 273.15
        elif temp_scale == "Farenheit":
            T = (temp_input - 32) * 5 / 9 + 273.15
        else:
            T = temp_input
    with col3:
        n = st.number_input("n (1 = niejonowy, 2 = jonowy)", value=1)
    with col4:
        c = st.number_input("Stężenie surfaktantu [mol/L]", value=1e-3, format="%.5f")

    c_m3 = c * 1000
    R = 8.314

    if a_premi:
        try:
            a_SI = a_premi / 1000  # mN/m -> N/m
            D = ((a_SI / (-2 * n * R * T * c_m3)) ** 2) * np.pi
            st.write(f"**Współczynnik dyfuzji D (premicelarny)** = {D:.4e} m²/s")
        except Exception as e:
            st.error(f"[Premicelarny] Błąd obliczeń: {e}")
    if a_mice:
        try:
            a_SI = a_mice / 1000  # mN/m -> N/m
            D = ((a_SI / (-2 * n * R * T * c_m3)) ** 2) * np.pi
            st.write(f"**Współczynnik dyfuzji D (micelarny)** = {D:.4e} m²/s")
        except Exception as e:
            st.error(f"[Micelarny] Błąd obliczeń: {e}")

if a_premi is not None and a_mice is not None:
    st.subheader("📈 Obliczanie stałej k₂ ze wzoru")

    try:
        pi = np.pi
        alpha = 1
        k2 = (4 / pi) * ((a_mice / a_premi) ** 2)
        st.write(r"$k_2 = \frac{4}{\pi} \cdot \left(\frac{a_{micelarny}}{a_{premicelarny}}\right)^2$")
        st.latex(f"k_2 = \\frac{{4}}{{{pi}}} \\cdot \\left(\\frac{{{a_mice:.4e}}}{{{a_premi:.4e}}}\\right)^2 = {k2:.4e}")
    except Exception as e:
        st.error(f"Nie udało się obliczyć k₂: {e}")
