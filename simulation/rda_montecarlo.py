"""
RDA Monte Carlo Simulation
===========================
Reestruturação Dinâmica de Ativos (RDA): Uma Abordagem Multicritérios de Recuperação Fiscal

Reproduces the 10,000-iteration Monte Carlo simulation described in Section 6.3 of the article.
All distributional assumptions are documented in data/parameters.json.

Author: [Nome do Autor]
License: MIT
"""

import numpy as np
import pandas as pd
import json
import os
from pathlib import Path

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
RNG  = np.random.default_rng(SEED)

# ── Load parameters ───────────────────────────────────────────────────────────
PARAMS_PATH = Path(__file__).parent.parent / "data" / "parameters.json"
with open(PARAMS_PATH, "r", encoding="utf-8") as f:
    PARAMS = json.load(f)

N_ITER      = PARAMS["simulation"]["n_iterations"]
HORIZON     = PARAMS["simulation"]["horizon_years"]
DISCOUNT    = PARAMS["simulation"]["discount_rate"]
IMPL_COST   = PARAMS["simulation"]["implementation_cost_pct"]


# ── Sampling helpers ──────────────────────────────────────────────────────────

def sample(key: str) -> np.ndarray:
    """Draw N_ITER samples from a triangular distribution defined in parameters.json."""
    d = PARAMS["variables"][key]
    return RNG.triangular(d["min"], d["mode"], d["max"], size=N_ITER)


# ── Pillar calculators ────────────────────────────────────────────────────────

def pilar1_asset_management() -> np.ndarray:
    """
    Pilar 1 – Gestão Ativa de Ativos Públicos
    ------------------------------------------
    Revenue = total_asset_value × monetization_rate × annual_yield_rate
    Source: Kaganova & McKellar (2006); SPGG-RS patrimonial reports (2024).
    """
    total_value       = sample("asset_total_value_brl")          # R$ billion
    monetization_rate = sample("asset_monetization_rate")        # % of mapped assets
    annual_yield      = sample("asset_annual_yield_rate")        # % of monetized value/yr

    gross_revenue = total_value * monetization_rate * annual_yield  # R$ billion/yr
    return gross_revenue * 1_000  # convert to R$ million/yr


def pilar2_technical_schools() -> np.ndarray:
    """
    Pilar 2 – Escolas Técnicas com Autossustentabilidade Financeira
    ---------------------------------------------------------------
    Net fiscal impact = (n_schools × annual_cost_per_school) × subsidy_reduction_rate
    Subsidy reduction = (self_sustainability_rate - baseline_subsidy_rate)
    Source: SENAI (2023); BNDES Education Reports (2022); Melo Neto & Froes (2001).
    """
    n_schools           = sample("ete_n_schools")                # number of units
    cost_per_school     = sample("ete_annual_cost_per_school")   # R$ million/yr per school
    self_sust_rate      = sample("ete_self_sustainability_rate") # % self-funded
    baseline_subsidy    = PARAMS["constants"]["ete_baseline_subsidy_rate"]  # 1.0 = 100%

    subsidy_reduction = self_sust_rate - (1 - baseline_subsidy)
    net_fiscal_impact = n_schools * cost_per_school * subsidy_reduction
    return net_fiscal_impact  # R$ million/yr


def pilar3_banrisul() -> np.ndarray:
    """
    Pilar 3 – Reestruturação do Banrisul
    ------------------------------------
    Annual recurring impact = incremental dividends only.
    One-off capitalization revenue (R$2.5–4.2bi) is reported separately in the article
    and is NOT included here to avoid double-counting with the annual flow table.
    Source: Banrisul (2024) Annual Report; BCB (2024) regional banking benchmarks.
    """
    base_dividends  = PARAMS["constants"]["banrisul_base_dividends_mln"]
    dividend_growth = sample("banrisul_dividend_growth_rate")
    return base_dividends * (dividend_growth - 1)  # incremental only, R$ million/yr


# ── Main simulation ───────────────────────────────────────────────────────────

def run_simulation() -> pd.DataFrame:
    """
    Run N_ITER Monte Carlo iterations.
    Returns a DataFrame with one row per iteration containing per-pillar and total impacts.
    """
    p1 = pilar1_asset_management()
    p2 = pilar2_technical_schools()
    p3 = pilar3_banrisul()

    gross_total  = p1 + p2 + p3
    impl_costs   = gross_total * IMPL_COST
    net_total    = gross_total - impl_costs

    rcl_baseline = PARAMS["constants"]["rcl_baseline_mln"]  # R$ million
    pct_rcl      = net_total / rcl_baseline * 100

    df = pd.DataFrame({
        "pilar1_asset_mgmt_mln":   p1,
        "pilar2_tech_schools_mln": p2,
        "pilar3_banrisul_mln":     p3,
        "gross_total_mln":         gross_total,
        "impl_costs_mln":          impl_costs,
        "net_total_mln":           net_total,
        "net_total_pct_rcl":       pct_rcl,
    })
    return df


# ── Summary statistics ────────────────────────────────────────────────────────

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute key percentiles and scenario labels used in the article (Table 3).
    Pessimistic = P10, Moderate = P50, Optimistic = P90.
    """
    cols = ["pilar1_asset_mgmt_mln", "pilar2_tech_schools_mln",
            "pilar3_banrisul_mln", "net_total_mln", "net_total_pct_rcl"]

    percentiles = [10, 25, 50, 75, 90]
    rows = []
    for p in percentiles:
        row = {"percentile": p}
        label_map = {10: "Pessimista", 50: "Moderado", 90: "Otimista"}
        row["scenario_label"] = label_map.get(p, "")
        for c in cols:
            row[c] = np.percentile(df[c], p)
        rows.append(row)

    summary = pd.DataFrame(rows)
    summary = summary.round(1)
    return summary


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Running RDA Monte Carlo simulation ({N_ITER:,} iterations)...\n")

    results  = run_simulation()
    summary  = summarize(results)

    # Save outputs
    out_dir = Path(__file__).parent.parent / "outputs"
    out_dir.mkdir(exist_ok=True)

    results.to_csv(out_dir / "raw_iterations.csv", index=False)
    summary.to_csv(out_dir / "results_summary.csv", index=False)

    print("── Scenario Summary (R$ million/year, annual average) ──────────────")
    print(summary[["scenario_label", "pilar1_asset_mgmt_mln", "pilar2_tech_schools_mln",
                   "pilar3_banrisul_mln", "net_total_mln", "net_total_pct_rcl"]].to_string(index=False))

    print(f"\n── Distribution of net fiscal impact (R$ million/year) ─────────────")
    print(f"  Mean:  {results['net_total_mln'].mean():>8.1f}")
    print(f"  Std:   {results['net_total_mln'].std():>8.1f}")
    print(f"  P10:   {results['net_total_mln'].quantile(0.10):>8.1f}  ← Pessimista")
    print(f"  P50:   {results['net_total_mln'].quantile(0.50):>8.1f}  ← Moderado")
    print(f"  P90:   {results['net_total_mln'].quantile(0.90):>8.1f}  ← Otimista")
    print(f"\nOutputs saved to: {out_dir}")
