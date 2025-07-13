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
    [ --orb-hits=ORB_HIT_RATIO ] [ (--output|-o)=OUTPUT_PNG_PATH ] \
    [ MASTERY_OPTIONS ]
```

### Compare all masteries at the same level

```
./mastery_calc.py compare \
    [ (--relative|-r) ] [ (--level|-l)=MASTERIES_LEVEL ] \
    [ --orb-hits=ORB_HIT_RATIO ] [ (--output|-o)=OUTPUT_PNG_PATH ] \
    [ MASTERY_OPTIONS ]
```

### Compare a single mastery at all its levels

```
./mastery_calc.py mastery \
    [ (--relative|-r) ] MASTERY_NAME \
    [ --orb-hits=ORB_HIT_RATIO ] [ (--output|-o)=OUTPUT_PNG_PATH ] \
    [ MASTERY_OPTIONS ]
```

### Mastery options

The following options are accepted for `MASTERY_OPTIONS`:

```
[ --coin=COIN_MASTERY_LEVEL ]
[ --extra-orb=EXTRA_ORB_MASTERY_LEVEL ]
[ --critical-coin=CRITICAL_COIN_MASTERY_LEVEL ]
[ --wake-skip=WAVE_SKIP_MASTERY_LEVEL ]
[ --intro-sprint=INTRO_SPRINT_MASTERY_LEVEL ]
[ --wave-accelerator=WAVE_ACCELERATOR_MASTERY_LEVEL ]
```

Each mastery option accepts the values `locked`, or `0` through `9`. By default,
each option is `locked` if not specified.

## Examples

```bash
# Compare cumulative earnings from different length runs with a custom orb-hit
# guess. Render the result to a PNG file.
./mastery_calc.py waves 2000 4000 8000 --orb-hits=0.8 -o longer-runs.png

# Compare cumulative earnings from each mastery at level 2 against a baseline of
# no masteries over a 10k wave run. Show results relative to the baseline.
./mastery_calc.py compare 10000 --level=2 --relative

# Compare cumulative earnings from each level of wave accelerator mastery over a
# 10k wave run with intro sprint mastery level set to 3. Show results relative
# to the baseline.
./mastery_calc.py mastery 10000 wave-accelerator --intro-sprint=3 --relative
```