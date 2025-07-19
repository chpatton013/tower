#!/usr/bin/env python3

import argparse
import os
import sys
import shlex
import subprocess
from multiprocessing import Pool
from typing import Iterator


def tiers(
    args: argparse.Namespace,
    tiers_sims: list[tuple[int, int]],
    reward: str,
    extra_name: str = "",
    extra_args: list[str] = [],
) -> list[str] | None:
    basename = [
        "tiers",
        reward,
        *[f"T{tier}W{wave}" for tier, wave in tiers_sims],
        *([extra_name] if extra_name else []),
        "dt",
    ]
    cmd = [
        "./mastery_calc.py",
        "tiers",
        *[f"{tier}:{wave}" for tier, wave in tiers_sims],
        f"--reward={reward}",
        "--elapsed",
        "--no-plot",
        "--no-print",
    ] + extra_args

    output = os.path.join(args.outputdir, "-".join(basename) + ".png")
    if os.path.exists(output) and not args.clobber:
        if args.ignore:
            print(f"{output} already exists, skipping...", file=sys.stderr)
            return None
        elif not args.clobber:
            print(f"{output} already exists, panic!", file=sys.stderr)
            raise FileExistsError(output)

    cmd.append(f"--output={output}")
    return cmd


def compare(
    args: argparse.Namespace,
    wave: int,
    tier: int,
    reward: str,
    level: int,
    extra_name: str = "",
    extra_args: list[str] = [],
) -> list[str] | None:
    basename = [
        "compare",
        reward,
        f"T{tier}W{wave}",
        f"L{level}",
        "rel",
        *([extra_name] if extra_name else []),
        "dt",
    ]
    cmd = [
        "./mastery_calc.py",
        "compare",
        str(wave),
        f"--tier={tier}",
        f"--reward={reward}",
        f"--level={level}",
        "--relative",
        "--elapsed",
        "--crop",
        "--no-plot",
        "--no-print",
    ] + extra_args

    output = os.path.join(args.outputdir, "-".join(basename) + ".png")
    if os.path.exists(output) and not args.clobber:
        if args.ignore:
            print(f"{output} already exists, skipping...", file=sys.stderr)
            return None
        elif not args.clobber:
            print(f"{output} already exists, panic!", file=sys.stderr)
            raise FileExistsError(output)

    cmd.append(f"--output={output}")
    return cmd


def generate_commands(args: argparse.Namespace) -> Iterator[list[str]]:
    def coins_extra_names(level: int) -> str:
        return "-".join([f"{m}{level}" for m in ["WA"]])

    def coins_extra_args(level: int) -> list[str]:
        return [f"--{m}={level}" for m in ["wave-accelerator"]]

    def rerolls_extra_names(level: int) -> str:
        return "-".join([f"{m}{level}" for m in ["Cash", "EB"]])

    def rerolls_extra_args(level: int) -> list[str]:
        return [f"--{m}={level}" for m in ["cash", "enemy-balance"]]

    tiers_sims = [(11, 10000), (12, 6000), (13, 5000), (14, 3500)]
    commands = [
        tiers(
            args,
            tiers_sims,
            "coins",
            extra_name=coins_extra_names(0),
            extra_args=coins_extra_args(0),
        ),
        tiers(
            args,
            tiers_sims,
            "coins",
            extra_name=coins_extra_names(2),
            extra_args=coins_extra_args(2),
        ),
        tiers(
            args,
            tiers_sims,
            "coins",
            extra_name=coins_extra_names(9),
            extra_args=coins_extra_args(9),
        ),
        tiers(args, tiers_sims, "cells"),
        tiers(
            args,
            tiers_sims,
            "rerolls",
            extra_name=rerolls_extra_names(0),
            extra_args=rerolls_extra_args(0),
        ),
        tiers(
            args,
            tiers_sims,
            "rerolls",
            extra_name=rerolls_extra_names(9),
            extra_args=rerolls_extra_args(9),
        ),
        compare(args, 10000, 11, "cells", 0),
        compare(args, 10000, 11, "cells", 2),
        compare(args, 10000, 11, "cells", 9),
        compare(args, 10000, 11, "coins", 0),
        compare(args, 10000, 11, "coins", 0, extra_name="roi", extra_args=["--roi"]),
        compare(args, 10000, 11, "coins", 2),
        compare(args, 10000, 11, "coins", 2, extra_name="roi", extra_args=["--roi"]),
        compare(args, 10000, 11, "coins", 9),
        compare(args, 10000, 11, "coins", 9, extra_name="roi", extra_args=["--roi"]),
        compare(args, 10000, 11, "rerolls", 0),
        compare(
            args,
            10000,
            11,
            "rerolls",
            0,
            extra_name="Cash0",
            extra_args=["--rerolls-with-cash=0"],
        ),
        compare(
            args,
            10000,
            11,
            "rerolls",
            2,
            extra_name="Cash0",
            extra_args=["--rerolls-with-cash=0"],
        ),
        compare(args, 10000, 11, "modules", 0),
        compare(args, 3500, 14, "cells", 0),
        compare(args, 3500, 14, "cells", 2),
        compare(args, 3500, 14, "cells", 9),
        compare(args, 3500, 14, "coins", 0),
        compare(args, 3500, 14, "coins", 0, extra_name="roi", extra_args=["--roi"]),
        compare(args, 3500, 14, "coins", 2),
        compare(args, 3500, 14, "coins", 2, extra_name="roi", extra_args=["--roi"]),
        compare(args, 3500, 14, "coins", 9),
        compare(args, 3500, 14, "coins", 9, extra_name="roi", extra_args=["--roi"]),
        compare(args, 3500, 14, "rerolls", 0),
        compare(
            args,
            3500,
            14,
            "rerolls",
            0,
            extra_name="Cash0",
            extra_args=["--rerolls-with-cash=0"],
        ),
        compare(
            args,
            3500,
            14,
            "rerolls",
            2,
            extra_name="Cash0",
            extra_args=["--rerolls-with-cash=0"],
        ),
        compare(args, 3500, 14, "modules", 0),
    ]

    yield from [cli for cli in commands if cli is not None]


def process_command(command: list[str]) -> None:
    print(shlex.join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("outputdir")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--ignore", action="store_true", default=False)
    g.add_argument("--clobber", action="store_true", default=False)
    args = parser.parse_args()

    try:
        pool = Pool()
        pool.map(process_command, generate_commands(args))
    finally:
        pool.close()
        pool.join()
