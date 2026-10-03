from math import floor
import numpy as np
import pandas as pd


def compute_optimal_war(N, X, P, players):
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    m = np.zeros((N + 1, B + 1))
    s = np.full((N + 1, B + 1), -1, dtype=int)

    # Consider each position from 1 to N
    for i in range(1, N + 1):
        # Consider each budget level from 0 to B
        for b in range(B + 1):
            # Default choice: no free agent signed for position i
            m[i, b] = m[i - 1, b]

            for j in range(P):
                p = players[i - 1][j]
                c = p.cost // COST_UNIT

                if c <= b:
                    war = m[i - 1, b - c] + p.war
                    if war > m[i, b]:
                        m[i, b] = war
                        s[i, b] = j
    print_matrix(m)
    print_matrix(s)

    optimal_war = m[N, B]
    return optimal_war, s


def print_matrix(matrix):
    df = pd.DataFrame(
        matrix,
        index=[f"Ruolo {i}" if i > 0 else "Base (0)" for i in range(matrix.shape[0])],
        columns=[f"b={b}" for b in range(matrix.shape[1])],
    )
    print(df.to_string())
