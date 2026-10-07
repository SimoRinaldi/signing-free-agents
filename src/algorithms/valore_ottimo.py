from math import floor
import pandas as pd


def compute_optimal_war(N, X, P, players):
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    m = [[0.0] * (B + 1) for _ in range(N + 1)]
    s = [[-1] * (B + 1) for _ in range(N + 1)]

    # Consider each position from 1 to N
    for i in range(1, N + 1):
        # Default choice: no free agent signed for position i
        m[i][:] = m[i - 1][:]

        for j in range(P):
            p = players[i - 1][j]
            c = p.cost // COST_UNIT
            war_p = p.war

            for b in range(c, B + 1):
                war = m[i - 1][b - c] + war_p
                if war > m[i][b]:
                    m[i][b] = war
                    s[i][b] = j

    optimal_war = m[N][B]
    return optimal_war, s


def print_matrix(matrix):
    df = pd.DataFrame(
        matrix,
        index=[f"Ruolo {i}" if i > 0 else "Base (0)" for i in range(matrix.shape[0])],
        columns=[f"b={b}" for b in range(matrix.shape[1])],
    )
    print(df.to_string())
