#!/bin/python3
# Example file showing a basic pygame "game loop"
import pygame
import sys
import enum
from enum import auto
from typing import Tuple

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

def main():
    # pygame setup
    pygame.init()
    resolution, fullscreen = get_resolution()
    
    if fullscreen:
        screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(resolution)

    clock = pygame.time.Clock()
    running = True

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        # RENDER YOUR GAME HERE

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()

if __name__ == "__main__":
    main()