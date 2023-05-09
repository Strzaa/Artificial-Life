import math
import random
import pygame
from Parameters import *

class Vector2D:  # class to do action on vectors
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, new):  # dodawanie wektorow
        self.x += new.x
        self.y += new.y

    def __add__(self, a):
        return Vector2D(a.x + self.x, a.y + self.y)

    def multi(self, value): #mnozenie
        self.x = self.x * value
        self.y = self.y * value

    def limit(self, max_):  # jezeli jest wiekszy od max to zmiejsz do podanej wartosci
        if self.mag() > max_:
            self.set_mag(max_)

    def mag(self):  # dlugosc wektora
        return math.sqrt(self.x * self.x + self.y * self.y)

    def set_mag(self, value):  # ustawienie dlugosci wektora
        if self.mag() == 0:
            self.x = 0
            self.y = 0
        else:
            self.x, self.y = value * self.x / self.mag(), value * self.y / self.mag()

    def distance(self, target):  # dystans miedzy 2 okiektami z artybutem position
        return math.sqrt(
            (self.x - target.position.x) * (self.x - target.position.x) +
            (self.y - target.position.y) * (self.y - target.position.y))

class Animal:  # klasa agentów
    def __init__(self, x, y, dna = None):
        self.position = Vector2D(x, y)
        self.acceleration = Vector2D(0, 0)  # przyspieszenie
        self.velocity = Vector2D(0.5, 0.5)  # predkosc, ona zmienia polozenie
        self.max_speed = agent_max_speed
        self.max_force = agent_max_force
        self.theta = 0  # kat wektora do osi x
        self.size = agent_size
        self.color = GREEN
        self.dna = [0] * 4
        if dna is None:
            for i in range(len(self.dna)):
                self.dna[i] = self.generate_dna(i)
        else:
            self.dna = dna
        self.enemy = False
        self.health = starting_health
        self.radius = self.dna[3]
        self.ready_to_reproduce = False

    def generate_dna(self, number):
        if number == 3:
            return random.uniform(agent_radius_min, agent_radius_max)
        else:
            random_number = random.uniform(-5, 5)
            while random_number == 0:
                random_number = random.uniform(-5, 5)
            return random_number

    def health_update(self, value=None):
        if value is None:
            self.health -= 0.005
        else:
            self.health += value
            if self.health >= agent_health: self.health = agent_health

        if self.health <= 0 and self in agents:
            del agents[agents.index(self)]
            return

        if self.ready_to_reproduce is False: self.color = self.lerpColor(RED, GREEN, self.health)

        if self.health >= health_reproduction_rate:
            self.ready_to_reproduce = True
        else:
            self.ready_to_reproduce = False

    def update(self):  # ustawienie nowych wartosci pozycji
        self.velocity.add(self.acceleration)
        self.velocity.limit(self.max_speed)
        self.position.add(self.velocity)

    def boundries(self):
        desired = None

        if self.position.x < move:
            desired = Vector2D(self.max_speed, self.velocity.y)
        elif self.position.x > width - move:
            desired = Vector2D(-self.max_speed, self.velocity.y)

        if self.position.y < move:
            desired = Vector2D(self.velocity.x, self.max_speed)
        elif self.position.y > height - move:
            desired = Vector2D(self.velocity.x, -self.max_speed)

        if desired is not None:
            desired.set_mag(self.max_speed)
            steer = Vector2D(desired.x - self.velocity.x, desired.y - self.velocity.y)
            steer.limit(self.max_force)
            self.acceleration = steer
        return desired

    def show(self):  # narysowanie
        self.theta = math.atan2(self.velocity.y, self.velocity.x)

        if self in agents or self in enemies:
            pygame.draw.polygon(screen, self.color,
                                [self.translate(Vector2D(self.size, 0)),
                                 self.translate(Vector2D(-self.size / 3, self.size / 2)),
                             self.translate(Vector2D(0, 0)), self.translate(Vector2D(-self.size / 3, -self.size / 2))])
        if self.enemy is False and self in agents:
            if debug: pygame.draw.circle(screen, WHITE, [self.position.x, self.position.y], self.radius, circle_width)

    def lerpColor(self, startColor, endColor, t):
        r = int(startColor[0] + (endColor[0] - startColor[0]) * t)
        g = int(startColor[1] + (endColor[1] - startColor[1]) * t)
        b = int(startColor[2] + (endColor[2] - startColor[2]) * t)
        return (r, g, b)

    def seek(self, target):  # sledzenie konkretnego obiektu
        if target is None: return Vector2D(0, 0)

        desired = Vector2D(target.position.x - self.position.x,
                           target.position.y - self.position.y)  # wektor gdzie chcemy sie udac do targetu
        desired.set_mag(self.max_speed)  # ustawienie dlugosci wektora
        steering_force = Vector2D(desired.x - self.velocity.x, desired.y - self.velocity.y)  # sila sterujaca

        if self.enemy: self.acceleration = steering_force
        return steering_force  # nowe przyspieszenie

    def apply_force(self, value):
        self.acceleration += value

        if self.acceleration.mag() >= self.max_force:
            self.acceleration.set_mag(self.max_force)

    def run(self, food, poison, enemies_list):
        if len(foods_g) < 1 or len(foods_p) < 1 or len(enemies) < 1: return

        food_dis, closest_food_index = self.find_closest(food)
        poison_dis, closest_poison_index = self.find_closest(poison)
        enemy_dis, closest_enemy_index = self.find_closest(enemies_list)

        food_force, poison_force, enemy_force = Vector2D(0, 0), Vector2D(0, 0), Vector2D(0, 0)

        if food_dis < self.radius:
            food_force = self.seek(food[closest_food_index])
            food_force.multi(self.dna[0])

        if poison_dis < self.radius:
            poison_force = self.seek(poison[closest_poison_index])
            poison_force.multi(self.dna[1])

        if enemy_dis < self.radius:
            enemy_force = self.seek(enemies_list[closest_enemy_index])
            enemy_force.multi(self.dna[2])

        force = food_force + poison_force + enemy_force

        self.apply_force(force)

        if food_dis < self.max_speed:
            del foods_g[closest_food_index]
            self.health_update(food_health)

        if poison_dis < self.max_speed:
            del foods_p[closest_poison_index]
            self.health_update(poison_health)

    def find_closest(self, list):
        closest_index = -1
        distance = 1000

        for x in list:
            tmp_dis = self.position.distance(x)
            if distance > tmp_dis:
                distance = tmp_dis
                closest_index = list.index(x)

        return distance, closest_index

    def find_closest_to_reproduce(self, list, agent):
        closest_index = -1
        distance = 1000

        for x in list:
            tmp_dis = self.position.distance(x)
            if distance > tmp_dis and x.ready_to_reproduce and x != agent:
                distance = tmp_dis
                closest_index = list.index(x)

        return distance, closest_index

    def translate(self, point):
        x = self.position.x + point.x * math.cos(self.theta) - point.y * math.sin(self.theta)
        y = self.position.y + point.x * math.sin(self.theta) + point.y * math.cos(self.theta)
        return [x, y]

    def reproduce(self, agent):
        if self.ready_to_reproduce and len(agents) > 1:
            self.color = PURPLE

            agent_dis, closest_agent_index = self.find_closest_to_reproduce(agents, agent)

            reproduction_force = Vector2D(0, 0)

            if agent_dis < self.radius:
                reproduction_force = self.seek(agents[closest_agent_index])
                reproduction_force.limit(self.max_force)

            self.apply_force(reproduction_force)
            if agent_dis <= self.max_speed and agents[closest_agent_index].ready_to_reproduce and len(agents) <= max_agents_number:
                self.ready_to_reproduce = False
                self.health = 0.5
                agents[closest_agent_index].health -= health_reproduction_rate
                agents[closest_agent_index].ready_to_reproduce = False

                new_dna = self.cross(agents[closest_agent_index])
                agents.append(Animal(self.position.x, self.position.y, new_dna))

    def cross(self, parent):
        new_dna = [0] * 4
        for i in range(len(self.dna)):
            new_dna[i] = (self.dna[i] + parent.dna[i]) / 2
            if random.random() <= mutation_chance:
                if random.random() <= 0.5:
                    new_dna[i] += self.dna[i] / 2
                else:
                    new_dna[i] -= self.dna[i] / 2

        print(new_dna)
        return new_dna

