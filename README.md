# Mastery Calculator

Calculate the effects of card masteries on cumulative run rewards.

## Usage

### Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Generate interesting figures

```
rm -rf ./figures
mkdir ./figures
./render_figures ./figures
```

### Compare different tier:wave combinations

```
./mastery_calc.py tiers TIER:WAVES [ TIER:WAVES... ] [ COMMON_OPTIONS ]
```

### Compare all masteries at the same level

```
./mastery_calc.py compare WAVES [ (--level|-l)=MASTERIES_LEVEL ] [ COMMON_OPTIONS ]
```

### Compare a single mastery at all its levels

```
./mastery_calc.py mastery WAVES MASTERY_NAME [ COMMON_OPTIONS ]
```

### Common option groups

The following options are accepted for `COMMON_OPTIONS`:

Simulation events
```
[ --tier=TIER ] # Which tier to simulate
[ --orb-hits=ORB_HIT_RATIO ] # Portion of enemies struck by orbs
```
Tier must be between 1-18, and orb hits must be between 0-1. Both default to 1
if not specified.

Reward normalization
```
[ --reward=( coins | cells | rerolls | modules ) ]
[ --elapsed ]         # Normalize rewards vs elapsed time
[ (--relative|-r) ]   # Divide by baseline values
[ --roi ]             # Divide by stone cost
[ (--difference|-d) ] # Subtract baseline values
```

Output options
```
[ --truncate ] # Truncate horizontally to shortest run
[ --crop ]     # Crop vertically to exclude outliers
[ --no-print ] # Do not print results
[ --no-plot ]  # Do not plot results
[ (--output|-o)=OUTPUT_PNG_PATH ] # Render plot to file
```

Mastery levels
```
[ --cash=CASH_MASTERY_LEVEL ]
[ --coin=COIN_MASTERY_LEVEL ]
[ --critical-coin=CRITICAL_COIN_MASTERY_LEVEL ]
[ --enemy-balance=ENEMY_BALANCE_MASTERY_LEVEL ]
[ --extra-orb=EXTRA_ORB_MASTERY_LEVEL ]
[ --intro-sprint=INTRO_SPRINT_MASTERY_LEVEL ]
[ --recovery-package=RECOVERY_PACKAGE_MASTERY_LEVEL ]
[ --wake-skip=WAVE_SKIP_MASTERY_LEVEL ]
[ --wave-accelerator=WAVE_ACCELERATOR_MASTERY_LEVEL ]
```
Each mastery level accepts the values `locked`, or `0` through `9`. By default,
each option is `locked` if not specified.

## Examples

```bash
# Compare cumulative coin earnings from different length runs on different
# tiers with a custom orb-hit guess. Render the result to PNG file.
./mastery_calc.py waves T10:2000 T6:4000 T2:8000 --orb-hits=0.8 -o plot.png

# Compare cumulative reroll earnings from each mastery at level 2 against a
# baseline of no masteries over a 10k wave run. Show results relative to the
# baseline, normalized by stone cost.
./mastery_calc.py compare 10000 --level=2 --relative --roi --reward=rerolls

# Compare cumulative coins earnings from each level of wave accelerator mastery
# over a 10k wave run with intro sprint mastery level set to 3. Show results
# relative to the baseline.
./mastery_calc.py mastery 10000 wave-accelerator --intro-sprint=3 --relative
```

## Results summary

> tl;dr: RPC#, Cash#, EB#, and EO#; followed by WS# and WA#

To determine which mastery has the best impact on your economy per stone spent,
you have to compare each reward you care about farming under different length
and difficulty configurations. We'll summarize the long and short farm run
configurations, and then look at whether short farm runs on higher tiers are
feasible with WA#.

