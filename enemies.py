# This section will take care of:
# Snake Enemies
# and Dog/Wolf Boss
import pygame as pg
from pygame.sprite import Sprite
from obstacles import Obstacles, Carrots
import random

class Snake(Sprite):
    def __init__(self, settings, screen, obstacles, carrots):
        super().__init__()
        snake_sheet = pg.image.load('images/snake-NESW.png').convert_alpha()
        self.settings = settings
        self.screen = screen
        self.health = 1
        self.snake_speed = 3
        self.obstacles = obstacles
        self.carrots = carrots
        self.snakes = []

        # Snake movement left
        self.left_1 = snake_sheet.subsurface((5, 103, 24, 21))
        self.left_2 = snake_sheet.subsurface((35, 103, 24, 21))
        self.left_3 = snake_sheet.subsurface((68, 103, 24, 21))

        # Snake movement right
        self.right_1 = snake_sheet.subsurface((2, 40, 24, 21))
        self.right_2 = snake_sheet.subsurface((34, 40, 24, 21))
        self.right_3 = snake_sheet.subsurface((66, 40, 24, 21))

        # Snake turning image
        self.turning = snake_sheet.subsurface((36, 69, 22, 24))

        self.original_snake_sprites = {
                                "moving_left1" : self.left_1,
                                "moving_left2" : self.left_2,
                                "moving_left3" : self.left_3,
                                "moving_right1" : self.right_1,
                                "moving_right2" : self.right_2,
                                "moving_right3" : self.right_3,
                                "turning" : self.turning,                                
                                }
        
        self.scale_factor = 2.5

        self.scaled_snake_animations = {}
        for name, original_sprites in self.original_snake_sprites.items():
            scaled_sprites = pg.transform.scale_by(original_sprites, self.scale_factor)
            self.scaled_snake_animations[name] = scaled_sprites
        
        self.turning_frame = ["turning"]
    
        self.walk_left_frames = [
            "moving_left1", "moving_left2", "moving_left3", "moving_left2"
        ]
        self.move_right_frames = [
            "moving_right1", "moving_right2", "moving_right3", "moving_right2"
        ]

        self.current_animation_frames = self.turning_frame
        self.frame_index = 0
        self.animation_frame_counter = 0
        self.facing_direction = "left"

        self.current_image = self.scaled_snake_animations[self.current_animation_frames[self.frame_index]]
        self.snake_rect = self.current_image.get_rect()

        screen_rect = self.screen.get_rect()
        self.snake_rect.bottom = screen_rect.bottom - 105
        self.ground_y = self.snake_rect.bottom

        self.x = float(self.snake_rect.x)
        self.y = float(self.snake_rect.y)

        # Movement flags for character movement.
        self.moving_right = False
        self.moving_left = False
        self.turning = False

        self.generate_snakes()  # Generate initial snakes

    def generate_snakes(self):
        """Randomly generate snake obstacles along the level."""
        level_length = 10000  # How far the level goes (in pixels)
        x = 500
        y = 640
        self.snake_img = self.scaled_snake_animations["moving_left1"]
        self.snake_rect = self.snake_img.get_rect(topleft=(x, y)) 
        snakes_in_level = 10  # Number of snakes to generate
        attempts = 0  # To avoid infinite loop in case of too many attempts
        max_attempts = 1000  # Limit attempts to avoid infinite loop
        while len(self.snakes) < snakes_in_level and attempts < max_attempts:
            x = random.randint(500, level_length - 1500)
            y = 640
            rect = pg.Rect(x, y, 60, 52)
            collision = False
            for obs in self.obstacles.obstacles:
                if rect.colliderect(obs['rect']):
                    collision = True
                    break
            for carrot in self.carrots.collectibles:
                if rect.colliderect(carrot['rect']):
                    collision = True
                    break
            if not collision:
                self.snakes.append({'type': 'snake',
                                    'img': self.snake_img,
                                    'x': x,
                                    'y': y,
                                    'rect': rect,
                                    'direction': 'left',
                                    'animation_frames': self.walk_left_frames[:],
                                    'frame_index': 0,
                                    'animation_counter': 0
                                    })
                x += random.randint(200, 500)  # Distance to next snake
            attempts += 1

    def update(self):
        for snake in self.snakes:
            # Update screen_x for drawing
            prev_x = snake['x']

            # Move snake and set animation frames
            if snake['direction'] == "left":
                snake['animation_frames'] = self.walk_left_frames
                snake['x'] -= self.snake_speed
            else:
                snake['animation_frames'] = self.move_right_frames
                snake['x'] += self.snake_speed

            # Create a swept rect covering the path from prev_x to new x
            swept_left = min(prev_x, snake['x'])
            swept_right = max(prev_x + snake['rect'].width, snake['x'] + snake['rect'].width)
            swept_rect = snake['rect'].copy()
            swept_rect.x = swept_left
            swept_rect.width = swept_right - swept_left

            # Use world coordinates for collision detection
            snake_world_rect = snake['rect'].copy()
            snake_world_rect.x = snake['x'] # Set to world x

            # Check for collision with any obstacle
            collided = False
            for obs in self.obstacles.obstacles:
                obs_world_rect = obs['rect'].copy()
                obs_world_rect.x = obs['x']  # Set to world x
                if snake_world_rect.colliderect(obs_world_rect):
                    collided = True
                    break

            # Turn around if collided
            if collided:
                snake['animation_frames'] = self.turning_frame
                snake['frame_index'] = 0  # Start turning animation from first frame
                if snake['direction'] == "left":
                    snake['direction'] = "right"
                    snake['x'] += self.snake_speed  # Move away from obstacle
                else:
                    snake['direction'] = "left"
                    snake['x'] -= self.snake_speed  # Move away from obstacle

            # Animate snake
            snake['animation_counter'] = snake.get('animation_counter', 0) + 1
            if snake['animation_counter'] >= self.settings.snake_animation_speed_frames:
                snake['frame_index'] = (snake['frame_index'] + 1) % len(snake['animation_frames'])
                snake['animation_counter'] = 0

            # Update image for this snake
            frame_name = snake['animation_frames'][snake['frame_index']]
            snake['img'] = self.scaled_snake_animations[frame_name]

            snake['rect'].x = snake['x']
            snake['rect'].y = snake['y']


    def blit_snakes(self, world_offset):
        """Draw snakes to the screen and show their rects."""
        for snake in self.snakes:
            screen_x = snake['x'] - world_offset
            if -100 < screen_x < self.settings.screen_width + 100:
                # Draw the snake image
                self.screen.blit(snake['img'], (screen_x, snake['y']))

