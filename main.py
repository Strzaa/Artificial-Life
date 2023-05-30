"""
TO DO:
BUTTONS AND SETTINGS MENU
"""
from Backend import *

# glowna petla gry
while run:
    clock.tick(animation_speed)  # predkosc animacji
    delta_time = clock.tick(animation_speed)  # czas zycia agentow
    screen.fill(BLACK)

# EVENTS
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:  # wyjscie z gry
            run = False

        if event.type == pygame.KEYDOWN:  # wcisniecie klawisza
            if event.unicode == '+':  # speed up
                animation_speed += 10
                if animation_speed >= 240: animation_speed = 240

            if event.unicode == '-':  # slow down
                animation_speed -= 10
                if animation_speed <= 10: animation_speed = 10

            if event.key == pygame.K_SPACE:  # stop
                simulation = not simulation

            if event.key == pygame.K_d:  # debug
                debug = not debug

            if event.key == pygame.K_s:  # start simulation
                start = not start
                if start: agents, enemies, foods_g, foods_p = setup()

            if event.key == pygame.K_r:  # restart the same simulation
                agents, enemies, foods_g, foods_p = setup()

# MENU
    if start is False:
        screen.fill(BLACK)
        menu(events)
        pygame.display.flip()
        continue

# SIMULATION

    for agent in agents:  # dla kazdego agenta
        if simulation:
            agent.time_life += delta_time
            agent.health_update(agents)
            if agent.boundries() is None:  # jak sie nie odbija od sciany
                agent.run(foods_g, foods_p, enemies, agents)
                agent.reproduce(agents)
            agent.update()
        agent.show(agents, enemies, debug)

    for enemy in enemies:  # dla kazdego przeciwnika
        if simulation:
            enemy.seek_agents(agents)
            enemy.enemy_distance(enemies)
            enemy.update()
        enemy.show(agents, enemies, debug)

    foods = foods_g + foods_p  # lista jedzenia

    for food in foods:  # dla kazdego jedzenia
        if simulation:
            food.update(foods_g, foods_p)
        food.show()

    draw_enviroment()  # rysowanie enviroment

    population_text_game(agents)   # text podczas symulacji

    pygame.display.flip()  # odswiezenie ekranu

