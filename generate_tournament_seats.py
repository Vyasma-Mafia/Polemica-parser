import json
import os
from collections import defaultdict
from datetime import datetime
from random import shuffle

import requests
import random

from crawler import get_bearer_token

POLEMICA_USERNAME = os.getenv("POLEMICA_USERNAME")
POLEMICA_PASSWORD = os.getenv("POLEMICA_PASSWORD")

random.seed(42)
token = get_bearer_token()
headers = {'Authorization': f'Bearer {token}'}
baseurl = "https://app.polemicagame.com/v1"
competition_id = "4822"
members_url = baseurl + "/competitions/" + competition_id + "/members"
teams_url = baseurl + "/competitions/" + competition_id + "/teams"
games_url = baseurl + "/competitions/" + competition_id + "/games"
admins_url = baseurl + "/competitions/" + competition_id + "/admins"
tour_games_dir = "tour_games"
seats = {1: {1: {1: 0, 2: 3, 3: 18, 4: 25, 5: 14, 6: 29, 7: 34, 8: 8, 9: 33, 10: 21},
             2: {1: 31, 2: 26, 3: 28, 4: 39, 5: 10, 6: 23, 7: 13, 8: 19, 9: 6, 10: 1},
             3: {1: 32, 2: 17, 3: 4, 4: 9, 5: 36, 6: 24, 7: 2, 8: 38, 9: 15, 10: 35},
             4: {1: 30, 2: 37, 3: 11, 4: 16, 5: 22, 6: 12, 7: 20, 8: 7, 9: 27, 10: 5}},
         2: {1: {1: 24, 2: 16, 3: 26, 4: 8, 5: 12, 6: 14, 7: 21, 8: 23, 9: 30, 10: 38},
             2: {1: 20, 2: 0, 3: 29, 4: 22, 5: 15, 6: 2, 7: 31, 8: 33, 9: 34, 10: 6},
             3: {1: 11, 2: 27, 3: 19, 4: 28, 5: 37, 6: 3, 7: 1, 8: 4, 9: 17, 10: 9},
             4: {1: 18, 2: 25, 3: 39, 4: 7, 5: 32, 6: 13, 7: 36, 8: 5, 9: 35, 10: 10}},
         3: {1: {1: 27, 2: 22, 3: 36, 4: 3, 5: 39, 6: 34, 7: 8, 8: 10, 9: 16, 10: 4},
             2: {1: 13, 2: 20, 3: 5, 4: 14, 5: 2, 6: 9, 7: 0, 8: 24, 9: 26, 10: 31},
             3: {1: 12, 2: 28, 3: 23, 4: 33, 5: 18, 6: 37, 7: 25, 8: 15, 9: 7, 10: 17},
             4: {1: 29, 2: 35, 3: 6, 4: 38, 5: 21, 6: 11, 7: 32, 8: 1, 9: 19, 10: 30}},
         4: {1: {1: 7, 2: 14, 3: 21, 4: 10, 5: 0, 6: 28, 7: 35, 8: 22, 9: 9, 10: 37},
             2: {1: 2, 2: 31, 3: 16, 4: 29, 5: 11, 6: 26, 7: 19, 8: 12, 9: 25, 10: 36},
             3: {1: 5, 2: 38, 3: 27, 4: 15, 5: 6, 6: 20, 7: 23, 8: 32, 9: 3, 10: 8},
             4: {1: 39, 2: 4, 3: 34, 4: 24, 5: 33, 6: 1, 7: 30, 8: 17, 9: 18, 10: 13}},
         5: {1: {1: 22, 2: 34, 3: 7, 4: 1, 5: 38, 6: 17, 7: 5, 8: 29, 9: 10, 10: 26},
             2: {1: 28, 2: 32, 3: 12, 4: 31, 5: 27, 6: 0, 7: 24, 8: 18, 9: 39, 10: 14},
             3: {1: 33, 2: 21, 3: 9, 4: 36, 5: 3, 6: 15, 7: 6, 8: 16, 9: 13, 10: 11},
             4: {1: 35, 2: 23, 3: 37, 4: 30, 5: 20, 6: 8, 7: 4, 8: 25, 9: 2, 10: 19}},
         6: {1: {1: 10, 2: 18, 3: 38, 4: 27, 5: 30, 6: 25, 7: 29, 8: 9, 9: 12, 10: 15},
             2: {1: 19, 2: 5, 3: 33, 4: 2, 5: 24, 6: 21, 7: 7, 8: 28, 9: 8, 10: 22},
             3: {1: 4, 2: 11, 3: 31, 4: 0, 5: 13, 6: 16, 7: 37, 8: 34, 9: 32, 10: 23},
             4: {1: 26, 2: 36, 3: 3, 4: 20, 5: 1, 6: 35, 7: 17, 8: 6, 9: 14, 10: 39}},
         7: {1: {1: 36, 2: 33, 3: 0, 4: 19, 5: 23, 6: 30, 7: 9, 8: 27, 9: 5, 10: 34},
             2: {1: 37, 2: 24, 3: 10, 4: 18, 5: 26, 6: 32, 7: 16, 8: 3, 9: 29, 10: 20},
             3: {1: 25, 2: 6, 3: 13, 4: 11, 5: 17, 6: 22, 7: 14, 8: 2, 9: 38, 10: 28},
             4: {1: 1, 2: 12, 3: 8, 4: 35, 5: 31, 6: 39, 7: 15, 8: 21, 9: 4, 10: 7}},
         8: {1: {1: 3, 2: 10, 3: 14, 4: 4, 5: 7, 6: 19, 7: 38, 8: 20, 9: 31, 10: 33},
             2: {1: 15, 2: 30, 3: 17, 4: 32, 5: 8, 6: 36, 7: 11, 8: 26, 9: 28, 10: 0},
             3: {1: 16, 2: 1, 3: 35, 4: 21, 5: 25, 6: 27, 7: 18, 8: 13, 9: 22, 10: 2},
             4: {1: 34, 2: 9, 3: 24, 4: 37, 5: 5, 6: 6, 7: 12, 8: 39, 9: 23, 10: 29}}}


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


