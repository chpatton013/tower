#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Self

ILMPLUS_UNLOCK_COST = 750
ILM_LEVEL = 0
ILMPLUS_LEVEL = 0
CHRONO_JUMP_LEVEL = 0

# cost, multiplier
ILM_UPGRADES = [
    (0, 10),
    (5, 11),
    (11, 13),
    (17, 16),
    (23, 20),
    (29, 26),
    (35, 34),
    (41, 43),
    (47, 55),
    (53, 69),
    (61, 87),
    (71, 108),
    (84, 134),
    (100, 164),
    (120, 200),
    (144, 243),
    (174, 293),
    (210, 352),
    (254, 421),
    (308, 502),
    (374, 597),
    (454, 708),
    (540, 838),
    (632, 989),
    (730, 1165),
    (834, 1370),
    (944, 1608),
    (1060, 1886),
    (1182, 2209),
    (1312, 2585),
    (1448, 3021),
]

# cost, multiplier
ILMPLUS_UPGRADES = [
    (0, 0),
    (ILMPLUS_UNLOCK_COST, 0.5),
    (300, 1.5),
    (360, 2.9),
    (430, 4.7),
    (510, 6.9),
    (620, 9.5),
    (750, 12.5),
    (900, 15.9),
    (1100, 19.7),
    (1350, 23.9),
    (1650, 28.5),
    (2050, 33.5),
    (2600, 38.9),
    (3300, 44.7),
    (4150, 50.9),
]

CHRONO_JUMP_UPGRADES = [5 * i for i in range(0, 11)]

ENEMY_TIME_TO_LIVE = 30
ENEMY_HITS_PER_SECOND = 1
AVERAGE_MINE_AGE_SECONDS = 0


def damage_mine(
    ilm_damage: float, ilmplus_mult: float, chrono_jump: float, mine_hit_index: int,
    mine_age_seconds: float = AVERAGE_MINE_AGE_SECONDS,
) -> float:
    effective_age = mine_age_seconds + chrono_jump * mine_hit_index
    return ilm_damage + ilm_damage * ilmplus_mult * effective_age


def damage_total(
    ilm_damage: float, ilmplus_mult: float, chrono_jump: float,
    mine_hit_count: int = ENEMY_TIME_TO_LIVE * ENEMY_HITS_PER_SECOND,
    mine_age_seconds: float = AVERAGE_MINE_AGE_SECONDS,
) -> float:
    return sum(
        damage_mine(ilm_damage, ilmplus_mult, chrono_jump, mine_hit_index, mine_age_seconds)
        for mine_hit_index in range(0, mine_hit_count)
    )


DAMAGE_TOTAL = [
    [
        [
            damage_total(ilm_damage, ilmlpus_mult, chrono_jump)
            for _, ilmlpus_mult in ILMPLUS_UPGRADES
        ]
        for _, ilm_damage in ILM_UPGRADES
    ]
    for chrono_jump in CHRONO_JUMP_UPGRADES
]


@dataclass(frozen=True)
class State:
    ilm_level: int
    ilmplus_level: int
    chrono_jump_level: int

    def score(self) -> float:
        return DAMAGE_TOTAL[self.chrono_jump_level][self.ilm_level][self.ilmplus_level]

    def ilm_upgrade(self) -> Self | None:
        next_ilm = self.ilm_level + 1
        if next_ilm >= len(ILM_UPGRADES):
            return None
        return State(next_ilm, self.ilmplus_level, self.chrono_jump_level)

    def ilmplus_upgrade(self) -> Self | None:
        next_ilmplus = self.ilmplus_level + 1
        if next_ilmplus >= len(ILMPLUS_UPGRADES):
            return None
        return State(self.ilm_level, next_ilmplus, self.chrono_jump_level)

    def cost_to_other(self, other: Self) -> float:
        cost = 0

        assert self.ilm_level <= other.ilm_level
        for ilm_index in range(self.ilm_level + 1, other.ilm_level + 1):
            cost += ILM_UPGRADES[ilm_index][0]

        assert self.ilmplus_level <= other.ilmplus_level
        for ilmplus_index in range(self.ilmplus_level + 1, other.ilmplus_level + 1):
            cost += ILMPLUS_UPGRADES[ilmplus_index][0]

        return cost

    def score_to_other(self, other: Self) -> float:
        return other.score() - self.score()

    def __str__(self) -> str:
        return f"State({self.ilm_level};{self.ilmplus_level})"


