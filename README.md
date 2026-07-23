# Geometric Compensation Design to Offset Mechanical Property Degradation in Recycled Aluminum Alloys for Lightweight Aerospace Structural Components

## Overview

This project investigates how much geometric/weight compensation is required
to preserve the safety factor of an aerospace structural bracket when the
base aluminum alloy (AlSi10MnMg) is manufactured with increasing recycled
scrap content (50-75%), and evaluates the net carbon footprint impact of
this trade-off.

The work combines three layers of analysis:

1. **Material data** — documented mechanical property degradation of
   AlSi10MnMg with increasing recycled scrap content, from a peer-reviewed
   source (see References).
2. **Mechanical design (FEA)** — a simplified version of the GE Jet Engine
   Bracket geometry modeled in FreeCAD, analyzed under three load cases
   with CalculiX.
3. **Computational sensitivity analysis** — a Python script that combines
   material degradation data with FEA stress results to estimate required
   geometric compensation and net CO2 impact.

## Repository Structure

```
GE_Bracket_Recycled_Al_Project/
├── README.md
├── requirements.txt
├── freecad/
│   └── GE_bracket_v2.FCStd
├── python_analysis/
│   ├── sensitivity_analysis.py
│   └── sensitivity_results.csv
└── figures/
    ├── sensitivity_analysis_plots.png
    └── *.PNG
```

## How to Run

1. Install Python 3.x
2. Install dependencies:
```
   pip install -r requirements.txt
```
3. Run the sensitivity analysis:
```
   cd python_analysis
   python sensitivity_analysis.py
```
4. To inspect the FEA model, open `freecad/GE_bracket_v2.FCStd` in
   FreeCAD 1.1+ (FEM workbench, CalculiX solver required).

## Key Findings (Summary)

- Under all three GE Bracket load cases, the simplified bracket geometry
  exceeds the yield strength of the AlSi10MnMg alloy even at 50% recycled
  scrap content, indicating this simplified (non-topology-optimized)
  geometry is undersized for these loads regardless of material source.
- Increasing recycled scrap content from 50% to 75% (with Mn addition)
  reduces yield strength by ~18%, requiring an estimated 10-22% linear
  dimensional increase to restore the 50%-scrap safety factor.
- Despite this mass penalty, the net carbon footprint of the compensated
  recycled-content part remains substantially lower than an equivalent
  100%-primary-aluminum part, since CO2 savings from recycling (~95%
  reduction per unit mass) outweigh the compensation penalty.

## Known Limitations

- The bracket geometry is a simplified representation of the GE Jet Engine
  Bracket, not the topology-optimized design from the original challenge.
- The geometric compensation estimate is an analytical approximation, not
  verified by re-running FEA at the scaled geometries (planned as future
  work in a follow-up project).
- Intermediate scrap-content data points (55-70%) are linearly interpolated
  between two experimentally reported endpoints (50% and 75%), since the
  source paper does not report exact intermediate values in text form.

## References

1. Piatkowski, J., Nowinska, K., Matula, T., Siwiec, G., Szucki, M., &
   Oleksiak, B. (2025). Microstructure and Mechanical Properties of
   AlSi10MnMg Alloy with Increased Content of Recycled Scrap. *Materials*,
   18(5), 1119. https://doi.org/10.3390/ma18051119
2. GE / GrabCAD (2013). GE Jet Engine Bracket Challenge.
   https://grabcad.com/challenges/ge-jet-engine-bracket-challenge
3. International Aluminium Institute (2022). Aluminium Sector Greenhouse
   Gas Emissions.
   https://international-aluminium.org/statistics/greenhouse-gas-emissions-aluminium-sector/

## Author

Shahrzad Rofoee — M.Sc. Biomedical Engineering (Amirkabir University of
Technology), B.Sc. Materials Science & Engineering (Hamadan University of
Technology).