class Food:
    def __init__(self, x, y, poison):
        self.position = Vector2D(x, y)
        self.poison = poison
        self.size = eatable_size

    def show(self):
        if self.poison:
            pygame.draw.ellipse(screen, RED, [self.position.x, self.position.y, self.size, self.size])
        else:
            pygame.draw.ellipse(screen, GREEN, [self.position.x, self.position.y, self.size, self.size])

    def update(self):
        if len(foods_p) < poison_number:
            foods_p.append(Food(random.randrange(0 + move, width - move), random.randrange(0 + move, height - move), True))
        if len(foods_g) < food_number:
            foods_g.append(Food(random.randrange(0 + move, width - move), random.randrange(0 + move, height - move), False))

class Enemy(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_force = enemy_max_force
        self.max_speed = enemy_max_speed
        self.color = WHITE
        self.enemy = True
        self.size = enemy_size

    def seek_agents(self, agents_list):
        if len(agents) < 1: return
        agent_dis, closest_agent_index = self.find_closest(agents_list)
        self.seek(agents_list[closest_agent_index])

        if agent_dis < self.max_speed:
            del agents[closest_agent_index]


pygame.init()

# create objects
agents = [Animal(random.randrange(width), random.randrange(height)) for _ in range(agents_number)]
enemies = [Enemy(random.randrange(width), random.randrange(height)) for _ in range(enemy_number)]
foods_g = [Food(random.randrange(0 + move, width - move), random.randrange(0 + move, height - move), False)
           for _ in range(food_number)]
foods_p = [Food(random.randrange(0 + move, width - move), random.randrange(0 + move, height - move), True)
           for _ in range(poison_number)]

# set up window and clock
screen = pygame.display.set_mode([width, height])
pygame.display.set_caption("Autonomous agents")
clock = pygame.time.Clock()

# variables to run the simulation
run = True
debug = False

# text
font = pygame.font.Font(font_path, size=font_size)
text = font.render("Population: " + str(len(agents)), True, WHITE)
text_rect = text.get_rect()
text_rect.center = (70, 30)

