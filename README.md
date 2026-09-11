# Molecular-Dynamics Analysis Pipeline

This repository contains a reproducible post-processing workflow for comparing four molecular-dynamics systems involving XRCC1 wild-type and R194W variants with LigIIIalpha and Polbeta:

- `XRCC1WT-LigIIIalpha`
- `XRCC1WT-Polbeta`
- `XRCC1R194W-LigIIIalpha`
- `XRCC1R194W-Polbeta`

The project analyzes trajectory-derived observables and MM/PBSA-related energy terms over 300 ns simulations.

## Pipeline Overview

```text
Trajectory calculations performed upstream
        |
        v
Excel or CSV time-series files
        |
        v
Parameter-specific block-analysis scripts
        |
        v
Block-statistics Excel workbooks
        |
        v
MD-analysis.ipynb
        |
        v
Comparison plots and cumulative-mean plots
```

The scripts in this repository summarize precomputed values. They do not calculate RMSD, radius of gyration, SASA, or MM/PBSA energies directly from coordinates. The upstream trajectory and energy calculations must be documented separately, including the software version, force field, frame-selection scheme, and MM/PBSA settings.

## Parameters

The workflow supports:

- RMSD
- Radius of gyration (`Rg`)
- Solvent-accessible surface area (`SASA`)
- Molecular-mechanics energy (`MM`)
- Poisson-Boltzmann energy (`PB`)
- Surface-area energy (`SA`)
- Estimated binding free energy (`Delta G_bind`)

Additional workbooks are present for hydrogen bonds and contacts and can be incorporated into future analysis extensions.

## Repository Structure

```text
.
├── MD-analysis.ipynb                         # Main plotting and analysis notebook
├── addon.ipynb                               # Additional notebook analyses
├── block_analysis.py                         # General block-analysis script
├── block_analysis-MM.py                      # MM block analysis
├── block_analysis-PB.py                      # PB block analysis
├── block_analysis-RG.py                      # Radius-of-gyration block analysis
├── block_analysis-SA.py                      # SA block analysis
├── block_analysis-SASA.py                    # SASA block analysis
├── block_analysis-bind.py                    # Binding-energy block analysis
├── Methodology.txt                           # Detailed methodology
├── Analysis.txt                              # Interpretation of comparison plots
├── *.xlsx                                    # Input and block-statistics workbooks
├── MD-10may/                                 # Molecular-dynamics files and trajectories
└── results/                                  # Generated figures
```

## Block Analysis

Each 300 ns simulation is divided into six consecutive, non-overlapping 50 ns intervals:

1. `0-50 ns`
2. `50-100 ns`
3. `100-150 ns`
4. `150-200 ns`
5. `200-250 ns`
6. `250-300 ns`

For every system and block, the scripts calculate:

- Number of valid observations (`N`)
- Arithmetic mean (`Mean`)
- Sample standard deviation (`SD`)
- Minimum (`Min`)
- Maximum (`Max`)

Rows with invalid time values are removed. Non-numeric observable values are treated as missing and excluded from the corresponding block statistics.

The output is written beside the input file with the suffix `_block_statistics.xlsx`.

## Cumulative-Mean Analysis

The notebook reads the block-statistics workbooks and uses the `Mean` column as input. For each system, it calculates the running arithmetic mean of the block means:

$$
CM_K = \\frac{1}{K} \\sum_{k=1}^{K} m_k
$$

where $m_k$ is the mean of block $k$ and $K$ is the number of blocks included.

This is an unweighted cumulative mean of block means. It does not pool raw observations and does not weight blocks by their number of valid observations. The notebook generates parameter- and system-specific PNG files in `results/` using the `_cumulative_mean.png` suffix.

## Requirements

The workflow uses Python and the following packages:

- pandas
- NumPy
- Matplotlib
- openpyxl

A virtual environment is recommended. Example setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pandas numpy matplotlib openpyxl
```

## Running the Pipeline

Run a parameter-specific script with an explicit input path:

```bash
python block_analysis-RG.py \
  --input /path/to/Rg-WT-replicate-and-R194W.xlsx \
  --output /path/to/Rg-WT-replicate-and-R194W_block_statistics.xlsx
```

The same command pattern applies to the MM, PB, SA, SASA, binding-energy, and general block-analysis scripts. Each script accepts configurable block size and total simulation time; the default values are 50 ns and 300 ns.

After generating the block-statistics workbooks, open and run `MD-analysis.ipynb` to generate comparison and cumulative-mean plots. The notebook expects the project directory to be `/home/naba/projects` unless the path variables are changed.

## Outputs

The pipeline produces:

- Block-statistics Excel files containing `System`, `Block`, `N`, `Mean`, `SD`, `Min`, and `Max`
- Comparison plots for the analyzed systems
- Cumulative-mean plots in `results/`

## Reproducibility Notes

- Use explicit input and output paths when running scripts.
- Keep the same block size and total simulation time across parameters when making direct comparisons.
- Confirm that all input files use consistent units.
- Record the original trajectory-analysis software and settings separately from this post-processing workflow.
- Check equilibration and autocorrelation before using block means for formal statistical inference.
- Treat the reported within-block standard deviations as descriptive dispersion, not automatically as confidence intervals.

## Limitations

The workflow is intended for descriptive temporal summaries and visualization. It does not perform statistical significance testing, replicate-level uncertainty analysis, autocorrelation correction, or hypothesis testing between systems. Such analyses should be added before drawing formal statistical conclusions.

## Citation and Documentation

See [Methodology.txt](Methodology.txt) for the detailed computational method and [Analysis.txt](Analysis.txt) for the interpretation of the generated comparison plots.
