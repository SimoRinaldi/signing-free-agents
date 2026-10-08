from load_scenario_by_json import load_scenario
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
import time
import tracemalloc


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


# ---------------------------------------------------------------------------------

N, X, players = load_scenario("scenarios/test_N9_X320_P20.json")
P = len(players[0]) if players else 0
print(f"Scenario caricato con successo! N: {N}, X: {X}, P: {P}")

print("\n")
print("-" * 10 + " Bottom Up Solver (con tabella s) " + "-" * 10)

optimal_war, time_ms, memory_kib = measure_performance(
    compute_optimal_war, N, X, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

print("\n")
print("-" * 10 + " Bottom Up Solver (solo matrice m) " + "-" * 10)

optimal_war, time_ms, memory_kib = measure_performance(
    compute_optimal_war_without_s, N, X, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

print("\n")
print("-" * 10 + " Space Efficient Solver " + "-" * 10)

optimal_war, time_ms, memory_kib = measure_performance(
    compute_optimal_war_with_one_vector, N, X, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

print("\n")
print("-" * 10 + " Top Down Memoized " + "-" * 10)

optimal_war, time_ms, memory_kib = measure_performance(
    compute_optimal_war_with_recursion, N, X, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

# Preparazione candidati filtrati secondo Pareto
COST_UNIT = 100000
total_budget = X // COST_UNIT
filtered_players = filter_players(players, COST_UNIT, total_budget)

print("\n")
print("-" * 10 + " Bottom Up Solver (Pareto Pruned) " + "-" * 10)

optimal_war, time_ms, memory_kib = measure_performance(
    compute_optimal_war_without_s, N, X, filtered_players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

print("\n")
print("-" * 10 + " Space Efficient Solver (Pareto Pruned) " + "-" * 10)

optimal_war, time_ms, memory_kib = measure_performance(
    compute_optimal_war_with_one_vector, N, X, filtered_players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_ms:.4f} ms")
print(f"Picco memoria RAM: {memory_kib:.2f} KiB")

print("\n")
print("-" * 10 + " Reconstruction Test " + "-" * 10)

# Ricostruzione con matrice decisionale s (approccio classico)
optimal_war_s, s = compute_optimal_war(N, X, players)
signed_players_s, cost_s = reconstruct_optimal_roster(N, X, players, s)
print(
    f"Roster ricostruito tramite matrice s (Costo: {cost_s}, Giocatori: {len(signed_players_s)}):"
)
for p in signed_players_s:
    print(f"  - {p.name}: {p.war} WAR (costo: {p.cost})")

# Ricostruzione diretta da matrice valori m (senza s, -50% RAM)
optimal_war_m, m = compute_optimal_war_without_s(N, X, players)
signed_players_m, cost_m = reconstruct_optimal_roster_without_s(N, X, players, m)
print(
    f"\nRoster ricostruito tramite matrice m senza s (Costo: {cost_m}, Giocatori: {len(signed_players_m)}):"
)
for p in signed_players_m:
    print(f"  - {p.name}: {p.war} WAR (costo: {p.cost})")

# Ricostruzione con matrice m e Pruning di Pareto
optimal_war_p, m_p = compute_optimal_war_without_s(N, X, filtered_players)
signed_players_p, cost_p = reconstruct_optimal_roster_without_s(
    N, X, filtered_players, m_p
)
print(
    f"\nRoster ricostruito tramite matrice m (Pareto Pruned) (Costo: {cost_p}, Giocatori: {len(signed_players_p)}):"
)
for p in signed_players_p:
    print(f"  - {p.name}: {p.war} WAR (costo: {p.cost})")
