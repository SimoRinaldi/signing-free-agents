def players_filter(players, cost_unit, total_budget):
    valid_players = []

    for players_list in players:
        role_valid = []
        for p in players_list:
            c = p.cost // cost_unit
            if p.war > 0.0 and c <= total_budget:
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
