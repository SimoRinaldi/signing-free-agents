from math import floor


# Metodo per calcolare il valore ottimo senza istanziare l'intera matrice m, ma solo un vettore di dimensione B+1
def compute_optimal_war_with_one_vector(N, X, players, cost_unit=100000):
    B = floor(X / cost_unit)

    solution = [0.0 for _ in range(B + 1)]

    for i in range(1, N + 1):

        for b in range(B, -1, -1):
            best_war = solution[b]

            for p in players[i - 1]:
                c = p.cost // cost_unit
                war_p = p.war

                if b >= c:
                    war = solution[b - c] + war_p
                    if war > best_war:
                        best_war = war

            solution[b] = best_war

    optimal_war = solution[B]
    return optimal_war
