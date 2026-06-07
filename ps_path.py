#!/usr/bin/env python3

import copy
from dataclasses import dataclass
from typing import Self

PSPLUS_UNLOCK_COST = 750
DAMAGE_TICK_COUNT = 30
PS_LEVEL = 0
PSPLUS_LEVEL = 0

# cost, multiplier
PS_UPGRADES = [
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
    (252, 421),
    (302, 502),
    (362, 597),
    (434, 708),
    (525, 838),
    (636, 989),
    (772, 1165),
    (938, 1370),
    (1134, 1608),
    (1360, 1886),
    (1616, 2209),
    (1902, 2585),
    (2228, 3021),
]

# cost, multiplier
PSPLUS_UPGRADES = [
    (cost, (1.5 + index * 0.7))
    for index, cost in enumerate(
        [
            0,
            PSPLUS_UNLOCK_COST,
            300,
            360,
            430,
            510,
            620,
            750,
            900,
            1100,
            1350,
            1650,
            2050,
            2600,
            3300,
            4150,
        ]
    )
]

DAMAGE_RAMP = [
    [
        tick_index * psplus_damage if tick_index > 0 else 1.0
        for _, psplus_damage in PSPLUS_UPGRADES
    ]
    for tick_index in range(DAMAGE_TICK_COUNT)
]

DAMAGE_SUM = copy.deepcopy(DAMAGE_RAMP)
for tick_index in range(1, len(DAMAGE_RAMP)):
    for psplus_index in range(len(DAMAGE_RAMP[tick_index])):
        DAMAGE_SUM[tick_index][psplus_index] += DAMAGE_SUM[tick_index - 1][psplus_index]

DAMAGE_TOTAL = [
    [
        damage_sum * ps_damage
        for damage_sum in DAMAGE_SUM[DAMAGE_TICK_COUNT - 1]
    ]
    for _, ps_damage in PS_UPGRADES
]

PS_REND_UPGRADES = [0.03 * i for i in range(0, 31)]
REND_ARMOR_MAX_UPGRADES = [8 + 0.25 * i for i in range(0, 31)]


@dataclass(frozen=True)
class State:
    ps_level: int
    psplus_level: int
    ps_rend_level: int
    rend_max_level: int

    def score(self) -> float:
        base_damage = DAMAGE_TOTAL[self.ps_level][self.psplus_level]
        rend_mult = PS_REND_UPGRADES[self.ps_rend_level] * REND_ARMOR_MAX_UPGRADES[self.rend_max_level]
        return base_damage * (1 + rend_mult)

    def ps_upgrade(self) -> Self | None:
        next_ps = self.ps_level + 1
        if next_ps >= len(PS_UPGRADES):
            return None
        return State(next_ps, self.psplus_level, self.ps_rend_level, self.rend_max_level)

    def psplus_upgrade(self) -> Self | None:
        next_psplus = self.psplus_level + 1
        if next_psplus >= len(PSPLUS_UPGRADES):
            return None
        return State(self.ps_level, next_psplus, self.ps_rend_level, self.rend_max_level)

    def cost_to_other(self, other: Self) -> float:
        cost = 0

        assert self.ps_level <= other.ps_level
        for ps_index in range(self.ps_level + 1, other.ps_level + 1):
            cost += PS_UPGRADES[ps_index][0]

        assert self.psplus_level <= other.psplus_level
        for psplus_index in range(self.psplus_level + 1, other.psplus_level + 1):
            cost += PSPLUS_UPGRADES[psplus_index][0]

        return cost

    def score_to_other(self, other: Self) -> float:
        return other.score() - self.score()

    def __str__(self) -> str:
        return f"State({self.ps_level};{self.psplus_level})"


def ps_first_path(start: State) -> list[State]:
    path = [start]
    while next_state := path[-1].ps_upgrade():
        path.append(next_state)
    while next_state := path[-1].psplus_upgrade():
        path.append(next_state)
    return path


def psplus_first_path(start: State) -> list[State]:
    path = [start]
    while next_state := path[-1].psplus_upgrade():
        path.append(next_state)
    while next_state := path[-1].ps_upgrade():
        path.append(next_state)
    return path


def greedy_path(start: State) -> list[State]:
    """Greedy with no lookahead - picks best immediate ROI."""
    path = [start]
    while True:
        last_state = path[-1]
        next_ps = last_state.ps_upgrade()
        next_psplus = last_state.psplus_upgrade()

        if next_ps is None and next_psplus is None:
            break
        if next_ps is None:
            assert next_psplus is not None
            path.append(next_psplus)
            continue
        if next_psplus is None:
            assert next_ps is not None
            path.append(next_ps)
            continue

        next_ps_roi = 0
        next_psplus_roi = 0
        if next_ps is not None:
            next_ps_cost = last_state.cost_to_other(next_ps)
            next_ps_score = last_state.score_to_other(next_ps)
            next_ps_roi = next_ps_score / next_ps_cost
        if next_psplus is not None:
            next_psplus_cost = last_state.cost_to_other(next_psplus)
            next_psplus_score = last_state.score_to_other(next_psplus)
            next_psplus_roi = next_psplus_score / next_psplus_cost
        if next_ps_roi > next_psplus_roi:
            path.append(next_ps)
        else:
            path.append(next_psplus)

    return path


