#!/usr/bin/env python3

import bisect
import argparse
import dataclasses
from typing import Iterator
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# Global constants

# fmt: off
GAME_SPEED = 6.25 * 0.8
WAVE_DURATION = 26.0
WAVE_COOLDOWN = 5.0
WAVE_SKIP_CHANCE = 0.19
WAVE_SKIP_COIN_BONUS = 1.10

TIER_COIN_BONUS = [1.0, 1.8, 2.6, 3.4, 4.2, 5.0, 5.8, 6.6, 7.5, 8.7, 10.3, 12.2, 14.7, 17.6, 21.3, 25.2, 29.1, 33.0]

SPAWN_RATE_SEQUENCE = [10, 11, 13, 15, 17, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36, 37, 39, 40, 42, 44, 46, 48, 49, 50, 52, 54, 56]
SPAWN_RATE_WAVES = [1, 3, 6, 20, 40, 60, 80, 100, 150, 200, 250, 300, 400, 600, 800, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500]
assert len(SPAWN_RATE_SEQUENCE) == len(SPAWN_RATE_WAVES)

SPAWN_CHANCE_TABLE = {
    "fast": [0.05, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.10, 0.11, 0.11, 0.12, 0.12, 0.13, 0.13, 0.13, 0.14, 0.15, 0.17, 0.18, 0.19, 0.20, 0.21, 0.21, 0.22, 0.23, 0.24, 0.24],
    "tank": [0.00, 0.02, 0.04, 0.06, 0.07, 0.08, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.13, 0.14, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.19, 0.20, 0.20, 0.20, 0.21, 0.21, 0.22],
    "ranged": [0.00, 0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.06, 0.07, 0.07, 0.08, 0.09, 0.10, 0.11, 0.11, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.19, 0.19, 0.20, 0.21],
    "protector": [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.01, 0.01, 0.02, 0.02, 0.02, 0.03, 0.03, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04],
}
assert all(len(row) == len(SPAWN_RATE_SEQUENCE) for row in SPAWN_CHANCE_TABLE.values())
SPAWN_CHANCE_TABLE["basic"] = [
    1.0 - sum(row[i] for row in SPAWN_CHANCE_TABLE.values())
    for i in range(len(SPAWN_RATE_SEQUENCE))
]

COIN_DROP_TABLE = {
    "basic": 0.33,
    "fast": 2.0,
    "tank": 4.0,
    "ranged": 2.0,
    "protector": 3.0,
}
assert sorted(COIN_DROP_TABLE.keys()) == sorted(SPAWN_CHANCE_TABLE.keys())

