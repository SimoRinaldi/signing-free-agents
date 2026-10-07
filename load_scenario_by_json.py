import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Player:
    name: str
    cost: int
    war: float


def load_scenario(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    X = data["budget"]
    roles_data = data["roles"]
    N = len(roles_data)

    # Si assume P costante per ruolo all'interno del file
    P = len(roles_data[0]["candidates"])

    # Costruzione della lista di oggetti Player (N ruoli x P candidati)
    players = []
    for role in roles_data:
        candidates = role["candidates"]
        if len(candidates) != P:
            raise ValueError(f"Il numero di candidati per ruolo deve essere costante.")

        role_players = []
        for c in candidates:
            player = Player(name=c["name"], cost=c["cost"], war=c["war"])
            role_players.append(player)

        players.append(role_players)

    return N, X, P, players
