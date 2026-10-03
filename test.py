from load_scenario_by_json import load_scenario
from valore_ottimo import compute_optimal_war
from soluzione_ottima import reconstruct_optimal_roster
import time

N, X, P, players = load_scenario("scenarios/test_N3_X5_P2.json")
print(f"Scenario caricato con successo! N: {N}, X: {X}, P: {P}")

start_time = time.perf_counter()
optimal_war, s = compute_optimal_war(N, X, P, players)
end_time = time.perf_counter()
print(f"Optimal WAR: {optimal_war}")
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time:.6f} seconds")
print(f"Tempo di esecuzione: {elapsed_time * 1000:.3f} ms")

signed_players, total_cost = reconstruct_optimal_roster(N, X, players, s)

print("Roster ottimale:")
for player in signed_players:
    print(f"  - {player.name}: {player.war} WAR")

print(f"Total cost: {total_cost}")