COIN_MASTERY_TABLE = [1.03, 1.06, 1.09, 1.12, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30]
EXTRA_ORB_MASTERY_TABLE = [1.04, 1.08, 1.12, 1.16, 1.20, 1.24, 1.28, 1.32, 1.36, 1.40]
CRITICAL_COIN_MASTERY_TABLE = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
WAVE_SKIP_MASTERY_TABLE = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55]
INTRO_SPRINT_MASTERY_TABLE = [180, 360, 540, 720, 900, 1080, 1260, 1440, 1620, 1800]
WAVE_ACCELERATOR_MASTERY_TABLE = [
    [1, 3, 5, 18, 36, 55, 73, 91, 136, 182, 227, 273, 364, 545, 727, 909, 1364, 1818, 2273, 2727, 3182, 3636, 4091, 4545, 5000, 5455, 5909],
    [1, 3, 5, 17, 33, 50, 67, 83, 125, 167, 208, 250, 333, 500, 667, 833, 1250, 1667, 2083, 2500, 2917, 3333, 3750, 4167, 4583, 5000, 5417],
    [1, 2, 5, 15, 31, 46, 62, 77, 115, 154, 192, 231, 308, 462, 615, 769, 1154, 1538, 1923, 2308, 2692, 3077, 3462, 3846, 4231, 4615, 5000],
    [1, 2, 4, 14, 29, 43, 57, 71, 107, 143, 179, 214, 286, 429, 571, 714, 1071, 1429, 1786, 2143, 2500, 2857, 3214, 3571, 3929, 4286, 4643],
    [1, 2, 4, 13, 27, 40, 53, 67, 100, 133, 167, 200, 267, 400, 533, 667, 1000, 1333, 1667, 2000, 2333, 2667, 3000, 3333, 3667, 4000, 4333],
    [1, 2, 4, 13, 25, 38, 50, 63, 94, 125, 156, 188, 250, 375, 500, 625, 938, 1250, 1563, 1875, 2188, 2500, 2813, 3125, 3438, 3750, 4063],
    [1, 2, 4, 12, 24, 35, 47, 59, 88, 118, 147, 176, 235, 353, 471, 588, 882, 1176, 1471, 1765, 2059, 2353, 2647, 2941, 3235, 3529, 3824],
    [1, 2, 3, 11, 22, 33, 44, 56, 83, 111, 139, 167, 222, 333, 444, 556, 833, 1111, 1389, 1667, 1944, 2222, 2500, 2778, 3056, 3333, 3611],
    [1, 2, 3, 11, 21, 32, 42, 53, 79, 105, 132, 158, 211, 316, 421, 526, 789, 1053, 1316, 1579, 1842, 2105, 2368, 2632, 2895, 3158, 3421],
    [1, 2, 3, 10, 20, 30, 40, 50, 75, 100, 125, 150, 200, 300, 400, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250]
]
assert all(len(row) == len(SPAWN_RATE_SEQUENCE) for row in WAVE_ACCELERATOR_MASTERY_TABLE)

MASTERY_LEVELS = [None, *range(0, 10)]
MASTERY_LEVEL_NAMES = [str(x) for x in range(0, 10)]
MASTERY_DISPLAY_NAMES = {
    "coin": "Coin",
    "extra-orb": "EO",
    "critical-coin": "CritCoin",
    "wave-skip": "WS",
    "intro-sprint": "IS",
    "wave-accelerator": "WA",
}
MASTERY_STONE_COSTS = {
    "coin": 1250,
    "extra-orb": 750,
    "critical-coin": 1000,
    "wave-skip": 1000,
    "intro-sprint": 1250,
    "wave-accelerator": 1000,
}
# fmt: on


# Data types

@dataclasses.dataclass
class Simulation:
    name: str = ""
    mastery: str | None = None
    tier: int = 1
    max_waves: int = 0
    orb_kills: float = 1.0
    coin: int | None = None
    extra_orb: int | None = None
    critical_coin: int | None = None
    wave_skip: int | None = None
    intro_sprint: int | None = None
    wave_accelerator: int | None = None

    def max_intro_wave(self) -> int:
        return (
            100
            if self.intro_sprint is None
            else INTRO_SPRINT_MASTERY_TABLE[self.intro_sprint]
        )

    def spawn_rate_row(self) -> list[int]:
        return (
            SPAWN_RATE_WAVES
            if self.wave_accelerator is None
            else WAVE_ACCELERATOR_MASTERY_TABLE[self.wave_accelerator]
        )

    def spawn_rate_index(self, wave: int):
        index = max(
            i for i, min_wave in enumerate(self.spawn_rate_row()) if min_wave <= wave
        )
        assert (
            0 <= index < len(SPAWN_RATE_SEQUENCE)
        ), f"Invalid spawn rate index: {index}"
        return index


@dataclasses.dataclass
class SimulationWaveResult:
    wave: int
    elapsed_time: float
    value: float


@dataclasses.dataclass
class SimulationRunResult:
    wave_results: list[SimulationWaveResult]
    relative: float | None = None
    roi: float | None = None


@dataclasses.dataclass
class PlotLine:
    name: str
    mastery: str | None = None
    xs: list[float] = dataclasses.field(default_factory=list)
    ys: list[float] = dataclasses.field(default_factory=list)
    relative: float | None = None
    roi: float | None = None


@dataclasses.dataclass
class Plot:
    title: str
    xlabel: str
    ylabel: str
    bottom: float | None = None
    log_scale: bool = False
    lines: list[PlotLine] = dataclasses.field(default_factory=list)


