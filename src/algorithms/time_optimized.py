from math import floor


# Metodo ricorsivo per il calcolo del WAR ottimale
def compute_optimal_war_with_recursion(N, X, players, cost_unit=100000):
    B = floor(X / cost_unit)

    memo = [[float(-b - 1) for b in range(B + 1)] for _ in range(N + 1)]

    def dp(i, b):
        if i == 0:
            return 0.0

        if memo[i][b] >= 0:
            return memo[i][b]

        best_war = dp(i - 1, b)

        for p in players[i - 1]:
            c = p.cost // cost_unit

            if c <= b:
                candidate_war = dp(i - 1, b - c) + p.war
                if candidate_war > best_war:
                    best_war = candidate_war

        memo[i][b] = best_war

        return best_war

    optimal_war = dp(N, B)

    return optimal_war
