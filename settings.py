import pygame as pg


class Settings:
    """A class to store all game settings."""

    def __init__(self):
        """Initialize game settings."""
        # Screen Settings
        self.screen_width = 1600
        self.screen_height = 800
        self.bg_x1 = 0
        self.bg_x2 = 0
        self.bg_x3 = 0
        self.bg_speed1 = 1  # Farthest, slowest
        self.bg_speed2 = 2  # Middle layer
        self.bg_speed3 = 5  # Closest, fastest
        self.level_length = 10000  # How far the level goes (in pixels)

        # Animation speed settings
        self.bunny_animation_speed_frames = 8
        self.snake_animation_speed_frames = 8

        self.layer_1 = pg.image.load('images/country-platform-files/layers/country-platform-back.png')
        self.scaled_1 = pg.transform.scale(self.layer_1, (self.screen_width, self.screen_height))
        self.layer_2 = pg.image.load('images/country-platform-files/layers/country-platform-forest.png')
        self.scaled_2 = pg.transform.scale(self.layer_2, (self.screen_width, self.screen_height))
        self.layer_3 = pg.image.load('images/country-platform-files/layers/country-platform-tiles-example.png')
        self.scaled_3 = pg.transform.scale(self.layer_3, (self.screen_width, self.screen_height))

    def update_bg(self, moving_right, moving_left):
        """Update background position based on bunny movement."""
        if moving_right:
            self.bg_x1 -= self.bg_speed1
            self.bg_x2 -= self.bg_speed2
            self.bg_x3 -= self.bg_speed3
        elif moving_left:
            if self.bg_x1 < self.screen_width:
                pass  # Prevent moving left if already at left edge
            else:
                self.bg_x1 += self.bg_speed1
                self.bg_x2 += self.bg_speed2
                self.bg_x3 += self.bg_speed3

        width = self.scaled_1.get_width()
        for attr in ['bg_x1', 'bg_x2', 'bg_x3']:
            x = getattr(self, attr)
            # Reset background position if it goes out of bounds
            if x <= -width:
                x += width
            elif x >= width:
                x -= width
            setattr(self, attr, x)

    def blitbg(self, screen):
        """Draw complete parallax background."""
        width = self.scaled_1.get_width()
        # Layer 1 (farthest)
        screen.blit(self.scaled_1, (self.bg_x1, 0))
        screen.blit(self.scaled_1, (self.bg_x1 + width, 0))
        # Layer 2 (middle)
        screen.blit(self.scaled_2, (self.bg_x2, 0))
        screen.blit(self.scaled_2, (self.bg_x2 + width, 0))
        # Layer 3 (closest/ground)
        screen.blit(self.scaled_3, (self.bg_x3, 0))
        screen.blit(self.scaled_3, (self.bg_x3 + width, 0))