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

The number of TM steps spent in one Bell is a quadratic polynomial in k. If t is the step count at the start of a Bell, then the next Bell starts at

    t' = t + (3/8)·k² + d  >  t + (3/8)·k²

where d are small numbers that depend on S and on k (d = β·k + γ with β, γ depending on S and k mod 4; d is always positive).
Example: for S = `11` and k mod 4 = 0, Bell 5 (k = 92, t = 2,930) takes 3/8·92² + d = 3,174 + 1,113 = 4,287 steps (d = 23/2·92 + 55) and Bell 6 starts at t' = 7,217 (see the list below).

The formula was found by direct simulation (`one_bell` in `python/tmsim.py`) and is exact in the following sense: for every word S of the table that does not halt and every residue of k mod 4,
the step count is exactly quadratic in k (checked for k = 80, 84, 88, 92 and the other residues, 11,436 cases, second difference always 12, i.e. leading coefficient 3/8), and with the fitted d it reproduces the steps of all 23 Bells in the list below.
For larger k it is an extrapolation of this pattern, not a proof.

Why 3/8? A plausible reading, not derived from the rules of the machine: during a Bell the head sweeps back and forth about k/2 times, and in the j-th sweep the part to the right of the head has grown by about 3 cells per consumed pair of ones, so a sweep costs about 3j steps; the sum Σ 3j for j < k/2 is 3k²/8.



The first 23 Bells (`python/bell-structure.py 23`). `t` = number of TM steps up to the start of the Bell, `k` and `S` as above (S written out in full), `c` = the constant of the transition to the next Bell, i.e. k<sub>n+1</sub> = 3·⌊k<sub>n</sub>/2⌋ + c<sub>n</sub>:

| n | t (steps) | k | k mod 4 | S | c |
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
By iteration of above formulas, the sequence of bells can be computed as ... (S,k) (S',k'),(S'',k'')...,
instead of simulation on the binary tape. It is possible, to compute in advance a table, where for each S the function (S', c) = f(S, bit 1 of k) is listed.

For this investigation we use a finite table (2880 words S, two entries each; an entry can also be HALT),
computed by direct simulation of the machine with `python/bell-table.py`. The words S are sorted by length, then by value; # is the line number in `table/tab.txt` (S is stored in `table/tab_names.txt` without its leading 1). Here are the first 10 entries, a few HALT entries (`111111` and `11101111` carry almost all of the halt rate in the Markov estimate below) and the last 10 entries:

| # | S | bit 1 of k = 0 → S', c | bit 1 of k = 1 → S', c |
|---:|---|---|---|
| 0 | `11` | `111`, c=8 | `11`, c=11 |
| 1 | `111` | `11`, c=8 | `110001`, c=5 |
| 2 | `1101` | `11`, c=14 | `111`, c=11 |
| 3 | `1111` | `11001`, c=8 | `11`, c=8 |
| 4 | `11001` | `1111`, c=8 | `111`, c=11 |
| 5 | `11011` | `110001`, c=8 | `11`, c=11 |
| 6 | `11101` | `111`, c=8 | `1100011`, c=5 |
| 7 | `11111` | `11`, c=8 | `110101`, c=5 |
| 8 | `110001` | `11101`, c=8 | `111`, c=11 |
| 9 | `110011` | `11111`, c=8 | `11`, c=17 |
| … | | | |
| 15 | `111111` | `110101`, c=5 | HALT |
| 31 | `1111111` | HALT | `111101`, c=9 |
| 54 | `11101111` | `11`, c=11 | HALT |
| 61 | `11111101` | `1101011`, c=5 | HALT |
| … | | | |
| 2870 | `1100011011010010001` | `111011011010010001`, c=8 | `1111011010010001`, c=11 |
| 2871 | `1100011011010010011` | `111011011010010011`, c=8 | `1111011010010011`, c=11 |
| 2872 | `1100011011010011001` | `111011011010011001`, c=8 | `1111011010011001`, c=11 |
| 2873 | `1100011011010011011` | `111011011010011011`, c=8 | `1111011010011011`, c=11 |
| 2874 | `1100011011011000001` | `111011011011000001`, c=8 | `1111011011000001`, c=11 |
| 2875 | `1100011011011000011` | `111011011011000011`, c=8 | `1111011011000011`, c=11 |
| 2876 | `1100011011011010001` | `111011011011010001`, c=8 | `1111011011010001`, c=11 |
| 2877 | `1100011011011010011` | `111011011011010011`, c=8 | `1111011011010011`, c=11 |
| 2878 | `1100011011011011001` | `111011011011011001`, c=8 | `1111011011011001`, c=11 |
| 2879 | `1100011011011011011` | `111011011011011011`, c=8 | `1111011011011011`, c=11 |

`unknown` (one entry, not in this excerpt) means that the Bell ends in a word longer than the table limit (18 symbols after the leading 1).

## HALT expected! (Markov estimate)
This is a heuristic, not a proof.

**Reasoning.** The next word S' and the question whether the machine halts depend only on S and on bit 1 of k (checked for every entry of the table with
several values of k, see `bell-table.py --verify`). Assume that bit 1 of k behaves like a fair coin toss in every Bell. Then the sequence of words S is a Markov chain on
the 2880 words of the table: each word has two successors with probability 1/2 each, and an entry HALT ends the chain.

