from functools import lru_cache

class knapsack:
    def __init__(self, size: list[int], weight: list[int]):
        self.size = size
        self.weight = weight

    @lru_cache(maxsize=4096 * 1024)
    def solve(self, cap1: int, cap2: int, i: int = 0):
        if cap1 < 0 or cap2 < 0:
            return -sum(self.weight), []
        if i == len(self.size):
            return 0, []
        res1 = self.solve(cap1, cap2, i + 1)
        res2 = self.solve(cap1 - self.size[i], cap2 - 1, i + 1)
        res2 = (res2[0] + self.weight[i], [i] + res2[1])
        return res1 if res1[0] >= res2[0] else res2

nicks = [
"Воробушек",
"Чаклз",
"Леброн",
"Вальхалла",
"Сандра",
"Читер",
"Псина",
"Домино",
"Музыка",
"Сложный",
"Рейми",
"Ллирик",
"Яблоко",
"Незлой",
"Шахист",
"Пагода",
"Вредная",
"Сильвер",
"Аоки",
"Шлюба",
"Пожарный",
"Ливси",
"Размен",
"ФДМ",
"Мунлайт",
"Док",
"Чаффи",
"Любезный",
"Орочимару",
"Певун",
"Мира",
"Евска",
"Ленивец",
"Фей",
"Ома",
"Зетоксик",
"Макарена",
"Мишель",
"Маринетка",
"Микочу",
"Ша",
"Милкис",
"Царица ночи",
"Каспер",
"Фростик",
"JTH",
"Авомарика",
"Зажигалочка",
"ТМС",
"Беливел",
]
size = [12.5, 12, 14, 11.5, 12.5, 13, 8.5, 11.5, 9.5, 9, 8, 9, 7.5, 8.5, 12.5, 11, 10, 12.5, 8.5, 10, 8, 8.5, 12.5,
        12.5, 9.5, 10.5, 7.5, 10.5, 9.5, 12.5, 9, 8, 7.5, 10, 10, 7, 11.5, 7, 7.5, 12, 7.5, 13, 8, 10, 12, 9, 7, 12.5,
        9.5, 9]
weight = [12.05, 11.1, 10.75, 10.15, 9.4, 9.15, 9.1, 8.85, 8.85, 8.85, 8.7, 8.5, 8.2, 8.1, 7.9, 7.6, 7.4, 7.15, 7.05, 7,
          6.8, 6.4, 6.3, 6.25, 6.2, 6.1, 6.05, 5.95, 5.8, 5.75, 5.7, 5.5, 5.5, 5.5, 5.4, 5.3, 5.2, 5.2, 5, 4.8, 4.75,
          4.3, 4.3, 4.2, 4.15, 3.5, 3.4, 3.3, 3, 2.6]
capacity = 100
solve = knapsack(size, weight).solve(100, 10)
print(solve[0])
for c in list(map(lambda it: nicks[it], solve[1])):
    print(c)

