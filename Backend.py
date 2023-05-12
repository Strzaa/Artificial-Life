import math
import random

import pygame
import pygame_widgets
from pygame_widgets.slider import Slider

pygame.init()

##########PARAMETRY#####################
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (119, 0, 200)
GREY = (169, 169, 169)
LIGHT_BLUE = (63, 79, 232)

# window
width = 1300
height = 700
move = 25

# sliders
slider_width, slider_height = 200, 15

# font
font_path = None
font_size = 24

# parameters
run = True
debug = False
simulation = True
start = False
animation_speed = 60

food_number = 150  #
poison_number = 50  #
agents_number = 80  #
max_agents_number = 250
enemy_number = 3  #

agent_health = 1
starting_health = 0.5
agent_max_speed = 6  #
agent_max_force = 1.2  #
agent_size = 12

poison_health = -0.8  #
food_health = 0.4  #
eatable_size = 3

enemy_max_speed = 3  #
enemy_max_force = 0.3  #
enemy_size = 40

agent_radius_min = 40  #
agent_radius_max = 250  #

circle_width = 2

mutation_chance = 0.05  #
health_reproduction_rate = 0.75  #

#############SET_UP##############################
# set up window and clock
screen = pygame.display.set_mode([width, height])
pygame.display.set_caption("Autonomous agents")
clock = pygame.time.Clock()

# text
font = pygame.font.Font(font_path, size=font_size)
font_menu = pygame.font.Font(font_path, size=font_size + 18)


# set up the simulation
def setup():
    agents = [Animal(random.randrange(width), random.randrange(height)) for _ in range(agents_number)]
    enemies = [Enemy(random.randrange(width), random.randrange(height)) for _ in range(enemy_number)]
    foods_g = [Food(random.randrange(0 + move, width - move), random.randrange(0 + move, height - move), False)
               for _ in range(food_number)]
    foods_p = [Food(random.randrange(0 + move, width - move), random.randrange(0 + move, height - move), True)
               for _ in range(poison_number)]
    return agents, enemies, foods_g, foods_p


# text during simulation
def population_text_game(agents):
    text = font.render("Population: " + str(len(agents)), True, WHITE)
    text_info = font.render(
        "<SPACE> Start / Stop, <+/-> Speed up / Slow down, <d> Debug radius, <r> Restart, <s> New Simulation",
        True, WHITE)

    text_info_rect = text_info.get_rect()
    text_rect = text.get_rect()

    text_info_rect.center = (400, height - 20)
    text_rect.center = (70, 30)

    screen.blit(text_info, text_info_rect)
    screen.blit(text, text_rect)


################CLASSES###############