- The visit frequencies of the chain (its stationary distribution) agree with the real orbit: over the first 300,000 Bells the total variation distance is 0.003;
  in the run to 10⁹ Bells the three most frequent words S = `11`, `111`, `110001` occurred with frequencies 0.3457, 0.2977, 0.1538, the same as in the model to the digits shown.
- The halt probability per Bell is the sum over all words of (visit frequency × fraction of HALT successors) = **8.87·10⁻¹³**.
  Almost all of it (61 % and 39 %) comes from the two words S = `111111` and S = `11101111`, each with one HALT successor.
- With a constant rate, P(halt within N Bells) = 1 − exp(−8.87·10⁻¹³ · N). Expected number of Bells until the halt: 1.13·10¹², median 7.8·10¹¹.

| Bells N | P(halt up to N) | simulation time with `bellntt` (2 cores, extrapolated) |
|---|---|---|
| 10⁹ | 0.089 % | 23 min (measured, no halt) |
| 10¹⁰ | 0.88 % | ≈ 12 h |
| 10¹¹ | 8.5 % | ≈ 16 days |
| 10¹² | 58.8 % | ≈ 1.4 years |
| 2·10¹² | 83 % | ≈ 4 years |
| 5·10¹² | 98.8 % | ≈ 16 years |
| 10¹³ | 99.99 % | ≈ 44 years |

The model has no memory: if there is still no halt after 10¹² Bells, the chance of a halt within the next 10¹² Bells is again 59 %.
The times for N > 10⁹ assume that the run time grows like N^1.5 and are accurate to a factor of about 3 only.

**Limits.** The fair-coin assumption is not proven: the bits of k come from the 3/2 dynamics, so correlations are possible, and they could change all the numbers above
(even whether a halt ever happens). Also note that the model says only that the HALT entries are rare, not where in the orbit they will be hit.
The model agrees with the 10⁹ Bells simulated so far, but at probability 0.089 % that run could not have shown a halt anyway.

## Memory demand
In order to simulate until HALT, we expect that we need to go until 10^12 Bells or higher, which requires some memory for storage of k:
k grows by a factor of about 3/2 per Bell. After N Bells its bit length is about N·log₂(3/2) = 0.5849625·N plus a small constant
(about 4 to 7 bits in the runs so far: B23 has k = 158,354, i.e. 18 bits; N = 10⁹ gives 584,962,508 bits).
The rounded factor 0.585 is not accurate enough for large N (at N = 10⁹ it is off by about 37,000 bits).
So k needs roughly N/13.7 bytes.

**Lower bound for the number of TM steps.** The table below also gives a lower bound for the TM steps t. It follows from two facts:
1. A Bell with k ones takes at least 3/8·k² steps (d > 0 in the formula above).
2. Every constant c in the table is at least 5, so k' = 3·⌊k/2⌋ + c ≥ 1.5·k, and therefore k_n ≥ 1.5^(n−23) · k₂₃ for n ≥ 23, with k₂₃ = 158,354.

Hence t_N ≥ t₂₃ + 3/8 · Σ_{n=23}^{N−1} k_n² ≥ 3/8 · k₂₃² · Σ 2.25^j ≥ 0.3 · k₂₃² · (2.25^(N−23) − 1) + t₂₃ ≈ 7.5·10⁹ · 2.25^(N−23) = 10^(0.35218·N + 1.78),
because 2.25 = 1.5² and log₁₀ 2.25 = 0.35218. The step count itself therefore has more than 0.35·N decimal digits, and for all N in the table it is far beyond what a step-by-step simulation can reach.
The bound rests on the step formula, which is verified for k = 80 to 92 and for all 23 listed Bells, not proved for every k. In practice t_N ≈ 0.3·k_N², which has the same exponent.


| Bells N | k | memory for k | TM steps t, lower bound |
|---|---|---|---|
| 10⁹ | 585 million bits | 73 MB | 10^(3.52·10⁸) |
| 10¹⁰ | 5.85 billion bits | 0.73 GB | 10^(3.52·10⁹) |
| 10¹¹ | 58.5 billion bits | 7.3 GB | 10^(3.52·10¹⁰) |
| 10¹² | 585 billion bits | 73 GB | 10^(3.52·10¹¹) |

Not included: the working buffers of the multiplication in `bellntt` (observed in the run to 10⁹: about 220 MB resident in total at 8·10⁸ Bells, with k then at 58 MB)
and the table (small).

## Runtime optimization: Block simulation and NTT
**Why.** For one Bell, k' = 3·⌊k/2⌋ + c has to be applied to a number with up to hundreds of millions of bits. A simple implementation (`src/bellrun.c`) groups 40 Bells per pass over k,
so every pass costs time proportional to the length of k and the total time grows like N². That is 12 s for 10⁷ Bells, 27 min for 10⁸ and about 2 days for 10⁹.

