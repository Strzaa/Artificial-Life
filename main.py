"""
TO DO:
BUTTONS AND SETTINGS MENU
"""
from Backend import *

# pygame init
pygame.init()

while run:
    clock.tick(animation_speed)
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

    text = font.render("Population: " + str(len(agents)), True, WHITE)
    screen.blit(text, text_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.unicode == '+':
                animation_speed += 10
                if animation_speed >= 240: animation_speed = 240
            if event.unicode == '-':
                animation_speed -= 10
                if animation_speed <= 10: animation_speed = 10

    pygame.display.flip()