def ilm_first_path(start: State) -> list[State]:
    path = [start]
    while next_state := path[-1].ilm_upgrade():
        path.append(next_state)
    while next_state := path[-1].ilmplus_upgrade():
        path.append(next_state)
    return path


def ilmplus_first_path(start: State) -> list[State]:
    path = [start]
    while next_state := path[-1].ilmplus_upgrade():
        path.append(next_state)
    while next_state := path[-1].ilm_upgrade():
        path.append(next_state)
    return path


def greedy_path(start: State) -> list[State]:
    """Greedy with no lookahead - picks best immediate ROI."""
    path = [start]
    while True:
        last_state = path[-1]
        next_ilm = last_state.ilm_upgrade()
        next_ilmplus = last_state.ilmplus_upgrade()

        if next_ilm is None and next_ilmplus is None:
            break
        if next_ilm is None:
            assert next_ilmplus is not None
            path.append(next_ilmplus)
            continue
        if next_ilmplus is None:
            assert next_ilm is not None
            path.append(next_ilm)
            continue

        next_ilm_roi = 0
        next_ilmplus_roi = 0
        if next_ilm is not None:
            next_ilm_cost = last_state.cost_to_other(next_ilm)
            next_ilm_score = last_state.score_to_other(next_ilm)
            next_ilm_roi = next_ilm_score / next_ilm_cost
        if next_ilmplus is not None:
            next_ilmplus_cost = last_state.cost_to_other(next_ilmplus)
            next_ilmplus_score = last_state.score_to_other(next_ilmplus)
            next_ilmplus_roi = next_ilmplus_score / next_ilmplus_cost
        if next_ilm_roi > next_ilmplus_roi:
            path.append(next_ilm)
        else:
            path.append(next_ilmplus)

    return path


def greedy_lookahead_path(start: State) -> list[State]:
    """
    Greedy with lookahead - considers bundles of consecutive ilm+ upgrades.

    Takes the smallest ilm+ bundle whose average ROI beats the next ilm upgrade.
    This handles cases where initial ilm+ upgrades have poor ROI but later ones
    in the sequence bring the average up enough to be competitive.
    """
    path = [start]
    while True:
        current = path[-1]
        next_ilm = current.ilm_upgrade()
        next_ilmplus = current.ilmplus_upgrade()

        # If no upgrades available, done
        if next_ilm is None and next_ilmplus is None:
            break

        # If only one type available, take it
        if next_ilm is None:
            path.append(next_ilmplus)
            continue
        if next_ilmplus is None:
            path.append(next_ilm)
            continue

        # Evaluate ilm upgrade ROI
        ilm_cost = current.cost_to_other(next_ilm)
        ilm_score = current.score_to_other(next_ilm)
        ilm_roi = ilm_score / ilm_cost

        # Find the smallest ilm+ bundle that beats the ilm upgrade
        # Strategy: grow the bundle until average ROI peaks, then take it if > ilm_roi
        best_bundle_size = 0
        best_bundle_roi = 0
        prev_bundle_roi = 0
        bundle_size = 0
        bundle_state = current
        while bundle_state := bundle_state.ilmplus_upgrade():
            bundle_size += 1

            # Calculate average ROI for this bundle
            bundle_cost = current.cost_to_other(bundle_state)
            bundle_benefit = current.score_to_other(bundle_state)
            bundle_roi = bundle_benefit / bundle_cost

            # Track the best bundle we've seen
            if bundle_roi > best_bundle_roi:
                best_bundle_roi = bundle_roi
                best_bundle_size = bundle_size

            if best_bundle_roi > ilm_roi:
                break

            # If ROI is decreasing and we've passed the ilm threshold, stop looking
            if bundle_roi < prev_bundle_roi and prev_bundle_roi > ilm_roi:
                break

            prev_bundle_roi = bundle_roi

        # Choose best option
        if best_bundle_roi > ilm_roi:
            # Take the best ilm+ bundle
            for _ in range(best_bundle_size):
                path.append(path[-1].ilmplus_upgrade())
        else:
            # Take the ilm upgrade
            path.append(next_ilm)

    return path



