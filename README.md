# bb6: does this 6-state Turing machine halt on the empty tape?

    1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE        (seed-DB notation; it halts when state A reads a 1)

Open question: does the machine ever halt? This repository holds the programs and data of an ongoing investigation.

## Idea in brief
After 8 initial steps the tape always looks like

    0^∞  1^k  F>  S  0^∞        with S = 1(0|1)*1

(a block of k ones, the head in state F on the first symbol of S). Such a configuration is called a *Bell*.
The next Bell is reached by

    k' = 3·⌊k/2⌋ + c ,        (S', c) = f(S, bit 1 of k)

where c is a small constant. f is a finite table (2880 words S, two entries each; an entry can also be HALT),
computed by direct simulation of the machine. k grows by a factor 3/2 per Bell, so after N Bells it has about 0.585·N bits.

## Status (14 Oct 2026)
- No halt up to 10⁹ Bells (`src/bellntt.c`, 23 min on 2 cores).
- Heuristic only, not a proof: if the next bit of k is treated as a fair coin, the halt rate is about 8.9·10⁻¹³ per Bell,
  expected about 1.1·10¹² Bells, P(halt by 10¹²) ≈ 59 %. Almost all of it comes from the words `11111` and `1101111`.
- Run times beyond 10⁹ are extrapolations (accurate to roughly a factor 3): 10¹⁰ ≈ 12 h, 10¹¹ ≈ 16 days, 10¹² ≈ 1.4 years on 2 cores.

## Files
| Path | Content |
|---|---|
| `python/bell-structure.py` | simulates the machine directly up to Bell 23 and prints the Bell boundaries and data |
| `python/bell-table.py` | builds the table f by direct simulation (k = 80 and 82 for every word S) |
| `python/tmsim.py` | Turing machine simulator used by both |
| `table/tab.txt`, `table/tab_names.txt` | the table f (read by the programs in `src/`), `table/halt-entries.txt`: its 42 halt entries |
| `src/bellntt.c` | fast simulation: blocks of Bells, own NTT multiplication, OpenMP, no GMP |
| `src/bellrun.c`, `src/bellrun.py` | reference simulation (blocks of 40 Bells) |
| `src/bellfast.py` | Python prototype of the block method |
| `tools/` | analysis helper scripts from earlier work, not documented |

## Usage

    python3 python/bell-structure.py 23            # Bell structure up to Bell 23 (a few seconds)
    python3 python/bell-table.py --out table       # rebuild the table (about 1 s); add --verify to test k-independence

    gcc -O3 -march=native -fopenmp -o src/bellntt src/bellntt.c
    cd table                                       # the programs read tab.txt and tab_names.txt from the current directory
    ../src/bellntt 10000000 40000                  # N Bells, block size B

Output: `KCHECK <k mod 2^64> <bit length of k> <state>`, then `kein Halt in … Bells` (no halt) or a HALT message.
Reference values: N = 10⁶ → `16887177590821663034 584970 11011`; N = 10⁷ → `10592086495055389818 5849632 10001`.
Good block sizes B: about 4·10⁴ for 10⁷, 4·10⁵ for 10⁸, 1.2·10⁶ for 10⁹ Bells.

## License
MIT
