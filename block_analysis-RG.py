import argparse
import os

import numpy as np
import pandas as pd


def find_input_file():
    """Find the likely RG data file without requiring interactive input."""
    folder = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if name.lower().endswith((".xlsx", ".xls", ".csv"))
        and not name.startswith("~$")
        and "_block_statistics" not in name
    ]
    rg_candidates = [
        path for path in candidates
        if os.path.basename(path).lower().startswith("rg")
    ]
    if len(rg_candidates) == 1:
        return rg_candidates[0]
    if len(candidates) == 1:
        return candidates[0]

    names = "\n".join(f"  {path}" for path in sorted(candidates))
    raise ValueError(
        "More than one input file was found. Run the script with the exact file path:\n"
        "python block_analysis-RG.py --input /full/path/to/your/file.xlsx\n\n"
        f"Files found:\n{names}"
    )


def parse_sheet(value):
    try:
        return int(value)
    except ValueError:
        return value


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate block statistics from an MD analysis Excel or CSV file."
    )
    parser.add_argument(
        "-i", "--input", dest="input_file",
        help="Input .xlsx, .xls, or .csv file. Opens a file picker when omitted."
    )
    parser.add_argument(
        "-o", "--output", dest="output_file",
        help="Output Excel file. Defaults to '<input>_block_statistics.xlsx'."
    )
    parser.add_argument(
        "-b", "--block-size", type=float, default=50,
        help="Block duration in ns (default: 50)."
    )
    parser.add_argument(
        "-t", "--total-time", type=float, default=300,
        help="Total simulation time in ns (default: 300)."
    )
    parser.add_argument(
        "-s", "--sheet", type=parse_sheet, default=0,
        help="Excel sheet name or zero-based index (default: 0)."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    file_path = args.input_file or os.environ.get(
        "MD_ANALYSIS_INPUT_FILE", ""
    ).strip()
    if not file_path:
        file_path = find_input_file()

    file_path = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"\nInput file not found:\n{file_path}\n"
            "Use --input to provide a valid file path."
        )
    if args.block_size <= 0 or args.total_time <= 0:
        raise ValueError("Block size and total time must be greater than zero.")

    print("\nSelected input file:")
    print(file_path)

    extension = os.path.splitext(file_path)[1].lower()
    if extension in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path, sheet_name=args.sheet)
    elif extension == ".csv":
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Use .xlsx, .xls, or .csv.")

    if df.empty or len(df.columns) < 2:
        raise ValueError(
            "The input file must contain a time column and at least one system column."
        )

    time_col = df.columns[0]
    df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col]).copy()
    system_columns = list(df.columns[1:])

    print("\nTime column:", time_col)
    print("\nSystems detected:")
    for system in system_columns:
        print(" -", system)

    number_of_blocks = int(np.ceil(args.total_time / args.block_size))
    df["Block_Number"] = np.minimum(
        (df[time_col] // args.block_size).astype(int),
        number_of_blocks - 1
    )

    block_labels = {}
    for index in range(number_of_blocks):
        start = index * args.block_size
        end = min((index + 1) * args.block_size, args.total_time)
        block_labels[index] = f"{start:g}-{end:g} ns"
    df["Block"] = df["Block_Number"].map(block_labels)

    results = []
    for system in system_columns:
        df[system] = pd.to_numeric(df[system], errors="coerce")
        for block, values in df.groupby("Block", observed=True)[system]:
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
    results_df["Block"] = pd.Categorical(
        results_df["Block"],
        categories=list(block_labels.values()),
        ordered=True
    )
    results_df = results_df.sort_values(
        ["System", "Block"]
    ).reset_index(drop=True)

    input_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = args.output_file or os.path.join(
        os.path.dirname(file_path),
        f"{input_name}_block_statistics.xlsx"
    )
    output_file = os.path.abspath(os.path.expanduser(output_file))
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    results_df.to_excel(output_file, index=False)

    print("\nBlock analysis completed successfully.")
    print("Output saved to:")
    print(output_file)
    print("\nResults:\n")
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    main()