# Argument handling

def tier_and_wave_arg(arg: str) -> tuple[int, int]:
    tier, _, wave = arg.partition(":")
    return int(tier), int(wave)


def add_simulation_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--orb-kills",
        type=float,
        default=1.0,
        help="Average portion of kills to orbs [0.0-1.0]",
    )
    parser.add_argument(
        "--log-scale",
        action="store_true",
        default=False,
        help="Render results on a log scale",
    )
    parser.add_argument("--output", "-o", default=None, help="Filename for saved plot")


def add_mastery_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--coin",
        choices=["locked", *MASTERY_LEVEL_NAMES],
        default=None,
        help="Coin mastery level",
    )
    parser.add_argument(
        "--extra-orb",
        choices=["locked", *MASTERY_LEVEL_NAMES],
        default=None,
        help="Extra orb mastery level",
    )
    parser.add_argument(
        "--critical-coin",
        choices=["locked", *MASTERY_LEVEL_NAMES],
        default=None,
        help="Critical coin mastery level",
    )
    parser.add_argument(
        "--wave-skip",
        choices=["locked", *MASTERY_LEVEL_NAMES],
        default=None,
        help="Wave skip mastery level",
    )
    parser.add_argument(
        "--intro-sprint",
        choices=["locked", *MASTERY_LEVEL_NAMES],
        default=None,
        help="Intro sprint mastery level",
    )
    parser.add_argument(
        "--wave-accelerator",
        choices=["locked", *MASTERY_LEVEL_NAMES],
        default=None,
        help="Wave accelerator mastery level",
    )


def mastery_level(name: str | None) -> int | None:
    if name is None or name == "locked":
        return None
    if int(name) in range(0, 10):
        return int(name)
    raise ValueError(f"Invalid mastery level: {name}")


def convert_mastery_args(args: argparse.Namespace) -> None:
    args.coin = mastery_level(args.coin)
    args.extra_orb = mastery_level(args.extra_orb)
    args.critical_coin = mastery_level(args.critical_coin)
    args.wave_skip = mastery_level(args.wave_skip)
    args.intro_sprint = mastery_level(args.intro_sprint)
    args.wave_accelerator = mastery_level(args.wave_accelerator)


def mastery_args_description(args: argparse.Namespace) -> list[str]:
    desc = []
    if args.coin and args.mastery != "coin":
        desc.append(f"Coin#{args.coin}")
    if args.extra_orb and args.mastery != "extra-orb":
        desc.append(f"EO#{args.extra_orb}")
    if args.critical_coin and args.mastery != "critical-coin":
        desc.append(f"CritCoin#{args.critical_coin}")
    if args.wave_skip and args.mastery != "wave-skip":
        desc.append(f"WS#{args.wave_skip}")
    if args.intro_sprint and args.mastery != "intro-sprint":
        desc.append(f"IS#{args.intro_sprint}")
    if args.wave_accelerator and args.mastery != "wave-accelerator":
        desc.append(f"WA#{args.wave_accelerator}")
    return desc


def add_relative_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--relative",
        "-r",
        action="store_true",
        default=False,
        help="Normalize all results against the baseline configuration",
    )


def add_wave_args(parser: argparse.ArgumentParser):
    parser.add_argument("wave", type=int, help="Wave number to simulate")


def relative_args_description(args: argparse.Namespace) -> list[str]:
    if args.relative:
        return ["Relative to baseline"]
    else:
        return ["Absolute coins"]


# Simulation logic

