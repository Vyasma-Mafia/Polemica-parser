import json
import os


def analyze_shots_and_checks(games_dir):
    stats = {
        "shot_sher_check_red_result_red_win": 0,
        "shot_sher_check_red_result_red_lose": 0,
        "shot_sher_check_black_result_red_win": 0,
        "shot_sher_check_black_result_red_lose": 0,
        "with_shot_peace": 0,
        "total_games": 0
    }

    for filename in os.listdir(games_dir):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(games_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            game_data = json.load(f)
            if game_data.get("result") is not None:
                stats["total_games"] += 1
            # Filter games where the first shot is by a role 3 player
            first_shot = list(
                set(map(lambda it: it["victim"],
                        filter(lambda it: it["night"] == 1,
                               game_data.get("shots", [])))))
            if len(first_shot) == 1:
                first_victim_role = list(map(lambda it: it["role"], filter(lambda it: it["position"] == first_shot[0],
                                                                           game_data.get("players", []))))[0]
                if first_victim_role in [2, 3]:
                    stats["with_shot_peace"] += 1
                if first_victim_role != 3:
                    continue
                # Find the first check made by a role 3 player
                for check in game_data.get('checks', []):
                    if check.get('role') == 3:
                        checked_player_role = next(
                            (player.get('role') for player in game_data.get('players', []) if
                             player.get('position') == check.get('player')),
                            None
                        )
                        result = game_data.get('result')

                        if checked_player_role == 2:
                            if result == 0:
                                stats["shot_sher_check_red_result_red_win"] += 1
                            else:
                                stats["shot_sher_check_red_result_red_lose"] += 1
                        elif checked_player_role in [0, 1]:
                            if result == 0:
                                stats["shot_sher_check_black_result_red_win"] += 1
                            else:
                                stats["shot_sher_check_black_result_red_lose"] += 1

                        # We've found the first check by role 3, so break out of the loop
                        break

    return stats


if __name__ == "__main__":
    # Path to the directory where the game files are stored
    games_dir = 'games'

    # Analyze the games and print the statistics
    statistics = analyze_shots_and_checks(games_dir)
    for (k, v) in statistics.items():
        print(k, v)
    # print(f"Statistics: {statistics}")
