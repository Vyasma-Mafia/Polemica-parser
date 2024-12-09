import json
import os

import requests

from crawler import get_bearer_token

token = get_bearer_token()
headers = {'Authorization': f'Bearer {token}'}
baseurl = "https://app.polemicagame.com/v1"
competition_id = "2695"
members_url = baseurl + "/competitions/" + competition_id + "/members"
games_url = baseurl + "/competitions/" + competition_id + "/games"
tour_games_dir = "tour_games"

seats = {1: {1: {1: 0, 2: 1, 3: 2, 4: 12, 5: 10, 6: 5, 7: 16, 8: 17, 9: 19, 10: 14},
             2: {1: 4, 2: 3, 3: 8, 4: 13, 5: 15, 6: 6, 7: 18, 8: 7, 9: 9, 10: 11}},
         2: {1: {1: 2, 2: 15, 3: 19, 4: 9, 5: 3, 6: 0, 7: 6, 8: 14, 9: 16, 10: 12},
             2: {1: 8, 2: 17, 3: 18, 4: 4, 5: 7, 6: 11, 7: 1, 8: 13, 9: 5, 10: 10}},
         3: {1: {1: 13, 2: 8, 3: 5, 4: 1, 5: 6, 6: 14, 7: 9, 8: 16, 9: 18, 10: 0},
             2: {1: 19, 2: 10, 3: 12, 4: 17, 5: 11, 6: 4, 7: 7, 8: 3, 9: 2, 10: 15}},
         4: {1: {1: 18, 2: 12, 3: 3, 4: 5, 5: 14, 6: 19, 7: 17, 8: 6, 9: 13, 10: 7},
             2: {1: 9, 2: 2, 3: 16, 4: 10, 5: 4, 6: 8, 7: 11, 8: 15, 9: 0, 10: 1}},
         5: {1: {1: 15, 2: 16, 3: 14, 4: 6, 5: 5, 6: 10, 7: 3, 8: 4, 9: 1, 10: 19},
             2: {1: 7, 2: 9, 3: 17, 4: 11, 5: 2, 6: 12, 7: 0, 8: 18, 9: 8, 10: 13}},
         6: {1: {1: 17, 2: 13, 3: 4, 4: 8, 5: 19, 6: 16, 7: 14, 8: 11, 9: 7, 10: 9},
             2: {1: 12, 2: 5, 3: 0, 4: 15, 5: 1, 6: 18, 7: 2, 8: 10, 9: 3, 10: 6}},
         7: {1: {1: 16, 2: 19, 3: 7, 4: 0, 5: 12, 6: 3, 7: 8, 8: 1, 9: 4, 10: 18},
             2: {1: 5, 2: 11, 3: 15, 4: 14, 5: 17, 6: 13, 7: 10, 8: 9, 9: 6, 10: 2}}}


def crawl_games():
    games = requests.get(games_url, headers=headers).json()
    for game_id in games:
        game = requests.get(games_url + "/" + str(game_id["id"]) + "?version=4", headers=headers).json()
        game_num = game["num"]
        table_num = game["table"]
        with open(f"{tour_games_dir}/{game_num}_{table_num}.json", 'w', encoding='utf-8') as f:
            json.dump(game, f, ensure_ascii=False, indent=4)


def print_members():
    members = requests.get(members_url, headers=headers).json()
    print(list(map(lambda it: it['player']['id'], members)))
    for member in members:
        print(member['player']['id'], member['player']['username'])


def delete_games():
    games = requests.get(games_url, headers=headers).json()
    for game_id in games:
        requests.delete(games_url + "/" + str(game_id["id"]), headers=headers)


def save_modified_games():
    members = requests.get(members_url, headers=headers).json()

    for filename in os.listdir(tour_games_dir):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(tour_games_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            game = json.load(f)
            game_num = game["num"]
            table = game["table"]
            game["id"] = None

            # for player in game["players"]:
            #     member = members[seats[game_num][table][player["position"]] - 1]
            #     player["player"]["id"] = member["player"]["id"]
            #     player["username"] = member["player"]["username"]
            print(game["players"])
            print(requests.post(games_url, json=game, headers=headers))


def save_modified_games_in_overlay_service():
    # Base URLs for your API
    host = 'http://51.250.18.236:8090'  # Replace with your actual host
    overlay_game_players_url = f'{host}/gamePlayers'
    overlay_games_url = f'{host}/games'
    headers = {
        'Content-Type': 'application/json'
    }
    for filename in os.listdir(tour_games_dir):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(tour_games_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            game = json.load(f)
            game_num = game["num"]
            table = game["table"]
            game_id = game.get("id", None)

            players_urls = []  # List to collect player URLs
            for player in game["players"]:
                player_data = {
                    "nickname": player["username"],
                    "checks": [],  # Adjust this if you have actual check data
                    "stat": {},  # Adjust this if you have actual stat data
                    "role": player.get("role", "red"),  # Default role to "red" if not provided
                    "place": player["position"],
                    "photoUrl": f'https://storage.yandexcloud.net/mafia-photos/{player["player"]["id"]}.jpg'
                }

                # Create the gamePlayer
                response = requests.post(overlay_game_players_url, headers=headers, json=player_data)
                if response.status_code == 201:  # HTTP 201 Created
                    player_response = response.json()
                    player_url = player_response['_links']['self']['href']
                    players_urls.append(player_url)
                else:
                    print(f"Failed to create gamePlayer for {player['username']}: {response.text}")
                    # Handle the error as needed, possibly exit or skip this player/game

            # After all players are created, create the game
            game_data = {
                "type": "CUSTOM",
                    "tournamentId": 2695,  # Replace with your actual tournament ID
                "tableNum": table,
                "gameNum": game_num,
                "players": players_urls
            }

            # Create the game
            response = requests.post(overlay_games_url, headers=headers, json=game_data)
            if response.status_code == 201:  # HTTP 201 Created
                game_response = response.json()
                print(f"Successfully created game {game_num} at table {table}")
            else:
                print(f"Failed to create game {game_num} at table {table}: {response.text}")
                # Handle the error as needed


if __name__ == "__main__":
    # crawl_games()
    # print_members()
    delete_games()
    save_modified_games()
    # save_modified_games_in_overlay_service()
