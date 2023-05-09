"""
TO DO:
GUI
RADIUS FOOD AND POISON AND ENEMY
BUTTONS AND SETTINGS MENU
FILE SLICE
"""
from Backend import *

# pygame init
pygame.init()

while run:
    clock.tick(40)
    screen.fill(BLACK)

    for agent in agents:
        agent.health_update()
        agent.update()
        if agent.boundries() is None:
            agent.run(foods_g, foods_p, enemies)
        agent.show()
        agent.reproduce(agent)

    for enemy in enemies:
        enemy.update()
        enemy.seek_agents(agents)
        enemy.show()

    foods = foods_g + foods_p

    for food in foods:
        food.show()
        food.update()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