def simulate_wave(sim: Simulation, wave: int) -> float:
    spawn_rate_index = sim.spawn_rate_index(wave)
    spawn_rate = SPAWN_RATE_SEQUENCE[spawn_rate_index]

    avg_spawn_count = spawn_rate * WAVE_DURATION * 8
    avg_spawn = {
        name: avg_spawn_count * row[spawn_rate_index]
        for name, row in SPAWN_CHANCE_TABLE.items()
    }

    avg_coin_drops = {
        name: avg_spawn[name] * drop for name, drop in COIN_DROP_TABLE.items()
    }
    if sim.critical_coin is not None:
        avg_coin_drops["basic"] *= 1.0 + CRITICAL_COIN_MASTERY_TABLE[sim.critical_coin]

    avg_coin_drop = sum(avg_coin_drops.values()) * TIER_COIN_BONUS[sim.tier - 1]

    if sim.coin is not None:
        avg_coin_drop *= COIN_MASTERY_TABLE[sim.coin]
    if sim.extra_orb is not None:
        avg_coin_drop *= 1 + (
            (EXTRA_ORB_MASTERY_TABLE[sim.extra_orb] - 1) * sim.orb_kills
        )

    return avg_coin_drop


def generate_intro_waves(sim: Simulation) -> Iterator[int]:
    yield 1
    yield from range(
        10, min(sim.max_intro_wave(), int(sim.max_waves / 10) * 10) + 1, 10
    )


def generate_regular_waves(sim: Simulation) -> Iterator[int]:
    yield from range(sim.max_intro_wave() + 1, sim.max_waves + 1)


def wave_skip_factor(
    sim: Simulation,
    no_skip_factor: float,
    single_skip_factor: float,
    double_skip_factor: float,
) -> float:
    double_wave_skip_chance = 0.0
    if sim.wave_skip is not None:
        double_wave_skip_chance = (
            WAVE_SKIP_CHANCE * WAVE_SKIP_MASTERY_TABLE[sim.wave_skip]
        )
    return (
        ((1 - WAVE_SKIP_CHANCE) * no_skip_factor)
        + ((WAVE_SKIP_CHANCE - double_wave_skip_chance) * single_skip_factor)
        + (double_wave_skip_chance * double_skip_factor)
    )


def simulate_run(sim: Simulation) -> Iterator[SimulationWaveResult]:
    elapsed_time = 0
    total_coins = 0

    yield SimulationWaveResult(wave=0, elapsed_time=elapsed_time, value=total_coins)

    # No coins are earned during intro sprint; other resources may be, but we aren't
    # calculating them yet.
    for wave in generate_intro_waves(sim):
        _ = simulate_wave(sim, wave)
        # Wave skip chance is not applied to intro waves
        elapsed_time += WAVE_DURATION
        yield SimulationWaveResult(
            wave=wave, elapsed_time=elapsed_time, value=total_coins
        )

    for wave in generate_regular_waves(sim):
        coins_this_wave = simulate_wave(sim, wave)
        coins_wave = coins_this_wave * wave_skip_factor(
            sim,
            1.0,
            WAVE_SKIP_COIN_BONUS,
            WAVE_SKIP_COIN_BONUS * WAVE_SKIP_COIN_BONUS,
        )

        elapsed_time += WAVE_DURATION * wave_skip_factor(sim, 3 / 3, 2 / 3, 1 / 3)
        total_coins += coins_wave

        yield SimulationWaveResult(
            wave=wave, elapsed_time=elapsed_time, value=total_coins
        )


def evaluate_sims(
    sims: list[Simulation],
) -> Iterator[tuple[Simulation, SimulationRunResult]]:
    for sim in sims:
        yield sim, SimulationRunResult(wave_results=list(simulate_run(sim)))


# Data normalization

def baseline_at_time(
    baseline_results: SimulationRunResult, elapsed_time: float
) -> float:
    index = bisect.bisect_left(
        baseline_results.wave_results, elapsed_time, key=lambda x: x.elapsed_time
    )
    if index == 0:
        return baseline_results.wave_results[0].value
    if index == len(baseline_results.wave_results):
        return baseline_results.wave_results[-1].value
    lower_result = baseline_results.wave_results[index - 1]
    higher_result = baseline_results.wave_results[index]
    assert higher_result.elapsed_time - lower_result.elapsed_time != 0
    lerp = (elapsed_time - lower_result.elapsed_time) / (
        higher_result.elapsed_time - lower_result.elapsed_time
    )
    return lower_result.value + (higher_result.value - lower_result.value) * lerp


