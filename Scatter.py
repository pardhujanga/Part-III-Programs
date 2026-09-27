import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------
# 1) CONFIGURATION
# ----------------------------

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

# ----------------------------
# 2) PARSE .dat FILE
# ----------------------------

def parse_dat_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip() == "[Data]":
            data_start_index = i
            break
    else:
        raise ValueError(f"No [Data] section found in {path}")

    header = lines[data_start_index + 1].strip().split(',')
    data_lines = lines[data_start_index + 2:]
    data = [line.strip().split(',') for line in data_lines if line.strip()]
    df = pd.DataFrame(data, columns=header)

    df["Temperature (K)"] = pd.to_numeric(df["Temperature (K)"], errors="coerce")
    for col in df.columns:
        if "Resistivity" in col:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

# ----------------------------
# 3) COLLECT iRRR DATA
# ----------------------------

results = []

for file_idx, entry in enumerate(files_and_columns, start=1):
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

        t_base_idx = (d["Temperature (K)"] - 300).abs().idxmin()
        rho_base = d.loc[t_base_idx, col]

        t_low_idx = d["Temperature (K)"].idxmin()
        rho_low = d.loc[t_low_idx, col]

        if pd.isna(rho_base) or pd.isna(rho_low):
            print(f"Missing data for {col} in {entry['path']}")
            continue

        irrr = rho_low / rho_base

        results.append({
            "rho_base": rho_base,
            "iRRR": irrr
        })

# ----------------------------
# 4) PLOT SCATTERPLOT
# ----------------------------

if results:
    df_result = pd.DataFrame(results)

    cmap = plt.get_cmap("tab20")  # colour map with good contrast
    colours = [cmap(i % 20) for i in range(len(df_result))]

    plt.figure(figsize=(8, 5))
    plt.scatter(df_result["rho_base"], df_result["iRRR"], color=colours, s=60)

    plt.xlabel("Resistivity at 300K (Ω·m)", fontsize=12)
    plt.ylabel("iRRR", fontsize=12)
    plt.title("iRRR vs ρ(300K)", fontsize=14)
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()
else:
    print("No valid data to plot.")

