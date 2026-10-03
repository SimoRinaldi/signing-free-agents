from math import floor
import numpy as np


def compute_optimal_war(N, X, P, players):
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    m = np.zeros((N + 1, B + 1))
    s = np.full((N + 1, B + 1), -1, dtype=int)

    # Consider each position from 1 to N
    for i in range(1, N + 1):
        # Default choice: no free agent signed for position i
        m[i, :] = m[i - 1, :]

        for j in range(P):
            p = players[i - 1][j]
            c = p.cost // COST_UNIT
            war_p = p.war

            for b in range(c, B + 1):
                war = m[i - 1, b - c] + war_p
                if war > m[i, b]:
                    m[i, b] = war
                    s[i, b] = j

    optimal_war = m[N, B]
    return optimal_war, s