def normalize_sims_vs_baseline(
    sim_results: list[tuple[Simulation, SimulationRunResult]],
    baseline_sim_name: str,
) -> Iterator[tuple[Simulation, SimulationRunResult]]:
    baseline_sim, baseline_results = next(
        (sim, run_result) for sim, run_result in sim_results if sim.name == baseline_sim_name
    )

    def baseline_value(sim: Simulation, wave_result: SimulationWaveResult) -> float:
        if sim == baseline_sim:
            return 1.0
        baseline = baseline_at_time(baseline_results, wave_result.elapsed_time)
        if baseline == 0:
            return 1.0
        else:
            return wave_result.value / baseline

    for sim, run_result in sim_results:
        normalized_results = []
        value = 1.0
        for wave_result in run_result.wave_results:
            value = baseline_value(sim, wave_result)
            normalized_results.append(
                SimulationWaveResult(
                    wave=wave_result.wave,
                    elapsed_time=wave_result.elapsed_time,
                    value=value,
                )
            )
        yield sim, dataclasses.replace(
            run_result, wave_results=normalized_results, relative=value
        )


def normalize_sims_vs_stone_cost(
    sim_results: list[tuple[Simulation, SimulationRunResult]],
) -> Iterator[tuple[Simulation, SimulationRunResult]]:
    for sim, run_result in sim_results:
        if sim.mastery is None:
            continue

        normalized_results = []
        value = 0.0
        for wave_result in run_result.wave_results:
            value = (wave_result.value - 1) / MASTERY_STONE_COSTS[sim.mastery]
            normalized_results.append(
                SimulationWaveResult(
                    wave=wave_result.wave,
                    elapsed_time=wave_result.elapsed_time,
                    value=value,
                )
            )
        yield sim, dataclasses.replace(
            run_result, wave_results=normalized_results, roi=value
        )


# Simulation config factories

def make_sim(args: argparse.Namespace, max_waves: int = 0, tier: int = 1) -> Simulation:
    return Simulation(
        tier=tier,
        max_waves=max_waves,
        orb_kills=args.orb_kills,
        coin=args.coin,
        extra_orb=args.extra_orb,
        critical_coin=args.critical_coin,
        wave_skip=args.wave_skip,
        intro_sprint=args.intro_sprint,
        wave_accelerator=args.wave_accelerator,
    )


def tiers_sim(sim: Simulation, tier: int, max_wave: int) -> Simulation:
    return dataclasses.replace(
        sim,
        name=f"T{tier}:W{max_wave}",
        tier=tier,
        max_waves=max_wave,
    )


def waves_sim(sim: Simulation, max_wave: int) -> Simulation:
    return dataclasses.replace(
        sim,
        name=f"{max_wave} waves",
        max_waves=max_wave,
    )


def mastery_sim(sim: Simulation, mastery: str, level: int | None) -> Simulation:
    sim = dataclasses.replace(sim, mastery=mastery)

    if level is None:
        sim = dataclasses.replace(sim, name=f"{mastery}: locked")
    else:
        sim = dataclasses.replace(sim, name=f"{mastery}: level {level}")

    if mastery == "coin":
        return dataclasses.replace(sim, coin=level)
    elif mastery == "extra-orb":
        return dataclasses.replace(sim, extra_orb=level)
    elif mastery == "critical-coin":
        return dataclasses.replace(sim, critical_coin=level)
    elif mastery == "wave-skip":
        return dataclasses.replace(sim, wave_skip=level)
    elif mastery == "intro-sprint":
        return dataclasses.replace(sim, intro_sprint=level)
    elif mastery == "wave-accelerator":
        return dataclasses.replace(sim, wave_accelerator=level)
    raise ValueError(f"Invalid mastery: {mastery}")


# Plotting

def interesting_waves(sim: Simulation) -> set[int]:
    return {
        1,
        sim.max_waves,
        *range(10, max(INTRO_SPRINT_MASTERY_TABLE) + 1, 10),
        *range(100, sim.max_waves + 1, 100),
        *{max_intro_wave + 1 for max_intro_wave in [100, *INTRO_SPRINT_MASTERY_TABLE]},
        *SPAWN_RATE_WAVES,
        *{wave for row in WAVE_ACCELERATOR_MASTERY_TABLE for wave in row},
    }


