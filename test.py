from load_scenario_by_json import load_scenario
from valore_ottimo import compute_optimal_war
from soluzione_ottima import reconstruct_optimal_roster

N, X, P, players = load_scenario("scenarios/test_N3_X20_P4.json")

print(f"Scenario caricato con successo! N: {N}, X: {X}, P: {P}")

optimal_war, s = compute_optimal_war(N, X, P, players)

print(f"Optimal WAR: {optimal_war}")

signed_players, total_cost = reconstruct_optimal_roster(N, X, players, s)

print("Roster ottimale:")
for player in signed_players:
    print(f"  - {player.name}: {player.war} WAR")

print(f"Total cost: {total_cost}")
