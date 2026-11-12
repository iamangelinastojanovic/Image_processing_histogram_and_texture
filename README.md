# Image Texture Analysis

First-order brightness texture of public H&E skeletal-muscle cross-sections. The report follows the MIT 6.819/6.869 structure: question, related measures, experiment, and the reasons the comparison cannot be read as a diagnosis.

## Question

Do first-order histogram measures and Haralick co-occurrence features separate uninjured muscle from cardiotoxin-injured muscle on the MyoAnalyst H&E sections?

## Data

Four mouse skeletal-muscle cross-sections from MyoAnalyst, Zenodo record [10.5281/zenodo.14915567](https://doi.org/10.5281/zenodo.14915567), file `HE_input.zip` (CC BY 4.0). One section is an uninjured PBS control. Three are cardiotoxin-injured (CTX), at days 7, 14 and 21. One of the injured sections is a knockout. Newcastle NCL-SM is the human biopsy set with the same scientific role, but it is published as a single 5.5 GB archive, so this project uses the smaller public H&E release.

## Reproduce

```bash
pip install -r requirements.txt
python run_experiment.py
```

The script downloads and unzips the sections into `data/` and writes `results/`. The ZIP and the TIFF sections are not part of this repository. The figures already in `results/` are.

## Result

On the whole section, uninjured PBS entropy is 5.41 bits and GLCM energy is 0.233. The injured sections sit at 6.67–6.99 bits and energy 0.030–0.061. Neighbor correlation does not separate the groups (about 0.97 in every section). There is only one uninjured section, so this describes these four slides, not a diagnosis.

Details are in [REPORT.md](REPORT.md).