def plot_sim_results(
    title: str,
    sim_results: list[tuple[Simulation, SimulationRunResult]],
    truncate: bool = False,
) -> Plot:
    plot = Plot(title=title, xlabel="Elapsed time (h)", ylabel="Coins")
    for sim, run_result in sim_results:
        line = PlotLine(
            name=sim.name,
            mastery=sim.mastery,
            relative=run_result.relative,
            roi=run_result.roi,
        )
        waves_to_plot = interesting_waves(sim)
        for wave_result in run_result.wave_results:
            if wave_result.wave not in waves_to_plot:
                continue
            line.xs.append(wave_result.elapsed_time)
            line.ys.append(wave_result.value)
        plot.lines.append(line)

    if truncate:
        domain = min(line.xs[-1] for line in plot.lines)
        for line in plot.lines:
            idx = next((i for i, x in enumerate(line.xs) if x > domain), len(line.xs))
            line.xs = line.xs[:idx]
            line.ys = line.ys[:idx]

    for line in plot.lines:
        line.xs = [x / 3600 / GAME_SPEED for x in line.xs]

    return plot


def render_plot(plot: Plot, output: str | None = None):
    _, ax = plt.subplots(1, 1, figsize=(12, 10))

    colors = list(mcolors.TABLEAU_COLORS.values())

    for i, line in enumerate(plot.lines):
        label = f"{line.name}"
        if line.relative is not None:
            relative = (line.relative - 1)
            label += f"\n({relative:+.2%})"
        if line.roi is not None:
            label += f"\n[{line.roi:.5%}/stone]"
        ax.plot(
            line.xs,
            line.ys,
            label=label,
            color=colors[i % len(colors)],
            linewidth=2,
            marker="o",
            markersize=4,
        )

    if plot.bottom is not None:
        ax.set_ylim(bottom=plot.bottom)
    if plot.log_scale:
        ax.set_yscale("log")

    ax.set_xlabel(plot.xlabel)
    ax.set_ylabel(plot.ylabel)
    ax.set_title(plot.title)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output is not None:
        plt.savefig(output, dpi=300, bbox_inches="tight")
        print(f"Plot saved as {output}")

    plt.show()


# Subcommand implementations

def do_waves(args: argparse.Namespace) -> Plot:
    args.mastery = None
    convert_mastery_args(args)
    config = make_sim(args)

    sims = [
        waves_sim(config, max_wave) for max_wave in sorted(args.waves, reverse=True)
    ]
    sim_results = list(evaluate_sims(sims))

    title = ", ".join(
        [
            f"Simulating waves {', '.join(str(wave) for wave in args.waves)}",
            *mastery_args_description(args),
        ]
    )
    plot = plot_sim_results(title, sim_results)
    plot.log_scale = args.log_scale
    return plot


def do_tiers(args: argparse.Namespace) -> Plot:
    args.mastery = None
    convert_mastery_args(args)
    args.tiers.sort()
    config = make_sim(args)

    sims = [tiers_sim(config, tier, wave) for tier, wave in args.tiers]
    sim_results = list(evaluate_sims(sims))
    if args.relative:
        baseline_sim_result = max(sim_results, key=lambda x: x[1].wave_results[-1].elapsed_time)
        baseline_sim_name = baseline_sim_result[0].name
        sim_results = list(normalize_sims_vs_baseline(sim_results, baseline_sim_name))

    title = ", ".join(
        [
            f"Simulating tiers {', '.join(f'T{tier}:W{wave}' for tier, wave in args.tiers)}",
            *relative_args_description(args),
            *mastery_args_description(args),
        ]
    )
    plot = plot_sim_results(title, sim_results)
    plot.log_scale = args.log_scale
    if args.relative:
        plot.bottom = 0.99
    return plot


