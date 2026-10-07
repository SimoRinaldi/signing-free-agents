from math import floor


def reconstruct_optimal_roster(N, X, players, s):
    COST_UNIT = 100000
    b = floor(X / COST_UNIT)
    signed_players = []
    total_cost = 0

    # Trace back decisions form position N down to 1
    for i in range(N, 0, -1):
        index = s[i][b]
        # Check if a free agent was signed for position i
        # (index -1 means no free agent signed)
        if index != -1:
            p = players[i - 1][index]
            signed_players.append(p)
            total_cost += p.cost
            b -= p.cost // COST_UNIT

    return signed_players, total_cost