class WolfBoss(Sprite):
    def __init__(self, settings, screen, bunny):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.bunny = bunny
        self.invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = 20  # Duration in frames
        self.wolf_sheet = pg.image.load("images/wolfsheet1.png").convert_alpha()

        self.wolf_standing = self.wolf_sheet.subsurface(pg.Rect(319, 352, 63, 31))
        self.wolf_attack1 = self.wolf_sheet.subsurface(pg.Rect(386, 352, 60, 31))
        self.wolf_attack2 = self.wolf_sheet.subsurface(pg.Rect(448, 351, 64, 32))
        self.wolf_attack3 = self.wolf_sheet.subsurface(pg.Rect(511, 352, 64, 31))

        self.wolf_sprites = {
            "standing": self.wolf_standing,
            "attack1": self.wolf_attack1,
            "attack2": self.wolf_attack2,
            "attack3": self.wolf_attack3
        }

        self.scaled_wolf_sprites = {}
        for name, original_sprite in self.wolf_sprites.items():
            scaled_sprite = pg.transform.scale_by(original_sprite, 5)
            self.scaled_wolf_sprites[name] = scaled_sprite

        self.wolf_attacking = [
            "attack1", "attack2", "attack3"
        ]      
        
        self.health = 5
        self.attack_power = 1
        self.last_attack_time = 0
        self.attack_cooldown = 3000  # 3 seconds in milliseconds

        self.current_animation_frames = ["standing"]  # Use a list for consistency
        self.frame_index = 0
        self.animation_frame_counter = 0
        self.facing_direction = "left"

        self.current_image = self.scaled_wolf_sprites[self.current_animation_frames[self.frame_index]]
        self.rect = self.current_image.get_rect()
        self.rect.x = self.settings.level_length - 1000
        self.rect.y = self.bunny.ground_y - self.rect.height + 20

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def attack_phase(self, world_offset):
        now = pg.time.get_ticks()
        bunny_rect = self.bunny.rect.copy()
        bunny_rect.x += world_offset
        bunny_rect.y = self.bunny.y
        distance_to_bunny = abs(self.rect.x - bunny_rect.x)

        # Start attack if in range and cooldown is up
        if distance_to_bunny <= 500:
            if not getattr(self, "is_attacking", False) and now - self.last_attack_time >= self.attack_cooldown:
                self.is_attacking = True
                pg.mixer.Sound('audio/crunchybite.ogg').play()
                self.current_animation_frames = self.wolf_attacking
                self.frame_index = 0
                self.animation_frame_counter = 0
                self.last_attack_time = now
        else:
            self.is_attacking = False
            self.current_animation_frames = ["standing"]
            self.frame_index = 0
            self.animation_frame_counter = 0

        if self.invincible:
            self.invincibility_timer += 1
            if self.invincibility_timer >= self.invincibility_duration:
                self.invincible = False
                self.invincibility_timer = 0

        # Animate attack or waiting
        self.animation_frame_counter += 1
        if getattr(self, "is_attacking", False):
            if self.animation_frame_counter >= getattr(self.settings, "wolf_animation_speed_frames", 4):
                self.frame_index += 1
                self.animation_frame_counter = 0
                if self.frame_index >= len(self.wolf_attacking):
                    self.is_attacking = False
                    self.current_animation_frames = ["standing"]
                    self.frame_index = 0
        else:
            self.frame_index = 0  # Always show first frame when waiting

        # --- Always update rect to match current frame ---
        screen_rect = self.screen.get_rect()
        current_frame_name = self.current_animation_frames[self.frame_index]
        current_image = self.scaled_wolf_sprites[current_frame_name]
        old_bottomleft = self.rect.bottomleft
        self.rect = current_image.get_rect()
        self.rect.bottomleft = old_bottomleft
        self.rect.bottom = screen_rect.bottom - 105  # Keep it above the ground
        self.current_image = current_image

    def draw(self, surface, world_offset=0):
        surface.blit(self.current_image, (self.rect.x - world_offset, self.rect.y))