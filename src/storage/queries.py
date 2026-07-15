import pandas as pd
from scipy.stats import ttest_rel
from sqlalchemy import text

from src.storage.db import engine


def load_runs(strategy=None) -> pd.DataFrame:
    query = "SELECT * FROM runs"
    params = {}

    if strategy is not None:
        query += " WHERE strategy = :strategy"
        params["strategy"] = strategy

    return pd.read_sql(text(query), engine, params=params)


def summary_stats() -> pd.DataFrame:
    runs = load_runs()
    if runs.empty:
        return pd.DataFrame()

    metrics = ["net_pnl", "sharpe", "sortino", "max_drawdown"]
    return runs.groupby("strategy")[metrics].agg(["mean", "std", "median"])


def sweep_summary() -> pd.DataFrame:
    runs = load_runs(strategy="avellaneda_stoikov")
    if runs.empty:
        return pd.DataFrame()

    runs = runs.dropna(subset=["gamma"])
    if runs.empty:
        return pd.DataFrame()

    summary = runs.groupby("gamma").agg(
        mean_sharpe=("sharpe", "mean"),
        std_sharpe=("sharpe", "std"),
        mean_net_pnl=("net_pnl", "mean"),
        std_net_pnl=("net_pnl", "std"),
        mean_max_drawdown=("max_drawdown", "mean"),
        std_max_drawdown=("max_drawdown", "std"),
    )
    return summary.sort_values("mean_sharpe", ascending=False)


def gamma_paired_comparison(best_gamma=None) -> str:
    runs = load_runs(strategy="avellaneda_stoikov")
    if runs.empty:
        return "No AS sweep data found."

    runs = runs.dropna(subset=["gamma"])
    if runs.empty:
        return "No gamma sweep data found."

    summary = sweep_summary()
    if summary.empty:
        return "No gamma sweep data found."

    if best_gamma is None:
        best_gamma = summary.index[0]

    gamma_values = sorted(gamma for gamma in runs["gamma"].unique() if gamma != best_gamma)
    if not gamma_values:
        return "Need at least two gamma values for paired gamma comparison."

    paired = runs.pivot_table(
        index=["seed", "sigma", "k", "A"],
        columns="gamma",
        values=["sharpe", "net_pnl"],
        aggfunc="first",
    )

    lines = [f"Best gamma by mean Sharpe: {best_gamma}", "Paired gamma comparison:"]
    for gamma in gamma_values:
        required_columns = {
            ("sharpe", best_gamma),
            ("sharpe", gamma),
            ("net_pnl", best_gamma),
            ("net_pnl", gamma),
        }
        if not required_columns.issubset(set(paired.columns)):
            continue

        comparison = paired[
            [
                ("sharpe", best_gamma),
                ("sharpe", gamma),
                ("net_pnl", best_gamma),
                ("net_pnl", gamma),
            ]
        ].dropna()
        if len(comparison) < 2:
            lines.append(f"gamma {best_gamma} vs {gamma}: not enough paired runs")
            continue

        best_sharpe = comparison[("sharpe", best_gamma)]
        other_sharpe = comparison[("sharpe", gamma)]
        best_pnl = comparison[("net_pnl", best_gamma)]
        other_pnl = comparison[("net_pnl", gamma)]

        sharpe_diff = best_sharpe - other_sharpe
        pnl_diff = best_pnl - other_pnl
        sharpe_test = ttest_rel(best_sharpe, other_sharpe)
        pnl_test = ttest_rel(best_pnl, other_pnl)

        lines.append(
            (
                f"gamma {best_gamma} - {gamma}: "
                f"paired={len(comparison)}, "
                f"mean Sharpe diff={sharpe_diff.mean():.6f}, "
                f"Sharpe p={sharpe_test.pvalue:.6f}, "
                f"mean PnL diff={pnl_diff.mean():.6f}, "
                f"PnL p={pnl_test.pvalue:.6f}"
            )
        )

    return "\n".join(lines)


def paired_comparison(as_gamma=None) -> str:
    runs = load_runs()
    if runs.empty:
        return "No runs found."

    as_runs = runs[runs["strategy"] == "avellaneda_stoikov"]
    if as_runs.empty:
        return "Not enough paired naive and avellaneda_stoikov runs found."

    if as_gamma is None:
        gamma_summary = sweep_summary()
        if not gamma_summary.empty:
            as_gamma = gamma_summary.index[0]

    if as_gamma is not None:
        runs = runs[
            (runs["strategy"] == "naive")
            | (
                (runs["strategy"] == "avellaneda_stoikov")
                & (runs["gamma"] == as_gamma)
            )
        ]

    paired = runs.pivot_table(
        index="seed",
        columns="strategy",
        values=["net_pnl", "sharpe"],
        aggfunc="first",
    ).dropna()

    required_columns = {
        ("net_pnl", "avellaneda_stoikov"),
        ("net_pnl", "naive"),
        ("sharpe", "avellaneda_stoikov"),
        ("sharpe", "naive"),
    }
    if paired.empty or not required_columns.issubset(set(paired.columns)):
        return "Not enough paired naive and avellaneda_stoikov runs found."
    if len(paired) < 2:
        return "At least two paired seeds are required for a paired t-test."

    pnl_as = paired[("net_pnl", "avellaneda_stoikov")]
    pnl_naive = paired[("net_pnl", "naive")]
    sharpe_as = paired[("sharpe", "avellaneda_stoikov")]
    sharpe_naive = paired[("sharpe", "naive")]

    pnl_test = ttest_rel(pnl_as, pnl_naive)
    sharpe_test = ttest_rel(sharpe_as, sharpe_naive)

    pnl_diff = pnl_as - pnl_naive
    sharpe_diff = sharpe_as - sharpe_naive

    return "\n".join(
        [
            (
                f"Paired runs: {len(paired)}"
                + (f" using AS gamma={as_gamma}" if as_gamma is not None else "")
            ),
            (
                "PnL AS - naive: "
                f"mean diff={pnl_diff.mean():.6f}, "
                f"t-stat={pnl_test.statistic:.6f}, "
                f"p-value={pnl_test.pvalue:.6f}"
            ),
            (
                "Sharpe AS - naive: "
                f"mean diff={sharpe_diff.mean():.6f}, "
                f"t-stat={sharpe_test.statistic:.6f}, "
                f"p-value={sharpe_test.pvalue:.6f}"
            ),
        ]
    )