def check_games():
    d = defaultdict(lambda: defaultdict(int))
    games = requests.get(games_url, headers=headers).json()
    for game_id in games:
        game = requests.get(games_url + "/" + str(game_id["id"]) + "?version=4", headers=headers).json()
        for player, i in zip(game["players"], range(len(game["players"]))):
            d[player["player"]["username"]][i + 1] += 1
            print(f'{game["num"]},1,{i + 1},{player["player"]["username"]}')
    for k, v in d.items():
        for k1, v1 in v.items():
            if (v1 != 2):
                print(k, k1, v1)


def print_members():
    players = get_members()
    # print(list(map(lambda it: it['player']['id'], members)))
    for i, (id, username) in zip(range(len(players)), players):
        print(i, id, username)


def get_members():
    players = []
    members = requests.get(members_url, headers=headers).json()
    teams = requests.get(teams_url, headers=headers).json()
    for team in sorted(teams, key=lambda x: -len(x["members"])):
        for member in team["members"]:
            players.append((member['id'], member['username']))
    for member in members:
        if (member['player']['id'], member['player']['username']) not in players:
            players.append((member['player']['id'], member['player']['username']))
    return players


def create_games():
    members = get_members()

    # val admins: Map<Long, PolemicaUser> =
    #             polemicaClient.getCompetitionAdmins(3359).associateBy { it.player.id }.mapValues { it.value.player }
    admins = requests.get(admins_url, headers=headers).json()
    admins = {admin['player']['id']: admin['player'] for admin in admins}
    admin_by_table_num = {
        1: 27516,
        2: 70516,
        3: 86000,
        4: 89123
    }
    for game_num in range(1, 8 + 1):
        for table_num in range(1, 5):
            players = list(map(lambda it: {
                "position": it,
                "username": members[seats[game_num][table_num][it]][1],
                "role": 2,
                "techs": [],
                "fouls": [],
                "guess": None,
                "player": {
                    "id": members[seats[game_num][table_num][it]][0],
                    "username": members[seats[game_num][table_num][it]][1]
                },
                "disqual": None,
                "award": None
            }, range(1, 11)))

            game = {
                "id": None,
                "master": admin_by_table_num[table_num],
                "referee": {
                    "id": admin_by_table_num[table_num],
                    "username": admins[admin_by_table_num[table_num]]["username"]
                },
                "scoringVersion": "3.0",
                "scoringType": 1,
                "version": 4,
                "zeroVoting": "none",
                "tags": None,
                "players": players,
                "checks": [],
                "shots": [],
                "stage": None,
                "votes": [],
                "comKiller": None,
                "bonuses": [],
                "started": datetime.now().isoformat(),
                "stop": None,
                "isLive": True,
                "result": None,
                "num": game_num,
                "table": table_num,
                "phase": 0,
                "factor": 1.0
            }
            res = requests.post(games_url, json=game, headers=headers)
            print(res.status_code, res.text)


def delete_games():
    games = requests.get(games_url, headers=headers).json()
    for game in games:
        if game.get("result", None) is not None:
            continue
        print("Delete", requests.delete(games_url + "/" + str(game["id"]), headers=headers))


def save_modified_games():
    members = requests.get(members_url, headers=headers).json()
    # random.shuffle(masters)
    for filename in os.listdir(tour_games_dir):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(tour_games_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            game = json.load(f)
            if game.get("result", None) is not None:
                continue
            game_num = game["num"]
            table = game["table"]
            if (table > 1):
                continue
            game["id"] = None
            game["isLive"] = True
            # master = masters[game_num - 1]
            # gameMembers = list(filter(lambda it: it["player"]["id"] != master, members))
            # random.shuffle(gameMembers)
            for player in game["players"]:
                print()
                member = members[seats[game_num][table][player["position"]] - 1]
                player["player"] = {}
                player["player"]["id"] = member["player"]["id"]
                player["username"] = member["player"]["username"]
            # game["master"] = master
            # game["referee"]["id"] = master
            res = requests.post(games_url, json=game, headers=headers)
            print(res.status_code, res.text)


def save_modified_games_in_overlay_service():
    # Base URLs for your API
    # host = 'http://51.250.18.236:8090'  # Replace with your actual host
    host = 'http://localhost:8080'  # Replace with your actual host
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
            # if game.get("result", None) is not None:
            #     continue

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


def update_overlay_game_texts():
    games = requests.get("http://51.250.18.236:8090/games?size=500").json()["_embedded"]["games"]
    for game in games:
        if game["tournamentId"] != 3359:
            continue
        print(game)
        text = f"Aurora Cup | Стол {game['tableNum']} | Игра {game['gameNum']}"
        requests.patch(game["_links"]["self"]["href"], json={"text": text})


if __name__ == "__main__":
    authorize()
    print_members()
    # crawl_games()
    # check_games()
    delete_games()
    create_games()
    # save_modified_games()
    # save_modified_games_in_overlay_service()
    # update_overlay_game_texts()
    # print(players)
