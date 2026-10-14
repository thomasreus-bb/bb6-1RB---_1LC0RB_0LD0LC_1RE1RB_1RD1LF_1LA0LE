#!/usr/bin/env python3
"""
tmsim.py - small Turing machine simulator used by bell-structure.py and bell-table.py.

The machine (seed-DB notation: for each state A..F two fields, for reading 0 and reading 1):
    1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE
Each field is  <write><move><next state>;  "---" means HALT (only A reading 1 halts).

Terms
-----
Bell configuration:  0^inf  1^k  F> S  0^inf     (S = 1(0|1)*1; head in state F on the first symbol of S)
Bell start:          Bell configurations with a "pure" left side (only ones left of the head) come in chains
                     in which k drops by 2.  A new Bell starts at the first such configuration whose k is
                     larger than that of the previous one.

Speed
-----
Step by step, B23 would need about 10^10 TM steps.  Three loops of the machine can be executed in one
operation without changing the result or the step count (accel=True):
    state B reading 1: write 0, move right, stay in B   -> erases a whole block of ones
    state C reading 1: write 0, move left,  stay in C   -> erases a whole block of ones
    states D / E reading 0: write 1, move right, D<->E  -> fills a whole block of zeros with ones
The step counter is increased by the block length.  With accel=False every step is done one by one
(used to cross-check the accelerated version).
"""

PROG = "1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE"
A, B, C, D, E, F = range(6)
MARGIN = 64            # always keep this many blank cells to the left and right of the head


def parse(prog):
    """Return table t[(state, symbol read)] = (symbol written, move +1/-1, next state), or None for HALT."""
    t = {}
    for s, block in enumerate(prog.split('_')):
        for r in (0, 1):
            f = block[3 * r:3 * r + 3]
            t[(s, r)] = None if f[0] == '-' else (int(f[0]), 1 if f[1] == 'R' else -1, 'ABCDEF'.index(f[2]))
    return t


class Machine:
    def __init__(self, prog=PROG, accel=True):
        self.table = parse(prog)
        self.accel = accel
        self.clear()

    def clear(self):
        # tape is a bytearray of 0/1 cells; pos is the head position as an index into it
        self.tape = bytearray(2 * MARGIN)
        self.pos = MARGIN
        self.state = A
        self.steps = 0

    def _grow(self):
        """Extend the tape with blank cells when the head gets close to an end (head index is adjusted)."""
        n = len(self.tape)
        if self.pos < MARGIN:
            add = max(n, 2 * MARGIN)
            self.tape[0:0] = bytes(add)
            self.pos += add
        if len(self.tape) - self.pos < MARGIN:
            self.tape.extend(bytes(max(len(self.tape), 2 * MARGIN)))

    def set_bell(self, k, S):
        """Build the Bell configuration 1^k F> S (S is a string of 0/1 starting with 1)."""
        self.clear()
        self.tape = bytearray(MARGIN) + bytearray([1]) * k + bytearray(int(c) for c in S) + bytearray(MARGIN)
        self.pos = MARGIN + k
        self.state = F

    def run_to_F(self):
        """Run until the machine enters state F.  Return True then; return False if the machine halts."""
        tape, table = self.tape, self.table
        pos, st, steps = self.pos, self.state, self.steps
        while True:
            if pos < MARGIN or len(tape) - pos < MARGIN:
                self.pos = pos
                self._grow()
                tape, pos = self.tape, self.pos
            b = tape[pos]
            # --- accelerated loops (exactly equivalent to doing the steps one by one) ---
            if self.accel and b == 1 and st == B:
                j = tape.find(0, pos)                  # next 0 to the right
                tape[pos:j] = bytes(j - pos)           # B: 1 -> 0, move right: erase the block of ones
                steps += j - pos
                pos = j
                continue
            if self.accel and b == 1 and st == C:
                j = tape.rfind(0, 0, pos)              # next 0 to the left
                tape[j + 1:pos + 1] = bytes(pos - j)   # C: 1 -> 0, move left: erase the block of ones
                steps += pos - j
                pos = j
                continue
            if self.accel and b == 0 and (st == D or st == E):
                j = tape.find(1, pos)                  # D0 = 1RE and E0 = 1RD: they alternate, writing
                if j < 0:                              # ones to the right until the next 1 is reached
                    raise RuntimeError('machine runs to the right over blank tape forever')
                n = j - pos
                tape[pos:j] = b'\x01' * n
                steps += n
                pos = j
                if n & 1:
                    st = D + E - st                    # odd number of steps: D and E are swapped
                continue
            # --- ordinary single step ---
            t = table[(st, b)]
            if t is None:
                self.pos, self.state, self.steps = pos, st, steps
                return False                           # HALT
            tape[pos] = t[0]
            pos += t[1]
            st = t[2]
            steps += 1
            if st == F:
                self.pos, self.state, self.steps = pos, st, steps
                return True

    def bell_config(self):
        """If the machine (in state F) currently shows a Bell configuration 1^k F> S, return (k, S), else None.
        Conditions: the cells left of the head are a block of ones with only blanks before it,
        the head is on a 1, and S extends up to the last 1 on the tape."""
        tape, pos = self.tape, self.pos
        if tape[pos] != 1:
            return None
        j = tape.rfind(0, 0, pos)                      # last 0 left of the head
        lo = j + 1                                     # block of ones: lo .. pos-1
        if lo == pos or tape.find(1) != lo:            # no block at all, or more ones further left
            return None
        hi = tape.rfind(1)                             # S = tape[pos .. hi]
        S = tape[pos:hi + 1].translate(bytes([48, 49]) + bytes(254)).decode()
        return pos - lo, S


def bells(machine=None):
    """Generate all Bell starts of the orbit on the empty tape: (n, step count, k, S).
    The first Bell is n = 1 (after 8 steps, k = 2, S = 11).  At HALT one last item (None, steps, None, None)."""
    m = machine or Machine()
    n, prev_k = 0, 0
    while m.run_to_F():
        cfg = m.bell_config()
        if cfg is None:
            continue
        k, S = cfg
        if k > prev_k:                                  # k grows again: a new Bell starts here
            n += 1
            yield n, m.steps, k, S
        prev_k = k
    yield None, m.steps, None, None


def one_bell(k, S, accel=True, max_steps=10**8):
    """Simulate one Bell directly, starting from 1^k F> S.
    Returns ('bell', k_new, S_new, steps) or ('halt', steps) or ('giveup', steps)."""
    m = Machine(accel=accel)
    m.set_bell(k, S)
    prev_k = k
    while True:
        if not m.run_to_F():
            return 'halt', m.steps
        if m.steps > max_steps:
            return 'giveup', m.steps
        cfg = m.bell_config()
        if cfg is None:
            continue
        if cfg[0] > prev_k:                            # next Bell start reached
            return 'bell', cfg[0], cfg[1], m.steps
        prev_k = cfg[0]