Figures
- [relative coins per hour from all masteries at level 0](./figures/compare-coins-T11W10000-L0-rel-dt.png)
- [relative coins per hour per stone from all masteries at level 0](./figures/compare-coins-T11W10000-L0-rel-roi-dt.png)
- [relative coins per hour from all masteries at level 2](./figures/compare-coins-T11W10000-L2-rel-dt.png)
- [relative coins per hour per stone from all masteries at level 2](./figures/compare-coins-T11W10000-L2-rel-roi-dt.png)
- [relative coins per hour from all masteries at level 9](./figures/compare-coins-T11W10000-L9-rel-dt.png)
- [relative coins per hour per stone from all masteries at level 9](./figures/compare-coins-T11W10000-L9-rel-roi-dt.png)
- [relative cells per hour from all masteries at level 0](./figures/compare-cells-T11W10000-L0-rel-dt.png)
- [relative cells per hour from all masteries at level 2](./figures/compare-cells-T11W10000-L2-rel-dt.png)
- [relative cells per hour from all masteries at level 9](./figures/compare-cells-T11W10000-L9-rel-dt.png)
- [relative modules per hour from all masteries at level 0](./figures/compare-modules-T11W10000-L0-rel-dt.png)
- [relative rerolls per hour from all masteries at level 0](./figures/compare-rerolls-T11W10000-L0-rel-dt.png)
- [relative rerolls per hour from all masteries at level 0 with Cash# at level 0](./figures/compare-rerolls-T11W10000-L0-rel-Cash0-dt.png)
- [relative rerolls per hour from all masteries at level 2 with Cash# at level 0](./figures/compare-rerolls-T11W10000-L2-rel-Cash0-dt.png)
- [coins between T11-T14 with WA# at level 0](./figures/tiers-coins-T11W10000-T12W6000-T13W5000-T14W3500-WA0-dt.png)
- [coins between T11-T14 with WA# at level 0](./figures/tiers-coins-T11W10000-T12W6000-T13W5000-T14W3500-WA2-dt.png)
- [coins between T11-T14 with WA# at level 0](./figures/tiers-coins-T11W10000-T12W6000-T13W5000-T14W3500-WA9-dt.png)
- [cells between T11-T14](./figures/tiers-cells-T11W10000-T12W6000-T13W5000-T14W3500-dt.png)
- [rerolls between T11-T14 with Cash# at level 0](./figures/tiers-rerolls-T11W10000-T12W6000-T13W5000-T14W3500-Cash0-EB0-dt.png)
- [rerolls between T11-T14 with Cash# at level 9](./figures/tiers-rerolls-T11W10000-T12W6000-T13W5000-T14W3500-Cash9-EB9-dt.png)

### Long farm run

Configuration
- T11 W10k
- Relative comparison of all masteries
- Normalized against elapsed time
- Compared per stone cost of mastery
- Assume orbs hit all enemies

Results
- Coins:
  - Level 0: EO# >> WS# >= WA# >= Coin# >> CritCoin# >= IS#
  - Level 2: EO# >> Coin# >= WA# >= WS# > IS# >= CritCoin#
  - Level 9: EO# >> Coin# > WS# >= WA# > IS# >= CritCoin#

- Elite cells:
  - Level 0: EB# > WS# > IS#
  - Level 2: EB# > WS# >= IS#
  - Level 9: EB# > IS# >= WS#

- Reroll shards:
  - If you assume you already have Cash#0:
    - Level 0: WS# > EB# > IS#
    - Level 2: Cash# > WS# > EB# > IS#
  - If you don't assume Cash#0:
    - Level 2: Cash# > WS# > Baseline >= IS#

- Module shards:
  - Level 0: RPC# >> WS# > Baseline >= IS#

### Short farm run

Configuration
- Same as long farm run, except T11 W5k

Results
- Coins:
  - Level 0: EO# > WA# > WS# > Coin# >> IS# >= CritCoin#
  - Level 2: EO# > WA# >> Coin# > WS# > IS# > CritCoin#
  - Level 9: EO# >> WA# > Coin# > WS# >= IS# > CritCoin#

- Elite cells:
  - Level 0: Same as long run
  - Level 2: EB# >= IS# > WS#
  - Level 9: EB# = IS# >= WS#

- Reroll shards:
  - Same as long run

- Module shards:
  - Same as long run

### Higher tiers

Configuration
- Relative comparison of all difficulties
  - Assume my own farm stats: T11W10000, T12W6000, T13W5000, T14W3500
- Varying WA#, Cash#, and EB#
- Normalized against elapsed time
- Assume orbs hit all enemies

Results:
- Coins:
  - WA# at level 0:
    - T12: Same as T11
    - T13: +11% from T11
    - T14: +16% from T11
  - WA# at level 2:
    - T12: +3% from T11
    - T13: +15% from T11
    - T14: +20% from T11
  - WA# at level 9:
    - T12: +9% from T11
    - T13: +26% from T11
    - T14: +33% from T11
- Cells: About a 10-20% reduction on higher tiers
  - T12: -20% from T11
  - T13: -20% from T11
  - T14: -10% from T11
- Rerolls:
  - Cash# and EB# at level 0:
    - T12: +8% from T11
    - T13: +20% from T11
    - T14: +40% from T11
  - Cash# and EB# at level 9:
    - T12: -7% from T11
    - T13: -2% from T11
    - T14: -4% from T11
- Modules: No variance

### Analysis

Coin gain from WA# in higher tiers doesn't exceed the benefits of Coin# unless
farming at T13. For example, comparing WA#0 to Coin#0 at T13: +11% vs +3%.
However, cell income is dropped by 20% for that configuration, so this is only
a viable option for people who can afford to deprioritize cell income.

If you could only pick four, RPC#, Cash#, EB#, and EO# are each best in their
respective classes. WS# and WA# share the honorable mention slot for their
versatility.

## Estimation methodology

Runs are simulated sequences of waves, emitting events as probabilities. Rewards
are calculated each wave by multiplying the event probabilities to the results
of encountering each event. Rewards are accumulated over the run and tracked as
cumulative values per-wave.

Results for different simulation configurations can
be directly compared and plotted against each other, either as absolute values,
normalized values relative to a baseline simulation, or the difference of values
from the target simulation and the baseline simulation. Relative values can
further be normalized against the stone-cost of their mastery.

This tool should produce accurate estimates of the instances of each event if
compared to real runs of the game. However, the rewards for those events are not
expected to be accurate relative to the real game. They are instead expected to
be accurate relative to each other ("internally consistent"). This is because
the tool does not model the effects of certain multipliers or effects that apply
consistently across a run. For example, econ-based UW bonus and uptime provide a
consistent boost to rewards when they apply, and over a long-enough run, they
will apply to a statistically consistent portion of the run. Factoring them in
would therefore have no effect on the relative benefits of different masteries,
and so is not beneficial to model.

### Known limitations

- Waves are modeled atomically, assuming that all enemies spawned in the wave
  are killed during that wave, and that no enemy lives long enough to have its
  coin rewards reduced by staleness.

### Bugs

- BHD's interaction with free upgrade count is not modeled.
- GT+'s interaction with enemy spawn count is not modeled.

### Future work

- Add a "difficulty" simulation type that models the expected maximum wave count
  you can reach across different tiers based on your highest wave on a baseline
  tier. Factor in enemy level skips and enemy health/attack scaling across
  tiers, assuming that reaching the same aggregate level of enemy health/attack
  will terminate the run at each tier. Consider the number of enemy spawns to
  calculate this aggregate value.

## Validation strategy

Lacking a mechanism to scientifically compare results of gameplay with different
mastery configurations or ground-truth data from the developer, our ability to
validate simulation results is limited to comparison of each configuration
against the integral of model equations. Deriving these functions requires
analysis of the sources of each in-game reward and the probabilities of the
events that yield them.

While the graph of the total rewards earned with a given configuration can
sometimes show the impact of a mastery, it is often more beneficial to graph the
quotient of relative rewards between mastery and baseline plots, or the
difference between them.

### Modeling techniques

Simulation of each wave produces a vector of probabilistic events and a
resulting vector of rewards derived from those events. Results from each wave
are summed over the course of the run, thereby approximating the integral of the
per-wave rewards. The limits of integration are the waves simulated.
We make the following definitions:
- `e(w)`: the function of event probability vectors for a given wave `w`
- `r(w)`: the function of per-event rewards for a given wave `w`
- `e(w) * r(w)`: the piecewise product of event probability and event rewards
- `f(w)`: `e(w) * r(w)`
Then the cumulative reward is `∫{a,b} f(w) dw`

However, our goal is to model rewards with respect to time, not waves. So we
have to transform from any given range of time to the corresponding range of
waves. The limits of integration are the time points of the wave simulated.
- `t(w)`: the function transforming wave numbers to time points
- `w(t)`: the function transforming time points to wave numbers
- `e(t)`: `e(w(t))`
- `r(t)`: `r(w(t))`
- `f(t)`: `e(t) * r(t)`
Then the cumulative reward is `∫{a,b} f(t) dt`

Masteries produce altered versions of the above functions. To demonstrate the
impact each mastery should have, we first have to define these functions for the
baseline configuration with no masteries. Then we can highlight per-mastery
differences, and derive the expected mastery models.

## Estimation models

- During intro sprint, waves advance at 10x the speed via repeated 9x wave skips
  and reward drop rates are altered.
  - Intro sprint lasts until wave `100`, unless extended by IS#.
  - Intro sprint is modeled as a piecewise function with separate domains from
    waves `[1,100)` to `[100,+inf)`:
    - `t(w) = w|{0,100}:0.1; {100,*}:1| * (WaveDuration + WaveCooldown)`
    - `w(t) = t|{0,t(100)}:10; {t(100),*}:1| / (WaveDuration + WaveCooldown)`
    - `f(w) = e(w) * w|{0,100}:IS_Factor; {100,*}:1| * r(w)`
- Wave skip reduces the amount of time spent on a wave to 0, and alters the
  rewards from a wave to the scaled value of rewards of the previous wave.
  - Wave skip is modeled as:
    - a constant scale factor to `w(t)` (by default, 0.19, but increased by WS#)
      - `w(t) = (WaveDuration + WaveCooldown) * (1 - WS_Chance)`
    - an interpolation by that scale factor between the current wave's rewards
      and a scaled value of the previous wave's rewards; if we assume those are
      approximately equal:
      - `f(w) = (1 - WS_Chance) * (e(w) * r(w)) + WS_Chance * (e(w) * r(w)) * WS_Bonus
      - `f(w) = e(w) * r(w) * (1 + WS_Chance * (WS_Bonus - 1))

### Coins

Coins are dropped by all enemies except bosses.

- `e(w) = w|{0,100}:0.1; {100,*}:1.0| * <BasicSpawnChance(w),...,EliteSpawnChance(w)>`
- `r(w) = w|{0,100}:0; {100,*}:1| * <0.33,...,4.0>`

Masteries that affect coin income are Coin#, CritCoin#, EB#, EO#, IS#, WA#, and
WS#.

#### Coin#

Coin# increases all coin rewards:
- `r'(w) = w|{0,100}:0; {100,*}:1| * <0.33,...,4.0> * Coin#`

This results in a linear increase in coin income:
- Absolute: the exponential and linear components of the curve have higher
  coefficients, scaling them vertically
- Relative: the ratio to baseline is a constant, which make horizontal lines of
  form `y = k * Coin#`
- Difference: the difference between functions accelerates towards a linear
  equation of the form `y = k * Coin# * t`

#### CritCoin#

CritCoin# increases coin rewards for basic enemies:
- `r'(w) = w|{0,100}:0; {100,*}:1| * <0.33,...,4.0> * <CritCoin#,...,1>`

This results in a linear increase in coin income:
- Absolute: the curve is translated in y+
- Relative: the ratio to baseline is a positive horizontal asymptote decreasing
  toward the line `y = k * CritCoin#`
- Difference: the difference between functions is a linear equation of the form
  `y = k * CritCoin# * t`

#### EB#

EB# increases the effective elite spawn chance:
- `EliteSpawnChance'(w) = EliteSpawnChance(w) * EB#`

This results in a linear increase in cell income:
- Absolute: the curve has a higher coefficient, and is scaled vertically
- Relative: the ratio to baseline is a constant, which make horizontal lines of
  form `y = k * EB#`
- Relative: the ratio to baseline is approximately linear until elite spawns max
  out, then asymptotically approaches a horizontal line of the form
  `y = k * EB#`
- Difference: the curve accelerates toward a linear equation of the form
  `y = k * EB# * t`

#### EO#

EO# increases all coin rewards for enemies hit by orbs:
- `r'(w) = w|{0,100}:0; {100,*}:1| * <0.33,...,4.0> * EO#`
In practice, this will be most enemies except for all scatter splits, which
represent a more-significant portion of enemies early on in a run. That causes
the relative graph to follow an asymptote instead of a plain horizontal line.

This results in a linear increase in coin income:
- Absolute: the exponential and linear components of the curve have higher
  coefficients, scaling them vertically
- Relative: the ratio to baseline is a positive horizontal asymptote
  approaching the line `y = k * EO#`
- Difference: the difference between functions accelerates towards a linear
  equation of the form `y = k * EO# * t`

#### IS#

IS# extends the period of 0% coin drop rate, but shifts the enemy spawn tables
in -t:
- `e'(w) = w|{0,i}:0.1; {i,*}:1.0| * <BasicSpawnChance(w),...,EliteSpawnChance(w)>`
- `w'(t) = t|{0,t(i)}:10; {t(i),*}:1| / (WaveDuration + WaveCooldown)`

This results in a constant increase in coin income:
- Absolute: the curve is translated in -t and -y, crossing the y-axis later, but
  reaching maximum slope sooner
- Relative: the ratio to baseline begins following an increasing horizontal
  asymptote, then transitions to a decreasing horizontal asymptote approaching
  the line `y = k * IS#`
- Difference: the difference between functions is approximately linear until
  reaching max enemy spawn rate, then smooths out to the horizontal line
  `y = k * IS#`

#### WA#

WA# compresses the common enemy spawn table in t:
- `e'(w) = w|{0,100}:0.1; {100,*}:1.0| * <BasicSpawnChance(w * WA#),...>`

This results in a constant increase in coin income:
- Absolute: the exponential portion of the curve is scaled in y
- Relative: the ratio to baseline begins following an increasing horizontal
  asymptote, then transitions to a decreasing horizontal asymptote approaching
  the line `y = k * (1 - WA#)`
- Difference: the difference between functions is approximately linear until
  reaching max enemy spawn rate, then smooths out to the horizontal line
  `y = k * (1 - WA#)`

#### WS#

WS# increases the effective wave skip chance:
- `WS_Chance' = (WS_Chance * WS#) + WS_Chance * (1 - WS_Chance * WS#)`
- `f'(w) = e(w) * r(w) * (1 + WS_Chance' * (WS_Bonus - 1))
- `w'(t) = w(t * WS#)`

This results in a linear increase in coin income:
- Absolute: the curve is compressed in t and dilated in y
- Relative: the ratio to baseline is a choppy positive horizontal asymptote
  decreasing towards `y = WS#`
- Difference: the difference between functions is approximately linear,
  following the line `y = k * WS# * t`

### Elite Cells

Elite cells are dropped by elite enemies.

- `e(w) = w|{0,100}:0.1; {100,*}:1.0| * EliteSpawnChance(w)`
- `r(w) = w|{0,100}:0.2; {100,*}:1.0| * avg(TierCellMin, TierCellMax)`

Masteries that affect cell income are EB#, IS#, and WS#.

#### EB#

EB# increases the effective elite spawn chance:
- `EliteSpawnChance'(w) = EliteSpawnChance(w) * EB#`

This results in a linear increase in cell income:
- Absolute: the curve has a higher coefficient, and is scaled vertically
- Relative: the ratio to baseline is a constant, which make horizontal lines of
  form `y = k * EB#`
- Difference: the difference between functions accelerates towards a linear
  equation of the form `y = k * EB# * t`

#### IS#

IS# extends the 20% cell drop rate and 10x elite spawn table advancement
periods, and shifts the elite spawn table in -t:
- `e'(w) = w|{0,i}:0.1; {i,*}:1.0| * EliteSpawnChance(w)`
- `r'(w) = w|{0,i}:0.2; {i,*}:1.0| * avg(TierCellMin, TierCellMax)`
- `w'(t) = t|{0,t(i)}:10; {t(i),*}:1| / (WaveDuration + WaveCooldown)`

This results in a constant increase in cell income:
- Absolute: the curve is translated in X- significantly and Y- slightly
- Relative: the ratio to baseline is a positive horizontal asymptote at
  decreasing towards `y = 0`
- Difference: the difference between functions is exponential during the
  exponential phase, then constant during the linear phase, resulting in an
  S-curve

#### WS#

WS# increases the effective wave skip chance:
- `WS_Chance' = (WS_Chance * WS#) + WS_Chance * (1 - WS_Chance * WS#)`
- `f'(w) = e(w) * r(w) * (1 + WS_Chance' * (WS_Bonus - 1))
- `w'(t) = w(t * WS#)`

This results in a linear increase in cell income:
- Absolute: the curve is compressed in t and dilated in y
- Relative: the ratio to baseline is a choppy positive horizontal asymptote
  decreasing towards `y = WS#`
- Difference: the difference between functions is exponential during the
  exponential phase, then linear during the linear phase

### Reroll Shards

Reroll shards are dropped by bosses.

- `e(w) = w|{0,100}:0; {100,*}:1| / TierBossPeriod`
- `r(w) = w|{0,100}:0; {100,*}:1| * TierRerollDrop`

Masteries that affect reroll shard income are Cash#, EB#, IS#, and WS#.

#### Cash#

Cash# adds a chance for elites to drop half as many reroll shards as bosses:
- `e(w) = w|{0,100}:0; {100,*}:1| * <TierBossPeriod,EliteSpawnChance(w)>`
- `r(w) = w|{0,100}:0; {100,*}:1| * <1.0,0.5> * TierRerollDrop`

This results in additional reroll rewards that follow an exponential curve until
elite spawns max out, after which they follow a linear curve:
- Absolute: the curve accelerates toward a scaled linear equation
- Relative: the ratio to baseline is approximately linear until elite spawns max
  out, then asymptotically approaches a horizontal line of the form
  `y = k * Cash#`
- Difference: the curve accelerates toward a linear equation of the form
  `y = k * Cash# * t`

#### EB#

EB# increases the effective elite spawn rate. With Cash#, this scales the number
of elites that can drop reroll shards:
- `EliteSpawnChance'(w) = EliteSpawnChance(w) * EB#`
- `e(w) = w|{0,100}:0; {100,*}:1| * <TierBossPeriod,EliteSpawnChance'(w)>`

This results in a constant scale factor to the increased rewards from Cash#:
- Absolute: the curve accelerates toward a scaled linear equation
- Relative: the ratio to baseline is approximately linear until elite spawns max
  out, then asymptotically approaches a horizontal line of the form
  `y = k * EB#`
- Difference: the curve accelerates toward a linear equation of the form
  `y = k * EB# * t`

#### IS#

IS# extends the period of 0% reroll shard drop rate, but shifts the elite spawn
table in -t. With Cash#, this increases reroll shard drop rate from more elites:
- `e'(w) = w|{0,i}:0; {i,*}:1| * EliteSpawnChance(w)`
- `w'(t) = t|{0,t(i)}:10; {t(i),*}:1| / (WaveDuration + WaveCooldown)`

This results in a constant increase in reroll income:
- Absolute: the curve is translated in -t and -y, crossing the y-axis later, but
  reaching maximum slope sooner
- Relative: the ratio to baseline begins following an increasing horizontal
  asymptote, then transitions to a decreasing horizontal asymptote approaching
  the line `y = k * IS#`
- Difference: the difference between functions is approximately linear until
  reaching max elite spawn rate, then smooths out to the horizontal line
  `y = k * IS#`

#### WS#

WS# increases the effective wave skip chance:
- `WS_Chance' = (WS_Chance * WS#) + WS_Chance * (1 - WS_Chance * WS#)`
- `f'(w) = e(w) * r(w) * (1 + WS_Chance' * (WS_Bonus - 1))
- `w'(t) = w(t * WS#)`

This results in a linear increase in reroll shard income:
- Absolute: the curve is compressed in t and dilated in y
- Relative: the ratio to baseline is a choppy positive horizontal asymptote
  decreasing towards `y = WS#`
- Difference: the difference between functions is approximately linear,
  following the line `y = k * WS# * t`

### Module Shards

Reroll shards are dropped by bosses.

- `e(w) = w|{0,100}:0; {100,*}:1| * <CommonModuleChance,RareModuleChance> / TierBossPeriod`
- `r(w) = <10,30>`

Masteries that affect module shard income are RPC#, IS#, and WS#.

#### RPC#

RPC# alters adds a new event that can drop common modules:
- `e(w) = w|{0,100}:0; {100,*}:1| * RecoveryPackageChance * <RPC#,0>`

This results in a consistently linear increase in module income.
- Absolute: the curve has a higher coefficient, and is scaled vertically
- Relative: the ratio to baseline is a constant, which make horizontal lines of
  form `y = k * RPC#`
- Difference: the difference between functions is a linear equation of the form
  `y = k * RPC# * t`

#### IS#

IS# extends the period of 0% module drop rate:
- `e'(w) = w|{0,i}:0; {i,*}:1| * <CommonModuleChance,RareModuleChance>`
- `w'(t) = t|{0,t(i)}:10; {t(i),*}:1| / (WaveDuration + WaveCooldown)`

This results in a constant decrease in cell income:
- Absolute: the curve is translated in X+ by `IS# - 100`
- Relative: the ratio to baseline is a positive horizontal asymptote
  increasing toward `y = 0`
- Difference: the difference between functions is constant, which make
  horizontal lines of the form `y = k * IS# / 100`

#### WS#

WS# increases the effective wave skip chance:
- `WS_Chance' = (WS_Chance * WS#) + WS_Chance * (1 - WS_Chance * WS#)`
- `f'(w) = e(w) * r(w) * (1 + WS_Chance' * (WS_Bonus - 1))
- `w'(t) = w(t * WS#)`

This results in a linear increase in cell income:
- Absolute: the curve is compressed in t
- Relative: the ratio to baseline is a choppy positive horizontal asymptote
  decreasing towards `y = WS#`
- Difference: the difference between functions is a linear equation of the form
  `y = k * WS# * t`
