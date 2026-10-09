from math import floor


# Metodo originale che calcola la matrice m e la matrice s e ritorna il WAR ottimale e la matrice s
def compute_optimal_war(N, X, players, cost_unit=100000):
    B = floor(X / cost_unit)

    m = [[0.0] * (B + 1) for _ in range(N + 1)]
    s = [[-1] * (B + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        m[i][:] = m[i - 1][:]

        for j, p in enumerate(players[i - 1]):
            c = p.cost // cost_unit
            war_p = p.war

            for b in range(c, B + 1):
                war = m[i - 1][b - c] + war_p
                if war > m[i][b]:
                    m[i][b] = war
                    s[i][b] = j

    optimal_war = m[N][B]
    return optimal_war, s


# Metodo modificato che calcola solo la matrice m e ritorna il WAR ottimale e la matrice m
def compute_optimal_war_without_s(N, X, players, cost_unit=100000):
    B = floor(X / cost_unit)

    m = [[0.0] * (B + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        m[i][:] = m[i - 1][:]

        for p in players[i - 1]:
            c = p.cost // cost_unit
            war_p = p.war

            for b in range(c, B + 1):
                war = m[i - 1][b - c] + war_p
                if war > m[i][b]:
                    m[i][b] = war

    optimal_war = m[N][B]
    return optimal_war, m
