# Does this 6-state Turing machine halt on the empty tape?

Machine (seed-DB notation):

    1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE

(Vorläufige README – wird noch neu geschrieben. / Preliminary README, to be rewritten.)

## Idea in brief
- After 8 initial steps the orbit consists of configurations `0^∞ 1^kᵢ F> Sᵢ 0^∞` with Sᵢ = 1(0|1)*1 ("Bells").
- kᵢ₊₁ = 3·⌊kᵢ/2⌋ + cᵢ and (Sᵢ₊₁, cᵢ) = f(Sᵢ, bit 1 of kᵢ). The table f is computed by direct simulation.
- The machine halts only if state A reads a 1.

## Status (14 Oct 2026)
- Simulation up to 10⁹ Bells: **no halt** (`bellntt`, 23 min on 2 cores).
- Markov heuristic (not a proof): halt rate ≈ 8.87·10⁻¹³ per Bell, expected ≈ 1.1·10¹² Bells;
  P(halt by 10⁹) ≈ 9·10⁻⁴, by 10¹¹ ≈ 8.5 %, by 10¹² ≈ 59 %.
- Extrapolation for `bellntt` (2 threads, accurate to a factor ~3 only): 10¹⁰ ≈ 12 h, 10¹¹ ≈ 16 days, 10¹² ≈ 1.4 years.

## Files
| Path | Content |
|---|---|
| `python/bell-structure.py` | direct simulation of the machine up to B23, prints the Bell boundaries and data |
| `python/bell-table.py` | builds the transition table by direct simulation (k = 80 and 82 per word S) |
| `python/tmsim.py` | the Turing machine simulator used by both |
| `table/tab.txt`, `table/tab_names.txt` | transition table (2880 words), read by the programs in `src/` |
| `table/halt-entries.txt` | the 42 halt entries of the table |
| `src/bellntt.c` | fast simulation (two-level blocks, own NTT, OpenMP, no GMP) |
| `src/bellrun.c`, `src/bellrun.py` | reference simulation with blocks of 40 Bells (C / Python) |
| `src/bellfast.py` | Python prototype of the block method |
| `tools/` | analysis helper scripts from earlier days (not documented individually) |
| `doc/` | daily reports (German) |

## Usage

    cd python
    python3 bell-structure.py 23                  # Bell structure up to B23
    python3 bell-table.py --out ../table          # rebuild the table (about 1 s)

    cd src
    gcc -O3 -march=native -fopenmp -o bellntt bellntt.c
    gcc -O3 -march=native -o bellrun bellrun.c
    cd ../table                                   # the programs read tab.txt, tab_names.txt from the current directory
    ../src/bellntt 10000000 40000                 # N Bells, block size B
    ../src/bellrun 10000000                       # reference

Output: `KCHECK <k mod 2^64> <bit length of k> <state>` and `kein Halt in … Bells`.
Reference values: N = 10⁶ → `16887177590821663034 584970 11011`; N = 10⁷ → `10592086495055389818 5849632 10001`;
N = 10⁹ → bit length 584962508, state 10001.
Good B: about 4·10⁴ at 10⁷, 4·10⁵ at 10⁸, 1.2·10⁶ at 10⁹. Memory: k has ≈ 0.585·N bits.

License: MIT.
