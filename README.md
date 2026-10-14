# bb6: does this 6-state Turing machine halt on the empty tape?

    1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE 

Open question: does the machine ever halt? This repository holds the programs and data of an ongoing investigation.

## Idea in brief
The TM is of type Bell, after 8 initial steps.
The bells can be separated and identified by a certain tape-configuration
    0^∞  1^k  F>  S  0^∞        with S = 1(0|1)*1

(a block of k ones, the head in state F on the first symbol of S).
The next Bell is reached by

    k' = 3·⌊k/2⌋ + c ,        (S', c) = f(S, bit 1 of k)

where c is a small constant. 

The first 23 Bells (`python/bell-structure.py 23`). `steps` = number of TM steps up to the start of the Bell, `k` and `S` as above (S written out in full), `c` = the constant of the transition to the next Bell, i.e. k<sub>n+1</sub> = 3·⌊k<sub>n</sub>/2⌋ + c<sub>n</sub>:

| n | steps (TM) | k | k mod 4 | S | c |
|---:|---:|---:|---:|---|---:|
| 1 | 8 | 2 | 2 | `11` | 11 |
| 2 | 105 | 14 | 2 | `11` | 11 |
| 3 | 430 | 32 | 0 | `11` | 8 |
| 4 | 1,237 | 56 | 0 | `111` | 8 |
| 5 | 2,930 | 92 | 0 | `11` | 8 |
| 6 | 7,217 | 146 | 2 | `111` | 5 |
| 7 | 16,716 | 224 | 0 | `110001` | 8 |
| 8 | 38,163 | 344 | 0 | `11101` | 8 |
| 9 | 85,508 | 524 | 0 | `111` | 8 |
| 10 | 192,969 | 794 | 2 | `11` | 11 |
| 11 | 439,774 | 1,202 | 2 | `11` | 11 |
| 12 | 997,271 | 1,814 | 2 | `11` | 11 |
| 13 | 2,254,896 | 2,732 | 0 | `11` | 8 |
| 14 | 5,085,303 | 4,106 | 2 | `111` | 5 |
| 15 | 11,448,622 | 6,164 | 0 | `110001` | 8 |
| 16 | 25,767,649 | 9,254 | 2 | `11101` | 5 |
| 17 | 57,973,932 | 13,886 | 2 | `1100011` | 11 |
| 18 | 130,462,393 | 20,840 | 0 | `1111` | 8 |
| 19 | 293,566,714 | 31,268 | 0 | `11001` | 8 |
| 20 | 660,559,285 | 46,910 | 2 | `1111` | 8 |
| 21 | 1,486,093,231 | 70,373 | 1 | `11` | 8 |
| 22 | 3,343,984,454 | 105,566 | 2 | `111` | 5 |
| 23 | 7,524,107,793 | 158,354 | 2 | `110001` | 11 |



Macro-Simulation: 
With above formulas, the sequence of bells can be computed as ... (S,K) (S',k'),(S'',k'')...,
instead of simulation on the binary tape. It is possible, to compute in advance a table, where for each S the function (S', c) = f(S, bit 1 of k) is listed.

For this investigation we use a finite table (2880 words S, two entries each; an entry can also be HALT),
computed by direct simulation of the machine. k grows by a factor of about 3/2 per Bell, so after N Bells its bit length is about N·log₂(3/2) = 0.5849625·N plus a small constant (about 4 to 7 bits in the runs so far: B23 has k = 158,354, i.e. 18 bits; N = 10⁹ gives 584,962,508 bits). The rounded factor 0.585 is not accurate enough for large N (at N = 10⁹ it is off by about 37,000 bits). So k needs roughly N/13.7 bytes of memory (73 MB for N = 10⁹).

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