def print_stats() -> None:
    print("ILM upgrades:")
    for index, (cost, damage) in enumerate(ILM_UPGRADES):
        print(f"  {index:2d}: {cost} stones ({damage:.2f} damage)")
    print()

    print("ILM+ upgrades:")
    for index, (cost, mult) in enumerate(ILMPLUS_UPGRADES):
        print(f"  {index:2d}: {cost} stones (+{mult:.2f} mult/sec)")
    print()

    def chrono_jump_level(index: int) -> str:
        if index == 0:
            return "locked"
        return f"level {index - 1}"

    print("Chrono Jump upgrades:")
    for index, jump in enumerate(CHRONO_JUMP_UPGRADES):
        level = chrono_jump_level(index)
        jump = CHRONO_JUMP_UPGRADES[index]
        print(f"  {level}: +{jump:.2f} sec/hit")
    print()

    for cj_index, damage_table in enumerate(DAMAGE_TOTAL):
        cj_level = chrono_jump_level(cj_index)
        cj_jump = CHRONO_JUMP_UPGRADES[cj_index]
        print(f"Damage total (Chrono Jump {cj_level}: +{cj_jump} sec/hit):")
        print(f"        {' '.join(f"ILM+{i if i >= 0 else 'lock'}".rjust(8) for i in range(-1, len(ILMPLUS_UPGRADES) - 1))}")
        print(f"        {' '.join("--------".rjust(8) for i in range(-1, len(ILMPLUS_UPGRADES) - 1))}")
        for ilm_index, damage_row in enumerate(damage_table):
            print(f"ILMd {ilm_index:2d}: {' '.join(f'{damage:8.0f}' for damage in damage_row)}")
        print()


def print_upgrade_path(name: str, path: list[State]) -> None:
    print(f"{name} upgrade path:")
    headers = [('upgrd', 5), ('damage', 11), ('(increase)', 10), ('cost', 11), ('(roi)', 17), ('total cost', 12)]
    print(f"  {' '.join(s.center(w) for s, w in headers)}")
    print(f"  {' '.join(("-" * w) for s, w in headers)}")
    last_state = None
    total_cost = 0
    for state in path:
        if last_state is not None:
            last_score = last_state.score()
            score = state.score()
            score_delta = (score - last_score) / last_score
            cost = last_state.cost_to_other(state)
            roi = score_delta / cost
            total_cost += cost

            description = None
            if last_state.ilm_level != state.ilm_level:
                assert last_state.ilmplus_level == state.ilmplus_level
                description = f"ILMd{state.ilm_level:2d}"
            elif last_state.ilmplus_level != state.ilmplus_level:
                assert last_state.ilm_level == state.ilm_level
                description = f"ILM+{(state.ilmplus_level - 1):2d}"
            assert description is not None

            print(f"  {description} {score:10.1f}x ({score_delta:+8.3%}) {cost:4d} stones ({roi:8.6%}/stone) {total_cost:5d} stones")
        last_state = state


print_stats()
START_STATE = State(ILM_LEVEL, ILMPLUS_LEVEL, 5)
print_upgrade_path("Optimal ILM w/ CJ=5", greedy_lookahead_path(START_STATE))
print()
# for cj_index, _ in enumerate(CHRONO_JUMP_UPGRADES):
#     print()
#     START_STATE = State(ILM_LEVEL, ILMPLUS_LEVEL, cj_index)
#     # print_upgrade_path("ILM first", ilm_first_path(START_STATE))
#     # print_upgrade_path("ILM+ first", ilmplus_first_path(START_STATE))
#     # print_upgrade_path(f"Greedy (no lookahead) CJ{cj_index}", greedy_path(START_STATE))
#     print_upgrade_path(f"Greedy (with lookahead) CJ{cj_index}", greedy_lookahead_path(START_STATE))