def do_compare(args: argparse.Namespace) -> Plot:
    args.level = mastery_level(args.level)
    convert_mastery_args(args)
    config = make_sim(args, args.wave)

    baseline_sim_name = "baseline"
    baseline_sim = dataclasses.replace(config, name=baseline_sim_name)

    sims = [baseline_sim] + [
        mastery_sim(config, mastery, args.level)
        for mastery in MASTERY_DISPLAY_NAMES.keys()
    ]
    sim_results = list(evaluate_sims(sims))
    if args.relative:
        sim_results = list(normalize_sims_vs_baseline(sim_results, baseline_sim_name))
        if args.roi:
            sim_results = list(normalize_sims_vs_stone_cost(sim_results))

    title = ", ".join(
        [
            f"Comparing masteries at level {args.level}",
            *relative_args_description(args),
            f"For {args.wave} waves",
        ]
    )
    plot = plot_sim_results(title, sim_results, truncate=True)
    plot.log_scale = args.log_scale
    if args.relative and not args.roi:
        plot.bottom = 0.99
    return plot


def do_mastery(args: argparse.Namespace) -> Plot:
    convert_mastery_args(args)
    config = make_sim(args, args.wave)

    sims = [mastery_sim(config, args.mastery, level) for level in MASTERY_LEVELS]
    baseline_sim_name = sims[0].name
    sim_results = list(evaluate_sims(sims))
    if args.relative:
        sim_results = list(normalize_sims_vs_baseline(sim_results, baseline_sim_name))

    title = ", ".join(
        [
            f"Comparing {MASTERY_DISPLAY_NAMES[args.mastery]}# levels",
            *relative_args_description(args),
            f"For {args.wave} waves",
            *mastery_args_description(args),
        ]
    )
    plot = plot_sim_results(title, sim_results, truncate=True)
    plot.log_scale = args.log_scale
    if args.relative:
        plot.bottom = 0.99
    return plot


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    # Simulate a sequence of waves with fixed mastery levels
    waves_subparser = subparsers.add_parser("waves")
    waves_subparser.add_argument(
        "waves",
        type=int,
        nargs="+",
        help="Sequence of wave numbers to simulate",
    )
    add_simulation_args(waves_subparser)
    add_mastery_args(waves_subparser)

    # Simulate a sequence of tier/wave pairs with fixed mastery levels
    tiers_subparser = subparsers.add_parser("tiers")
    tiers_subparser.add_argument(
        "tiers",
        type=tier_and_wave_arg,
        nargs="+",
        help="Sequence of tier/wave pairs to simulate",
    )
    add_relative_args(tiers_subparser)
    add_simulation_args(tiers_subparser)
    add_mastery_args(tiers_subparser)

    # Compare all masteries at a single level
    compare_subparser = subparsers.add_parser("compare")
    add_wave_args(compare_subparser)
    add_relative_args(compare_subparser)
    compare_subparser.add_argument(
        "--level",
        "-l",
        choices=MASTERY_LEVEL_NAMES,
        default="1",
        help="Compare all masteries at this level",
    )
    compare_subparser.add_argument(
        "--roi",
        action="store_true",
        help="Normalize all results against stone cost",
    )
    add_simulation_args(compare_subparser)
    add_mastery_args(compare_subparser)

    # Compare all levels of a single mastery
    mastery_subparser = subparsers.add_parser("mastery")
    add_wave_args(mastery_subparser)
    mastery_subparser.add_argument(
        "mastery",
        choices=MASTERY_DISPLAY_NAMES.keys(),
        help="Compare all mastery levels of this mastery",
    )
    add_relative_args(mastery_subparser)
    add_simulation_args(mastery_subparser)
    add_mastery_args(mastery_subparser)

    args = parser.parse_args()

    if not 0.0 <= args.orb_kills <= 1.0:
        parser.error("--orb-kills must be between 0.0 and 1.0")

    if args.subcommand == "waves":
        plot = do_waves(args)
    elif args.subcommand == "tiers":
        plot = do_tiers(args)
    elif args.subcommand == "compare":
        plot = do_compare(args)
    elif args.subcommand == "mastery":
        plot = do_mastery(args)
    else:
        parser.error(f"Invalid subcommand: {args.subcommand}")
    render_plot(plot, output=args.output)
