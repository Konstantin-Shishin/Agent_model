import json
import math

import matplotlib.pyplot as plt
import random
from enum import Enum, auto
import os
import numpy as np


class BypassType(Enum):
    CROSS = auto()
    RIM = auto()
    FULL_GRAPH = auto()


from enum import Enum, auto


class BypassType(Enum):
    CROSS = auto()
    RIM = auto()
    FULL_GRAPH = auto()


class Agent:
    def __init__(self, bypass_type=BypassType.CROSS, a=False, stubborn=False, conformist=False):
        self.bypass_type = bypass_type
        self.a = a
        self.st = stubborn
        self.cf = conformist

    def compute_opinion(self, count_a, count_b):
        #Если агент упрямый, его мнение не изменится.
        if self.st:
            return

        # Если агент конформист, он будет следовать мнению большинства,
        # даже если количество одинаково.
        if self.cf:
            if count_a >= count_b:
                self.a = True
            else:
                self.a = False
        else:
            # Если агент не конформист, его мнение изменится только,
            # если есть явное большинство.
            if count_a > count_b:
                self.a = True
            elif count_b > count_a:
                self.a = False
            # Если количество агентов с мнением A равно количеству агентов с мнением B,
            # и агент не конформист, его мнение не изменится.

    # Теперь добавим логику выбора метода обхода на основе self.bypass_type
    def bypass(self, opinion_field, row, column):
        if self.bypass_type == BypassType.CROSS:
            self.bypass_cross(opinion_field, row, column)
        elif self.bypass_type == BypassType.RIM:
            self.bypass_rim(opinion_field, row, column)
        elif self.bypass_type == BypassType.FULL_GRAPH:
            self.bypass_full_graph(opinion_field, row, column)

    def bypass_cross(self, opinion_field, row, column):
        rows, columns = len(opinion_field), len(opinion_field[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        count_a, count_b = 0, 0
        for dr, dc in directions:
            new_r, new_c = row + dr, column + dc
            if 0 <= new_r < rows and 0 <= new_c < columns:
                if opinion_field[new_r][new_c].a:
                    count_a += 1
                else:
                    count_b += 1
        self.compute_opinion(count_a, count_b)

    def bypass_rim(self, opinion_field, row, column):
        rows, columns = len(opinion_field), len(opinion_field[0])
        count_a, count_b = 0, 0
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                new_r, new_c = row + dr, column + dc
                if 0 <= new_r < rows and 0 <= new_c < columns:
                    if opinion_field[new_r][new_c].a:
                        count_a += 1
                    else:
                        count_b += 1
        self.compute_opinion(count_a, count_b)

    def bypass_full_graph(self, opinion_field, row, column):
        # Считаем мнения всех агентов в поле
        count_a = sum(sum(1 for agent in row if agent.a) for row in opinion_field)
        count_b = sum(sum(1 for agent in row if not agent.a) for row in opinion_field)
        # Теперь используем эти подсчеты для обновления мнения
        self.compute_opinion(count_a, count_b)


class Simulation:
    def __init__(self, agents, field_size=(10, 10), num_steps=20):
        self.agents = agents
        self.field_size = field_size
        self.num_steps = num_steps
        # Измените эту строку, чтобы использовать агентов из списка
        self.opinion_field = [[agents[i * field_size[1] + j] for j in range(field_size[1])]
                              for i in range(field_size[0])]

    def print_opinion_distribution(self, opinion_field):
        count_a = sum(sum(1 for agent in row if agent.a) for row in opinion_field)
        count_b = sum(sum(1 for agent in row if not agent.a) for row in opinion_field)
        print(f"Количество A: {count_a}, Количество B: {count_b}")

    def simulate(self):
        data = []
        for step in range(self.num_steps):
            # Логируем состояние поля перед обновлением
            print(f"Шаг {step}, распределение мнений до обновления:")
            self.print_opinion_distribution(self.opinion_field)

            # Выполняем обновление мнения агентов на поле
            for i in range(len(self.opinion_field)):
                for j in range(len(self.opinion_field[i])):
                    self.opinion_field[i][j].bypass(self.opinion_field, i, j)
            # Сохраняем карту мнений
            save_opinion_map(self.opinion_field, step)
            # Собираем статистику о текущем состоянии мнения в популяции
            count_a = sum(sum(1 for agent in row if agent.a) for row in self.opinion_field)
            count_b = sum(sum(1 for agent in row if not agent.a) for row in self.opinion_field)
            total_agents = self.field_size[0] * self.field_size[1]
            share_a = count_a / total_agents
            share_b = count_b / total_agents
            entropy = -share_a * (share_a or 1) * math.log(share_a or 1) - share_b * (share_b or 1) * math.log(
                share_b or 1)
            # Записываем текущее состояние в данные для графика
            data.append({'Time': step, 'Entropy': entropy, 'Share opinion A': share_a})

            # Логируем распределение после обновления
            print(f"Шаг {step}, распределение мнений после обновления:")
            self.print_opinion_distribution(self.opinion_field)
        return data


# Функция для чтения данных из JSON-файла
def read_data_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


# Функция для построения графиков
def plot_graphs(data):
    time = []
    entropy = []
    share_a = []

    for entry in data:
        time.append(entry['Time'])
        entropy.append(entry['Entropy'])
        share_a.append(entry['Share opinion A'])

    plt.plot(time, entropy, label='Энтропия')
    plt.plot(time, share_a, label='Доля мнения A')

    plt.title('Изменение энтропии и доли мнения A по времени')
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.legend()

    plt.show()


def generate_test_json(filename, num_agents=100):
    data = {
        'agents': [
            {
                'bypass_type': 'CROSS',
                'a': random.choice([True, False]),
                'st': random.choice([True, False]),
                'cf': random.choice([True, False])
            }
            for _ in range(num_agents)
        ]
    }
    with open(filename, 'w') as file:
        json.dump(data, file)


def generate_test_json_random(filename, num_agents=100):
    data = {
        'agents': [
            {'bypass_type': random.choice(list(BypassType.__members__.keys())),
             'a': random.choice([True, False]),
             'st': random.choice([True, False]),
             'cf': random.choice([True, False])
             } for _ in range(num_agents)
        ]
    }
    with open(filename, 'w') as file:
        json.dump(data, file)


def generate_test_json_balanced(filename, num_agents=100):
    half_agents = num_agents // 2
    agents = []
    # Генерируем равное количество агентов с мнением A и B
    for _ in range(half_agents):  # Половина агентов с мнением A
        agents.append({
            'bypass_type': random.choice(list(BypassType.__members__.keys())),
            'a': True,  # Мнение A
            'st': random.choice([True, False]),
            'cf': random.choice([True, False])
        })
    for _ in range(num_agents - half_agents):  # Остальные с мнением B
        agents.append({
            'bypass_type': random.choice(list(BypassType.__members__.keys())),
            'a': False,  # Мнение B
            'st': random.choice([True, False]),
            'cf': random.choice([True, False])
        })
    # Перемешиваем агентов для случайного распределения
    random.shuffle(agents)
    data = {'agents': agents}
    with open(filename, 'w') as file:
        json.dump(data, file)


def save_opinion_map(opinion_field, step, folder='opinion_maps'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    # Создаем изображение, где каждый пиксель соответствует мнению агента
    # Агенты с мнением A будут синими, а с мнением B - красными
    img = np.zeros((len(opinion_field), len(opinion_field[0]), 3), dtype=int)
    for i, row in enumerate(opinion_field):
        for j, agent in enumerate(row):
            if agent.a:
                img[i, j] = [0, 0, 255]  # Синий цвет для мнения A
            else:
                img[i, j] = [255, 0, 0]  # Красный цвет для мнения B

    plt.imshow(img)
    plt.axis('off')  # Скрываем оси
    # Сохраняем изображение
    plt.savefig(f'{folder}/step_{step}.png', bbox_inches='tight', pad_inches=0)
    plt.close()  # Закрываем текущее изображение, чтобы избежать переполнения памяти


if __name__ == "__main__":
    filename = 'test.json'
    count = 900
    generate_test_json_random(filename,count)
    # Чтение данных из JSON-файла
    data = read_data_from_json(filename)

    # Инициализируем агентов для симуляции
    agents_data = data['agents']
    agents = [
        Agent(bypass_type=BypassType[agent['bypass_type']], a=agent['a'], stubborn=agent['st'], conformist=agent['cf'])
        for agent in agents_data]

    # Создаем симуляцию
    simulation = Simulation(agents,(30, 30))

    # Выполняем симуляцию
    simulation_data = simulation.simulate()

    # Построение графиков
    plot_graphs(simulation_data)
