import pygame as pg
from pygame.sprite import Sprite
import random

class Obstacles(Sprite):
    """A class to represent obstacles in the game."""

    def __init__(self, settings, screen):
        """Initialize the obstacles and set their positions along the screen."""
        self.screen = screen
        self.settings = settings
        self.rock_img = pg.transform.scale(pg.image.load("images/Rock Pile.png"), (75, 75))
        self.puddle_img = pg.transform.scale(pg.image.load("images/puddle_light_blue.png"), (100, 65))
        self.rock_rect = self.rock_img.get_rect()
        self.puddle_rect = self.puddle_img.get_rect()

        self.obstacles = []
        self.generate_obstacles()

    def generate_obstacles(self):
        """Randomly generate obstacles along the level."""
        self.obstacles.clear()
        level_length = 10000  # How far the level goes (in pixels)
        x = 500
        while x < level_length - 1500:
            kind = random.choice(['rock', 'puddle'])
            if kind == 'rock':
                y = 640
                img = self.rock_img
                rock_rect = pg.Rect(x, y, self.rock_rect.width, self.rock_rect.height)
            else:
                y = 655
                img = self.puddle_img
                puddle_rect = pg.Rect(x, y, 100, 65)
            self.obstacles.append({'type': kind, 'img': img, 'x': x, 'y': y, 'rect': rock_rect if kind == 'rock' else puddle_rect})
            x += random.randint(600, 1000)  # Distance to next obstacle

    def update(self, world_offset):
        """Update obstacle positions based on background scroll."""
        for obs in self.obstacles:
            obs['screen_x'] = obs['x'] - world_offset
            obs['rect'].x = obs['screen_x']

            # Use world coordinates for collision detection
            obstacle_world_rect = obs['rect'].copy()
            obstacle_world_rect.x = obs['x'] # Set to world x

    def blit_obstacles(self):
        """Draw the obstacles to the screen."""
        for obs in self.obstacles:
            # Only draw if on screen
            if -100 < obs['screen_x'] < self.settings.screen_width + 100:
                self.screen.blit(obs['img'], (obs['screen_x'], obs['y']))

class Carrots(Obstacles):
    """A class to represent carrot obstacles in the game."""

    def __init__(self, settings, screen):
        """Initialize the carrot obstacles."""
        super().__init__(settings, screen)
        self.screen = screen
        self.settings = settings
        self.carrot_img = pg.transform.scale(pg.image.load("images/carrot.png"), (35, 35))
        self.carrot_rect = self.carrot_img.get_rect()
        self.collectibles = []  # Placeholder for carrot collectibles
        self.generate_carrots()

    def generate_carrots(self):
        """Randomly generate carrot obstacles along the level."""
        self.collectibles.clear()
        level_length = 10000  # How far the level goes (in pixels)
        x = 500
        y = random.randint(500, 665)
        self.carrot_rect = pg.Rect(x, y, 35, 35)
        carrots_in_level = 20  # Number of carrots to generate
        attempts = 0 # To avoid infinite loop in case of too many attempts
        max_attempts = 1000  # Limit attempts to avoid infinite loop
        while len(self.collectibles) < carrots_in_level and attempts < max_attempts:
            x = random.randint(500, level_length - 1500)
            y = random.randint(500, 665)
            rect = pg.Rect(x, y, 35, 35)
            collision = False
            for carrot in self.collectibles:
                if carrot['rect'].colliderect(rect):
                    collision = True
                    break
            if not collision:
                self.collectibles.append({'type': 'carrot', 'img': self.carrot_img, 'x': x, 'y': y, 'rect': rect})
                x += random.randint(500, 700)  # Distance to next carrot
            attempts += 1

    def update(self, world_offset):
        """Update obstacle positions based on background scroll."""
        for carrot in self.collectibles:
            carrot['screen_x'] = carrot['x'] - world_offset
            carrot['rect'].x = carrot['screen_x']


    def blit_carrots(self):
        """Draw carrots to the screen."""
        for carrot in self.collectibles:
            if -100 < carrot['screen_x'] < self.settings.screen_width + 100:
                self.screen.blit(carrot['img'], (carrot['screen_x'], carrot['y']))