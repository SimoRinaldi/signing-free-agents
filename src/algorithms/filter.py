# Metodo che filtra i giocatori in base al costo e al WAR, restituendo solo quelli validi per ogni ruolo.
def filter_players(players, cost_unit=100000, total_budget=None):
    valid_players = []

    for players_list in players:
        role_valid = []
        for p in players_list:
            c = p.cost // cost_unit
            if p.war > 0.0 and (total_budget is None or c <= total_budget):
                role_valid.append(p)

        role_valid.sort(key=lambda p: (p.cost, -p.war))
        valid_players.append(role_valid)

    filtered_players = []

    for role_candidates in valid_players:
        role_valid = []
        max_war = 0.0

        for p in role_candidates:
            if p.war > max_war:
                role_valid.append(p)
                max_war = p.war

        filtered_players.append(role_valid)

    return filtered_players
