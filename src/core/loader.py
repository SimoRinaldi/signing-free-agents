import json
from pathlib import Path
from typing import Union
from src.core.models import Player, Role, Scenario


def load_scenario_from_json(file_path: Union[str, Path]) -> Scenario:
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenario_name = data.get("scenario_name", path.stem)
    budget = int(data["budget"])
    cost_unit = int(data.get("cost_unit", 100000))
    roles_data = data["roles"]

    if not roles_data:
        raise ValueError(f"Lo scenario '{scenario_name}' non contiene ruoli.")

    # Il numero di candidati per ruolo deve essere costante
    p_count = len(roles_data[0]["candidates"])

    roles = []
    for role_item in roles_data:
        candidates = role_item["candidates"]
        if len(candidates) != p_count:
            raise ValueError("Il numero di candidati per ruolo deve essere costante.")

        role_players = [
            Player(name=c["name"], cost=int(c["cost"]), war=float(c["war"]))
            for c in candidates
        ]
        roles.append(
            Role(name=role_item.get("role_name", "Ruolo"), candidates=role_players)
        )

    return Scenario(
        name=scenario_name,
        budget=budget,
        cost_unit=cost_unit,
        roles=roles,
    )


load_scenario = load_scenario_from_json
