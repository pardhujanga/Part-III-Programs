import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Load the file
file_path = r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\FeSb2_CVT2_1.dat"

# --- Parse data as before ---
with open(file_path, 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == '[Data]':
        data_start_index = i
        break

header_line = lines[data_start_index + 1].strip()
columns = header_line.split(',')
data_lines = lines[data_start_index + 2:]
data = [line.strip().split(',') for line in data_lines if line.strip()]
df = pd.DataFrame(data, columns=columns)

# Convert temperature and all bridge resistivities
df["Temperature (K)"] = pd.to_numeric(df["Temperature (K)"], errors='coerce')
bridge_cols = [col for col in df.columns if "Resistivity" in col]
for col in bridge_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Boltzmann constant
k_B = 8.617333262145e-5  # eV/K

# --- Loop over each bridge column ---
for col in bridge_cols:
    d = df[["Temperature (K)", col]].dropna()

        # Skip columns with too little valid data
    if len(d) < 5 or d[col].isna().all():
        print(f"Skipping {col} — not enough valid data.")
        continue

    d["1/T (1/K)"] = 1 / d["Temperature (K)"]
    d["ln(Resistivity)"] = np.log(d[col])
    d = d.replace([np.inf, -np.inf], np.nan).dropna()


    # --- Fit 1: near 1/T = 0 ---
    fit1 = d[d["1/T (1/K)"] < 0.015]
    res1 = linregress(fit1["1/T (1/K)"], fit1["ln(Resistivity)"])
    slope1, intercept1, r1, p1, stderr1 = res1
    Ea1 = slope1 * k_B * 1000  # meV
    Ea1_err = stderr1 * k_B * 1000  # meV

    # --- Fit 2: 0.03 < 1/T < 0.06 ---
    fit2 = d[(d["1/T (1/K)"] > 0.025) & (d["1/T (1/K)"] < 0.055)]
    res2 = linregress(fit2["1/T (1/K)"], fit2["ln(Resistivity)"])
    slope2, intercept2, r2, p2, stderr2 = res2
    Ea2 = slope2 * k_B * 1000  # meV
    Ea2_err = stderr2 * k_B * 1000  # meV



    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(d["1/T (1/K)"], d["ln(Resistivity)"], 'o-', color= 'black', label="Data")

    x1 = np.linspace(fit1["1/T (1/K)"].min(), fit1["1/T (1/K)"].max(), 100)
    x2 = np.linspace(fit2["1/T (1/K)"].min(), fit2["1/T (1/K)"].max(), 100)

    plt.plot(x1, slope1 * x1 + intercept1, 'r--', label=f"Eₐ = {Ea1:.1f} ± {Ea1_err:.1f} meV")
    plt.plot(x2, slope2 * x2 + intercept2, 'g--', label=f"Eₐ = {Ea2:.2f} ± {Ea2_err:.2f} meV")


    plt.xlabel("1 / Temperature (1/K)")
    plt.ylabel("ln(Resistivity/Ω·m)")
    plt.title("ln(Resistivity) vs 1/T")
    plt.legend()
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()
