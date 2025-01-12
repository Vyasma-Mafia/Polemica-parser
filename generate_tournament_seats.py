import json
import os

import requests
import random

from crawler import get_bearer_token

POLEMICA_USERNAME = os.getenv("POLEMICA_USERNAME")
POLEMICA_PASSWORD = os.getenv("POLEMICA_PASSWORD")

random.seed(42)
token = get_bearer_token()
headers = {'Authorization': f'Bearer {token}'}
baseurl = "https://app.polemicagame.com/v1"
competition_id = "2873"
members_url = baseurl + "/competitions/" + competition_id + "/members"
games_url = baseurl + "/competitions/" + competition_id + "/games"
tour_games_dir = "tour_games"


def authorize():
    global token, headers
    token = requests.post(baseurl + "/auth/login",
                          data={"username": POLEMICA_USERNAME, "password": POLEMICA_PASSWORD}).json()["access_token"]
    headers = {'Authorization': f'Bearer {token}'}


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
    # print(list(map(lambda it: it['player']['id'], members)))
    for member in members:
        print(member['player']['id'], member['player']['username'])


def delete_games():
    games = requests.get(games_url, headers=headers).json()
    for game_id in games:
        print("Delete", requests.delete(games_url + "/" + str(game_id["id"]), headers=headers))


def save_modified_games():
    members = requests.get(members_url, headers=headers).json()
    # random.shuffle(masters)
    for filename in os.listdir(tour_games_dir):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(tour_games_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            game = json.load(f)
            game_num = game["num"]
            table = game["table"]
            game["id"] = None
            game["isLive"] = True
            # master = masters[game_num - 1]
            # gameMembers = list(filter(lambda it: it["player"]["id"] != master, members))
            # random.shuffle(gameMembers)
            # for player, member in zip(game["players"], gameMembers):
            #     player["player"]["id"] = member["player"]["id"]
            #     player["username"] = member["player"]["username"]
            # game["master"] = master
            # game["referee"]["id"] = master
            res = requests.post(games_url, json=game, headers=headers)
            print(res.status_code, res.text)


def save_modified_games_in_overlay_service():
    # Base URLs for your API
    host = 'http://51.250.18.236:8090'  # Replace with your actual host
    # host = 'http://localhost:8080'  # Replace with your actual host
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
                    "guess": [],  # Adjust this if you have actual check data
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
                "type": "POLEMICA",
                "tournamentId": competition_id,  # Replace with your actual tournament ID
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
    authorize()
    crawl_games()
    print_members()
    delete_games()
    save_modified_games()
    save_modified_games_in_overlay_service()
