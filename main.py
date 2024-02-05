#!/bin/python3
# Example file showing a basic pygame "game loop"
import itertools
import math
import pygame
import sys
import enum
import random
from enum import auto
from typing import Any, Callable, Iterable, List, Optional, Protocol, Tuple, Dict

from pygame.sprite import AbstractGroup

def get_resolution() -> Tuple[Tuple[int, int], bool]:
    if len(sys.argv) < 2 or sys.argv[1] == "windowed":
        return (640, 480), False
    else:
        return (1280, 960), True

class Controls(enum.Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    SHOOT = auto()
    BOMB = auto()
    FOCUS = auto()

PygameKey = int
def load_controls() -> Dict[PygameKey, Controls]:
    return {
        pygame.K_UP: Controls.UP,
        pygame.K_DOWN: Controls.DOWN,
        pygame.K_LEFT: Controls.LEFT,
        pygame.K_RIGHT: Controls.RIGHT,
        pygame.K_z: Controls.SHOOT,
        pygame.K_x: Controls.BOMB,
        pygame.K_LSHIFT: Controls.FOCUS,
    }

CONTROL_SCHEME = load_controls()

def get_inputs(control_scheme=CONTROL_SCHEME) -> Dict[Controls, bool]:
    all_pressed = pygame.key.get_pressed()
    return {control_name: all_pressed[key] for key, control_name in control_scheme.items()}

PLAYER_SPEED = 5

class Player(pygame.sprite.Sprite):
    image = pygame.image.load("sprites/reimu0.png")  # Maybe have several frames of animation
    pos = pygame.math.Vector2(320, 320)

    def update(self, controls):
        offset = movement(controls)
        self.pos += offset * PLAYER_SPEED
        self.constrain_position()
    
    def constrain_position(self):
        if self.pos.x > 640:
            self.pos.x = 640
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y > 480:
            self.pos.y = 480
        if self.pos.y < 0:
            self.pos.y = 0

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.pos)

class EnemyType(enum.Enum):
    SMALL = auto()
    LARGE = auto()
    BOSS = auto()

class Bullet(pygame.sprite.Sprite):
    SPEED: int = 15
    pos: pygame.math.Vector2
    direction: pygame.math.Vector2

    def __init__(self, spawn_point: pygame.sprite.Sprite, direction: float) -> None:
        self.image = pygame.image.load("sprites/bullet.png")
        self.pos = pygame.math.Vector2(spawn_point)
        self.direction = pygame.math.Vector2()
        self.direction.from_polar((self.SPEED, direction))

    def update(self) -> None:
        self.pos += self.direction
        self.pos.x = int(self.pos.x)
        self.pos.y = int(self.pos.y)
    
    def on_screen(self) -> bool:
        return 0 <= self.pos.x <= 640 and 0 <= self.pos.y <= 480

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.pos)

class Enemy(pygame.sprite.Sprite):
    TOP_LEFT = pygame.math.Vector2(0, 0)
    TOP_RIGHT = pygame.math.Vector2(640, 0)

    def elapsed_time(self, time: int) -> int:
        return time-self.spawn_time

    def TOP_LEFT_ARC(spawn_time: int):
        def move(time):
            angle = -(time-spawn_time)  # Angle in degrees measured from (positive x axis) = 0
            radius = 100
            offset = pygame.math.Vector2()
            offset.from_polar((radius, angle))
            return Enemy.TOP_LEFT + offset
        return move
    def TOP_RIGHT_ARC(spawn_time: int):
        def move(time):
            angle = 180+(time-spawn_time)  # Angle in degrees measured from (positive x axis) = 0
            radius = 100
            offset = pygame.math.Vector2()
            offset.from_polar((radius, angle))
            return Enemy.TOP_RIGHT + offset
        return move

    def ANCHORED(x: int):
        def anchored(time: int):
            return pygame.math.Vector2(x, 100)
    
        return anchored

    movement_function: Callable[[int], pygame.math.Vector2]
    pos = pygame.math.Vector2()
    spawn_time: int

    def __init__(self, enemy_type: EnemyType, movement_function: Callable[[int], pygame.math.Vector2]) -> None:
        self.image = pygame.image.load(f"sprites/{self.get_image(enemy_type)}")
        print(enemy_type)
        self.movement_function = movement_function

    def get_image(self, enemy_type: EnemyType) -> str:
        print(enemy_type)
        if enemy_type is EnemyType.SMALL:
            return "enemy_small.png"
        elif enemy_type is EnemyType.LARGE:
            return "enemy_large.png"
        else:
            return "enemy_small.png"

    @classmethod
    def random_zako(cls, current_time: int):
        enemy_type = random.choices(
            (EnemyType.SMALL, EnemyType.LARGE),
            (0.9, 0.1)
        )[0]

        movement_type = random.choice(
            (cls.TOP_LEFT_ARC(current_time), cls.TOP_RIGHT_ARC(current_time), cls.ANCHORED(random.randint(0, 640)))
        )

        return cls(enemy_type, movement_type)

    def update(self, current_time: int) -> None:
        # Move self
        self.pos = self.movement_function(current_time)

    def get_bullets(self) -> List[Bullet]:
        if random.randint(0, 10) == 0:
            return [Bullet(self.pos, direction=90)]
        else:
            return []

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.pos)

