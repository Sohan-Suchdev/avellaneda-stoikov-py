from pathlib import Path
import os

import matplotlib

if os.environ.get("MPLBACKEND"):
    matplotlib.use(os.environ["MPLBACKEND"])
import matplotlib.pyplot as plt  # noqa: E402

from src.storage.db import DB_PATH
from src.storage.queries import load_runs, paired_comparison, summary_stats


REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
BATCH_DISTRIBUTIONS_PATH = REPORTS_DIR / "batch_distributions.png"


def print_batch_report():
    if not Path(DB_PATH).exists():
        print("No results.db found. Run a batch first.")
        return

    stats = summary_stats()
    if stats.empty:
        print("results.db has no run data.")
        return

    print("Summary stats:")
    print(stats)
    print()
    print("Paired comparison:")
    print(paired_comparison())


def plot_batch_distributions():
    if not Path(DB_PATH).exists():
        print("No results.db found; skipping batch distribution plot.")
        return None

    runs = load_runs()
    if runs.empty:
        print("No run data found; skipping batch distribution plot.")
        return None

    naive = runs[runs["strategy"] == "naive"]
    as_runs = runs[runs["strategy"] == "avellaneda_stoikov"]
    if naive.empty or as_runs.empty:
        print("Both naive and avellaneda_stoikov runs are required for plots.")
        return None

    paired = runs.pivot_table(
        index="seed",
        columns="strategy",
        values="net_pnl",
        aggfunc="first",
    ).dropna()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    axes[0, 0].hist(naive["net_pnl"], bins=40, alpha=0.6, label="Naive", color="red")
    axes[0, 0].hist(
        as_runs["net_pnl"],
        bins=40,
        alpha=0.6,
        label="Avellaneda-Stoikov",
        color="blue",
    )
    axes[0, 0].set_title("PnL Distribution")
    axes[0, 0].set_xlabel("Net PnL")
    axes[0, 0].set_ylabel("Frequency")
    axes[0, 0].legend()

    axes[0, 1].hist(naive["sharpe"], bins=40, alpha=0.6, label="Naive", color="red")
    axes[0, 1].hist(
        as_runs["sharpe"],
        bins=40,
        alpha=0.6,
        label="Avellaneda-Stoikov",
        color="blue",
    )
    axes[0, 1].set_title("Sharpe Distribution")
    axes[0, 1].set_xlabel("Sharpe")
    axes[0, 1].set_ylabel("Frequency")
    axes[0, 1].legend()

    axes[1, 0].hist(
        naive["max_drawdown"],
        bins=40,
        alpha=0.6,
        label="Naive",
        color="red",
    )
    axes[1, 0].hist(
        as_runs["max_drawdown"],
        bins=40,
        alpha=0.6,
        label="Avellaneda-Stoikov",
        color="blue",
    )
    axes[1, 0].set_title("Max Drawdown Distribution")
    axes[1, 0].set_xlabel("Max Drawdown")
    axes[1, 0].set_ylabel("Frequency")
    axes[1, 0].legend()

    if {"avellaneda_stoikov", "naive"}.issubset(paired.columns):
        pnl_diff = paired["avellaneda_stoikov"] - paired["naive"]
    else:
        pnl_diff = []
    axes[1, 1].hist(pnl_diff, bins=40, alpha=0.75, color="purple")
    axes[1, 1].axvline(0, color="black", linestyle="--", linewidth=1)
    axes[1, 1].set_title("Paired PnL Difference")
    axes[1, 1].set_xlabel("AS - Naive Net PnL")
    axes[1, 1].set_ylabel("Frequency")

    plt.tight_layout()
    fig.savefig(BATCH_DISTRIBUTIONS_PATH, dpi=150)
    plt.close(fig)

    print(f"Saved batch distribution plot to {BATCH_DISTRIBUTIONS_PATH}")
    return BATCH_DISTRIBUTIONS_PATH
