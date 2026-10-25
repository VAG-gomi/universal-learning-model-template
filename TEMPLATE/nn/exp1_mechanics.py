#!/usr/bin/env python3
"""exp1_mechanics.py -- EXP1 Step 0 mechanics checks (§2.5(b)).

Scripted, deterministic, NO training. Verifies for every EXP1
world (W20, W30, M1, M2, M3, plus the W10 trained world, the
three held-out variants, and W10-vs-World equivalence):
  reset contract, bounds clipping, wall blocking, door
  closed-entry blocked, door open-entry allowed, crush
  (enter on the last open tick, then stay -> crushed),
  goal-reached logging, observe() read-only, the 20/10
  door schedule over 60 ticks, and a full log audit
  (no "move to" ever lands on a blocked cell or a
  closed door cell). M1 additionally: obstacles block
  and a BFS path start -> door -> goal exists. M2
  additionally: the next-door-bit region rule and a
  crush at the second door. W10 additionally: a
  scripted walk on make_w10() produces logs identical
  to the same walk on world.World(20, 10).

Prints one line per check; exits 0 iff every check passes.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from world import World, ACTIONS
from world_exp1 import (PERIOD, OPEN_LEN, make_world, bfs_path_exists,
                        M1_OBSTACLES)

RESULTS = []
ALL_LOGS = {}  # world name -> concatenated logs (for the audit)


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print("%-58s %s %s" % (name, "PASS" if ok else "FAIL", detail))


def walk_to(w, tx, ty, cap=500):
    """Walk to (tx, ty) moving y-first then x. Y-first matters:
    the scripted paths run down the start column and then
    along the door row, never along row 0 into a wall column.
    Paths used here avoid blocked cells by construction."""
    steps = 0
    while w.agent != (tx, ty) and steps < cap:
        x, y = w.agent
        if y != ty:
            w.step((0, 1 if ty > y else -1))
        else:
            w.step((1 if tx > x else -1, 0))
        steps += 1
    return w.agent == (tx, ty)


def wait_until_phase(w, phase, cap=40):
    while w.tick % PERIOD != phase and cap > 0:
        w.step(ACTIONS["stay"])
        cap -= 1
    return w.tick % PERIOD == phase


def cross_door(w, staging, door):
    """Cross one door safely: walk to staging, wait for
    phase 8, push (enters on phase 8), step right at once
    (exits on phase 9, still open). Entering on phase 9
    and leaving on phase 10 would be a crush -- the
    world's rule, not a script bug -- so crossings are
    timed to phase 8, never phase 9."""
    if not walk_to(w, staging[0], staging[1]):
        return False
    if not wait_until_phase(w, 8):
        return False
    w.step(ACTIONS["right"])
    if w.agent != door:
        return False
    w.step(ACTIONS["right"])
    return w.agent == (door[0] + 1, door[1])


def goal_walk(w, legs, goal):
    """Scripted path: for each (staging, door) leg, cross
    the door safely; then walk right along the last
    door's row, then down the goal column. M2 has two
    legs; every other world has one."""
    for staging, door in legs:
        if not cross_door(w, staging, door):
            return False
    last_door = legs[-1][1]
    if not walk_to(w, goal[0], last_door[1]):
        return False
    if not walk_to(w, goal[0], goal[1]):
        return False
    return w.agent == goal


# (world, [(staging, door), ...], goal) per world.
WORLDS = {
    "W10": ([((4, 5), (5, 5))], (9, 9)),
    "W10h": ([((4, 2), (5, 2))], (9, 9)),
    "W20": ([((9, 10), (10, 10))], (19, 19)),
    "W20h": ([((9, 5), (10, 5))], (19, 19)),
    "W30": ([((14, 15), (15, 15))], (29, 29)),
    "W30h": ([((14, 7), (15, 7))], (29, 29)),
    "M1": ([((9, 10), (10, 10))], (19, 19)),
    "M2": ([((9, 10), (10, 10)), ((14, 10), (15, 10))], (19, 19)),
    "M3": ([((24, 25), (25, 25))], (49, 49)),
}


def run_world_checks(name):
    legs, goal = WORLDS[name]
    staging, door = legs[0]
    w = make_world(name)
    logs = []

    # --- reset contract ---
    w.step(ACTIONS["right"])
    w.reset(start_tick=7)
    check("%s reset(start_tick=7)" % name,
          w.tick == 7 and w.agent == (0, 0) and w.log == []
          and w.period == PERIOD and w.open_len == OPEN_LEN,
          "tick=%d agent=%s log=%d" % (w.tick, w.agent, len(w.log)))
    w.reset()

    # --- bounds clipping ---
    w.step(ACTIONS["left"])
    w.step(ACTIONS["up"])
    check("%s bounds clip at (0,0)" % name, w.agent == (0, 0),
          "agent=%s" % (w.agent,))
    w.reset()

    # --- wall blocking (non-door row) ---
    wall_x = door[0]
    wall_row = door[1] + 1 if door[1] + 1 < w.grid_size else door[1] - 1
    walk_to(w, wall_x - 1, wall_row)
    before = w.agent
    w.step(ACTIONS["right"])
    check("%s wall push blocked" % name,
          w.agent == before
          and w.log[-1] == (w.tick - 1, "agent",
                            "blocked at (%d, %d)" % (wall_x, wall_row)),
          "agent=%s last=%s" % (w.agent, w.log[-1]))
    logs += w.log
    w.reset()

    # --- door closed-entry blocked / open-entry allowed ---
    walk_to(w, staging[0], staging[1])
    wait_until_phase(w, 15)
    w.step(ACTIONS["right"])
    check("%s closed door push blocked" % name,
          w.agent == staging
          and "blocked at (%d, %d)" % door in w.log[-1][2],
          "agent=%s last=%s" % (w.agent, w.log[-1]))
    wait_until_phase(w, 0)
    w.step(ACTIONS["right"])
    check("%s open door entry allowed" % name, w.agent == door,
          "agent=%s" % (w.agent,))
    logs += w.log
    w.reset()

    # --- crush: enter on the last open tick (phase 9), then stay ---
    walk_to(w, staging[0], staging[1])
    wait_until_phase(w, 9)
    t_enter = w.tick
    w.step(ACTIONS["right"])
    entered = w.agent == door
    t_crush = w.tick
    w.step(ACTIONS["stay"])
    crushed = (t_crush, "agent", "crushed") in w.log
    no_move = not any(e[0] == t_crush and e[2].startswith("move to")
                      for e in w.log)
    check("%s crush on last-open entry" % name,
          entered and crushed and no_move and w.agent == (0, 0),
          "enter_tick=%d crush_tick=%d agent=%s"
          % (t_enter, t_crush, w.agent))
    logs += w.log
    w.reset()

    # --- goal walk ---
    ok = goal_walk(w, legs, goal)
    reached = any(e[1] == "goal" and e[2] == "reached" for e in w.log)
    check("%s scripted goal walk" % name, ok and reached,
          "agent=%s ticks=%d" % (w.agent, w.tick))
    logs += w.log
    w.reset()

    # --- observe() read-only ---
    o1 = w.observe()
    tick0, log0 = w.tick, list(w.log)
    o2 = w.observe()
    o3 = w.observe()
    check("%s observe read-only" % name,
          o1 == o2 == o3 and w.tick == tick0 and w.log == log0,
          "obs=%s" % (o1,))

    # --- door schedule over 60 ticks ---
    w.reset()
    for _ in range(60):
        w.step(ACTIONS["stay"])
    expected = [(0, "door", "open"), (10, "door", "closed"),
                (20, "door", "open"), (30, "door", "closed"),
                (40, "door", "open"), (50, "door", "closed")]
    actual = [e for e in w.log if e[1] == "door"]
    check("%s 20/10 door schedule" % name, actual == expected,
          "events=%d" % len(actual))
    logs += w.log
    ALL_LOGS[name] = logs
    return w


def run_m1_checks():
    w = make_world("M1")
    # Obstacle push: (3,2) -> right into obstacle (4,2).
    walk_to(w, 3, 2)
    w.step(ACTIONS["right"])
    check("M1 obstacle push blocked",
          w.agent == (3, 2)
          and w.log[-1][2] == "blocked at (4, 2)",
          "agent=%s last=%s" % (w.agent, w.log[-1]))
    check("M1 BFS path start->door->goal", bfs_path_exists(w),
          "obstacles=%d" % len(M1_OBSTACLES))
    # No obstacle touches start, goal, door, or door approaches.
    bad = [c for c in M1_OBSTACLES
           if c in [(0, 0), (19, 19), (10, 10), (9, 10), (11, 10)]]
    check("M1 obstacles avoid key cells", not bad, "bad=%s" % (bad,))


def run_m2_checks():
    w = make_world("M2")
    # Next-door region rule (index selection; values coincide
    # under the shared schedule, so the index is the check).
    w.agent = (0, 0)
    i0 = w.next_door_index()
    w.agent = (10, 10)
    i1 = w.next_door_index()
    w.agent = (11, 10)
    i2 = w.next_door_index()
    w.agent = (15, 10)
    i3 = w.next_door_index()
    w.agent = (16, 10)
    i4 = w.next_door_index()
    check("M2 next-door region rule",
          (i0, i1, i2, i3, i4) == (0, 0, 1, 1, 1),
          "indices=%s" % ((i0, i1, i2, i3, i4),))
    # Crush at the second door: cross door1 safely, stage
    # at (14,10), enter door2 on phase 9, stay -> crushed.
    w.reset()
    cross_door(w, (9, 10), (10, 10))
    walk_to(w, 14, 10)
    wait_until_phase(w, 9)
    w.step(ACTIONS["right"])
    entered2 = w.agent == (15, 10)
    t_crush = w.tick
    w.step(ACTIONS["stay"])
    check("M2 crush at second door",
          entered2 and (t_crush, "agent", "crushed") in w.log
          and w.agent == (0, 0),
          "agent=%s crush_tick=%d" % (w.agent, t_crush))
    # Wall2 push blocked on a non-door row.
    w.reset()
    cross_door(w, (9, 10), (10, 10))
    walk_to(w, 14, 11)
    w.step(ACTIONS["right"])
    check("M2 second wall push blocked",
          w.agent == (14, 11)
          and w.log[-1][2] == "blocked at (15, 11)",
          "agent=%s last=%s" % (w.agent, w.log[-1]))


def run_w10_equivalence():
    """Same scripted walk on make_w10() and World(20, 10):
    logs must be identical."""
    def drive(w):
        cross_door(w, (4, 5), (5, 5))
        walk_to(w, 9, 5)
        walk_to(w, 9, 9)
        return list(w.log)

    a = make_world("W10")
    b = World(period=PERIOD, open_len=OPEN_LEN)
    la, lb = drive(a), drive(b)
    check("W10 make_w10 == World(20,10) logs",
          la == lb and a.agent == b.agent == (9, 9),
          "events=%d/%d agent=%s" % (len(la), len(lb), a.agent))


def run_log_audit():
    """No 'move to' in any mechanics log lands on a blocked
    cell or a closed door cell."""
    bad = []
    for name, logs in ALL_LOGS.items():
        w = make_world(name)
        blocked = w.blocked_cells()
        doors = set(w.door_cells)
        for tick, node, event in logs:
            if node == "agent" and event.startswith("move to ("):
                x, y = (int(v) for v in
                        event[len("move to ("):-1].split(","))
                if (x, y) in blocked:
                    bad.append((name, tick, event, "blocked cell"))
                if (x, y) in doors and (tick % PERIOD) >= OPEN_LEN:
                    bad.append((name, tick, event, "closed door"))
    check("log audit: no blocked/closed-door landings", not bad,
          "violations=%d" % len(bad))


def main():
    for name in WORLDS:
        run_world_checks(name)
    run_m1_checks()
    run_m2_checks()
    run_w10_equivalence()
    run_log_audit()
    n_ok = sum(1 for _n, ok, _d in RESULTS if ok)
    print("MECHANICS: %d/%d PASS" % (n_ok, len(RESULTS)))
    if n_ok != len(RESULTS):
        for n, ok, d in RESULTS:
            if not ok:
                print("  FAILED: %s %s" % (n, d))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
