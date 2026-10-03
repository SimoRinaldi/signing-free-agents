from load_scenario_by_json import load_scenario
from src.algorithms.alg_01_bottom_up import (
    compute_optimal_war as compute_war_standard,
    compute_optimal_war_original,
)
from src.algorithms.reconstruct_optimal_roster import reconstruct_optimal_roster
from src.algorithms.alg_02_space_efficient_solver import (
    compute_optimal_war as compute_war_single_row,
)
from src.algorithms.alg_03_top_down_memoized_solver import compute_optimal_war_memoized
import time
import pandas as pd


def get_pure_execution_time(func, *args, repetitions=10):
    """Esegue l'algoritmo più volte e restituisce il tempo computazionale

    più puro possibile (in millisecondi).
    """
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
    return result, min_time_ms


def print_matrix(matrix):
    df = pd.DataFrame(
        matrix,
        index=[f"Ruolo {i}" if i > 0 else "Base (0)" for i in range(matrix.shape[0])],
        columns=[f"b={b}" for b in range(matrix.shape[1])],
    )
    print(df.to_string())


# ---------------------------------------------------------------------------------

N, X, P, players = load_scenario("scenarios/test_N9_X320_P20.json")
print(f"Scenario caricato con successo! N: {N}, X: {X}, P: {P}")

print("\n")
print("-" * 10 + " Bottom Up Solver " + "-" * 10)

(optimal_war, s), time_dp_ms = get_pure_execution_time(
    compute_war_standard, N, X, P, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_dp_ms:.4f} ms")

print("\n")
print("-" * 10 + " Bottom Up Solver " + "-" * 10)

(optimal_war, s), time_dp_ms = get_pure_execution_time(
    compute_optimal_war_original, N, X, P, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_dp_ms:.4f} ms")

print("\n")
print("-" * 10 + " Space Efficient Solver " + "-" * 10)

(optimal_war, s), time_dp_ms = get_pure_execution_time(
    compute_war_single_row, N, X, P, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_dp_ms:.4f} ms")

print("\n")
print("-" * 10 + " Top Down Memoized " + "-" * 10)

(optimal_war, s), time_dp_ms = get_pure_execution_time(
    compute_optimal_war_memoized, N, X, P, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_dp_ms:.4f} ms")

"""
(signed_players, total_cost), time_dp_ms = get_pure_execution_time(
    reconstruct_optimal_roster, N, X, players, s, repetitions=15
)

print("Roster ottimale:")
for player in signed_players:
    print(f"  - {player.name}: {player.war} WAR")

print(f"Total cost: {total_cost}")"""
