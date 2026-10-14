#!/usr/bin/env python3
"""
bell-structure.py - Bell structure of the Turing machine, by direct simulation

Machine:  1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE      (halts when A reads a 1)

The program runs the machine on the empty tape (simulator: tmsim.py), detects the Bell
boundaries and prints the data of every Bell.

A Bell configuration has the form
        0^inf  1^k  F> S  0^inf          with  S = 1(0|1)*1
(only ones left of the head, head in state F on the first symbol of S).
Bell B_n starts where k grows again compared with the previous Bell configuration
(in between, k drops in steps of 2).  The transition to the next Bell is
        k_(n+1) = 3 * floor(k_n / 2) + c_n ,        (S_(n+1), c_n) = f(S_n, bit 1 of k_n)
with a small constant c_n.  This program shows S_n and c_n for each Bell;
bell-table.py computes the complete table f.

Usage:   python3 bell-structure.py [N] [--plain] [--full] [--csv FILE]
    N         last Bell to compute (default 23)
    --plain   execute every TM step individually (slow; only for cross-checking)
    --full    print S completely (otherwise long S are abbreviated)
    --csv F   also write the data to file F
Output columns:
    n      number of the Bell          step  TM steps up to the start of the Bell
    k      length of the block of ones left of the head (k mod 4 in the next column)
    |S|    length of S                 c     c_(n-1), i.e. k_n = 3*floor(k_(n-1)/2) + c_(n-1)
    S      the word S (start ... end if long)
"""
import sys
import time
from tmsim import Machine, bells


def short(S, full):
    # abbreviate long words: first 16 and last 16 symbols
    return S if full or len(S) <= 40 else f"{S[:16]}...{S[-16:]}"


def main():
    args = sys.argv[1:]
    plain, full = '--plain' in args, '--full' in args
    csv = None
    if '--csv' in args:
        csv = open(args[args.index('--csv') + 1], 'w')
        args = [a for a in args if a != args[args.index('--csv') + 1]]
    nums = [a for a in args if a.isdigit()]
    N = int(nums[0]) if nums else 23

    # bells() yields every Bell start; c is obtained from two consecutive k values
    print(f"{'n':>3} {'step':>14} {'k':>9} {'k%4':>3} {'|S|':>4} {'c':>3}  S")
    t0 = time.time()
    prev_k = None
    for n, step, k, S in bells(Machine(accel=not plain)):
        if n is None:
            print(f"HALT after {step} steps")
            break
        c = '' if prev_k is None else k - 3 * (prev_k // 2)
        print(f"{n:>3} {step:>14} {k:>9} {k % 4:>3} {len(S):>4} {c!s:>3}  {short(S, full)}")
        if csv:
            csv.write(f"{n};{step};{k};{S};{c}\n")
        prev_k = k
        if n >= N:
            break
    print(f"time {time.time() - t0:.1f} s")


if __name__ == '__main__':
    main()
