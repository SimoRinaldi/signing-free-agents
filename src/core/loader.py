import json
from pathlib import Path
from src.core.models import Player, Role, Scenario


def load_scenario_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenario_name = data.get("scenario_name", Path(file_path).stem)
    budget = int(data["budget"])
    cost_unit = int(data.get("cost_unit", 100000))
    roles_data = data["roles"]

    # Si assume P costante per ruolo all'interno del file
    P = len(roles_data[0]["candidates"])

    roles = []
    for role_item in roles_data:
        candidates = role_item["candidates"]
        if len(candidates) != P:
            raise ValueError("Il numero di candidati per ruolo deve essere costante.")

        role_players = [
            Player(name=c["name"], cost=c["cost"], war=c["war"])
            for c in candidates
        ]
        roles.append(Role(name=role_item.get("role_name", "Ruolo"), candidates=role_players))

    return Scenario(
        name=scenario_name,
        budget=budget,
        cost_unit=cost_unit,
        roles=roles,
    )


load_scenario = load_scenario_from_json