class Vector2D:  # class to do action on vectors
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, new):  # dodawanie wektorow
        self.x += new.x
        self.y += new.y

    def __add__(self, a):
        return Vector2D(a.x + self.x, a.y + self.y)

    def multi(self, value):  # mnozenie
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
    def __init__(self, x, y, dna=None):
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

    def health_update(self, agents, value=None):
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

    def show(self, agents, enemies, debug):  # narysowanie
        self.theta = math.atan2(self.velocity.y, self.velocity.x)

        if self in agents or self in enemies:
            pygame.draw.polygon(screen, self.color,
                                [self.translate(Vector2D(self.size, 0)),
                                 self.translate(Vector2D(-self.size / 3, self.size / 2)),
                                 self.translate(Vector2D(0, 0)),
                                 self.translate(Vector2D(-self.size / 3, -self.size / 2))])
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

        return steering_force  # nowe przyspieszenie

    def apply_force(self, value):
        self.acceleration += value

        if self.acceleration.mag() >= self.max_force:
            self.acceleration.set_mag(self.max_force)

    def run(self, foods_g, foods_p, enemies, agents):
        if len(foods_g) < 1 or len(foods_p) < 1 or len(enemies) < 1: return

        food_dis, closest_food_index = self.find_closest(foods_g)
        poison_dis, closest_poison_index = self.find_closest(foods_p)
        enemy_dis, closest_enemy_index = self.find_closest(enemies)

        food_force, poison_force, enemy_force = Vector2D(0, 0), Vector2D(0, 0), Vector2D(0, 0)

        if food_dis < self.radius:
            food_force = self.seek(foods_g[closest_food_index])
            food_force.multi(self.dna[0])

        if poison_dis < self.radius:
            poison_force = self.seek(foods_p[closest_poison_index])
            poison_force.multi(self.dna[1])

        if enemy_dis < self.radius:
            enemy_force = self.seek(enemies[closest_enemy_index])
            enemy_force.multi(self.dna[2])

        force = food_force + poison_force + enemy_force

        self.apply_force(force)

        if food_dis < self.max_speed:
            del foods_g[closest_food_index]
            self.health_update(agents, food_health)

        if poison_dis < self.max_speed:
            del foods_p[closest_poison_index]
            self.health_update(agents, poison_health)

    def find_closest(self, list):
        closest_index = -1
        distance = 1000

        for x in list:
            tmp_dis = self.position.distance(x)
            if distance > tmp_dis and x != self:
                distance = tmp_dis
                closest_index = list.index(x)

        return distance, closest_index

    def find_closest_to_reproduce(self, list):
        closest_index = -1
        distance = 1000

        for x in list:
            tmp_dis = self.position.distance(x)
            if distance > tmp_dis and x.ready_to_reproduce and x != self:
                distance = tmp_dis
                closest_index = list.index(x)

        return distance, closest_index

    def translate(self, point):
        x = self.position.x + point.x * math.cos(self.theta) - point.y * math.sin(self.theta)
        y = self.position.y + point.x * math.sin(self.theta) + point.y * math.cos(self.theta)
        return [x, y]

    def reproduce(self, agents):
        if self.ready_to_reproduce and len(agents) > 1:
            self.color = PURPLE

            agent_dis, closest_agent_index = self.find_closest_to_reproduce(agents)

            reproduction_force = Vector2D(0, 0)

            if agent_dis < self.radius:
                reproduction_force = self.seek(agents[closest_agent_index])
                reproduction_force.limit(self.max_force)

            self.apply_force(reproduction_force)
            if agent_dis <= self.max_speed and agents[closest_agent_index].ready_to_reproduce and len(
                    agents) <= max_agents_number:
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

    def update(self, foods_g, foods_p):
        if len(foods_p) < poison_number:
            foods_p.append(
                Food(random.randrange(0 + move, width - move), random.randrange(0 + move, height - move), True))
        if len(foods_g) < food_number:
            foods_g.append(
                Food(random.randrange(0 + move, width - move), random.randrange(0 + move, height - move), False))


