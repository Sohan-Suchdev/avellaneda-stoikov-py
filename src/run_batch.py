import argparse

import numpy as np
from sqlalchemy import select

from src.analysis import calculate_metrics
from src.config import SimulationConfig
from src.simulation import Strategy, run_simulation
from src.storage.db import SessionLocal, create_tables
from src.storage.models import Run


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-runs", type=int, default=1000)
    parser.add_argument(
        "--strategy",
        choices=["naive", "avellaneda_stoikov", "both"],
        default="both",
    )
    parser.add_argument("--gamma", type=float)
    parser.add_argument("--sigma", type=float)
    parser.add_argument("--k", type=float)
    parser.add_argument("--A", type=float)
    return parser.parse_args()


def _build_config(args) -> SimulationConfig:
    default_config = SimulationConfig()
    return SimulationConfig(
        gamma=args.gamma if args.gamma is not None else default_config.gamma,
        sigma=args.sigma if args.sigma is not None else default_config.sigma,
        k=args.k if args.k is not None else default_config.k,
        A=args.A if args.A is not None else default_config.A,
    )


def _selected_strategies(strategy_arg: str) -> list[Strategy]:
    if strategy_arg == "both":
        return [Strategy.NAIVE, Strategy.AVELLANEDA_STOIKOV]

    return [Strategy(strategy_arg)]


def _run_row(config: SimulationConfig, strategy: Strategy, seed: int) -> Run:
    rng = np.random.default_rng(seed)
    result = run_simulation(config, strategy, rng=rng)
    metrics = calculate_metrics(result, config.sharpe_annualization_factor)

    return Run(
        strategy=strategy.value,
        seed=seed,
        gamma=config.gamma if strategy is Strategy.AVELLANEDA_STOIKOV else None,
        sigma=config.sigma,
        k=config.k,
        A=config.A,
        net_pnl=metrics.net_pnl,
        sharpe=metrics.sharpe,
        sortino=metrics.sortino,
        max_drawdown=metrics.max_drawdown,
        max_abs_inventory=metrics.max_abs_inventory,
        fees_paid=metrics.fees_paid,
    )


def _existing_run_keys(
    session,
    config: SimulationConfig,
    strategies: list[Strategy],
    n_runs: int,
):
    strategy_values = [strategy.value for strategy in strategies]
    statement = select(Run.strategy, Run.seed, Run.gamma, Run.sigma, Run.k, Run.A).where(
        Run.strategy.in_(strategy_values),
        Run.seed.in_(range(n_runs)),
        Run.sigma == config.sigma,
        Run.k == config.k,
        Run.A == config.A,
    )

    if Strategy.AVELLANEDA_STOIKOV in strategies and Strategy.NAIVE not in strategies:
        statement = statement.where(Run.gamma == config.gamma)
    elif Strategy.NAIVE in strategies and Strategy.AVELLANEDA_STOIKOV not in strategies:
        statement = statement.where(Run.gamma.is_(None))
    else:
        statement = statement.where(
            (Run.strategy == Strategy.NAIVE.value)
            | (
                (Run.strategy == Strategy.AVELLANEDA_STOIKOV.value)
                & (Run.gamma == config.gamma)
            )
        )

    return session.execute(statement).all()


def run_batch(config: SimulationConfig, strategies: list[Strategy], n_runs: int) -> int:
    create_tables()

    completed_runs = 0
    with SessionLocal() as session:
        existing_keys = _existing_run_keys(session, config, strategies, n_runs)
        if existing_keys:
            sample = ", ".join(
                (
                    f"({strategy}, seed={seed}, gamma={gamma}, "
                    f"sigma={sigma}, k={k}, A={arrival_intensity})"
                )
                for strategy, seed, gamma, sigma, k, arrival_intensity in existing_keys[:5]
            )
            raise SystemExit(
                "Existing batch rows found for requested strategy/seed/parameter "
                "combinations. Clear results.db before re-running the same batch, "
                f"or choose a different parameter grid. Sample: {sample}"
            )

        for seed in range(n_runs):
            for strategy in strategies:
                session.add(_run_row(config, strategy, seed))
                completed_runs += 1

                if completed_runs % 100 == 0:
                    session.commit()
                    print(f"Completed {completed_runs} runs")

        session.commit()

    print(f"Completed {completed_runs} runs")
    return completed_runs


def main():
    args = _parse_args()
    config = _build_config(args)
    strategies = _selected_strategies(args.strategy)

    run_batch(config, strategies, args.n_runs)


if __name__ == "__main__":
    main()
