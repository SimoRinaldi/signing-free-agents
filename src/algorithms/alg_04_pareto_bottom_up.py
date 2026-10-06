from math import floor


def extract_pareto_frontier(candidates, cost_unit: int, max_budget: int):
    """Estrae la frontiera di Pareto per i candidati di un singolo ruolo.

    Un candidato A domina un candidato B se:
        costo(A) <= costo(B) E war(A) >= war(B) (con almeno una disuguaglianza stretta).

    Regole di pruning:
    1. Giocatori con WAR <= 0.0 vengono scartati (dominati dalla scelta base di non ingaggiare nessuno: costo 0, WAR 0.0).
    2. Giocatori con costo > max_budget vengono scartati (inammissibili rispetto al budget totale X).
    3. Tra candidati con lo stesso costo, viene mantenuto solo quello con WAR massimo.
    4. Scorrendo i candidati per costo crescente, vengono mantenuti solo quelli il cui WAR
       e' strettamente superiore al massimo WAR visto finora.

    Complessita':
        O(P log P) per l'ordinamento + O(P) per la scansione lineare.

    Ritorna:
        Lista di tuple (c, war, orig_idx) ordinate per costo c strettamente crescente
        e WAR strettamente crescente, dove:
        - c: costo discretizzato (cost // cost_unit)
        - war: valore WAR del giocatore
        - orig_idx: indice originale nella lista dei candidati del ruolo (per la ricostruzione)
    """
    valid = []
    for orig_idx, p in enumerate(candidates):
        c = p.cost // cost_unit
        if p.war > 0.0 and c <= max_budget:
            valid.append((c, p.war, orig_idx))

    if not valid:
        return []

    # Ordina per costo crescente; a parità di costo, per WAR decrescente
    valid.sort(key=lambda item: (item[0], -item[1]))

    frontier = []
    max_war_seen = 0.0

    for c, war, orig_idx in valid:
        # Se il WAR e' strettamente maggiore di qualsiasi candidato visto a costo inferiore,
        # il candidato appartiene alla frontiera di Pareto
        if war > max_war_seen:
            frontier.append((c, war, orig_idx))
            max_war_seen = war

    return frontier


def compute_optimal_war(N, X, P, players, return_tables: bool = False):
    """Calcola il massimo WAR ottenibile utilizzando una variante Bottom-Up con

    pruning di Pareto dei candidati dominati.

    Complessita' temporale:
        O(N * P log P + N * B * P'), dove P' <= P e' la dimensione media della frontiera di Pareto.
    Complessita' spaziale:
        O(N * B) per la matrice DP m (e opzionalmente s).
    """
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    m = [[0.0] * (B + 1) for _ in range(N + 1)]
    s = [[-1] * (B + 1) for _ in range(N + 1)] if return_tables else None

    # Considera ciascun ruolo da 1 a N
    for i in range(1, N + 1):
        # Scelta di default: nessun free agent ingaggiato per il ruolo i
        m[i][:] = m[i - 1][:]

        # Preprocessing: estrazione della frontiera di Pareto dei candidati del ruolo i
        frontier = extract_pareto_frontier(players[i - 1], COST_UNIT, B)

        # Itera esclusivamente sui candidati non dominati (P' <= P)
        for c, war_p, orig_idx in frontier:
            for b in range(c, B + 1):
                war = m[i - 1][b - c] + war_p
                if war > m[i][b]:
                    m[i][b] = war
                    if s is not None:
                        s[i][b] = orig_idx

    optimal_war = m[N][B]
    if return_tables:
        return optimal_war, m, s
    return optimal_war


def compute_optimal_war_space_efficient(N, X, P, players):
    """Variante con pruning di Pareto e ottimizzazione spaziale a singolo vettore (1D).

    Complessita' temporale:
        O(N * P log P + N * B * P')
    Complessita' spaziale:
        O(B)
    """
    COST_UNIT = 100000
    B = floor(X / COST_UNIT)

    solution = [0.0 for _ in range(B + 1)]

    for i in range(1, N + 1):
        frontier = extract_pareto_frontier(players[i - 1], COST_UNIT, B)

        # Scansione del budget a ritroso per preservare i valori dello stato i - 1
        for b in range(B, -1, -1):
            best_war = solution[b]

            for c, war_p, _ in frontier:
                if b < c:
                    break  # La frontiera e' ordinata per costo crescente: i successivi avranno costo >= c
                war = solution[b - c] + war_p
                if war > best_war:
                    best_war = war

            solution[b] = best_war

    optimal_war = solution[B]
    return optimal_war