**Block simulation (two levels).** Bell by Bell, only the lowest bits of k matter for the path: k' = 3·⌊k/2⌋ + c shifts k right by one bit, and the word S and the constant c depend on the lowest two bits.
So for a block of B Bells only the lowest B+2 bits of k decide which words S occur and which constants c are added. Write k = q·2^(B+2) + r. Then, after B Bells, the new k is

    k_B = 3^B · q · 4 + L        (L is computed from the low part r alone, with the table)

- **Inner level (low part).** L is obtained by simulating the B Bells on the short number r only, in passes of 40 Bells at a time (`bellrun.c` does the same 40-Bell passes on the whole k, which is why it needs time ∝ N²).
- **Outer level (long part).** The long part q of k is not touched Bell by Bell, but multiplied once by 3^B. That is a multiplication of a number with up to N·0.585 bits by one with 1.585·B bits.
With the schoolbook method this costs as much as before; with a fast multiplication it costs only about n·log n. This is where the NTT comes in.

**NTT (number theoretic transform).** Write a number as a polynomial in 2^w whose coefficients are its w-bit pieces. The product of two numbers is then the product of two
polynomials (carries are added afterwards). A polynomial is determined by its values at enough points, and the product of two polynomials has values equal to the products of the values.
The NTT is the fast Fourier transform done with whole numbers modulo a prime p instead of with floating-point numbers, so there are no rounding errors:

1. Choose a prime p with 2^24 | p − 1, so that a root of unity of order 2^m (m ≤ 24) exists modulo p.
2. Transform both numbers (log n butterfly stages, about n·log n operations).
3. Multiply the transformed values point by point.
4. Transform back and add up the carries.

In `bellntt.c`:
- two 63-bit primes (p = 9223372036636672001 and 9223372036737335297) and the Chinese remainder theorem (CRT), so that the true coefficients, which are larger than one prime, are recovered (the two primes are handled by two OpenMP threads);
- Montgomery multiplication instead of divisions by p;
- the forward transform leaves its output in bit-reversed order and the inverse transform expects exactly that order, so no bit reversal is needed;
- the transform of 3^B is computed once and reused for all blocks;
- q is cut into chunks of the transform length and the partial products are added where they overlap (overlap-add), so memory stays small.

The block size B (second argument of `bellntt`) does not change the result, only the speed. It is a trade-off: a larger B means fewer big multiplications, but a longer low part to be simulated (at N = 10⁹ the two parts take about the same time: 669 s and 713 s).

| Bells N | good block size B |
|---|---|
| 10⁷ | about 4·10⁴ |
| 10⁸ | about 4·10⁵ |
| 10⁹ | about 1.2·10⁶ |

| Bells N | `bellrun` (no NTT) | `bellntt` (2 threads) |
|---|---|---|
| 10⁷ | 12 s | 1.7 s |
| 10⁸ | 1630 s | 39 s |
| 10⁹ | ≈ 1.9 days (extrapolated) | 1383 s (669 s low part, 713 s products) |

**Checking the result.** At the end each program prints a fingerprint of the final state, `KCHECK <k mod 2^64> <bit length of k> <state>`, where `<state>` is the word S without its leading 1.
Two programs that print the same fingerprint for the same N have computed the same orbit. Then comes `no halt in … Bells`, or, if a HALT entry of the table is reached, a message `HALT at Bell …` with the word S.
Reference values:

| Bells N | `KCHECK` |
|---|---|
| 10⁶ | `16887177590821663034 584970 11011` |
| 10⁷ | `10592086495055389818 5849632 10001` |
| 10⁹ | `825729492582408624 584962508 10001` (`bellntt` only, not cross-checked with `bellrun`) |

`bellntt` gives the same fingerprint as `bellrun` for 10⁶ and 10⁷ Bells with several values of B. That the coefficients stay below the product of the two primes
for the largest runs was not proven, only tested this way.

## Status (14 Oct 2026)
- Simulated until 10^9 Bells, No HALT up to 10⁹ Bells (`src/bellntt.c`, 23 min on 2 cores).
- Heuristic only, not a proof: if the next bit of k is treated as a fair coin, the halt rate is about 8.9·10⁻¹³ per Bell,
  expected about 1.1·10¹² Bells, P(halt by 10¹²) ≈ 59 %. Almost all of it comes from the words S = `111111` and S = `11101111`.
- Run times beyond 10⁹ are extrapolations (accurate to roughly a factor 3): 10¹⁰ ≈ 12 h, 10¹¹ ≈ 16 days, 10¹² ≈ 1.4 years on 2 cores.

## Volunteers wanted:
- Who is willing to make a simulation until 10^11 or higher ?
- This investigation was made together with AI Sonnet 5.5. It would be desirable to carry out an independent review using a different AI model


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

Output: a `KCHECK` fingerprint, then "no halt" or a HALT message (details in the section "Runtime optimization: Block simulation and NTT").

## License
MIT
