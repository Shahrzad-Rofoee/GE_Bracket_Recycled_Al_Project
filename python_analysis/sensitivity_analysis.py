"""
sensitivity_analysis.py

Project: Geometric Compensation Design to Offset Mechanical Property
Degradation in Recycled Aluminum Alloys for Lightweight Aerospace
Structural Components (GE Jet Engine Bracket case study)
"""
# ============================================================
# DATA SOURCE (read before editing)
# ============================================================
# All material property values below come from the EXPERIMENTAL
# RESULTS section (not the introduction) of:
#
#   Piatkowski, J., Nowinska, K., Matula, T., Siwiec, G., Szucki, M.,
#   & Oleksiak, B. (2025). Microstructure and Mechanical Properties of
#   AlSi10MnMg Alloy with Increased Content of Recycled Scrap.
#   Materials, 18(5), 1119. https://doi.org/10.3390/ma18051119
#
# Specifically, for the manganese-modified alloy variant:
#   - At 50% scrap content: UTS = 268 MPa, YS = 200 MPa, elongation = 6.8%
#   - At 75% scrap content: UTS = 227 MPa, YS = 164 MPa, elongation = 5.2%
#
# Intermediate points (55, 60, 65, 70%) are NOT reported as exact
# numbers in the paper's text (only shown in a chart, Figure 3).
# This script obtains them by LINEAR INTERPOLATION between the two
# documented endpoints above. This must be disclosed as a
# methodological simplification in the final report.

import numpy as np
import matplotlib.pyplot as plt

# ---- Scrap content levels studied (every 5%, from 50% to 75%) ----
scrap_pct = np.array([50, 55, 60, 65, 70, 75])

# ---- Anchor points directly from the paper (Mn-modified alloy) ----
scrap_anchor = np.array([50, 75])
UTS_anchor = np.array([268.0, 227.0])   # MPa
YS_anchor = np.array([200.0, 164.0])    # MPa
A_anchor = np.array([6.8, 5.2])         # % elongation

# ---- Linear interpolation for the intermediate points ----
UTS = np.interp(scrap_pct, scrap_anchor, UTS_anchor)
YS = np.interp(scrap_pct, scrap_anchor, YS_anchor)
A = np.interp(scrap_pct, scrap_anchor, A_anchor)

print("Scrap % :", scrap_pct)
print("UTS MPa :", UTS)
print("YS MPa  :", YS)
print("Elong % :", A)
# ============================================================
# FEA STRESS RESULTS (from this project's FreeCAD/CalculiX analysis)
# ============================================================
# Baseline material used in FEA: generic aluminum,
# E = 70 GPa, density = 2680 kg/m3, Poisson = 0.33
# (elastic constants assumed constant across scrap content, since
# the cited paper does not report modulus changes with scrap content)

load_cases = {
    "LC1_vertical_8000lb": 246.25,    # MPa, 35586 N vertical
    "LC2_horizontal_8500lb": 684.0,   # MPa, 37812 N horizontal
    "LC3_angled42_9500lb": 526.64,    # MPa, 42258 N at 42 deg
}

# ---- Safety Factor at each scrap level, for each load case ----
# SF = Yield Strength / Max von Mises Stress
sf_table = {}
for name, stress in load_cases.items():
    sf_table[name] = YS / stress
    print(f"\n{name} (stress = {stress} MPa):")
    for i, sp in enumerate(scrap_pct):
        print(f"  scrap={sp}%  SF={sf_table[name][i]:.3f}")

# ============================================================
# REQUIRED GEOMETRIC COMPENSATION
# ============================================================
# Engineering assumption (must be stated in Methods/Limitations):
# For a linear-elastic structure under a FIXED external load, stress
# scales approximately as 1/(scale^p), where:
#   p = 1  -> pure axial/tension scaling
#   p = 2  -> pure bending scaling
# Since the bracket has a MIX of both (confirmed by FEA: horizontal
# load produces much higher stress than vertical, indicating strong
# bending behavior), both bounding cases are reported.

def required_scale_factor(sf_current, sf_target, p):
    return (sf_target / sf_current) ** (1.0 / p)

results = []
for name, stress in load_cases.items():
    sf_baseline = YS[0] / stress  # SF at 50% scrap (reference)
    for i, sp in enumerate(scrap_pct):
        sf_now = sf_table[name][i]
        scale_axial = required_scale_factor(sf_now, sf_baseline, p=1)
        scale_bending = required_scale_factor(sf_now, sf_baseline, p=2)
        results.append({
            "load_case": name,
            "scrap_pct": sp,
            "YS_MPa": YS[i],
            "SF": sf_now,
            "scale_axial_p1": scale_axial,
            "scale_bending_p2": scale_bending,
        })

print("\n\n=== Required geometric scale factor (relative to 50% scrap) ===")
for r in results:
    print(f"{r['load_case']:<25} scrap={r['scrap_pct']:>3}%  "
          f"scale(axial)={r['scale_axial_p1']:.3f}  "
          f"scale(bending)={r['scale_bending_p2']:.3f}")

