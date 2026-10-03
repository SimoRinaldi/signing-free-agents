from load_scenario_by_json import load_scenario
from valore_ottimo import compute_optimal_war
from soluzione_ottima import reconstruct_optimal_roster
import time


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


# ---------------------------------------------------------------------------------

N, X, P, players = load_scenario("scenarios/test_N3_X20_P4.json")
print(f"Scenario caricato con successo! N: {N}, X: {X}, P: {P}")

(optimal_war, s), time_dp_ms = get_pure_execution_time(
    compute_optimal_war, N, X, P, players, repetitions=15
)
print(f"Optimal WAR: {optimal_war:.2f}")
print(f"Tempo computazionale effettivo: {time_dp_ms:.4f} ms")

(signed_players, total_cost), time_dp_ms = get_pure_execution_time(
    reconstruct_optimal_roster, N, X, players, s, repetitions=15
)

print("Roster ottimale:")
for player in signed_players:
    print(f"  - {player.name}: {player.war} WAR")

print(f"Total cost: {total_cost}")
