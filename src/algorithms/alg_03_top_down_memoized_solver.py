from math import floor


def compute_optimal_war_memoized(N, X, P, players):
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    # memo[i][b]: memorizza il massimo WAR calcolato per lo stato (i, b)
    # Inizializzato a -1.0 per distinguere le celle già visitate da quelle inesplorate
    memo = [[-1.0] * (B + 1) for _ in range(N + 1)]

    def dp(i, b):
        # Caso base: nessun ruolo rimasto da considerare
        if i == 0:
            return 0.0

        # Se il sottoproblema è già stato risolto in precedenza, riusa il valore
        if memo[i][b] != -1.0:
            return memo[i][b]

        # Scelta di default: nessun ingaggio per il ruolo i
        best_war = dp(i - 1, b)

        # Valuta ciascun candidato per il ruolo corrente
        for j in range(P):
            p = players[i - 1][j]
            c = p.cost // COST_UNIT

            if c <= b:
                candidate_war = dp(i - 1, b - c) + p.war
                if candidate_war > best_war:
                    best_war = candidate_war

        # Memoization: salva i risultati per evitare ricalcoli futuri
        memo[i][b] = best_war

        return best_war

    # Avvio della risoluzione partendo dal problema globale (ruolo N, budget B)
    optimal_war = dp(N, B)

    return optimal_war
