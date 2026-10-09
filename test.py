from pathlib import Path
import matplotlib.pyplot as plt

from src.core.loader import load_scenario
from src.benchmark.profiler import PerformanceProfiler
from src.benchmark.exporter import DataExporter
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

    print("\n")
    print("-" * 10 + " Bottom Up Solver (con tabella s) " + "-" * 10)

    optimal_war, time_ms, memory_kib = profiler.profile(
        compute_optimal_war, N, X, players, cost_unit
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")
    bottom_up_execution_times.append(time_ms)
    exporter.add_metric(
        {
            "scenario": scenario.name,
            "N": N,
            "budget": X,
            "B": scenario.B,
            "P": P,
            "instance_size": scenario.instance_size,
            "algorithm": "Bottom Up (con s)",
            "optimal_war": optimal_war,
            "time_ms": time_ms,
            "memory_kib": memory_kib,
        }
    )

    print("\n")
    print("-" * 10 + " Bottom Up Solver (solo matrice m) " + "-" * 10)

    optimal_war, time_ms, memory_kib = profiler.profile(
        compute_optimal_war_without_s, N, X, players, cost_unit
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")
    exporter.add_metric(
        {
            "scenario": scenario.name,
            "N": N,
            "budget": X,
            "B": scenario.B,
            "P": P,
            "instance_size": scenario.instance_size,
            "algorithm": "Bottom Up (solo m)",
            "optimal_war": optimal_war,
            "time_ms": time_ms,
            "memory_kib": memory_kib,
        }
    )

    print("\n")
    print("-" * 10 + " Space Efficient Solver " + "-" * 10)

    optimal_war, time_ms, memory_kib = profiler.profile(
        compute_optimal_war_with_one_vector, N, X, players, cost_unit
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")
    exporter.add_metric(
        {
            "scenario": scenario.name,
            "N": N,
            "budget": X,
            "B": scenario.B,
            "P": P,
            "instance_size": scenario.instance_size,
            "algorithm": "Space Efficient (1D)",
            "optimal_war": optimal_war,
            "time_ms": time_ms,
            "memory_kib": memory_kib,
        }
    )

    print("\n")
    print("-" * 10 + " Top Down Memoized " + "-" * 10)

    optimal_war, time_ms, memory_kib = profiler.profile(
        compute_optimal_war_with_recursion, N, X, players, cost_unit
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")
    exporter.add_metric(
        {
            "scenario": scenario.name,
            "N": N,
            "budget": X,
            "B": scenario.B,
            "P": P,
            "instance_size": scenario.instance_size,
            "algorithm": "Top Down (Memoized)",
            "optimal_war": optimal_war,
            "time_ms": time_ms,
            "memory_kib": memory_kib,
        }
    )

    # Preparazione candidati filtrati secondo Pareto
    filtered_players = filter_players(players, cost_unit, scenario.B)

    print("\n")
    print("-" * 10 + " Bottom Up Solver (Pareto Pruned) " + "-" * 10)

    optimal_war, time_ms, memory_kib = profiler.profile(
        compute_optimal_war_without_s, N, X, filtered_players, cost_unit
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")
    exporter.add_metric(
        {
            "scenario": scenario.name,
            "N": N,
            "budget": X,
            "B": scenario.B,
            "P": P,
            "instance_size": scenario.instance_size,
            "algorithm": "Bottom Up (Pareto)",
            "optimal_war": optimal_war,
            "time_ms": time_ms,
            "memory_kib": memory_kib,
        }
    )

    print("\n")
    print("-" * 10 + " Space Efficient Solver (Pareto Pruned) " + "-" * 10)

    optimal_war, time_ms, memory_kib = profiler.profile(
        compute_optimal_war_with_one_vector, N, X, filtered_players, cost_unit
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")
    exporter.add_metric(
        {
            "scenario": scenario.name,
            "N": N,
            "budget": X,
            "B": scenario.B,
            "P": P,
            "instance_size": scenario.instance_size,
            "algorithm": "Space Efficient (Pareto)",
            "optimal_war": optimal_war,
            "time_ms": time_ms,
            "memory_kib": memory_kib,
        }
    )

    print("\n")
    print("-" * 10 + " Reconstruction Test " + "-" * 10)

    # Ricostruzione con matrice decisionale s (approccio classico)
    optimal_war_s, s = compute_optimal_war(N, X, players, cost_unit)
    signed_players_s, cost_s = reconstruct_optimal_roster(N, X, players, s, cost_unit)
    print(
        f"Roster ricostruito tramite matrice s (Costo: {cost_s}, Giocatori: {len(signed_players_s)}):"
    )
    for p in signed_players_s:
        print(f"  - {p.name}: {p.war} WAR (costo: {p.cost})")

    # Ricostruzione diretta da matrice valori m (senza s, -50% RAM)
    optimal_war_m, m = compute_optimal_war_without_s(N, X, players, cost_unit)
    signed_players_m, cost_m = reconstruct_optimal_roster_without_s(
        N, X, players, m, cost_unit
    )
    print(
        f"\nRoster ricostruito tramite matrice m senza s (Costo: {cost_m}, Giocatori: {len(signed_players_m)}):"
    )
    for p in signed_players_m:
        print(f"  - {p.name}: {p.war} WAR (costo: {p.cost})")

    # Ricostruzione con matrice m e Pruning di Pareto
    optimal_war_p, m_p = compute_optimal_war_without_s(
        N, X, filtered_players, cost_unit
    )
    signed_players_p, cost_p = reconstruct_optimal_roster_without_s(
        N, X, filtered_players, m_p, cost_unit
    )
    print(
        f"\nRoster ricostruito tramite matrice m (Pareto Pruned) (Costo: {cost_p}, Giocatori: {len(signed_players_p)}):"
    )
    for p in signed_players_p:
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

# -------------------------------------------------------------------------------------------------------------------
print(bottom_up_execution_times)

plt.figure(figsize=(10, 5))
plt.plot(
    scenarios_names,
    bottom_up_execution_times,
    marker="o",
    color="royalblue",
    linewidth=2,
)

plt.title("Andamento Tempi di Esecuzione nei Vari Scenari")
plt.xlabel("Scenario")
plt.ylabel("Tempo (ms)")
plt.xticks(rotation=30, ha="right")  # ruota i nomi per non sovrapporli
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

# Salva il file immagine PNG ad alta risoluzione
plt.savefig("andamento_tempi_bottom_up.png", dpi=300)
print("Grafico salvato con successo in 'andamento_tempi_bottom_up.png'!")
plt.show()
