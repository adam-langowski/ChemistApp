
Bioinformatyka 2025 MGR

# OPIS APLIKACJI

## 📈 Izoterma napięcia powierzchniowego — Model Szyszkowskiego

Ta zakładka umożliwia analizę danych eksperymentalnych opisujących zależność napięcia powierzchniowego od stężenia surfaktantu w roztworze. Wykorzystywany jest model Szyszkowskiego z ustaloną wartością napięcia powierzchniowego czystej wody (γ₀ = 72 mN/m), a parametry izotermy są dopasowywane do danych metodą najmniejszych kwadratów.

**Funkcjonalności**:

- Wczytywanie danych z pliku CSV (z kolumnami `stezenie` i `napiecie`).
- Dopasowanie krzywej modelu Szyszkowskiego do danych pomiarowych.
- Obliczanie i prezentacja kluczowych parametrów fizykochemicznych:
  - **B** i **A** — parametry modelu,
  - **CMC** — krytyczne stężenie micelarne,
  - **Γ (CMC)** i **Γ_max** — nadmiar powierzchniowy,
  - **ΔG_m** — energia swobodna micelizacji,
  - **R²** — współczynnik dopasowania modelu.
- **Interaktywna analiza wpływu parametrów modelu na kształt krzywej i wartość CMC**.
- Wsparcie dla surfaktantów jonowych i niejonowych (z możliwością określenia stopnia dysocjacji α).
- Eksport wyników analizy do pliku CSV.

Podgląd:

![1744667220563](image/README/1744667220563.png)
