import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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


df = parse_dat_file(r"C:\Users\pardh\Dropbox\My PC (LAPTOP-I599KVKH)\Downloads\iRRR plots\DAT files\TVT1_Rxx_FeSb2_TVT1_CH1_GenericCooldown_00002_current1000uA.dat")
print(df.columns.tolist())
