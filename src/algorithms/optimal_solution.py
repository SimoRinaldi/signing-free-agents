from math import floor


# Metodo per ricostruire la rosa ottima a partire dalla matrice decisionale s
def reconstruct_optimal_roster(N, X, players, s, cost_unit=100000):
    b = floor(X / cost_unit)
    signed_players = []
    total_cost = 0

    for i in range(N, 0, -1):
        index = s[i][b]
        if index != -1:
            p = players[i - 1][index]
            signed_players.append(p)
            total_cost += p.cost
            b -= p.cost // cost_unit

    return signed_players, total_cost


# Metodo per ricostruire la rosa ottima a partire dalla matrice dei valori m
def reconstruct_optimal_roster_without_s(N, X, players, m, cost_unit=100000):
    b = floor(X / cost_unit)
    signed_players = []
    total_cost = 0

    for i in range(N, 0, -1):
        current_war = m[i][b]
        if abs(current_war - m[i - 1][b]) < 1e-9:
            continue

        for p in players[i - 1]:
            c = p.cost // cost_unit
            if b >= c and abs(m[i - 1][b - c] + p.war - current_war) < 1e-9:
                signed_players.append(p)
                total_cost += p.cost
                b -= c
                break

    return signed_players, total_cost