BLACK = pygame.Color("black")
WHITE = pygame.Color("white")

def main():
    # pygame setup
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()
    pygame.display.set_caption("東方空想者 ~ Skyclad Iconoclast v1.06")
    resolution, fullscreen = get_resolution()
    
    if fullscreen:
        screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(resolution)

    clock = pygame.time.Clock()
    running = True

    SHOOT_SFX = pygame.mixer.Sound("sfx/shoot.wav")
    PUCHUN = pygame.mixer.Sound("sfx/puchun.wav")

    sin = 0
    score = 0
    player = Player()
    enemies = []
    friendly_bullets = []
    enemy_bullets = []
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill(BLACK)

        # RENDER YOUR GAME HERE
        sin, new_enemy, should_shoot, new_enemy_bullets = update(player, enemies, sin, clock.get_time(), get_inputs(), itertools.chain(friendly_bullets, enemy_bullets))
        if new_enemy:
            enemies.append(new_enemy)
        
        enemy_bullets.extend(new_enemy_bullets)
        enemy_bullets = prune_bullets(enemy_bullets)
        friendly_bullets = prune_bullets(friendly_bullets)
        if collide_player_and_enemy_bullets(player.pos, enemy_bullets):
            PUCHUN.play()
        
        for enemy in collide_enemies_and_player_bullets(enemies, friendly_bullets):
            sin = (sin + 5) * 2
            sin = min(sin, 300)
            score += int(1000 * 1.2 * 30**(sin//100))
            enemies.remove(enemy)
            

        if should_shoot:
            friendly_bullets.append(Bullet(player.pos + pygame.math.Vector2(26, 0), -90))
            SHOOT_SFX.play()


        draw(screen, player, enemies, sin, friendly_bullets, enemy_bullets, score)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()


def movement(controls: Dict[Controls, bool]) -> pygame.math.Vector2:
    translation = pygame.math.Vector2(0, 0)
    if controls[Controls.LEFT]:
        translation.x = -1
    elif controls[Controls.RIGHT]:
        translation.x = 1
    
    if controls[Controls.UP]:
        translation.y = -1
    elif controls[Controls.DOWN]:
        translation.y = 1
    
    # Slow down if focussing
    if controls[Controls.FOCUS]:
        translation *= 0.5

    return translation

def prune_bullets(bullets: List[Bullet]):
    # Remove all bullets that aren't on the screen any more
    return [bullet for bullet in bullets if bullet.on_screen()]

def update(player: Player, enemies: List[Enemy], sin: int, current_time: int, controls: Dict[Controls, bool], bullets: Iterable[Bullet]) -> Tuple[int, Optional[Enemy], bool, List[Bullet]]:
    player.update(controls)
    for enemy in enemies:
        enemy.update(current_time)

    enemy_bullets = []
    for enemy in enemies:
        enemy_bullets.extend(enemy.get_bullets())
    
    for bullet in bullets:
        bullet.update()

    enemy = None
    if random.randint(0, 30) == 0:
        enemy = Enemy.random_zako(current_time)

    new_sin = min(300, max(sin - 0.5, 0))
    return (new_sin, enemy, controls[Controls.SHOOT], enemy_bullets)

def draw(screen: pygame.Surface, player: Player, enemies: List[Enemy], sin: int, friendly_bullets: List[Bullet], enemy_bullets: List[Bullet], score: int) -> None:
    # Draw player
    player.draw(screen)

    # Draw enemies
    for enemy in enemies:
        enemy.draw(screen)
    
    # Draw bullets
    for bullet in itertools.chain(friendly_bullets, enemy_bullets):
        bullet.draw(screen)
    
    # Draw UI
    ## Draw score
    font = pygame.font.SysFont(pygame.font.get_default_font(), 48)
    screen.blit(font.render(str(score), True, WHITE), (0, 0))

    ## Draw bar representing amount of harm done
    sin_capped = min(sin, 300)
    sin_color = interpolate_sin(sin)
    screen.blit(font.render("Sin", True, WHITE), (160, 5))
    pygame.draw.rect(screen, WHITE, (160, 40, 310, 60))
    pygame.draw.rect(screen, sin_color, (165, 45, sin_capped, 50))

def collide_player_and_enemy_bullets(player_pos: pygame.math.Vector2, enemy_bullets: List[Bullet]) -> bool:
    # Return True if player should die to bullet
    return any(player_pos.distance_squared_to(enemy_bullet.pos) <= 64 for enemy_bullet in enemy_bullets)

def collide_enemies_and_player_bullets(enemies: List[Enemy], player_bullets: List[Bullet]) -> List[Enemy]:
    # Return list of all enemies that need to be killed
    return [enemy for enemy in enemies if any(enemy.pos.distance_squared_to(bullet.pos) < 900 for bullet in player_bullets)]

def interpolate_sin(value: int) -> pygame.Color:
    c = pygame.Color(0, 0, 0)
    c.hsva = (100-value//3, 100, 100, 40)
    return c

if __name__ == "__main__":
    main()