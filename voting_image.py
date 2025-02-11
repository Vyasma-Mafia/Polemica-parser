from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def plot_game(
    num_players = 10,
    absent_players = [],
    verified_red_players = [],
    sheriffs = [],
    votes = [],
    round_edges=True
):

    tmp = defaultdict(list)
    for (f, t) in votes:
        tmp[t].append((f, t))
    tmp2 = dict()
    for i, (k, v) in enumerate(tmp.items()):
        for e in v:
            tmp2[e] = i + 1
    votes = tmp2
    # Создаем граф
    G = nx.DiGraph()

    # Все игроки
    all_players = list(range(1, num_players + 1))
    G.add_nodes_from(all_players)

    # Добавляем связи между игроками
    G.add_edges_from(votes.keys())

    # Определяем позиции узлов по кругу
    angle = np.linspace(0, 2 * np.pi, len(all_players), endpoint=False)
    pos = {player: (np.cos(a + np.pi), np.sin(a)) for player, a in zip(all_players, angle)}

    # Цвет узлов: серый для покинувших игроков, красный для проверенных красных, зеленый для остальных
    node_colors = [
        'gray' if node in absent_players
        else 'red' if node in verified_red_players
        else 'yellow' if node in sheriffs
        else 'green' for node in all_players
    ]

    # Подписываем участников
    labels = {player: f"{player}" for player in all_players}

    # Цвета для схем голосования
    distinct_colors = ['blue', 'green', 'orange', 'purple', 'pink', 'brown']
    vote_colors = {key: distinct_colors[idx % len(distinct_colors)] for idx, key in enumerate(set(votes.values()))}

    # Получаем цвета для каждого ребра на основе голосования
    edge_colors = [vote_colors[votes[edge]] for edge in G.edges()]

    # Настройка для рисования кривых линий
    connectionstyle = 'arc3,rad=0.2' if round_edges else 'arc3,rad=0.0'

    # Создаем круговую визуализацию графа
    plt.figure(figsize=(10, 10))
    nx.draw(
        G,
        pos,
        with_labels=True,
        labels=labels,
        node_color=node_colors,
        node_size=3000,
        font_weight='bold',
        font_size=25,
        edge_color=edge_colors,
        arrows=True,
        arrowsize=20,
        width=2,
        connectionstyle=connectionstyle
    )

    # Добавляем метки на стрелках для порядка голосования
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=votes,
        font_color='black',
        font_size=20,
        connectionstyle=connectionstyle,
        label_pos=0.3
    )

    # Генерация текста легенды
    vote_text_parts = [f"{v}: {a} -> {b}" for (a, b), v in votes.items()]
    vote_text = "\n".join(vote_text_parts)

    plt.text(
        0, 0,
        vote_text,
        fontsize=20,
        family='monospace',
        verticalalignment='center',
        bbox=dict(facecolor='white', alpha=0.5)
    )

    plt.axis('equal')
    plt.title("Игра: текущее распределение игроков")
    plt.show()


# Пример использования функции
votes_example = {
    (2, 4),
    (3, 4),
    (7, 4),
    (1, 5),
    (4, 3),
    (5, 2),
    (8, 2),
    (10, 9),
    (9, 10),

}

plot_game(
    num_players=10,
    absent_players={6},
    verified_red_players={},
    sheriffs={9, 10},
    votes=votes_example,
    round_edges=True
)