# ============================================================
# PLOTS
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# (a) Material property degradation
ax = axes[0, 0]
ax.plot(scrap_pct, UTS, "o-", label="UTS")
ax.plot(scrap_pct, YS, "s-", label="YS")
ax.scatter(scrap_anchor, UTS_anchor, color="black", zorder=5, marker="*", s=120,
           label="Reported data points (paper)")
ax.scatter(scrap_anchor, YS_anchor, color="black", zorder=5, marker="*", s=120)
ax.set_xlabel("Recycled scrap content (%)")
ax.set_ylabel("Stress (MPa)")
ax.set_title("(a) Mechanical property degradation vs. scrap content")
ax.legend()
ax.grid(alpha=0.3)

# (b) Elongation degradation
ax = axes[0, 1]
ax.plot(scrap_pct, A, "^-", color="darkorange")
ax.scatter(scrap_anchor, A_anchor, color="black", zorder=5, marker="*", s=120)
ax.set_xlabel("Recycled scrap content (%)")
ax.set_ylabel("Elongation at fracture (%)")
ax.set_title("(b) Ductility degradation vs. scrap content")
ax.grid(alpha=0.3)

# (c) Safety Factor vs scrap content
ax = axes[1, 0]
for name in load_cases:
    sf_vals = [r["SF"] for r in results if r["load_case"] == name]
    ax.plot(scrap_pct, sf_vals, "o-", label=name)
ax.axhline(1.0, color="red", linestyle="--", linewidth=1, label="SF = 1 (yield)")
ax.set_xlabel("Recycled scrap content (%)")
ax.set_ylabel("Safety Factor (YS / max von Mises stress)")
ax.set_title("(c) Safety factor vs. scrap content (current geometry)")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# (d) Required linear scale factor
ax = axes[1, 1]
for name in load_cases:
    scale_vals = [r["scale_bending_p2"] for r in results if r["load_case"] == name]
    ax.plot(scrap_pct, scale_vals, "s-", label=f"{name} (bending, p=2)")
ax.axhline(1.0, color="gray", linestyle=":", linewidth=1)
ax.set_xlabel("Recycled scrap content (%)")
ax.set_ylabel("Required linear scale factor")
ax.set_title("(d) Geometric compensation vs. 50%-scrap baseline")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("sensitivity_analysis_plots.png", dpi=150)
print("\nPlots saved to sensitivity_analysis_plots.png")
plt.show()
# ============================================================
# SAVE RESULTS TO CSV (for GitHub / report tables)
# ============================================================
import csv

with open("sensitivity_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Results table saved to sensitivity_results.csv")
# ============================================================
# NET CARBON EFFECT (Life Cycle Assessment)
# ============================================================
# Baseline part mass, measured directly from the FreeCAD model
# (Pocket001.Shape.Volume = 69084.60 mm^3, density = 2680 kg/m^3):
baseline_mass_kg = 0.185146733406816

# ---- CO2 emission factors ----
# Source: International Aluminium Institute (2022).
# Aluminium Sector Greenhouse Gas Emissions.
# https://international-aluminium.org/statistics/greenhouse-gas-emissions-aluminium-sector/
co2_primary_per_tonne = 15.1    # tonnes CO2e per tonne primary aluminum
co2_recycled_per_tonne = 0.52   # tonnes CO2e per tonne recycled aluminum

# ---- CO2 footprint of the baseline (100% primary) part ----
co2_primary_part = baseline_mass_kg * 1e-3 * co2_primary_per_tonne  # tonnes CO2e
print(f"\nCO2 footprint, 100% primary Al, baseline mass: {co2_primary_part*1000:.4f} kg CO2e")

# ---- CO2 footprint of each recycled-content scenario, INCLUDING the
#      extra mass needed for geometric compensation (bending assumption) ----
print("\n=== Net Carbon Effect: recycled content vs. compensated mass ===")
for name in load_cases:
    print(f"\n-- {name} --")
    for r in results:
        if r["load_case"] != name:
            continue
        sp = r["scrap_pct"]
        scale = r["scale_bending_p2"]
        # mass scales with volume; assuming isotropic scaling, volume ~ scale^3
        compensated_mass_kg = baseline_mass_kg * (scale ** 3)

        # CO2 mix: (scrap%) recycled + (100-scrap%) primary, by mass
        recycled_frac = sp / 100.0
        primary_frac = 1 - recycled_frac
        co2_per_tonne_mix = (recycled_frac * co2_recycled_per_tonne
                              + primary_frac * co2_primary_per_tonne)
        co2_compensated_part = compensated_mass_kg * 1e-3 * co2_per_tonne_mix  # tonnes

        print(f"  scrap={sp:>3}%  mass={compensated_mass_kg*1000:.4f} g  "
              f"CO2={co2_compensated_part*1000:.4f} kg CO2e  "
              f"(vs. primary baseline: {co2_primary_part*1000:.4f} kg CO2e)")