def greedy_lookahead_path(start: State) -> list[State]:
    """
    Greedy with lookahead - considers bundles of consecutive PS+ upgrades.

    Takes the smallest PS+ bundle whose average ROI beats the next PS upgrade.
    This handles cases where initial PS+ upgrades have poor ROI but later ones
    in the sequence bring the average up enough to be competitive.
    """
    path = [start]
    while True:
        current = path[-1]
        next_ps = current.ps_upgrade()
        next_psplus = current.psplus_upgrade()

        # If no upgrades available, done
        if next_ps is None and next_psplus is None:
            break

        # If only one type available, take it
        if next_ps is None:
            path.append(next_psplus)
            continue
        if next_psplus is None:
            path.append(next_ps)
            continue

        # Evaluate PS upgrade ROI
        ps_cost = current.cost_to_other(next_ps)
        ps_score = current.score_to_other(next_ps)
        ps_roi = ps_score / ps_cost

        # Find the smallest PS+ bundle that beats the PS upgrade
        # Strategy: grow the bundle until average ROI peaks, then take it if > ps_roi
        best_bundle_size = 0
        best_bundle_roi = 0
        prev_bundle_roi = 0
        bundle_size = 0
        bundle_state = current
        while bundle_state := bundle_state.psplus_upgrade():
            bundle_size += 1

            # Calculate average ROI for this bundle
            bundle_cost = current.cost_to_other(bundle_state)
            bundle_benefit = current.score_to_other(bundle_state)
            bundle_roi = bundle_benefit / bundle_cost

            # Track the best bundle we've seen
            if bundle_roi > best_bundle_roi:
                best_bundle_roi = bundle_roi
                best_bundle_size = bundle_size

            if best_bundle_roi > ps_roi:
                break

            # If ROI is decreasing and we've passed the PS threshold, stop looking
            if bundle_roi < prev_bundle_roi and prev_bundle_roi > ps_roi:
                break

            prev_bundle_roi = bundle_roi

        # Choose best option
        if best_bundle_roi > ps_roi:
            # Take the best PS+ bundle
            for _ in range(best_bundle_size):
                path.append(path[-1].psplus_upgrade())
        else:
            # Take the PS upgrade
            path.append(next_ps)

    return path


def print_stats() -> None:
    print("PS upgrades:")
    for index, (cost, damage) in enumerate(PS_UPGRADES):
        print(f"  {index:2d}: {cost} stones ({damage:.2f} damage)")
    print()

    print("PS+ upgrades:")
    for index, (cost, damage) in enumerate(PSPLUS_UPGRADES):
        print(f"  {index:2d}: {cost} stones ({damage:.2f} damage)")
    print()

    print("Damage ramp:")
    print(f"        {' '.join(f"PS+{i if i >= 0 else 'lock'}".rjust(8) for i in range(-1, len(PSPLUS_UPGRADES) - 1))}")
    print(f"        {' '.join("--------".rjust(8) for i in range(-1, len(PSPLUS_UPGRADES) - 1))}")
    for tick_index, damage_row in enumerate(DAMAGE_RAMP):
        tick = tick_index + 1
        print(f"tck {tick:2d}: {' '.join(f'{damage:8.1f}' for damage in damage_row)}")
    print()

    print("Damage sum:")
    print(f"        {' '.join(f"PS+{i if i >= 0 else 'lock'}".rjust(8) for i in range(-1, len(PSPLUS_UPGRADES) - 1))}")
    print(f"        {' '.join("--------".rjust(8) for i in range(-1, len(PSPLUS_UPGRADES) - 1))}")
    for tick_index, damage_row in enumerate(DAMAGE_SUM):
        tick = tick_index + 1
        print(f"tck {tick:2d}: {' '.join(f'{damage:8.1f}' for damage in damage_row)}")
    print()

    print("Damage total:")
    print(f"        {' '.join(f"PS+{i if i >= 0 else 'lock'}".rjust(8) for i in range(-1, len(PSPLUS_UPGRADES) - 1))}")
    print(f"        {' '.join("--------".rjust(8) for i in range(-1, len(PSPLUS_UPGRADES) - 1))}")
    for ps_index, damage_row in enumerate(DAMAGE_TOTAL):
        print(f"PSd {ps_index:2d}: {' '.join(f'{damage:8.0f}' for damage in damage_row)}")
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
            if last_state.ps_level != state.ps_level:
                assert last_state.psplus_level == state.psplus_level
                description = f"PSd{state.ps_level:2d}"
            elif last_state.psplus_level != state.psplus_level:
                assert last_state.ps_level == state.ps_level
                description = f"PS+{(state.psplus_level - 1):2d}"
            assert description is not None

            print(f"  {description} {score:10.1f}x ({score_delta:+8.3%}) {cost:4d} stones ({roi:8.6%}/stone) {total_cost:5d} stones")
        last_state = state


print_stats()
START_STATE = State(PS_LEVEL, PSPLUS_LEVEL, 30, 30)
# START_STATE = State(PS_LEVEL, PSPLUS_LEVEL, 30, 30)
# print_upgrade_path("PS first", ps_first_path(START_STATE))
# print_upgrade_path("PS+ first", psplus_first_path(START_STATE))
# print_upgrade_path("Greedy (no lookahead)", greedy_path(START_STATE))
# print_upgrade_path("Greedy (with lookahead)", greedy_lookahead_path(START_STATE))
print_upgrade_path("Optimal PS", greedy_lookahead_path(START_STATE))
print()
