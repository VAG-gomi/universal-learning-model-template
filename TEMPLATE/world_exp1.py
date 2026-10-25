#!/usr/bin/env python3
"""world_exp1.py -- EXP1 expanded worlds (WO-TBM-EXP1, Step 0).

Additive only. world.py is NEVER edited, and no template file is
changed by this module. The worlds here mirror world.World's
mechanics exactly (same step structure, same log strings, same
crush / block / goal rules), generalized along two axes only:
  (1) grid size N (goal (N-1, N-1), wall column(s) and door
      cell(s) per world, clipping to N-1);
  (2) multiple wall columns (M2) and interior obstacle cells (M1).

Schedule: 20/10 everywhere (period=20, open_len=10), shared by
all doors of a world. The door bit reported by observe() is the
NEXT door's open state: the first door whose wall column the
agent has not yet passed (agent.x <= wall_x); once the agent
has passed every wall column, the last door's state is shown.
Under the shared 20/10 schedule every door's state coincides at
every tick, so the next-door rule is structural here (which door
the bit refers to); its switch condition is what a future
phase-varied design would exercise. This is pinned, not hidden:
see nn/decisions_exp1_design.md §2.

Worlds (all period=20, open_len=10):
  W10  10x10, wall x=5,  door (5,5)    [geometry identical to World]
  W20  20x20, wall x=10, door (10,10)
  W30  30x30, wall x=15, door (15,15)
  M1   20x20 maze, wall x=10, door (10,10), interior obstacles
  M2   20x20 two sequential doors, walls x=10 and x=15,
       doors (10,10) and (15,10)
  M3   50x50, wall x=25, door (25,25)
Held-out variants (trained-world geometry with the door row moved
to floor(wall_x / 2)): W10h door (5,2), W20h door (10,5),
W30h door (15,7).

M1 obstacle layout (fixed; BFS-verified solvable in
nn/exp1_mechanics.py): left vertical x=4, y=2..8; left
horizontal y=13, x=2..6; right vertical x=14, y=12..18;
right horizontal y=6, x=13..17. No obstacle touches the
start (0,0), the goal, the door cell, or either door
approach cell (9,10)/(11,10); the row-10 corridor stays
open, so a path start -> door -> goal always exists.
Obstacles are unobserved: the agent sees only position +
door bit, exactly as with the wall column, so an obstacle
is learned about only by bumping into it.
"""

import os
import sys
from collections import deque

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from world import ACTIONS, door_is_open

PERIOD = 20
OPEN_LEN = 10

AGENT_START = (0, 0)

# M1 interior obstacles (fixed layout; see module docstring).
M1_OBSTACLES = frozenset(
    [(4, y) for y in range(2, 9)]
    + [(x, 13) for x in range(2, 7)]
    + [(14, y) for y in range(12, 19)]
    + [(x, 6) for x in range(13, 18)]
)


def door_is_open_exp1(tick, period=PERIOD, open_len=OPEN_LEN):
    """Shared-schedule door rule (same rule as world.door_is_open)."""
    return door_is_open(tick, period, open_len)


