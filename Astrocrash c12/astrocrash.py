import pygame
import math
import random
import os
import sys

# Initialize pygame
pygame.init()

# Constants     - khung cua so chuong trinh
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Astrocrash")
clock = pygame.time.Clock()

# Resource path     - duong dan lay tai nguyen tai thu muc chua file py
if getattr(sys, 'frozen', False):
    RESOURCE_PATH = sys._MEIPASS
else:
    RESOURCE_PATH = os.path.dirname(os.path.abspath(__file__))

def load_image(filename, size=None):
    image = pygame.image.load(os.path.join(RESOURCE_PATH, filename)).convert_alpha()
    if size:
        image = pygame.transform.smoothscale(image, size)
    return image

def load_sound(filename):
    return pygame.mixer.Sound(os.path.join(RESOURCE_PATH, filename))

def load_music(filename):
    pygame.mixer.music.load(os.path.join(RESOURCE_PATH, filename))

# Load assets
background_image = load_image("background.png", (WIDTH, HEIGHT))
ship_image = load_image("ship.png", (60, 60))
missile_image = load_image("missile.png", (30, 40))
asteroid_image = load_image("asteroid.png", (80, 80))
explosion_image = load_image("explosion.png", (60, 60))
shoot_sound = load_sound("shoot.wav")
boom_sound = load_sound("boom.wav")
load_music("background_music.mp3")
pygame.mixer.music.play(-1)

# Classes
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = ship_image
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.angle = 0
        self.speed = 0
        self.head_offset = 30

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle += 5
        if keys[pygame.K_RIGHT]:
            self.angle -= 5
        if keys[pygame.K_UP]:
            self.speed += 0.1
        if keys[pygame.K_DOWN]:
            self.speed -= 0.1

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        rad = math.radians(-self.angle)
        self.rect.x += self.speed * math.cos(rad)
        self.rect.y += self.speed * math.sin(rad)

        self.rect.x %= WIDTH
        self.rect.y %= HEIGHT

    def get_head_position(self):
        rad = math.radians(-self.angle)
        offset_x = self.head_offset * math.cos(rad)
        offset_y = self.head_offset * math.sin(rad)
        head_x = self.rect.centerx + offset_x
        head_y = self.rect.centery + offset_y
        return head_x, head_y

    def shoot(self):
        shoot_sound.play()
        missile_x, missile_y = self.get_head_position()
        return Missile(missile_x, missile_y, self.angle)


class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.transform.rotate(missile_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = 10

    def update(self):
        rad = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(rad)
        self.rect.y -= self.speed * math.sin(rad)
        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = asteroid_image

        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, WIDTH)
            y = 0
        elif side == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT
        elif side == 'left':
            x = 0
            y = random.randint(0, HEIGHT)
        else:
            x = WIDTH
            y = random.randint(0, HEIGHT)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.uniform(1, 3)
        self.angle = math.degrees(math.atan2(HEIGHT // 2 - y, WIDTH // 2 - x)) + random.uniform(-30, 30)

    def update(self):
        rad = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(rad)
        self.rect.y += self.speed * math.sin(rad)
        self.rect.x %= WIDTH
        self.rect.y %= HEIGHT


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = explosion_image
        self.rect = self.image.get_rect(center=(x, y))
        self.life = 20

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()

# Sprite groups     - bieu dien do hoa
all_sprites = pygame.sprite.Group()
missiles = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
explosions = pygame.sprite.Group()

ship = Ship()
all_sprites.add(ship)

for _ in range(5):
    asteroid = Asteroid()
    all_sprites.add(asteroid)
    asteroids.add(asteroid)

# Game state
score = 0
running = True
playing = False
font = pygame.font.SysFont(None, 48)

# Game loop     - vong lap logic, cap nhat, hien thi len man hinh
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not playing:
                playing = True
            elif event.key == pygame.K_SPACE:
                missile = ship.shoot()
                all_sprites.add(missile)
                missiles.add(missile)

    if playing:
        all_sprites.update()

        hits = pygame.sprite.groupcollide(asteroids, missiles, True, True)
        for hit in hits:
            boom_sound.play()
            score += 10
            explosion = Explosion(hit.rect.centerx, hit.rect.centery)
            all_sprites.add(explosion)
            explosions.add(explosion)
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

        # Check for collision between ship and asteroid     - ship cham asteroid thi game over
        if pygame.sprite.spritecollideany(ship, asteroids):
            boom_sound.play()
            playing = False

    # Draw
    screen.blit(background_image, (0, 0))
    all_sprites.draw(screen)

    if playing:
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
    else:
        if score > 0:
            game_over_text = font.render("Game Over", True, WHITE)
        else:
            game_over_text = font.render("Press any key to Start", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()