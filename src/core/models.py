from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass(frozen=True)
class Player:
    name: str
    cost: int
    war: float


@dataclass(frozen=True)
class Role:
    name: str
    candidates: List[Player]

    @property
    def P(self) -> int:
        return len(self.candidates)


@dataclass
class Scenario:
    name: str
    budget: int
    cost_unit: int
    roles: List[Role]

    @property
    def N(self) -> int:
        return len(self.roles)

    @property
    def B(self) -> int:
        return self.budget // self.cost_unit

    @property
    def P(self) -> int:
        return len(self.roles[0].candidates) if self.roles else 0

    @property
    def instance_size(self) -> int:
        return self.N * self.B * self.P

    def get_players_matrix(self) -> List[List[Player]]:
        return [list(role.candidates) for role in self.roles]


@dataclass(frozen=True)
class RosterSolution:
    optimal_war: float
    players: List[Player]
    total_cost: int

    @classmethod
    def create(cls, players: List[Player]) -> "RosterSolution":
        total_cost = sum(p.cost for p in players)
        optimal_war = round(sum(p.war for p in players), 4)
        return cls(optimal_war=optimal_war, players=players, total_cost=total_cost)


@dataclass(frozen=True)
class BenchmarkMetric:
    scenario: str
    N: int
    budget: int
    B: int
    P: int
    instance_size: int
    algorithm: str
    optimal_war: float
    time_ms: float
    memory_kib: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
