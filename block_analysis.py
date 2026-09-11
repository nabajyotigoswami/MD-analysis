import pandas as pd
import numpy as np
import os

# --------------------------------------------------
# USER INPUT
# --------------------------------------------------

FILE = input(
    "\nEnter or paste the full path of the Excel/CSV file:\n"
).strip().strip('"').strip("'")

BLOCK_SIZE = 50
TOTAL_TIME = 300
SHEET_NAME = 0

# --------------------------------------------------
# CHECK FILE
# --------------------------------------------------

if not os.path.exists(FILE):
    raise FileNotFoundError(
        f"\nFile not found:\n{FILE}\n"
        "Please check the path and run the script again."
    )

print("\nSelected file:")
print(FILE)

# --------------------------------------------------
# READ FILE
# --------------------------------------------------

extension = os.path.splitext(FILE)[1].lower()

if extension in [".xlsx", ".xls"]:
    df = pd.read_excel(
        FILE,
        sheet_name=SHEET_NAME
    )

elif extension == ".csv":
    df = pd.read_csv(FILE)

else:
    raise ValueError(
        "Unsupported file format. Use .xlsx, .xls, or .csv."
    )

# --------------------------------------------------
# IDENTIFY TIME COLUMN
# --------------------------------------------------

time_col = df.columns[0]

df[time_col] = pd.to_numeric(
    df[time_col],
    errors="coerce"
)

df = df.dropna(
    subset=[time_col]
).copy()

system_columns = list(df.columns[1:])

print("\nTime column:", time_col)

print("\nSystems detected:")
for system in system_columns:
    print(" -", system)

# --------------------------------------------------
# ASSIGN BLOCKS
# --------------------------------------------------

number_of_blocks = int(
    np.ceil(TOTAL_TIME / BLOCK_SIZE)
)

df["Block_Number"] = np.minimum(
    (df[time_col] // BLOCK_SIZE).astype(int),
    number_of_blocks - 1
)

block_labels = {}

for i in range(number_of_blocks):

    start = i * BLOCK_SIZE
    end = min(
        (i + 1) * BLOCK_SIZE,
        TOTAL_TIME
    )

    block_labels[i] = f"{start}-{end} ns"

df["Block"] = df["Block_Number"].map(
    block_labels
)

# --------------------------------------------------
# CALCULATE BLOCK STATISTICS
# --------------------------------------------------

results = []

for system in system_columns:

    df[system] = pd.to_numeric(
        df[system],
        errors="coerce"
    )

    grouped = df.groupby(
        "Block",
        observed=True
    )[system]

    for block, values in grouped:

        values = values.dropna()

        results.append({
            "System": system,
            "Block": block,
            "N": values.count(),
            "Mean": values.mean(),
            "SD": values.std(),
            "Min": values.min(),
            "Max": values.max()
        })

results_df = pd.DataFrame(results)

# --------------------------------------------------
# SORT BLOCKS
# --------------------------------------------------

block_order = list(
    block_labels.values()
)

results_df["Block"] = pd.Categorical(
    results_df["Block"],
    categories=block_order,
    ordered=True
)

results_df = results_df.sort_values(
    ["System", "Block"]
).reset_index(drop=True)

# --------------------------------------------------
# OUTPUT FILE
# --------------------------------------------------

input_folder = os.path.dirname(FILE)

input_name = os.path.splitext(
    os.path.basename(FILE)
)[0]

OUTPUT_FILE = os.path.join(
    input_folder,
    f"{input_name}_block_statistics.xlsx"
)

results_df.to_excel(
    OUTPUT_FILE,
    index=False
)

# --------------------------------------------------
# FINISH
# --------------------------------------------------

print("\nBlock analysis completed successfully.")

print("\nOutput saved at:")
print(OUTPUT_FILE)

print("\nResults:\n")
print(results_df.to_string(index=False))
# --------------------------------------------------
# OUTPUT FILE
# --------------------------------------------------

input_folder = os.path.dirname(FILE)

input_name = os.path.splitext(
    os.path.basename(FILE)
)[0]

OUTPUT_FILE = os.path.join(
    input_folder,
    f"{input_name}_block_statistics.xlsx"
)

# --------------------------------------------------
# SAVE RESULTS TO EXCEL
# --------------------------------------------------

results_df.to_excel(
    OUTPUT_FILE,
    index=False
)

# --------------------------------------------------
# FINAL MESSAGE ONLY
# --------------------------------------------------

print("\nBlock analysis completed successfully.")
print("Results saved to:")
print(OUTPUT_FILE)