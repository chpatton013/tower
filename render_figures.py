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
        return "-".join([f"{m}{level}" for m in ["IS", "WA"]])

    def coins_extra_args(level: int) -> list[str]:
        return [f"--{m}={level}" for m in ["intro-sprint", "wave-accelerator"]]

    def cells_extra_names(level: int) -> str:
        return "-".join([f"{m}{level}" for m in ["IS", "EB"]])

    def cells_extra_args(level: int) -> list[str]:
        return [f"--{m}={level}" for m in ["intro-sprint", "enemy-balance"]]

    def rerolls_extra_names(level: int) -> str:
        return "-".join([f"{m}{level}" for m in ["Cash", "EB"]])

    def rerolls_extra_args(level: int) -> list[str]:
        return [f"--{m}={level}" for m in ["cash", "enemy-balance"]]

    def modules_extra_names(level: int) -> str:
        return "-".join([f"{m}{level}" for m in ["IS", "RPC"]])

    def modules_extra_args(level: int) -> list[str]:
        return [f"--{m}={level}" for m in ["intro-sprint", "recovery-package"]]

    tiers_sims = {11: 10000, 12: 8000, 13: 6000, 14: 4000}
    gt_sims = {0: "000", 0.15: "015", 0.30: "030", 0.45: "045"}
    bhd_sims = {0: "0", 3: "3", 5: "5", 7: "7", 10: "10"}
    commands = [
        tiers(args, list(tiers_sims.items()), "coins"),
        tiers(args, list(tiers_sims.items()), "coins", extra_name=coins_extra_names(0), extra_args=coins_extra_args(0)),
        tiers(args, list(tiers_sims.items()), "coins", extra_name=coins_extra_names(9), extra_args=coins_extra_args(9)),
        tiers(args, list(tiers_sims.items()), "cells"),
        tiers(args, list(tiers_sims.items()), "cells", extra_name=cells_extra_names(0), extra_args=cells_extra_args(0)),
        tiers(args, list(tiers_sims.items()), "cells", extra_name=cells_extra_names(9), extra_args=cells_extra_args(9)),
        tiers(args, list(tiers_sims.items()), "rerolls"),
        tiers(args, list(tiers_sims.items()), "rerolls", extra_name=rerolls_extra_names(0), extra_args=rerolls_extra_args(0)),
        tiers(args, list(tiers_sims.items()), "rerolls", extra_name=rerolls_extra_names(9), extra_args=rerolls_extra_args(9)),
        tiers(args, list(tiers_sims.items()), "modules"),
        tiers(args, list(tiers_sims.items()), "modules", extra_name=modules_extra_names(0), extra_args=modules_extra_args(0)),
        tiers(args, list(tiers_sims.items()), "modules", extra_name=modules_extra_names(9), extra_args=modules_extra_args(9)),
    ]
    for level in [2, 9]:
        for gt, gt_name in gt_sims.items():
            bhd = 7
            bhd_name = bhd_sims[bhd]
            commands += [
                compare(args, tiers_sims[11], 11, "coins", level, extra_name=f"gt{gt_name}-roi", extra_args=[f"--golden-combo={gt}", "--roi"]),
                compare(args, tiers_sims[14], 14, "coins", level, extra_name=f"gt{gt_name}-roi-noIS", extra_args=[f"--golden-combo={gt}", "--roi", "--omit=intro-sprint"]),
                compare(args, tiers_sims[11], 11, "coins", level, extra_name=f"bhd{bhd_name}-gt{gt_name}-roi", extra_args=[f"--bhd={bhd}", f"--golden-combo={gt}", "--roi"]),
                compare(args, tiers_sims[14], 14, "coins", level, extra_name=f"bhd{bhd_name}-gt{gt_name}-roi", extra_args=[f"--bhd={bhd}", f"--golden-combo={gt}", "--roi"]),
                compare(args, tiers_sims[14], 14, "coins", level, extra_name=f"bhd{bhd_name}-gt{gt_name}-roi-noIS", extra_args=[f"--bhd={bhd}", f"--golden-combo={gt}", "--roi", "--omit=intro-sprint"]),
            ]
    for tier in [11, 14]:
        for level in [2, 9]:
            for bhd, bhd_name in bhd_sims.items():
                commands += [
                    compare(args, tiers_sims[tier], tier, "coins", level, extra_name=f"bhd{bhd_name}-roi", extra_args=[f"--bhd={bhd}", "--roi"]),
                    compare(args, tiers_sims[tier], tier, "coins", level, extra_name=f"bhd{bhd_name}-roi-noIS", extra_args=[f"--bhd={bhd}", "--roi", "--omit=intro-sprint"]),
                ]
        for level in [0, 4, 9]:
            commands += [
                compare(args, tiers_sims[tier], tier, "cells", level),
                compare(args, tiers_sims[tier], tier, "coins", level),
                compare(args, tiers_sims[tier], tier, "coins", level, extra_name="roi", extra_args=["--roi"]),
                compare(args, tiers_sims[tier], tier, "coins", level, extra_name="roi-noIS", extra_args=["--roi", "--omit=intro-sprint"]),
                compare(args, tiers_sims[tier], tier, "rerolls", level),
                compare(args, tiers_sims[tier], tier, "rerolls", level, extra_name="Cash0", extra_args=["--rerolls-with-cash=0"]),
                compare(args, tiers_sims[tier], tier, "modules", level),
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
