#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
from multiprocessing import Pool
from typing import Iterator

from mastery_calc import MASTERY_LEVEL_NAMES, MASTERY_DISPLAY_NAMES, TIERS, REWARD_NAMES


def mastery_basename(
    wave: int, mastery: str, tier: int, reward: str, relative: bool
) -> str:
    return (
        "_".join(
            [
                "mastery",
                f"W{wave}",
                f"M{mastery}",
                f"T{tier}",
                f"R{reward}",
                *(["relative"] if relative else []),
            ]
        )
        + ".png"
    )


def mastery_command(
    output: str,
    wave: int,
    mastery: str,
    tier: int,
    reward: str,
    relative: bool,
    extra_args: list[str],
) -> list[str]:
    return [
        "./mastery_calc.py",
        "mastery",
        str(wave),
        mastery,
        "--tier",
        str(tier),
        "--reward",
        reward,
        *(["--relative"] if relative else []),
        "--no-plot",
        "--no-print",
        "-o",
        output,
        *extra_args,
    ]


def compare_basename(
    wave: int, tier: int, level: str, reward: str, relative: bool, roi: bool
) -> str:
    return (
        "_".join(
            [
                "compare",
                f"W{wave}",
                f"T{tier}",
                f"L{level}",
                f"R{reward}",
                *(["relative"] if relative else []),
                *(["roi"] if roi else []),
            ]
        )
        + ".png"
    )


def compare_command(
    output: str,
    wave: int,
    tier: int,
    level: str,
    reward: str,
    relative: bool,
    roi: bool,
    extra_args: list[str],
) -> list[str]:
    return [
        "./mastery_calc.py",
        "compare",
        str(wave),
        "--tier",
        str(tier),
        "--level",
        level,
        "--reward",
        reward,
        *(["--relative"] if relative else []),
        *(["--roi"] if roi else []),
        "--no-plot",
        "--no-print",
        "-o",
        output,
        *extra_args,
    ]


def generate_compare_commands(
    outputdir: str, wave: int, extra_args: list[str]
) -> Iterator[list[str]]:
    for level in MASTERY_LEVEL_NAMES:
        for tier in TIERS:
            for reward in REWARD_NAMES:
                for rel, roi in [(False, False), (True, False), (True, True)]:
                    basename = compare_basename(wave, tier, level, reward, rel, roi)
                    output = os.path.join(outputdir, basename)
                    if not os.path.exists(output) or not args.clobber:
                        yield compare_command(
                            output, wave, tier, level, reward, rel, roi, extra_args
                        )


def generate_mastery_commands(
    outputdir: str, wave: int, extra_args: list[str]
) -> Iterator[list[str]]:
    for mastery in MASTERY_DISPLAY_NAMES:
        for tier in TIERS:
            for reward in REWARD_NAMES:
                for rel in [False, True]:
                    basename = mastery_basename(wave, mastery, tier, reward, rel)
                    output = os.path.join(outputdir, basename)
                    if not os.path.exists(output) or not args.clobber:
                        yield mastery_command(
                            output, wave, mastery, tier, reward, rel, extra_args
                        )


def process_command(command: list[str]) -> None:
    print(shlex.join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("outputdir")
    parser.add_argument("--wave", default=10000)
    parser.add_argument(
        "--no-clobber", dest="clobber", action="store_false", default=True
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--all", dest="all", action="store_true", default=False)
    g.add_argument("--compare-only", dest="compare", action="store_true", default=False)
    g.add_argument("--mastery-only", dest="mastery", action="store_true", default=False)
    args, unknown = parser.parse_known_args()
    if args.all:
        args.compare = True
        args.mastery = True

    try:
        pool = Pool()
        if args.compare:
            pool.map(process_command, generate_compare_commands(args.outputdir, args.wave, unknown))
        if args.mastery:
            pool.map(process_command, generate_mastery_commands(args.outputdir, args.wave, unknown))
    finally:
        pool.close()
        pool.join()
