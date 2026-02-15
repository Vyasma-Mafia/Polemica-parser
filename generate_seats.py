from ortools.sat.python import cp_model
from typing import List, Tuple, Dict, Optional
import json


class TournamentSeating:
    def __init__(self, num_participants: int, num_rounds: int, team_size: int, seats_per_table: int = 10):
        self.num_participants = num_participants
        self.num_rounds = num_rounds
        self.team_size = team_size
        self.seats_per_table = seats_per_table

        if num_participants % seats_per_table != 0:
            raise ValueError(f'num_participants ({num_participants}) must be a multiple of {seats_per_table}')

        self.num_tables = num_participants // seats_per_table

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        # Variables
        self.table_assignments = {}  # (round, player) -> table_id
        self.seat_assignments = {}  # (round, player) -> seat_num

        # Caches
        self.pair_meetings = {}  # (p1, p2) -> IntVar (number of times they meet)

        self._init_variables()

    def _init_variables(self):
        """Initialize CP-SAT variables."""
        for r in range(self.num_rounds):
            for p in range(self.num_participants):
                # Table: 1..num_tables
                self.table_assignments[r, p] = self.model.NewIntVar(1, self.num_tables, f't_r{r}_p{p}')
                # Seat: 1..seats_per_table
                self.seat_assignments[r, p] = self.model.NewIntVar(1, self.seats_per_table, f's_r{r}_p{p}')

    def add_base_constraints(self):
        """Add fundamental rules of the tournament."""
        # 1. All players must be in unique (Table, Seat) positions each round.
        for r in range(self.num_rounds):
            seat_ids = []
            for p in range(self.num_participants):
                # Create a unique identifier for (Table, Seat) pair
                # seat_id = (table - 1) * seats_per_table + (seat - 1)
                # Domain: 0 .. num_participants - 1
                t_idx = self.table_assignments[r, p] - 1
                s_idx = self.seat_assignments[r, p] - 1

                # We create a variable for seat_id to enforce AllDifferent
                sid = self.model.NewIntVar(0, self.num_participants - 1, f'sid_r{r}_p{p}')
                self.model.Add(sid == t_idx * self.seats_per_table + s_idx)
                seat_ids.append(sid)

            self.model.AddAllDifferent(seat_ids)

        # 2. Max usage of each seat number (at most twice per player across all rounds)
        for p in range(self.num_participants):
            for s in range(1, self.seats_per_table + 1):
                # We need to count how many times player 'p' is assigned to seat 's'
                is_in_seat_vars = []
                for r in range(self.num_rounds):
                    # Create a boolean: is_in_seat <=> seat_assignments[r, p] == s
                    b = self.model.NewBoolVar(f'p{p}_is_s{s}_r{r}')
                    self.model.Add(self.seat_assignments[r, p] == s).OnlyEnforceIf(b)
                    self.model.Add(self.seat_assignments[r, p] != s).OnlyEnforceIf(b.Not())
                    is_in_seat_vars.append(b)

                # Constraint: sum of matches <= 2
                self.model.Add(sum(is_in_seat_vars) <= ((self.num_rounds + 9) // 10))

    def add_constraints_from_config(self, exclusions: List[Tuple[int, int]], special_pairs: List[Tuple[int, int]]):
        """Add business constraints from configuration."""

        # 1. Team Constraints: Players with same (id // 2) cannot play at same table
        teams = {}
        for p in range(self.num_participants):
            team_id = p // self.team_size
            if team_id not in teams:
                teams[team_id] = []
            teams[team_id].append(p)

        for team_members in teams.values():
            if len(team_members) < 2:
                continue
            # Pairwise 'NotEqual' constraint for team members
            for i in range(len(team_members)):
                for j in range(i + 1, len(team_members)):
                    p1, p2 = team_members[i], team_members[j]
                    for r in range(self.num_rounds):
                        self.model.Add(self.table_assignments[r, p1] != self.table_assignments[r, p2])

        # 2. Special Pairs: Cannot play at same table
        for p1, p2 in special_pairs:
            for r in range(self.num_rounds):
                self.model.Add(self.table_assignments[r, p1] != self.table_assignments[r, p2])

        # 3. Excluded Tables: Specific players cannot play at specific tables
        for p, t in exclusions:
            for r in range(self.num_rounds):
                self.model.Add(self.table_assignments[r, p] != t)

    def add_symmetry_breaking(self):
        """Fix variables to reduce search space without losing valid solutions."""
        # Fix Player 0 to Table 1, Seat 1 in Round 0
        print("Adding symmetry breaking (P0 -> T1, S1 @ R0)...")
        self.model.Add(self.table_assignments[0, 0] == 1)
        self.model.Add(self.seat_assignments[0, 0] == 1)

    def add_fairness_objective(self, min_meetings=0, max_meetings=4, excluded_pairs: List[Tuple[int, int]] = None,
                               prefer_at_least_one=True):
        """
        Add fairness objective: minimize squared deviation from ideal meeting count.
        Ideal meetings per pair is num_rounds/num_tables. This approach penalizes outliers
        more heavily than max-min difference, producing more balanced distributions.

        Args:
            min_meetings: Hard minimum (0 = no hard constraint, use soft via objective)
            max_meetings: Hard maximum meetings per pair
            excluded_pairs: Pairs that cannot meet (already constrained to 0, skipped from objective)
            prefer_at_least_one: If True, add soft penalty for pairs that never meet
        """
        if excluded_pairs is None:
            excluded_pairs = []

        # Pre-process excluded pairs into a set for fast lookup (order independent)
        excluded_set = set()
        for p1, p2 in excluded_pairs:
            excluded_set.add(tuple(sorted((p1, p2))))

        ideal_meetings = self.num_rounds / self.num_tables
        print(
            f"Adding fairness objective (squared deviation): Min {min_meetings} (hard), Max {max_meetings} meetings per pair...")
        print(f"  Ideal meetings per pair: {ideal_meetings:.2f} (minimizing squared deviations from ideal)")
        if prefer_at_least_one:
            print("  Using soft constraint to prefer at least 1 meeting per pair (penalizes zero meetings).")
        print(f"Excluding {len(excluded_set)} special pairs from meeting constraints and objective.")

        meeting_vars = []
        zero_meeting_penalties = []
        squared_deviations = []

        # Ideal meetings per pair: num_rounds / num_tables
        # Use integer arithmetic: deviation = meetings * num_tables - num_rounds
        # When meetings = ideal, deviation = 0

        # Iterate all unique pairs
        for p1 in range(self.num_participants):
            for p2 in range(p1 + 1, self.num_participants):
                # Skip same team (already constrained to 0)
                is_team_member = (p1 // self.team_size == p2 // self.team_size)
                if is_team_member:
                    continue

                # Check if this pair is in special excluded list (e.g., cannot play together)
                is_special_pair = tuple(sorted((p1, p2))) in excluded_set
                is_excluded = is_special_pair

                # Calculate how many times they meet
                meet_vars = []
                for r in range(self.num_rounds):
                    # b = 1 if p1 and p2 are at the same table in round r
                    b = self.model.NewBoolVar(f'meet_{p1}_{p2}_r{r}')
                    self.model.Add(self.table_assignments[r, p1] == self.table_assignments[r, p2]).OnlyEnforceIf(b)
                    self.model.Add(self.table_assignments[r, p1] != self.table_assignments[r, p2]).OnlyEnforceIf(
                        b.Not())
                    meet_vars.append(b)

                # Meetings count variable
                meetings = self.model.NewIntVar(0, self.num_rounds, f'meetings_{p1}_{p2}')
                self.model.Add(meetings == sum(meet_vars))

                # Hard constraints
                # Skip min_meetings for special pairs (as they must be 0)
                if not is_excluded:
                    if min_meetings > 0:
                        self.model.Add(meetings >= min_meetings)

                if max_meetings < self.num_rounds:
                    self.model.Add(meetings <= max_meetings)

                # Soft constraint: penalize zero meetings (if prefer_at_least_one)
                # This helps even when min_meetings > 0, as it encourages meeting at least once
                if prefer_at_least_one and not is_excluded:
                    is_zero = self.model.NewBoolVar(f'zero_{p1}_{p2}')
                    self.model.Add(meetings == 0).OnlyEnforceIf(is_zero)
                    self.model.Add(meetings > 0).OnlyEnforceIf(is_zero.Not())
                    zero_meeting_penalties.append(is_zero)

                # Calculate squared deviation from ideal (only for non-excluded pairs)
                if not is_excluded:
                    # Deviation from ideal: deviation = meetings * num_tables - num_rounds
                    # When meetings = ideal (num_rounds/num_tables), deviation = 0
                    deviation = self.model.NewIntVar(
                        -self.num_rounds * self.num_tables,
                        self.num_rounds * self.num_tables,
                        f'deviation_{p1}_{p2}'
                    )
                    self.model.Add(deviation == meetings * self.num_tables - self.num_rounds)

                    # Absolute deviation
                    deviation_abs = self.model.NewIntVar(
                        0,
                        self.num_rounds * self.num_tables,
                        f'deviation_abs_{p1}_{p2}'
                    )
                    self.model.AddAbsEquality(deviation_abs, deviation)

                    # Squared deviation
                    # Maximum possible squared deviation: (num_rounds * num_tables)^2
                    max_squared = (self.num_rounds * self.num_tables) ** 2
                    squared_deviation = self.model.NewIntVar(
                        0,
                        max_squared,
                        f'squared_deviation_{p1}_{p2}'
                    )
                    self.model.AddMultiplicationEquality(squared_deviation, [deviation_abs, deviation_abs])
                    squared_deviations.append(squared_deviation)

                meeting_vars.append(meetings)
                self.pair_meetings[(p1, p2)] = meetings

        # Objective: minimize sum of squared deviations + zero-meeting penalties
        objective_terms = []

        if squared_deviations:
            objective_terms.extend(squared_deviations)

        # Add zero-meeting penalties with a weight (use a smaller weight to not dominate squared deviations)
        # Weight should be chosen so that one zero meeting penalty is less than typical squared deviation
        # For example, if ideal is ~2.8, a deviation of 1 gives squared deviation of 1
        # So we can use weight of 1 or less
        if prefer_at_least_one and zero_meeting_penalties:
            # Use weight of 1: each zero meeting adds 1 to objective
            # This is reasonable since squared deviations are typically larger
            objective_terms.extend(zero_meeting_penalties)

        if objective_terms:
            self.model.Minimize(sum(objective_terms))

    def solve(self, time_limit_seconds=300.0, stop_after_first=False, log_progress=False, two_phase=True):
        """
        Solve the model.

        If two_phase=True and an objective exists, first finds a feasible solution,
        then optimizes for the objective.
        """
        self.solver.parameters.max_time_in_seconds = time_limit_seconds
        self.solver.parameters.num_search_workers = 32
        self.solver.parameters.random_seed = 42
        self.solver.parameters.randomize_search = True
        self.solver.parameters.log_search_progress = log_progress

        if two_phase and not stop_after_first:
            # Phase 1: Find any feasible solution quickly
            print("Phase 1: Finding initial feasible solution...")
            self.solver.parameters.stop_after_first_solution = True
            self.solver.parameters.max_time_in_seconds = time_limit_seconds / 2
            status = self.solver.Solve(self.model)

            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                print("Phase 1 failed: No feasible solution found.")
                return status

            print(f"Phase 1 complete: Found feasible solution (obj={self.solver.ObjectiveValue()})")

            # Phase 2: Optimize
            print("Phase 2: Optimizing for fairness...")
            self.solver.parameters.stop_after_first_solution = False
            self.solver.parameters.max_time_in_seconds = time_limit_seconds
            status = self.solver.Solve(self.model)
            return status
        else:
            if stop_after_first:
                self.solver.parameters.stop_after_first_solution = True

            # Optionally enable logging to see objective improvement
            self.solver.parameters.log_search_progress = log_progress

            print(f"Solving with limit {time_limit_seconds}s (Stop First: {stop_after_first})...")
            status = self.solver.Solve(self.model)
            return status

    def export_solution_dict(self, status) -> Optional[Dict]:
        """
        Export solution in the format used by generate_tournament_seats.py.
        Returns: Dict[round (1-indexed)][table (1-indexed)][seat (1-indexed)] = player_id (0-indexed)
        """
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        seats = {}
        for r in range(self.num_rounds):
            round_num = r + 1  # Convert to 1-indexed
            seats[round_num] = {}

            # Initialize all tables
            for t in range(1, self.num_tables + 1):
                seats[round_num][t] = {}

            # Fill in player assignments
            for p in range(self.num_participants):
                t = self.solver.Value(self.table_assignments[r, p])
                s = self.solver.Value(self.seat_assignments[r, p])
                seats[round_num][t][s] = p

        return seats

    def print_solution(self, status):
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print(f"\nSolution found! Status: {self.solver.StatusName(status)}")
            print(f"Objective Value: {self.solver.ObjectiveValue()}")

            # Fairness stats
            if self.pair_meetings:
                meetings = [self.solver.Value(v) for v in self.pair_meetings.values()]
                print(
                    f"Pair Meetings Stats: Min={min(meetings)}, Max={max(meetings)}, Avg={sum(meetings) / len(meetings):.2f}")
                from collections import Counter
                c = Counter(meetings)
                print("Distribution of meetings (Count: Pairs):")
                for k in sorted(c.keys()):
                    print(f"  {k} meetings: {c[k]} pairs")

            print("\nRound 1 (Index 0) Configuration:")
            r = 0
            table_map = {t: [] for t in range(1, self.num_tables + 1)}
            for p in range(self.num_participants):
                t = self.solver.Value(self.table_assignments[r, p])
                s = self.solver.Value(self.seat_assignments[r, p])
                table_map[t].append((p, s))

            for t in sorted(table_map.keys()):
                print(f"  Table {t}: {sorted(table_map[t], key=lambda x: x[1])}")
        else:
            print("No solution found within time limit.")


def run_optimization():
    # --- Configuration ---
    NUM_PARTICIPANTS = 40
    NUM_ROUNDS = 8
    TEAM_SIZE = 2

    # Exclusions (Player ID, Table ID)
    # Table ID is 1-based (1..5)
    exclusions = []

    # Special Pairs (Player ID, Player ID) - Cannot sit at same table
    special_pairs = [
        (4, 6)
    ]

    # --- Execution ---
    generator = TournamentSeating(NUM_PARTICIPANTS, NUM_ROUNDS, TEAM_SIZE)

    generator.add_base_constraints()
    generator.add_constraints_from_config(exclusions, special_pairs)
    generator.add_symmetry_breaking()

    # Fairness:
    # 1. Soft constraint: Prefer everyone to play with everyone else at least once.
    #    - EXCEPTION: Special Pairs and Team Members are skipped.
    # 2. No one plays too often (max_meetings=4). This ensures balanced distribution.
    # 3. Objective minimizes maximum meetings and penalizes zero meetings for fairness.
    generator.add_fairness_objective(min_meetings=0, max_meetings=7, excluded_pairs=special_pairs,
                                     prefer_at_least_one=True)

    # Allow time to optimize for fairness
    status = generator.solve(time_limit_seconds=3000, stop_after_first=False, log_progress=True)
    generator.print_solution(status)

    # Export solution in the format for generate_tournament_seats.py
    seats_dict = generator.export_solution_dict(status)
    if seats_dict:
        print("\n" + "=" * 80)
        print("SOLUTION DICT (for generate_tournament_seats.py):")
        print("=" * 80)

        # Format as Python dict literal
        import pprint
        print("seats = ", end="")
        pprint.pprint(seats_dict, width=120, compact=False)
        print("=" * 80)

        # Also save to file as JSON
        output_file = "seats_solution.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(seats_dict, f, indent=1, ensure_ascii=False)
        print(f"\nSolution also saved to JSON file: {output_file}")

        # Save as Python code too
        python_file = "seats_solution.py"
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write("seats = ")
            import pprint
            pprint.pprint(seats_dict, stream=f, width=120, compact=False)
        print(f"Solution also saved as Python code: {python_file}")
    else:
        print("\nNo solution to export.")


if __name__ == "__main__":
    run_optimization()
