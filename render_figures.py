#!/usr/bin/env python3

import argparse
import os
import sys
import shlex
import subprocess
from multiprocessing import Pool
from typing import Iterator


def generate_tiers_command(
    args: argparse.Namespace,
    tiers: list[tuple[int, int]],
    reward: str,
    extra_name: str = "",
    extra_args: list[str] = [],
) -> list[str] | None:
    basename = [
        "tiers",
        *[f"T{tier}W{wave}" for tier, wave in tiers],
        f"R{reward}",
        *([extra_name] if extra_name else []),
    ]
    cmd = [
        "./mastery_calc.py",
        "tiers",
        *[f"{tier}:{wave}" for tier, wave in tiers],
        f"--reward={reward}",
        "--no-plot",
        "--no-print",
    ]

    output = os.path.join(args.outputdir, "_".join(basename) + ".png")
    if os.path.exists(output) and not args.clobber:
        if args.ignore:
            print(f"{output} already exists, skipping...", file=sys.stderr)
            return None
        elif not args.clobber:
            print(f"{output} already exists, panic!", file=sys.stderr)
            raise FileExistsError(output)

    cmd.append(f"--output={output}")
    cmd.extend(extra_args)
    return cmd


def generate_compare_command(
    args: argparse.Namespace,
    level: str,
    reward: str,
    rel: bool,
    roi: bool,
    extra_name: str = "",
    extra_args: list[str] = [],
) -> list[str] | None:
    basename = [
        "compare",
        f"W{args.wave}",
        f"T{args.tier}",
        f"L{level}",
        f"R{reward}",
        *([extra_name] if extra_name else []),
    ]
    cmd = [
        "./mastery_calc.py",
        "compare",
        str(args.wave),
        f"--tier={args.tier}",
        f"--level={level}",
        f"--reward={reward}",
        "--no-plot",
        "--no-print",
    ]

    if rel:
        basename.append("relative")
        cmd.append("--relative")
    if roi:
        basename.append("roi")
        cmd.append("--roi")

    output = os.path.join(args.outputdir, "_".join(basename) + ".png")
    if os.path.exists(output) and not args.clobber:
        if args.ignore:
            print(f"{output} already exists, skipping...", file=sys.stderr)
            return None
        elif not args.clobber:
            print(f"{output} already exists, panic!", file=sys.stderr)
            raise FileExistsError(output)

    cmd.append(f"--output={output}")
    cmd.extend(extra_args)
    return cmd


def generate_mastery_command(
    args: argparse.Namespace,
    mastery: str,
    reward: str,
    rel: bool,
    extra_name: str = "",
    extra_args: list[str] = [],
) -> list[str] | None:
    basename = [
        "mastery",
        f"W{args.wave}",
        f"M{mastery}",
        f"T{args.tier}",
        f"R{reward}",
        *([extra_name] if extra_name else []),
    ]
    cmd = [
        "./mastery_calc.py",
        "mastery",
        str(args.wave),
        mastery,
        f"--tier={args.tier}",
        f"--reward={reward}",
        "--no-plot",
        "--no-print",
    ]

    if rel:
        basename.append("relative")
        cmd.append("--relative")

    output = os.path.join(args.outputdir, "_".join(basename) + ".png")
    if os.path.exists(output) and not args.clobber:
        if args.ignore:
            print(f"{output} already exists, skipping...", file=sys.stderr)
            return None
        elif not args.clobber:
            print(f"{output} already exists, panic!", file=sys.stderr)
            raise FileExistsError(output)

    cmd.append(f"--output={output}")
    cmd.extend(extra_args)
    return cmd


def generate_commands(
    args: argparse.Namespace, extra_args: list[str] = []
) -> Iterator[list[str]]:
    tiers_sims = [(11, 10000), (12, 6000), (13, 5000), (14, 3500)]
    rel_roi = [(False, False), (True, False), (True, True)]
    coin_masteries = [
        "coin",
        "critical-coin",
        "enemy-balance",
        "extra-orb",
        "intro-sprint",
        "wave-accelerator",
        "wave-skip",
    ]
    cell_masteries = [
        "enemy-balance",
        "intro-sprint",
        "wave-accelerator",
        "wave-skip",
    ]
    reroll_masteries = [
        "enemy-balance",
        "intro-sprint",
        "wave-accelerator",
        "wave-skip",
    ]
    module_masteries = [
        "intro-sprint",
        "recovery-package",
        "wave-accelerator",
        "wave-skip",
    ]

    commands = []
    commands.extend(
        generate_tiers_command(
            args,
            tiers_sims,
            reward,
            extra_name=f"WA{level}",
            extra_args=[f"--wave-accelerator={level}", *extra_args],
        )
        for level in args.levels
        for reward in ["coins", "cells"]
    )
    commands.extend(
        generate_compare_command(args, level, "coins", rel, roi, extra_args=extra_args)
        for level in args.levels
        for rel, roi in rel_roi
    )
    commands.extend(
        generate_mastery_command(args, mastery, "coins", rel, extra_args=extra_args)
        for mastery in coin_masteries
        for rel in [False, True]
    )
    commands.extend(
        generate_mastery_command(args, mastery, "cells", rel, extra_args=extra_args)
        for mastery in cell_masteries
        for rel in [False, True]
    )
    commands.extend(
        generate_mastery_command(
            args,
            mastery,
            "rerolls",
            rel,
            extra_name=f"Cash{cash}",
            extra_args=[f"--cash={cash}", *extra_args],
        )
        for mastery in reroll_masteries
        for rel in [False, True]
        for cash in args.levels
    )
    commands.extend(
        generate_mastery_command(args, mastery, "modules", rel, extra_args=extra_args)
        for mastery in module_masteries
        for rel in [False, True]
    )

    yield from [cli for cli in commands if cli is not None]


def process_command(command: list[str]) -> None:
    print(shlex.join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("outputdir")
    parser.add_argument("--tier", default=11)
    parser.add_argument("--wave", default=10000)
    parser.add_argument("--levels", nargs="+", default=["0", "2", "9"])
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--ignore", action="store_true", default=False)
    g.add_argument("--clobber", action="store_true", default=False)
    args, unknown = parser.parse_known_args()

    try:
        pool = Pool()
        pool.map(process_command, generate_commands(args, unknown))
    finally:
        pool.close()
        pool.join()
