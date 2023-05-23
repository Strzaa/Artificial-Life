"""
TO DO:
BUTTONS AND SETTINGS MENU
"""
from Backend import *

while run:
    clock.tick(animation_speed)
    screen.fill(BLACK)

# EVENTS
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.unicode == '+':
                animation_speed += 10
                if animation_speed >= 240: animation_speed = 240

            if event.unicode == '-':
                animation_speed -= 10
                if animation_speed <= 10: animation_speed = 10

            if event.key == pygame.K_SPACE:
                simulation = not simulation

            if event.key == pygame.K_d:
                debug = not debug

            if event.key == pygame.K_s:
                start = not start
                if start: agents, enemies, foods_g, foods_p = setup()

            if event.key == pygame.K_r:
                agents, enemies, foods_g, foods_p = setup()

# MENU
    if start is False:
        screen.fill(BLACK)
        menu(events)
        pygame.display.flip()
        continue

# SIMULATION
    for agent in agents:
        if simulation:
            agent.health_update(agents)
            if agent.boundries() is None:
                agent.run(foods_g, foods_p, enemies, agents)
                agent.reproduce(agents)
            agent.update()
        agent.show(agents, enemies, debug)

    for enemy in enemies:
        if simulation:
            enemy.seek_agents(agents)
            enemy.enemy_distance(enemies)
            enemy.update()
        enemy.show(agents, enemies, debug)

    foods = foods_g + foods_p

    for food in foods:
        if simulation:
            food.update(foods_g, foods_p)
        food.show()

    population_text_game(agents)

    pygame.display.flip()

