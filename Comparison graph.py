import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def parse_dat_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip() == '[Data]':
            data_start = i
            break

    header = lines[data_start + 1].strip().split(',')
    data_lines = lines[data_start + 2:]
    data = [line.strip().split(',') for line in data_lines if line.strip()]
    df = pd.DataFrame(data, columns=header)

    df["Temperature (K)"] = pd.to_numeric(df["Temperature (K)"], errors='coerce')
    for col in df.columns:
        if "Resistivity" in col:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# --- File paths and columns to include ---
files_and_columns = [
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\TVT1_Rxx_FeSb2_TVT1_CH1_GenericCooldown_00002_current1000uA.dat",
        "columns": ["Bridge 1 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\TVT1_Rxx_FeSb2_TVT1_CH1_GenericCooldown_00002_current100uA.dat",
        "columns": ["Bridge 1 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\TVT_2_FeSb2_ch3_2.dat",
        "columns": ["Bridge 3 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\TVT_2_FeSb2_ch1_ch3.dat",
        "columns": ["Bridge 1 Resistivity (Ohm-m)","Bridge 3 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\FeSb2_TVT2_2_3_4_diff_current.dat",
        "columns": ["Bridge 3 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\FeSb2_TVT2_2_3_4.dat",
        "columns": ["Bridge 1 Resistivity (Ohm-m)","Bridge 3 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\FeSb2_CVT456_warmup.dat",
        "columns": ["Bridge 1 Resistivity (Ohm-m)","Bridge 2 Resistivity (Ohm-m)","Bridge 3 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\FeSb2_CVT2_456.dat",
        "columns": ["Bridge 1 Resistivity (Ohm-m)","Bridge 2 Resistivity (Ohm-m)","Bridge 3 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\FeSb2_CVT2_123_warmup.dat",
        "columns": ["Bridge 1 Resistivity (Ohm-m)","Bridge 3 Resistivity (Ohm-m)"]
    },
    {
        "path": r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\FeSb2_CVT2_1.dat",
        "columns": ["Bridge 1 Resistivity (Ohm-m)","Bridge 3 Resistivity (Ohm-m)"]
    }
]

# --- Preprocess and collect all data ---
all_traces = []

for i, entry in enumerate(files_and_columns):
    df = parse_dat_file(entry["path"])
    for col in entry["columns"]:
        if col not in df.columns:
            print(f"Column {col} not found in {entry['path']}")
            continue

        d = df[["Temperature (K)", col]].dropna()
        d = d.replace([np.inf, -np.inf], np.nan).dropna()

        if len(d) < 5:
            print(f"Skipping {col} — not enough data")
            continue

        closest_idx = (d["Temperature (K)"] - 300).abs().idxmin()
        rho_300_val = d.loc[closest_idx, col]
        if pd.isna(rho_300_val):
            print(f"No valid resistivity near 300 K in {col} from {entry['path']}")
            continue

        d["Normalised Resistivity"] = d[col] / rho_300_val

        file_idx = i + 1
        bridge_idx = [int(s) for s in col.split() if s.isdigit()][0]
        label = f"{file_idx}.{bridge_idx}"

        all_traces.append((d["Temperature (K)"], d["Normalised Resistivity"], label))

# --- Colour map: RGB gradient using viridis ---
n = len(all_traces)
colors = [mcolors.to_hex(plt.cm.viridis(i / max(n - 1, 1))) for i in range(n)]

# --- Plotting ---
plt.figure(figsize=(10, 6))

for i, (T, norm_rho, label) in enumerate(all_traces):
    plt.plot(T, norm_rho, label=label, color=colors[i], linewidth=1.8)

plt.xlabel("Temperature (K)", fontsize=12)
plt.ylabel("Normalised Resistivity (ρ / ρ₃₀₀ₖ)", fontsize=12)
plt.title("Normalised Resistivity vs Temperature", fontsize=14)
plt.xscale('log')
plt.grid(True, which="both", linestyle='--', linewidth=0.5)
plt.legend(title="File.Bridge", fontsize=9, title_fontsize=10, loc="best")
plt.tight_layout()
plt.show()

