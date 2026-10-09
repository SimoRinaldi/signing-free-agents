from pathlib import Path
import time
import tracemalloc
import matplotlib.pyplot as plt

from src.core.loader import load_scenario
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


def get_pure_execution_time(func, *args, repetitions=10):
    times = []
    result = None
    for i in range(repetitions):
        start = time.perf_counter()
        current_result = func(*args)
        end = time.perf_counter()

        times.append((end - start) * 1000)

        if i == 0:
            result = current_result

    min_time_ms = min(times)
    if isinstance(result, tuple):
        result = result[0]
    return result, min_time_ms


def get_peak_memory(func, *args):
    """Misura il picco di memoria RAM allocata con una singola esecuzione dedicata."""
    tracemalloc.start()
    tracemalloc.reset_peak()

    result = func(*args)

    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if isinstance(result, tuple):
        result = result[0]

    peak_kib = peak_bytes / 1024
    return result, peak_kib


def measure_performance(func, *args, repetitions=10):
    result, time_ms = get_pure_execution_time(func, *args, repetitions=repetitions)
    _, peak_kib = get_peak_memory(func, *args)
    return result, time_ms, peak_kib


def get_instance_size(file_path):
    return load_scenario(file_path).instance_size


# ---------------------------------------------------------------------------------
scenarios_dir = Path("scenarios")

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

    optimal_war, time_ms, memory_kib = measure_performance(
        compute_optimal_war, N, X, players, cost_unit, repetitions=15
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")
    bottom_up_execution_times.append(time_ms)

    print("\n")
    print("-" * 10 + " Bottom Up Solver (solo matrice m) " + "-" * 10)

    optimal_war, time_ms, memory_kib = measure_performance(
        compute_optimal_war_without_s, N, X, players, cost_unit, repetitions=15
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

    print("\n")
    print("-" * 10 + " Space Efficient Solver " + "-" * 10)

    optimal_war, time_ms, memory_kib = measure_performance(
        compute_optimal_war_with_one_vector, N, X, players, cost_unit, repetitions=15
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

    print("\n")
    print("-" * 10 + " Top Down Memoized " + "-" * 10)

    optimal_war, time_ms, memory_kib = measure_performance(
        compute_optimal_war_with_recursion, N, X, players, cost_unit, repetitions=15
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

    # Preparazione candidati filtrati secondo Pareto
    filtered_players = filter_players(players, cost_unit, scenario.B)

    print("\n")
    print("-" * 10 + " Bottom Up Solver (Pareto Pruned) " + "-" * 10)

    optimal_war, time_ms, memory_kib = measure_performance(
        compute_optimal_war_without_s, N, X, filtered_players, cost_unit, repetitions=15
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

    print("\n")
    print("-" * 10 + " Space Efficient Solver (Pareto Pruned) " + "-" * 10)

    optimal_war, time_ms, memory_kib = measure_performance(
        compute_optimal_war_with_one_vector, N, X, filtered_players, cost_unit, repetitions=15
    )
    print(f"Optimal WAR: {optimal_war:.2f}")
    print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
    print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

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
    signed_players_m, cost_m = reconstruct_optimal_roster_without_s(N, X, players, m, cost_unit)
    print(
        f"\nRoster ricostruito tramite matrice m senza s (Costo: {cost_m}, Giocatori: {len(signed_players_m)}):"
    )
    for p in signed_players_m:
        print(f"  - {p.name}: {p.war} WAR (costo: {p.cost})")

    # Ricostruzione con matrice m e Pruning di Pareto
    optimal_war_p, m_p = compute_optimal_war_without_s(N, X, filtered_players, cost_unit)
    signed_players_p, cost_p = reconstruct_optimal_roster_without_s(
        N, X, filtered_players, m_p, cost_unit
    )
    print(
        f"\nRoster ricostruito tramite matrice m (Pareto Pruned) (Costo: {cost_p}, Giocatori: {len(signed_players_p)}):"
    )
    for p in signed_players_p:
        print(f"  - {p.name}: {p.war} WAR (costo: {p.cost})")

    print("=" * 90 + "\n")

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
