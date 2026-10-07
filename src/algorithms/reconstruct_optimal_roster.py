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


def reconstruct_optimal_roster_from_matrix(N, X, players, m):
    """Ricostruisce il roster ottimo direttamente dalla matrice dei valori m

    senza necessitare della matrice decisionale s (variante a memoria dimezzata).
    """
    COST_UNIT = 100000
    b = floor(X / COST_UNIT)
    signed_players = []
    total_cost = 0

    # Risale le decisioni dal ruolo N fino al ruolo 1
    for i in range(N, 0, -1):
        current_war = m[i][b]
        # Se il valore coincide con la riga precedente, non è stato ingaggiato nessuno per il ruolo i
        # essendo float uso eps come uguaglianza
        if abs(current_war - m[i - 1][b]) < 1e-9:
            continue

        # Altrimenti identifica il candidato che ha generato il valore ottimo
        for p in players[i - 1]:
            c = p.cost // COST_UNIT
            if b >= c and abs(m[i - 1][b - c] + p.war - current_war) < 1e-9:
                signed_players.append(p)
                total_cost += p.cost
                b -= c
                break

    return signed_players, total_cost
