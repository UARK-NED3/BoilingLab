import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 1. Set font to Liberation Serif
# ============================================================
plt.rcParams["font.family"] = "Liberation Serif"

# ============================================================
# 2. File path
# ============================================================
file_path = "/kaggle/input/datasets/zulkar06/pressure-temperature/modified.lvm"

# ============================================================
# 3. Find the actual data header
# ============================================================
with open(file_path, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

data_start = None

for i, line in enumerate(lines):
    if line.startswith("X_Value"):
        data_start = i
        break

if data_start is None:
    raise ValueError("Could not find the X_Value header.")

# ============================================================
# 4. Read only required columns
# ============================================================
df = pd.read_csv(
    file_path,
    sep="\t",
    skiprows=data_start,
    usecols=[
        "X_Value",
        "Temperature_0",
        "Temperature_1",
        "Temperature_2",
        "Voltage 1"
    ]
)

# ============================================================
# 5. Rename columns
# ============================================================
df.rename(columns={
    "X_Value": "Time",
    "Voltage 1": "Pressure_kPa"
}, inplace=True)

# Remove missing values
df = df.dropna()

# ============================================================
# 6. Temperature Distribution Plot
# ============================================================
plt.figure(figsize=(10, 6))

plt.plot(
    df["Time"],
    df["Temperature_0"],
    linewidth=1.5,
    label="Temperature 0"
)

plt.plot(
    df["Time"],
    df["Temperature_1"],
    linewidth=1.5,
    label="Temperature 1"
)

plt.plot(
    df["Time"],
    df["Temperature_2"],
    linewidth=1.5,
    label="Temperature 2"
)

plt.xlabel("Time (s)", fontsize=14)
plt.ylabel("Temperature (°C)", fontsize=14)
plt.title("Temperature Distribution", fontsize=16)

plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)

plt.tight_layout()

# Save PNG
plt.savefig(
    "/kaggle/working/temperature_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# 7. Pressure vs Time Plot
# ============================================================
plt.figure(figsize=(10, 6))

plt.plot(
    df["Time"],
    df["Pressure_kPa"],
    linewidth=1.5,
    label="Pressure"
)

plt.xlabel("Time (s)", fontsize=14)
plt.ylabel("Pressure (kPa)", fontsize=14)
plt.title("Pressure vs Time", fontsize=16)

plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)

plt.tight_layout()

# Save PNG
plt.savefig(
    "/kaggle/working/pressure_vs_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# 8. Confirm
# ============================================================
print("Done!")
print("Temperature plot: temperature_distribution.png")
print("Pressure plot: pressure_vs_time.png")