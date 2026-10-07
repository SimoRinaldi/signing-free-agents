from math import floor


# Metodo originale che calcola la matrice m e la matrice s e ritorna il WAR ottimale e la matrice s
def compute_optimal_war(N, X, players):
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    m = [[0.0] * (B + 1) for _ in range(N + 1)]
    s = [[-1] * (B + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        m[i][:] = m[i - 1][:]

        for j in range(len(players[i - 1])):
            p = players[i - 1][j]
            c = p.cost // COST_UNIT
            war_p = p.war

            for b in range(c, B + 1):
                war = m[i - 1][b - c] + war_p
                if war > m[i][b]:
                    m[i][b] = war
                    if s is not None:
                        s[i][b] = j

    optimal_war = m[N][B]
    return optimal_war, s


# Metodo modificato che calcola solo la matrice m e ritorna il WAR ottimale e la matrice m
def compute_optimal_war_without_s(N, X, players):
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    m = [[0.0] * (B + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        m[i][:] = m[i - 1][:]

        for j in range(len(players[i - 1])):
            p = players[i - 1][j]
            c = p.cost // COST_UNIT
            war_p = p.war

            for b in range(c, B + 1):
                war = m[i - 1][b - c] + war_p
                if war > m[i][b]:
                    m[i][b] = war

    optimal_war = m[N][B]
    return optimal_war, m
