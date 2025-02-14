from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.animation import FuncAnimation

def plot_game_animation(
    num_players = 10,
    absent_players = [],
    verified_red_players = [],
    sheriffs = [],
    votes = [],
    round_edges=True,
    interval=1000  # Интервал между кадрами в миллисекундах
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

    # Настройка для рисования кривых линий
    connectionstyle = 'arc3,rad=0.2' if round_edges else 'arc3,rad=0.0'

    fig, ax = plt.subplots(figsize=(10, 10))

    def update(frame):
        ax.clear()
        # Создаем граф до текущего фрейма
        current_edges = [edge for edge, label in votes.items() if label <= frame + 1]
        edge_colors = [vote_colors[votes[edge]] for edge in current_edges]

        # Создаем круговую визуализацию графа
        G.clear_edges()
        G.add_edges_from(current_edges)

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
            connectionstyle=connectionstyle,
            ax=ax
        )

        # Добавляем метки на стрелках для порядка голосования
        edge_labels = {edge: votes[edge] for edge in current_edges}
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_color='black',
            font_size=20,
            label_pos=0.3,
            ax=ax
        )

        ax.set_title("Игра: текущее распределение игроков")
        ax.set_axis_off()

    # Запускаем анимацию
    anim = FuncAnimation(
        fig,
        update,
        frames=len(set(votes.values())),
        interval=interval,
        repeat=False
    )

    plt.show()
    anim.save('game_animation.gif')



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

plot_game_animation(
    num_players=10,
    absent_players={6},
    verified_red_players={},
    sheriffs={9, 10},
    votes=votes_example,
    round_edges=True
)