class Enemy(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_force = enemy_max_force
        self.max_speed = enemy_max_speed
        self.color = WHITE
        self.enemy = True
        self.size = enemy_size
        self.radius = 20

    def seek_agents(self, agents):
        if len(agents) < 1: return
        agent_dis, closest_agent_index = self.find_closest(agents)
        force_agent = self.seek(agents[closest_agent_index])
        self.apply_force(force_agent)

        if agent_dis < self.max_speed:
            del agents[closest_agent_index]

    def enemy_distance(self, enemies):
        if len(enemies) < 2: return
        enemy_dis, closest_enemy_index = self.find_closest(enemies)
        if enemy_dis < self.radius:
            force = Vector2D(enemies[closest_enemy_index].position.x - self.position.x,
                             enemies[closest_enemy_index].position.y - self.position.y)
            force.multi(-1)
            force.set_mag(self.max_force)
            self.apply_force(force)


class Sliders:
    def __init__(self, slider_x, slider_y, min, max, step):
        self.slider_x = slider_x
        self.slider_y = slider_y
        self.min = min
        self.max = max
        self.step = step

        self.slider = self.create()

    def create(self):
        return Slider(screen, self.slider_x, self.slider_y, slider_width, slider_height, min=self.min, max=self.max,
                      step=self.step, colour=GREY, handleColour=LIGHT_BLUE)


class Text:
    def __init__(self, text, value_start, x, y):
        self.text = text
        self.value_start = value_start
        self.x = x
        self.y = y

        text_ = font.render(self.text + str(self.value_start), True, WHITE)
        self.text_rect = text_.get_rect()
        self.text_rect.center = (self.x, self.y)

    def show(self, value):
        text = font.render(self.text + str(value), True, WHITE)
        screen.blit(text, self.text_rect)


###############MENU###############
# agents
population = Sliders(100, 120, 10, 200, 1)
population_text = Text("Start Population: ", population.slider.getValue(),
                       population.slider_x + 100, population.slider_y - 30)
population.slider.setValue(agents_number)

agent_max_speed_menu = Sliders(100, 210, 1, 15, 0.5)
agent_max_speed_text = Text("Agent max speed: ", agent_max_speed_menu.slider.getValue(),
                            agent_max_speed_menu.slider_x + 100, agent_max_speed_menu.slider_y - 30)
agent_max_speed_menu.slider.setValue(agent_max_speed)

agent_max_force_menu = Sliders(100, 300, 0.1, 5, 0.25)
agent_max_force_text = Text("Agent max force: ", agent_max_force_menu.slider.getValue(),
                            agent_max_force_menu.slider_x + 100, agent_max_force_menu.slider_y - 30)
agent_max_force_menu.slider.setValue(agent_max_force)

agent_radius_min_menu = Sliders(100, 390, 10, 99, 1)
agent_radius_min_text = Text("Agent radius min : ", agent_radius_min_menu.slider.getValue(),
                             agent_radius_min_menu.slider_x + 100, agent_radius_min_menu.slider_y - 30)
agent_radius_min_menu.slider.setValue(agent_radius_min)

agent_radius_max_menu = Sliders(100, 480, 100, 400, 1)
agent_radius_max_text = Text("Agent radius max : ", agent_radius_max_menu.slider.getValue(),
                             agent_radius_max_menu.slider_x + 100, agent_radius_max_menu.slider_y - 30)
agent_radius_max_menu.slider.setValue(agent_radius_max)

mutation_chance_menu = Sliders(100, 570, 0.001, 0.5, 0.005)
mutation_chance_text = Text("Mutation chance : ", mutation_chance_menu.slider.getValue(),
                            mutation_chance_menu.slider_x + 100, mutation_chance_menu.slider_y - 30)
mutation_chance_menu.slider.setValue(mutation_chance)

health_reproduction_rate_menu = Sliders(100, 660, 0.01, 0.99, 0.05)
health_reproduction_rate_text = Text("Health to reproduce : ", health_reproduction_rate_menu.slider.getValue(),
                                     health_reproduction_rate_menu.slider_x + 100,
                                     health_reproduction_rate_menu.slider_y - 30)
health_reproduction_rate_menu.slider.setValue(health_reproduction_rate)

# enemy
enemy_number_menu = Sliders(390, 120, 1, 10, 1)
enemy_number_text = Text("Enemy number : ", enemy_number_menu.slider.getValue(),
                         enemy_number_menu.slider_x + 100, enemy_number_menu.slider_y - 30)
enemy_number_menu.slider.setValue(enemy_number)

enemy_max_speed_menu = Sliders(390, 210, 1, 15, 0.5)
enemy_max_speed_text = Text("Enemy max speed: ", enemy_max_speed_menu.slider.getValue(),
                            enemy_max_speed_menu.slider_x + 100, enemy_max_speed_menu.slider_y - 30)
enemy_max_speed_menu.slider.setValue(enemy_max_speed)

enemy_max_force_menu = Sliders(390, 300, 0.1, 5, 0.25)
enemy_max_force_text = Text("Enemy max force: ", enemy_max_force_menu.slider.getValue(),
                            enemy_max_force_menu.slider_x + 100, enemy_max_force_menu.slider_y - 30)
enemy_max_force_menu.slider.setValue(enemy_max_force)

# food
food_number_menu = Sliders(680, 120, 10, 200, 10)
food_number_text = Text("Food number : ", food_number_menu.slider.getValue(),
                        food_number_menu.slider_x + 100, food_number_menu.slider_y - 30)
food_number_menu.slider.setValue(food_number)

food_health_menu = Sliders(680, 210, 0.01, 1, 0.01)
food_health_text = Text("Food health gain : ", food_health_menu.slider.getValue(),
                        food_health_menu.slider_x + 100, food_health_menu.slider_y - 30)
food_health_menu.slider.setValue(food_health)

# poison
poison_number_menu = Sliders(970, 120, 10, 200, 10)
poison_number_text = Text("Poison number : ", poison_number_menu.slider.getValue(),
                          poison_number_menu.slider_x + 100, poison_number_menu.slider_y - 30)
poison_number_menu.slider.setValue(poison_number)

poison_health_menu = Sliders(970, 210, 0.01, 1, 0.01)
poison_health_text = Text("Poison health decrease : ", poison_health_menu.slider.getValue(),
                          poison_health_menu.slider_x + 100, poison_health_menu.slider_y - 30)
poison_health_menu.slider.setValue(-1 * poison_health)


def menu(events):
    # agents
    population_text.show(population.slider.getValue())
    agent_max_speed_text.show(agent_max_speed_menu.slider.getValue())
    agent_max_force_text.show(agent_max_force_menu.slider.getValue())
    agent_radius_min_text.show(agent_radius_min_menu.slider.getValue())
    agent_radius_max_text.show(agent_radius_max_menu.slider.getValue())
    mutation_chance_text.show(round(mutation_chance_menu.slider.getValue(), 3))
    health_reproduction_rate_text.show(round(health_reproduction_rate_menu.slider.getValue(), 2))

    # enemy
    enemy_number_text.show(enemy_number_menu.slider.getValue())
    enemy_max_speed_text.show(enemy_max_speed_menu.slider.getValue())
    enemy_max_force_text.show(enemy_max_force_menu.slider.getValue())

    # food
    food_number_text.show(food_number_menu.slider.getValue())
    food_health_text.show(round(food_health_menu.slider.getValue(), 2))

    # poison
    poison_number_text.show(poison_number_menu.slider.getValue())
    poison_health_text.show(round(poison_health_menu.slider.getValue(), 2))

    # agents variables
    global agents_number
    agents_number = population.slider.getValue()
    global agent_max_speed
    agent_max_speed = agent_max_speed_menu.slider.getValue()
    global agent_max_force
    agent_max_force = agent_max_force_menu.slider.getValue()
    global agent_radius_min
    agent_radius_min = agent_radius_min_menu.slider.getValue()
    global agent_radius_max
    agent_radius_max = agent_radius_max_menu.slider.getValue()
    global mutation_chance
    mutation_chance = mutation_chance_menu.slider.getValue()
    global health_reproduction_rate
    health_reproduction_rate = health_reproduction_rate_menu.slider.getValue()

    # enemies variables
    global enemy_number
    enemy_number = enemy_number_menu.slider.getValue()
    global enemy_max_speed
    enemy_max_speed = enemy_max_speed_menu.slider.getValue()
    global enemy_max_force
    enemy_max_force = enemy_max_force_menu.slider.getValue()

    # food variables
    global food_number
    food_number = food_number_menu.slider.getValue()
    global food_health
    food_health = food_health_menu.slider.getValue()

    # poison variables
    global poison_number
    poison_number = poison_number_menu.slider.getValue()
    global poison_health
    poison_health = -1 * poison_health_menu.slider.getValue()

    # names
    text_agent = font_menu.render("AGENTS", True, GREEN)
    text_agent_rect = text_agent.get_rect()
    text_agent_rect.center = (200, 40)

    text_enemy = font_menu.render("ENEMIES", True, RED)
    text_enemy_rect = text_agent.get_rect()
    text_enemy_rect.center = (490, 40)

    text_food = font_menu.render("FOOD", True, BLUE)
    text_food_rect = text_agent.get_rect()
    text_food_rect.center = (800, 40)

    text_poison = font_menu.render("POISON", True, PURPLE)
    text_poison_rect = text_agent.get_rect()
    text_poison_rect.center = (1070, 40)

    text_info = font_menu.render("<s> Start Simulation", True, WHITE)
    text_info_rect = text_agent.get_rect()
    text_info_rect.center = (1070, 670)

    screen.blit(text_agent, text_agent_rect)
    screen.blit(text_enemy, text_enemy_rect)
    screen.blit(text_food, text_food_rect)
    screen.blit(text_poison, text_poison_rect)
    screen.blit(text_info, text_info_rect)

    pygame_widgets.update(events)
