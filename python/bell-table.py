#!/usr/bin/env python3
"""
bell-table.py - builds the Bell transition table by direct simulation

For every word S (Bell configuration  1^k F> S) and each of the two cases
        bit 1 of k = 0  (k mod 4 in {0, 1})      and      bit 1 of k = 1  (k mod 4 in {2, 3})
the machine is simulated from  1^k F> S  up to the start of the next Bell (using k = 80 and k = 82).
The result is  (S', c)  with  k' = 3*floor(k/2) + c.  With --verify the program checks that the result
does not depend on the exact choice of k (k = 81, 83, 84, 86, 160, 162, 1000, 1002 are also tried).

Starting from S = 11 the table is extended by every word S that occurs as a result (closure under the
transition).  Words whose length (without the leading 1, "S_pascal") exceeds MAXLEN are not followed;
the entry is then -2 ("unknown").  Halt of the machine: entry -1.

Output (the format read by bellrun.c / bellrun.py):
    tab.txt        first line n; then one line per word:  "S'(bit 1 of k = 0)  c0  S'(bit 1 of k = 1)  c1"
                   (S' as a line number of the table, -1 = halt, -2 = unknown)
    tab_names.txt  one line per word: S without its leading 1 ("S_pascal"), sorted by length, then value

Usage:   python3 bell-table.py [--maxlen 18] [--verify] [--out DIRECTORY]
"""
import os
import sys
import time
from tmsim import one_bell

K0 = (80, 82)                    # k values used for bit 1 = 0 and bit 1 = 1
VERIFY_K = (81, 83, 84, 86, 160, 162, 1000, 1002)


def argval(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def transition(S, bit, verify=False):
    """Simulate one Bell from 1^k F> S.  Returns (S_new | 'halt', c)."""
    res = None
    for k in ([K0[bit]] + ([x for x in VERIFY_K if (x >> 1) & 1 == bit] if verify else [])):
        r = one_bell(k, S)
        if r[0] == 'halt':
            out = ('halt', 0)
        elif r[0] == 'bell':
            out = (r[2], r[1] - 3 * (k // 2))
        else:
            raise RuntimeError(f'Bell for S={S}, k={k} does not end: {r}')
        if res is None:
            res = out
        elif res != out:
            raise RuntimeError(f'result depends on k: S={S}, bit={bit}: k={K0[bit]} -> {res}, k={k} -> {out}')
    return res


def main():
    maxlen = int(argval('--maxlen', 18))
    verify = '--verify' in sys.argv
    outdir = argval('--out', '.')
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    trans = {}                                  # S_pascal -> [(S_pascal'|'halt'|'unknown', c)] for bit 0 and bit 1
    todo = ['1']                                # start word S = 11, i.e. S_pascal = '1' (work list)
    while todo:
        sp = todo.pop()               # compute both transitions of this word
        if sp in trans:
            continue
        trans[sp] = []
        for bit in (0, 1):
            nxt, c = transition('1' + sp, bit, verify)
            if nxt == 'halt':
                trans[sp].append(('halt', 0))
            else:
                npascal = nxt[1:]
                if len(npascal) > maxlen:
                    trans[sp].append(('unknown', 0))
                else:
                    trans[sp].append((npascal, c))
                    if npascal not in trans:
                        todo.append(npascal)
        if len(trans) % 500 == 0:
            print(f'{len(trans)} words, time {time.time() - t0:.0f} s', file=sys.stderr)
    # write the table: states are numbered in the order (length, value) of S_pascal
    names = sorted(trans, key=lambda w: (len(w), w))
    index = {w: i for i, w in enumerate(names)}
    with open(f'{outdir}/tab.txt', 'w') as f:
        f.write(f'{len(names)}\n')
        for w in names:
            row = []
            for nxt, c in trans[w]:
                row += [-1 if nxt == 'halt' else -2 if nxt == 'unknown' else index[nxt], c]
            f.write(' '.join(map(str, row)) + '\n')
    with open(f'{outdir}/tab_names.txt', 'w') as f:
        f.write('\n'.join(names))
    nh = sum(1 for w in names for nxt, c in trans[w] if nxt == 'halt')
    nu = sum(1 for w in names for nxt, c in trans[w] if nxt == 'unknown')
    print(f'{len(names)} words, {nh} halt entries, {nu} unknown, longest word {max(map(len, names))}, '
          f'time {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
