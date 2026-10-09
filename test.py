from pathlib import Path

from src.core.loader import load_scenario
from src.benchmark.profiler import PerformanceProfiler
from src.benchmark.exporter import DataExporter
from src.benchmark.plotter import PerformancePlotter
from src.algorithms.optimal_value import (
    compute_optimal_war,
    compute_optimal_war_without_s,
)
from src.algorithms.optimal_solution import (
    reconstruct_optimal_roster,
    reconstruct_optimal_roster_without_s,
)
from src.algorithms.space_optimized import compute_optimal_war_with_one_vector
from src.algorithms.time_optimized import compute_optimal_war_with_recursion
from src.algorithms.filter import filter_players


def get_instance_size(file_path):
    return load_scenario(file_path).instance_size


# ---------------------------------------------------------------------------------
scenarios_dir = Path("scenarios")
profiler = PerformanceProfiler(repetitions=15)
exporter = DataExporter(output_dir="results")

scenarios_names = []
bottom_up_execution_times = []

for file_path in sorted(scenarios_dir.glob("*.json"), key=get_instance_size):
    print(f"Elaborazione: {file_path.name}")
    scenarios_names.append(file_path.stem)

    scenario = load_scenario(file_path)
    N, X, players = scenario.N, scenario.budget, scenario.get_players_matrix()
    cost_unit = scenario.cost_unit
    P = scenario.P
    print(f"Scenario caricato con successo! N: {N}, X: {X}, P: {P}")

    filtered_players = filter_players(players, cost_unit, scenario.B)

    # Elenco dei solver da testare per ciascuno scenario
    solvers = [
        ("Bottom Up Solver (con tabella s)", compute_optimal_war, players),
        ("Bottom Up Solver (solo matrice m)", compute_optimal_war_without_s, players),
        ("Space Efficient Solver", compute_optimal_war_with_one_vector, players),
        ("Top Down Memoized", compute_optimal_war_with_recursion, players),
        (
            "Bottom Up Solver (Pareto Pruned)",
            compute_optimal_war_without_s,
            filtered_players,
        ),
        (
            "Space Efficient Solver (Pareto Pruned)",
            compute_optimal_war_with_one_vector,
            filtered_players,
        ),
    ]

    for name, solver_func, input_players in solvers:
        print("\n" + "-" * 10 + f" {name} " + "-" * 10)
        optimal_war, time_ms, memory_kib = profiler.profile(
            solver_func, N, X, input_players, cost_unit
        )
        print(f"Optimal WAR: {optimal_war:.2f}")
        print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
        print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

        if name == "Bottom Up Solver (con tabella s)":
            bottom_up_execution_times.append(time_ms)

        exporter.add_metric(
            {
                "scenario": scenario.name,
                "N": N,
                "budget": X,
                "B": scenario.B,
                "P": P,
                "instance_size": scenario.instance_size,
                "algorithm": name,
                "optimal_war": optimal_war,
                "time_ms": time_ms,
                "memory_kib": memory_kib,
            }
        )

    print("\n" + "-" * 10 + " Reconstruction Test " + "-" * 10)

    # Calcolo matrici per la ricostruzione
    optimal_war_s, s = compute_optimal_war(N, X, players, cost_unit)
    optimal_war_m, m = compute_optimal_war_without_s(N, X, players, cost_unit)
    optimal_war_p, m_p = compute_optimal_war_without_s(
        N, X, filtered_players, cost_unit
    )

    reconstructions = [
        ("tramite matrice s", reconstruct_optimal_roster(N, X, players, s, cost_unit)),
        (
            "tramite matrice m senza s",
            reconstruct_optimal_roster_without_s(N, X, players, m, cost_unit),
        ),
        (
            "tramite matrice m (Pareto Pruned)",
            reconstruct_optimal_roster_without_s(
                N, X, filtered_players, m_p, cost_unit
            ),
        ),
    ]

    for desc, (signed_players, total_cost) in reconstructions:
        print(
            f"\nRoster ricostruito {desc} (Costo: {total_cost}, Giocatori: {len(signed_players)}):"
        )
        for p in signed_players:
            print(f"  - {p.name}: {p.war} WAR (costo: {p.cost})")

    # Esportazione matrici per ispezione
    role_labels = ["Base"] + [r.name for r in scenario.roles]
    exporter.export_matrix_to_csv(
        m, f"matrice_m_{scenario.name}.csv", row_labels=role_labels
    )
    exporter.export_matrix_to_csv(
        s, f"matrice_s_{scenario.name}.csv", row_labels=role_labels
    )

    # Stampo a video le matrici per scenari piccoli
    if scenario.B <= 10:
        print("\n" + "-" * 10 + f" Ispezione Tabelle ({scenario.name}) " + "-" * 10)
        print("Matrice m (Valori):")
        print(exporter.format_matrix(m, row_labels=role_labels))
        print("\nMatrice s (Decisioni):")
        print(exporter.format_matrix(s, row_labels=role_labels))

    print("=" * 90 + "\n")

# Esporta metriche complessive su CSV
csv_metrics_path = exporter.export_metrics_to_csv("benchmark_metrics.csv")
print(f"Tutte le metriche sono state salvate con successo in '{csv_metrics_path}'!\n")

# Generazione dei grafici prestazionali
plotter = PerformancePlotter(show_plots=True)
generated_plots = plotter.plot_all()
for p in generated_plots:
    print(f"Grafico generato con successo: '{p}'")
