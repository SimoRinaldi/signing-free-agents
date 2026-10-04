from math import floor


def compute_optimal_war(N, X, P, players):
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    solution = [0.0 for _ in range(B + 1)]
    # Consider each position from 1 to N
    for i in range(1, N + 1):

        # Consider budget levels from c to B
        for b in range(B, -1, -1):
            # Default choice: no free agent signed for position i
            best_war = solution[b]

            for j in range(P):
                p = players[i - 1][j]
                c = p.cost // COST_UNIT
                war_p = p.war

                if b >= c:
                    war = solution[b - c] + war_p
                    if war > best_war:
                        best_war = war

            solution[b] = best_war

    optimal_war = solution[B]
    return optimal_war
