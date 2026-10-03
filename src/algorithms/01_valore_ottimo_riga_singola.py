from math import floor


def compute_optimal_war(N, X, P, players):
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    previous_role_solution = [0.0 for _ in range(B + 1)]
    current_role_solution = [0.0 for _ in range(B + 1)]
    s = [[-1] * (B + 1) for _ in range(N + 1)]
    # Consider each position from 1 to N
    for i in range(1, N + 1):
        # Initialize with previous role values to account for the option of signing no player for position i
        current_role_solution[:] = previous_role_solution[:]

        for j in range(P):
            p = players[i - 1][j]
            c = p.cost // COST_UNIT
            war_p = p.war

            # Consider budget levels from c to B
            for b in range(c, B + 1):
                war = previous_role_solution[b - c] + war_p
                if war > current_role_solution[b]:
                    current_role_solution[b] = war
                    s[i][b] = j

        # Prepare for next position: shift current solution to previous
        previous_role_solution[:] = current_role_solution[:]

    optimal_war = current_role_solution[B]
    return optimal_war, s
