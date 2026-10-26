from pathlib import Path
from typing import List

from src.core.loader import load_scenario
from src.core.models import BenchmarkMetric
from src.benchmark.profiler import PerformanceProfiler
from src.benchmark.exporter import DataExporter
from src.benchmark.plotter import PerformancePlotter
from src.benchmark.strategy import AlgorithmName, SolverStrategy

from src.algorithms.optimal_value import (
    compute_optimal_war,
    compute_optimal_war_without_s,
)
from src.algorithms.space_optimized import compute_optimal_war_with_one_vector
from src.algorithms.time_optimized import compute_optimal_war_with_recursion
from src.algorithms.filter import filter_players


def get_benchmark_strategies() -> List[SolverStrategy]:
    return [
        SolverStrategy(AlgorithmName.BOTTOM_UP_WITH_S, compute_optimal_war),
        SolverStrategy(AlgorithmName.BOTTOM_UP_WITHOUT_S, compute_optimal_war_without_s),
        SolverStrategy(AlgorithmName.BOTTOM_UP_VECTOR, compute_optimal_war_with_one_vector),
        SolverStrategy(AlgorithmName.TOP_DOWN, compute_optimal_war_with_recursion),
        SolverStrategy(
            AlgorithmName.BOTTOM_UP_FILTER,
            compute_optimal_war_without_s,
            use_filter=True,
        ),
        SolverStrategy(
            AlgorithmName.BOTTOM_UP_VECTOR_FILTER,
            compute_optimal_war_with_one_vector,
            use_filter=True,
        ),
    ]


def main():
    scenarios_dir = Path("scenarios")
    profiler = PerformanceProfiler(repetitions=15)
    exporter = DataExporter(output_dir="results")

    scenario_files = sorted(
        scenarios_dir.glob("*.json"), key=lambda p: load_scenario(p).instance_size
    )

    strategies = get_benchmark_strategies()
    total_scenarios = len(scenario_files)
    print(f"\nAvvio benchmark su {total_scenarios} scenari in '{scenarios_dir}/'...\n")

    for idx, file_path in enumerate(scenario_files, 1):
        scenario = load_scenario(file_path)
        N, X, players = scenario.N, scenario.budget, scenario.get_players_matrix()
        cost_unit = scenario.cost_unit
        P = scenario.P

        print(
            f"[{idx:02d}/{total_scenarios:02d}] {scenario.name} "
            f"(N={N}, B={scenario.B}, P={P}) ... ",
            end="",
            flush=True,
        )

        filtered_players = filter_players(players, cost_unit, scenario.B)

        for strategy in strategies:
            input_players = strategy.resolve_input(players, filtered_players)
            optimal_war, time_ms, memory_kib = profiler.profile(
                strategy.func, N, X, input_players, cost_unit
            )

            exporter.add_metric(
                BenchmarkMetric(
                    scenario=scenario.name,
                    N=N,
                    budget=X,
                    B=scenario.B,
                    P=P,
                    instance_size=scenario.instance_size,
                    algorithm=strategy.name,
                    optimal_war=optimal_war,
                    time_ms=time_ms,
                    memory_kib=memory_kib,
                )
            )

        # Esportazione matrici m ed s per ispezione
        _, s = compute_optimal_war(N, X, players, cost_unit)
        _, m = compute_optimal_war_without_s(N, X, players, cost_unit)
        role_labels = ["Base"] + [r.name for r in scenario.roles]
        exporter.export_matrix_to_csv(
            m, f"matrice_m_{scenario.name}.csv", row_labels=role_labels
        )
        exporter.export_matrix_to_csv(
            s, f"matrice_s_{scenario.name}.csv", row_labels=role_labels
        )

        print("OK")

    # Salvataggio metriche su CSV
    csv_metrics_path = exporter.export_metrics_to_csv("benchmark_metrics.csv")
    print(f"\nMetriche salvate in '{csv_metrics_path}'")

    # Generazione dei grafici e della tabella comparativa PNG
    plotter = PerformancePlotter(show_plots=False)
    generated_files = plotter.plot_all()
    print("Grafici e tabella generati in 'results/':")
    for f in generated_files:
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
