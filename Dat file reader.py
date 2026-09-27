import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# --- Step 1: Read the file and locate the data block ---
# the 'r' before the file path is to ensure the string is read as a raw string. This is to avoid the classic windows path problem
file_path = r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\TVT1_Rxx_FeSb2_TVT1_CH1_GenericCooldown_00001.dat"

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
if not bridge_cols:
    print("No resistivity columns found.")
else:
    for col in bridge_cols:
        d = df[["Temperature (K)", col]].dropna()
        d["T (K)"] = d["Temperature (K)"]
        d["Resistivity"] = d[col]
        d = d.replace([np.inf, -np.inf], np.nan).dropna()


        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(d["T (K)"], d["Resistivity"], 'o-', color= 'black', label="Data")

        plt.xlabel("Temperature (K)")
        plt.ylabel("Resistivity (Ω·m)")
        plt.title("Resistivity vs T")
        plt.legend()
        plt.grid(True, linestyle='--', linewidth=0.5)
        plt.tight_layout()
        plt.show()

