import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------
# 1) CONFIGURATION
# ----------------------------
file_path = r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\FeSb2_TVT2_2_3_4.dat"
default_error_fraction = 0.02  # 2% fallback error

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
        raise ValueError("No [Data] section found")

    header = lines[data_start_index + 1].strip().split(',')
    data_lines = lines[data_start_index + 2:]
    data = [row.strip().split(',') for row in data_lines if row.strip()]
    df = pd.DataFrame(data, columns=header)

    df["Temperature (K)"] = pd.to_numeric(df["Temperature (K)"], errors="coerce")
    for col in df.columns:
        if "Resistivity" in col or "Std. Dev." in col:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

# ----------------------------
# 3) PLOT EACH BRIDGE INDIVIDUALLY
# ----------------------------
df = parse_dat_file(file_path)

bridge_cols = [c for c in df.columns if "Resistivity" in c and "Std. Dev." not in c]

for idx, col in enumerate(bridge_cols, start=1):
    d = df[["Temperature (K)", col]].dropna()
    d = d.replace([np.inf, -np.inf], np.nan).dropna()

    if len(d) < 5:
        print(f"Skipping {col}: not enough data")
        continue

    std_col = col.replace("Resistivity", "Std. Dev.")
    if std_col in df.columns:
        d["Error"] = pd.to_numeric(df[std_col], errors="coerce")
        d = d.dropna(subset=["Error"])
    else:
        d["Error"] = default_error_fraction * d[col]

    if len(d) < 5:
        print(f"Skipping {col}: not enough points with error data")
        continue

    # Plot
    plt.figure(figsize=(8, 5))
    plt.errorbar(
        d["Temperature (K)"],
        d[col],
        yerr=d["Error"],
        fmt='o',
        markersize=4,
        capsize=2,
        ecolor='gray',
        elinewidth=1,
        label=col
    )

    plt.xlabel("Temperature (K)", fontsize=12)
    plt.ylabel("Resistivity (Ω·m)", fontsize=12)
    plt.title("Resitivity vs Temperature", fontsize=13)
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()
