import pygame
import math
import random
from pygame import mixer

# Inicializar pygame
pygame.init()

# Crear pantalla
screen = pygame.display.set_mode((800, 600))

# Fondo
background = pygame.image.load('background.png')

# Sonido de fondo
mixer.music.load('background.wav')
mixer.music.play(-1)

# Título e ícono
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Jugador
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480
playerX_change = 0

# Enemigos
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, 735))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(1)
    enemyY_change.append(40)

# Bala del jugador
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletY_change = 10
bullet_state = "ready"

# Jefe
bossImg = pygame.image.load('boss.png')
bossX = random.randint(100, 600)
bossY = 50
bossX_change = 2
bossY_change = 40
boss_active = False
boss_health = 5

# Bala del jefe
boss_bulletImg = pygame.image.load('boss_bullet.png')
boss_bulletX = 0
boss_bulletY = 0
boss_bulletY_change = 5
boss_bullet_state = "ready"

# Puntaje
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
textX = 10
textY = 10

# Texto de Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)

def show_score(x, y):
    score = font.render("Score :" + str(score_value), True, (0, 255, 0))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_text, (200, 250))
    pygame.display.update()
    pygame.time.wait(10000)  # Esperar 10 segundos (10000 milisegundos)
    pygame.quit()
    exit()


def player(x, y):
    screen.blit(playerImg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))

def fire_boss_bullet(x, y):
    global boss_bullet_state
    boss_bullet_state = "fire"
    screen.blit(boss_bulletImg, (x + 24, y + 40))

def boss(x, y):
    screen.blit(bossImg, (x, y))

def isCollision(x1, y1, x2, y2):
    distance = math.hypot(x1 - x2, y1 - y2)
    return distance < 27

# Game Loop
running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Movimiento
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -1
            if event.key == pygame.K_RIGHT:
                playerX_change = 1
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    bullet_Sound = mixer.Sound('laser.wav')
                    bullet_Sound.play()
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                playerX_change = 0

    # Movimiento del jugador
    playerX += playerX_change
    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    # Enemigos
    if not boss_active:
        for i in range(num_of_enemies):
            if enemyY[i] > 440:
                for j in range(num_of_enemies):
                    enemyY[j] = 2000
                game_over_text()
                break

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = 1
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -1
                enemyY[i] += enemyY_change[i]

            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosion_Sound = mixer.Sound('explosion.wav')
                explosion_Sound.play()
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 736)
                enemyY[i] = random.randint(50, 150)

            enemy(enemyX[i], enemyY[i], i)

    # Aparece jefe cada 10 puntos
    if score_value != 0 and score_value % 10 == 0 and not boss_active:
        boss_active = True
        bossX = random.randint(100, 600)
        bossY = 50
        boss_health = 5
        boss_bullet_state = "ready"

    # Movimiento del jefe
    if boss_active:
        bossX += bossX_change
        if bossX <= 0 or bossX >= 736:
            bossX_change *= -1
            bossY += bossY_change

        boss(bossX, bossY)

        # Disparo del jefe
        if boss_bullet_state == "ready":
            boss_bulletX = bossX
            boss_bulletY = bossY
            fire_boss_bullet(boss_bulletX, boss_bulletY)

        if boss_bullet_state == "fire":
            fire_boss_bullet(boss_bulletX, boss_bulletY)
            boss_bulletY += boss_bulletY_change
            if boss_bulletY > 600:
                boss_bullet_state = "ready"

        # Colisión con el jefe
        if isCollision(bossX, bossY, bulletX, bulletY):
            bulletY = 480
            bullet_state = "ready"
            boss_health -= 1
            explosion_Sound = mixer.Sound('explosion.wav')
            explosion_Sound.play()
            if boss_health <= 0:
                boss_active = False
                score_value += 5

        # Colisión de bala del jefe con jugador
        if isCollision(boss_bulletX, boss_bulletY, playerX, playerY):
            game_over_text()
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            boss_active = False

    # Movimiento de la bala del jugador
    if bulletY <= 0:
        bulletY = 480
        bullet_state = "ready"

    if bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change

    player(playerX, playerY)
    show_score(textX, textY)
    pygame.display.update()
