from dataclasses import dataclass
from typing import Any, Callable, List
from src.core.models import Player


class AlgorithmName:
    BOTTOM_UP_WITH_S = "Bottom Up (matrice s)"
    BOTTOM_UP_WITHOUT_S = "Bottom Up (matrice m)"
    BOTTOM_UP_VECTOR = "Bottom Up (vettore)"
    TOP_DOWN = "Top Down"
    BOTTOM_UP_FILTER = "Bottom Up (matrice m, filtro)"
    BOTTOM_UP_VECTOR_FILTER = "Bottom Up (vettore, filtro)"


@dataclass(frozen=True)
class SolverStrategy:
    name: str
    func: Callable[..., Any]
    use_filter: bool = False

    def resolve_input(
        self, raw_players: List[List[Player]], filtered_players: List[List[Player]]
    ) -> List[List[Player]]:
        return filtered_players if self.use_filter else raw_players