class Exp1World(object):
    """Grid world with the exact mechanics of world.World, generalized.

    wall_xs: wall columns, in crossing order (left to right).
    door_cells: one door cell per wall column, same order.
    obstacles: interior blocked cells (M1 only; empty otherwise).
    The goal is always (grid_size-1, grid_size-1); the start (0,0).
    """

    def __init__(self, grid_size, wall_xs, door_cells, obstacles=(),
                 period=PERIOD, open_len=OPEN_LEN):
        assert len(wall_xs) == len(door_cells)
        assert len(wall_xs) >= 1
        for wx, dc in zip(wall_xs, door_cells):
            assert dc[0] == wx
            assert 0 <= dc[1] < grid_size
        self.grid_size = grid_size
        self.wall_xs = list(wall_xs)
        self.door_cells = list(door_cells)
        self.obstacles = frozenset(obstacles)
        self.goal_pos = (grid_size - 1, grid_size - 1)
        self.period = period
        self.open_len = open_len
        self.tick = 0
        self.log = []
        self.agent = AGENT_START
        self._door_prev = None
        self._was_on_goal = False

    # ------------------------------------------------------------------
    # geometry helpers
    # ------------------------------------------------------------------
    def is_blocked_cell(self, cell):
        """True iff `cell` blocks movement (wall, obstacle, but never
        a door cell)."""
        x, _y = cell
        if cell in self.obstacles:
            return True
        return x in self.wall_xs and cell not in self.door_cells

    def blocked_cells(self):
        """All blocked cells (for verification, not for the agent)."""
        cells = set(self.obstacles)
        for wx in self.wall_xs:
            for y in range(self.grid_size):
                c = (wx, y)
                if c not in self.door_cells:
                    cells.add(c)
        return cells

    def next_door_index(self):
        """Index of the next door: the first door whose wall column
        the agent has not yet passed (agent.x <= wall_x); if the
        agent has passed every wall column, the last door."""
        ax = self.agent[0]
        for i, wx in enumerate(self.wall_xs):
            if ax <= wx:
                return i
        return len(self.wall_xs) - 1

    def next_door_cell(self):
        return self.door_cells[self.next_door_index()]

    # ------------------------------------------------------------------
    # World-compatible interface
    # ------------------------------------------------------------------
    def reset(self, start_tick=0):
        """Same contract as world.World.reset."""
        self.tick = start_tick
        self.agent = AGENT_START
        self.log = []
        self._door_prev = None
        self._was_on_goal = False

    def observe(self):
        """Read-only snapshot: (agent_position, next-door open now).

        The door state is the shared schedule's state at the
        current tick; it does not change the world in any way.
        """
        return (self.agent,
                door_is_open_exp1(self.tick, self.period, self.open_len))

    def step(self, action):
        """Mirror of world.World.step, with instance geometry.

        1) log the door transition if the shared schedule changed;
        2) crush if the agent is in ANY door cell while closed;
        3) move (blocked into wall/obstacle/closed-door cells);
        4) log goal arrivals on transition into the goal cell.
        """
        t = self.tick

        # 1) door state this tick; log initial state and transitions.
        open_now = door_is_open_exp1(t, self.period, self.open_len)
        if open_now != self._door_prev:
            self.log.append((t, "door", "open" if open_now else "closed"))
            self._door_prev = open_now

        # 2) crush check: caught in a door cell when the door is closed.
        if self.agent in self.door_cells and not open_now:
            self.log.append((t, "agent", "crushed"))
            self.agent = AGENT_START
            self._was_on_goal = False
            self.tick += 1
            return

        # 3) move the agent (actions are (dx, dy) pairs; clipped).
        dx, dy = action
        nx = min(max(self.agent[0] + dx, 0), self.grid_size - 1)
        ny = min(max(self.agent[1] + dy, 0), self.grid_size - 1)
        target = (nx, ny)
        enters_door_while_closed = (target in self.door_cells
                                    and not open_now)
        blocked = self.is_blocked_cell(target) or \
            enters_door_while_closed
        if blocked and target != self.agent:
            self.log.append((t, "agent", "blocked at (%d, %d)" % (nx, ny)))
        else:
            self.agent = target
            self.log.append((t, "agent", "move to (%d, %d)" % (nx, ny)))

        # 4) goal: log arrivals (transition into the goal cell only).
        on_goal = self.agent == self.goal_pos
        if on_goal and not self._was_on_goal:
            self.log.append((t, "goal", "reached"))
        self._was_on_goal = on_goal

        self.tick += 1


# ----------------------------------------------------------------------
# factories (one per world; all period=20, open_len=10)
# ----------------------------------------------------------------------

def make_w10():
    return Exp1World(10, [5], [(5, 5)])


def make_w10_heldout():
    return Exp1World(10, [5], [(5, 2)])


def make_w20():
    return Exp1World(20, [10], [(10, 10)])


def make_w20_heldout():
    return Exp1World(20, [10], [(10, 5)])


def make_w30():
    return Exp1World(30, [15], [(15, 15)])


def make_w30_heldout():
    return Exp1World(30, [15], [(15, 7)])


def make_m1():
    return Exp1World(20, [10], [(10, 10)], obstacles=M1_OBSTACLES)


def make_m2():
    return Exp1World(20, [10, 15], [(10, 10), (15, 10)])


def make_m3():
    return Exp1World(50, [25], [(25, 25)])


FACTORIES = {
    "W10": make_w10,
    "W10h": make_w10_heldout,
    "W20": make_w20,
    "W20h": make_w20_heldout,
    "W30": make_w30,
    "W30h": make_w30_heldout,
    "M1": make_m1,
    "M2": make_m2,
    "M3": make_m3,
}

# Sweep roles: inside trained worlds, their held-out variants, and
# outside (discovery-only) worlds. W10 is both a sweep world and the
# fidelity world (geometry identical to world.World).
INSIDE_WORLDS = ["W10", "W20", "W30"]
HELDOUT_OF = {"W10": "W10h", "W20": "W20h", "W30": "W30h"}
OUTSIDE_WORLDS = ["M1", "M2", "M3"]


def make_world(name):
    """Construct a fresh EXP1 world by registry name."""
    try:
        return FACTORIES[name]()
    except KeyError:
        raise ValueError("unknown EXP1 world %r" % (name,))


def bfs_path_exists(world, start=AGENT_START):
    """True iff a path start -> door(s) -> goal exists avoiding
    blocked cells (doors passable). Breadth-first search over the
    grid; doors must be visited in crossing order (left to right),
    which the search enforces by staging through each door cell."""
    blocked = world.blocked_cells()
    goal = world.goal_pos

    def reachable(a, b):
        seen = {a}
        q = deque([a])
        while q:
            x, y = q.popleft()
            if (x, y) == b:
                return True
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = (x + dx, y + dy)
                if (0 <= nb[0] < world.grid_size
                        and 0 <= nb[1] < world.grid_size
                        and nb not in seen and nb not in blocked):
                    seen.add(nb)
                    q.append(nb)
        return False

    cur = start
    for dc in world.door_cells:
        if not reachable(cur, dc):
            return False
        cur = dc
    return reachable(cur, goal)
