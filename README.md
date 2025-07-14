# Mastery Calculator

Compare cumulative coin earnings for card masteries in The Tower.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Compare different numbers of waves

```
./mastery_calc.py waves WAVES [ WAVES [ WAVES... ] ] \
    [ --tier=TIER ] [ --reward=( coins | cells | rerolls | modules ) ] \
    [ --orb-hits=ORB_HIT_RATIO ] [ (--output|-o)=OUTPUT_PNG_PATH ] \
    [ MASTERY_OPTIONS ]
```

### Compare different numbers of tier:wave pairs

```
./mastery_calc.py tiers TIER:WAVES [ TIER:WAVES [ TIER:WAVES... ] ] \
    [ --reward=( coins | cells | rerolls | modules ) ] \
    [ --orb-hits=ORB_HIT_RATIO ] [ (--output|-o)=OUTPUT_PNG_PATH ] \
    [ MASTERY_OPTIONS ]
```

### Compare all masteries at the same level

```
./mastery_calc.py compare WAVES \
    [ --tier=TIER ] [ --reward=( coins | cells | rerolls | modules ) ] \
    [ (--relative|-r) [ --roi ] ] [ (--level|-l)=MASTERIES_LEVEL ] \
    [ --orb-hits=ORB_HIT_RATIO ] [ (--output|-o)=OUTPUT_PNG_PATH ] \
    [ MASTERY_OPTIONS ]
```

### Compare a single mastery at all its levels

```
./mastery_calc.py mastery WAVES \
    [ --tier=TIER ] [ --reward=( coins | cells | rerolls | modules ) ] \
    [ (--relative|-r) ] MASTERY_NAME \
    [ --orb-hits=ORB_HIT_RATIO ] [ (--output|-o)=OUTPUT_PNG_PATH ] \
    [ MASTERY_OPTIONS ]
```

### Mastery options

The following options are accepted for `MASTERY_OPTIONS`:

```
[ --cash=CASH_MASTERY_LEVEL ]
[ --coin=COIN_MASTERY_LEVEL ]
[ --critical-coin=CRITICAL_COIN_MASTERY_LEVEL ]
[ --enemy-balance=ENEMY_BALANCE_MASTERY_LEVEL ]
[ --extra-orb=EXTRA_ORB_MASTERY_LEVEL ]
[ --intro-sprint=INTRO_SPRINT_MASTERY_LEVEL ]
[ --recovery-package=RECOVERY_PACKAGE_MASTERY_LEVEL \
[ --wake-skip=WAVE_SKIP_MASTERY_LEVEL ]
[ --wave-accelerator=WAVE_ACCELERATOR_MASTERY_LEVEL ]
```

Each mastery option accepts the values `locked`, or `0` through `9`. By default,
each option is `locked` if not specified.

## Examples

```bash
# Compare cumulative coin earnings from different length runs with a custom
# orb-hit guess. Render the result to a PNG file.
./mastery_calc.py waves 2000 4000 8000 --orb-hits=0.8 -o longer-runs.png

# Compare cumulative coin earnings from different length runs on different
# tiers.
./mastery_calc.py waves T10:2000 T6:4000 T2:8000

# Compare cumulative reroll earnings from each mastery at level 2 against a
# baseline of no masteries over a 10k wave run. Show results relative to the
# baseline, normalized by stone cost.
./mastery_calc.py compare 10000 --level=2 --relative --roi --reward=rerolls

# Compare cumulative coins earnings from each level of wave accelerator mastery
# over a 10k wave run with intro sprint mastery level set to 3. Show results
# relative to the baseline.
./mastery_calc.py mastery 10000 wave-accelerator --intro-sprint=3 --relative
```