from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import INFEASIBLE

SEATS_PER_TABLE = 10


def generate_seats(num_participants: int, num_rounds: int, max_difference: int):
    if num_participants % SEATS_PER_TABLE != 0:
        raise ValueError('num_participants must be a multiple of 10')
    num_tables = num_participants // SEATS_PER_TABLE
    total_seats = num_tables * SEATS_PER_TABLE

    model = cp_model.CpModel()

    # Variables
    # seat_id[r][p]: the seat assignment (1..total_seats) for participant p in round r
    seat_id = {}
    for r in range(num_rounds):
        for p in range(num_participants):
            seat_id[r, p] = model.NewIntVar(1, total_seats, f'seat_id_r{r}_p{p}')

    # Variables
    # t_i[r][p]: table (1..num_tables) for participant p in round r
    t_i = {}
    # s_i[r][p]: seat number (1..10) for participant p in round r
    s_i = {}
    for r in range(num_rounds):
        for p in range(num_participants):
            t_i[r, p] = model.NewIntVar(1, num_tables, f'table_r{r}_p{p}')
            s_i[r, p] = model.NewIntVar(1, SEATS_PER_TABLE, f'seat_r{r}_p{p}')
            # Link seat_id with t_i and s_i
            model.Add(seat_id[r, p] == (t_i[r, p] - 1) * SEATS_PER_TABLE + s_i[r, p])

    # Constraints
    # 1. In each round, all seat_ids must be different
    for r in range(num_rounds):
        model.AddAllDifferent([seat_id[r, p] for p in range(num_participants)])

    # 2. Each participant occupies each seat number at most twice
    for p in range(num_participants):
        for s in range(1, SEATS_PER_TABLE + 1):
            count_var = model.NewIntVar(0, 2, f'count_p{p}_s{s}')
            indicators = []
            for r in range(num_rounds):
                indicator = model.NewBoolVar(f'indicator_p{p}_s{s}_r{r}')
                model.Add(s_i[r, p] == s).OnlyEnforceIf(indicator)
                model.Add(s_i[r, p] != s).OnlyEnforceIf(indicator.Not())
                indicators.append(indicator)
            model.Add(count_var == sum(indicators))
            model.Add(count_var <= 2)  # Each participant can sit in each seat at most twice

    # 3. Each participant plays exactly once per round
    # (Already implied by the assignment of seat_id per round per participant)

    # 4. Team members (same remainder when divided by 3) cannot sit together
    for r in range(num_rounds):
        for p1 in range(num_participants):
            for p2 in range(p1 + 1, num_participants):
                if p1 // 3 == p2 // 3:  # Same team
                    model.Add(t_i[r, p1] != t_i[r, p2])

    # 5. Special constraints for specific pairs
    special_pairs = [(5, 42), (0, 42), (36, 43), (29, 33), (1, 33), (18, 33)]
    for r in range(num_rounds):
        for p1, p2 in special_pairs:
            model.Add(t_i[r, p1] != t_i[r, p2])

    # 6. Participant 30 should never be at table 3
    for r in range(num_rounds):
        model.Add(t_i[r, 30] != 3)

    # 7. Compute how many times each pair of participants plays together
    times_together = {}
    squared_deviations = []
    # Ideal is that each pair should play together num_rounds/num_tables times
    # We'll multiply by num_tables to avoid floats

    for p1 in range(num_participants):
        for p2 in range(p1 + 1, num_participants):
            times_together[p1, p2] = model.NewIntVar(0, num_rounds,
                                                     f'times_together_p{p1}_p{p2}')
            same_table = []
            for r in range(num_rounds):
                st = model.NewBoolVar(f'same_table_r{r}_p{p1}_p{p2}')
                model.Add(t_i[r, p1] == t_i[r, p2]).OnlyEnforceIf(st)
                model.Add(t_i[r, p1] != t_i[r, p2]).OnlyEnforceIf(st.Not())
                same_table.append(st)
            model.Add(times_together[p1, p2] == sum(same_table))

            # Calculate deviation from ideal (num_rounds/num_tables)
            # Multiply by num_tables to get rid of fractions
            deviation = model.NewIntVar(-num_rounds * num_tables, num_rounds * num_tables, f'deviation_p{p1}_p{p2}')
            model.Add(deviation == times_together[p1, p2] * num_tables - num_rounds)

            # Square the deviation
            deviation_abs = model.NewIntVar(0, num_rounds * num_tables, f'deviation_abs_p{p1}_p{p2}')
            model.Add(deviation_abs <= max_difference * num_tables)
            model.AddAbsEquality(deviation_abs, deviation)
            squared_deviation = model.NewIntVar(0, (num_rounds * num_tables) ** 2, f'squared_deviation_p{p1}_p{p2}')
            model.AddMultiplicationEquality(squared_deviation, [deviation_abs, deviation_abs])
            squared_deviations.append(squared_deviation)

    # Objective: minimize total squared deviation
    model.Minimize(sum(squared_deviations))

    # Create the solver and solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 1800.0  # Set a time limit to 30 minutes
    solver.parameters.num_search_workers = 8  # Set the number of search workers
    solver.parameters.random_seed = 42  # Set a random seed
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Print the seating arrangement
        rounds = {}
        for r in range(1, num_rounds + 1):
            rounds[r] = {}
            for t in range(1, num_tables + 1):
                rounds[r][t] = {}
                for s in range(1, SEATS_PER_TABLE + 1):
                    rounds[r][t][s] = 0
        for r in range(num_rounds):
            print(f'Round {r + 1}:')
            tables = {t: [] for t in range(1, num_tables + 1)}
            for p in range(num_participants):
                table = solver.Value(t_i[r, p])
                seat = solver.Value(s_i[r, p])
                tables[table].append((p, seat))
                rounds[r + 1][table][seat] = p
            for t in range(1, num_tables + 1):
                print(f'  Table {t}:')
                for p, seat in sorted(tables[t], key=lambda x: x[1]):
                    print(f'    Seat {seat}: Participant {p}')
            print()

        # Print statistics about how often pairs play together
        for p in range(num_participants):
            times_list = []
            for other_p in range(num_participants):
                if p != other_p:
                    if p < other_p:
                        times = solver.Value(times_together[p, other_p])
                    else:
                        times = solver.Value(times_together[other_p, p])
                    times_list.append(times)
            avg = sum(times_list) / len(times_list)
            min_val = min(times_list)
            max_val = max(times_list)
            print(f'Participant {p}: Average {avg:.2f}, Min {min_val}, Max {max_val}')

        return rounds
    elif status == INFEASIBLE:
        print('Infeasible solution found.')
        raise Exception('Infeasible solution found')
    else:
        print('No solution found.')
        raise Exception('No solution found')


if __name__ == '__main__':
    print(generate_seats(50, 15, 4))  # 50 participants, 15 rounds, max deviation of 6
