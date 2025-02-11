from numpy.f2py.auxfuncs import throw_error
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
    # seat_id[r][p]: the seat assignment (1..20) for participant p in round r
    seat_id = {}
    for r in range(num_rounds):
        for p in range(num_participants):
            seat_id[r, p] = model.NewIntVar(1, total_seats, f'seat_id_r{r}_p{p}')

    # Variables
    # t_i[r][p]: table (1 or 2) for participant p in round r
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

    # 2. Each participant occupies each seat number at most once
    for p in range(num_participants):
        model.AddAllDifferent([s_i[r, p] for r in range(num_rounds)])

    # 3. Each participant plays exactly once per round
    # (Already implied by the assignment of seat_id per round per participant)

    # 4. Compute how many times each pair of participants plays together
    times_together = {}
    deviations = []
    squared_deviations = []
    # Ideal number of times two participants should play together
    ideal_times_together = num_rounds

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

            # Calculate deviation from ideal_times_together
            deviation = model.NewIntVar(-num_rounds * num_tables, num_rounds * num_tables, f'deviation_p{p1}_p{p2}')
            model.Add(deviation == times_together[p1, p2] * num_tables - ideal_times_together)

            # Square the deviation
            deviation_abs = model.NewIntVar(0, num_rounds * num_tables, f'deviation_abs_p{p1}_p{p2}')
            model.Add(deviation_abs <= max_difference * num_tables)
            model.AddAbsEquality(deviation_abs, deviation)
            squared_deviation = model.NewIntVar(0, num_rounds * num_rounds * num_tables * num_tables, f'squared_deviation_p{p1}_p{p2}')
            model.AddMultiplicationEquality(squared_deviation, [deviation_abs, deviation_abs])
            squared_deviations.append(squared_deviation)

    # Objective: minimize total squared deviation
    model.Minimize(sum(squared_deviations))

    # Create the solver and solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 600.0  # Set a time limit if needed
    solver.parameters.num_search_workers = 8  # Set the number of search workers if needed
    solver.parameters.random_seed = 42  # Set a random seed if needed
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Print the seating arrangement
        rounds: dict[int, dict[int, dict[int, int]]] = {}
        for r in range(1, num_rounds + 1):
            rounds[r] = {}
            for t in range(1, num_tables + 1):
                rounds[r][t] = {}
                for s in range(1, SEATS_PER_TABLE + 1):
                    rounds[r][t][s] = 0
        for r in range(num_rounds):
            print(f'Round {r + 1}:')
            tables = {1: [], 2: []}
            for p in range(num_participants):
                table = solver.Value(t_i[r, p])
                seat = solver.Value(s_i[r, p])
                tables[table].append((p + 1, seat))
                rounds[r + 1][table][seat] = p
            for t in range(1, num_tables + 1):
                print(f'  Table {t}:')
                for p, seat in sorted(tables[t], key=lambda x: x[1]):
                    print(f'    Seat {seat}: Participant {p}')
            print()
        # Optionally, output the times each pair played together
        for p1 in range(num_participants):
            timess = []
            for p2 in range(p1 + 1, num_participants):
                times = solver.Value(times_together[p1, p2])
                timess.append(times)
            print(f'Participants {p1} played with another participants: {", ".join(map(str, timess))}')
        return rounds
    elif status == INFEASIBLE:
        print('Infeasible solution found.')
        raise Exception('Infeasible solution found')
    else:
        print('No solution found.')
        raise Exception('No solution found')


if __name__ == '__main__':
    print(generate_seats(10, 8, 4))
