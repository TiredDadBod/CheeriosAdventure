# This section will focus on the main character, Cheerio
import pygame as pg
from pygame.sprite import Sprite
from obstacles import Obstacles

class Bunny(Sprite):
    """Class for the main character."""

    def __init__(self, settings, screen):
        """Initialize the main character."""
        super().__init__()
        # Bunny's stats.
        self.normal_speed = 5
        self.slower_speed = 1
        self.speed = self.normal_speed
        self.attack_power = 2
        self.health = 3
        self.bunny_lives = 3
        self.invincible = False
        self.invincibility_duration = 120  # frames (2 seconds = 120 frames)
        self.invincibility_timer = 0

        self.initial_jump_velocity = -12
        self.gravity = 0.5

        self.y_velocity = 0
        self.on_ground = True

        self.is_attacking = False
        self.attack_offset = 0
        self.attack_start_x = 0

        self.settings = settings
        self.screen = screen
        self.obstacles = Obstacles(settings, screen)

        # This is the Bunny Sprite Sheet
        bunny_sheet = pg.image.load('images/bunnysheet5.png').convert_alpha()

        # Bunny standing still.
        self.original_facing_right = bunny_sheet.subsurface(pg.Rect(27,217,25,27))
        self.original_facing_left = bunny_sheet.subsurface(pg.Rect(26,288,25,27))

        # Bunny moving right.
        self.original_walking_right1 = bunny_sheet.subsurface(pg.Rect(58,215,26,28))
        self.original_walking_right2 = bunny_sheet.subsurface(pg.Rect(90,217,33,28))
        self.original_walking_right3 = bunny_sheet.subsurface(pg.Rect(134,217,29,25))

        # Bunny moving left.
        self.original_walking_left1 = bunny_sheet.subsurface(pg.Rect(60,287,26,28))
        self.original_walking_left2 = bunny_sheet.subsurface(pg.Rect(96,288,33,28))
        self.original_walking_left3 = bunny_sheet.subsurface(pg.Rect(138,291,29,25))

        # Bunny jumping right.
        self.original_jump_right1 = bunny_sheet.subsurface(pg.Rect(58,180,26,26))
        self.original_jump_right2 = bunny_sheet.subsurface(pg.Rect(134,178,29,25))

        # Bunny jumping left.
        self.original_jump_left1 = bunny_sheet.subsurface(pg.Rect(58,254,26,26))
        self.original_jump_left2 = bunny_sheet.subsurface(pg.Rect(136,258,29,25))

        # Bunny attacking right.
        self.original_right_attack1 = bunny_sheet.subsurface(pg.Rect(210,220,27,22))
        self.original_right_attack2 = bunny_sheet.subsurface(pg.Rect(242,223,28,19))
        self.original_right_attack3 = bunny_sheet.subsurface(pg.Rect(274,223,28,19))
        # Bunny attacking left.
        self.original_left_attack1 = bunny_sheet.subsurface(pg.Rect(207,293,27,22))
        self.original_left_attack2 = bunny_sheet.subsurface(pg.Rect(240,295,28,19))
        self.original_left_attack3 = bunny_sheet.subsurface(pg.Rect(274,294,28,19))

        # Storage for original sprites.
        self.original_sprites = {
                                "facing_right" : self.original_facing_right,
                                "facing_left" : self.original_facing_left,
                                "walking_right1" : self.original_walking_right1,
                                "walking_right2" : self.original_walking_right2,
                                "walking_right3" : self.original_walking_right3,
                                "walking_left1" : self.original_walking_left1,
                                "walking_left2" : self.original_walking_left2,
                                "walking_left3" : self.original_walking_left3,
                                "jump_right1" : self.original_jump_right1,
                                "jump_right2" : self.original_jump_right2,
                                "jump_left1" : self.original_jump_left1,
                                "jump_left2" : self.original_jump_left2,
                                "right_attack1" : self.original_right_attack1,
                                "right_attack2" : self.original_right_attack2,
                                "right_attack3" : self.original_right_attack3,
                                "left_attack1" : self.original_left_attack1,
                                "left_attack2" : self.original_left_attack2,
                                "left_attack3" : self.original_left_attack3,
                                }
        
        self.scale_factor = 3

        self.scaled_animations = {}
        for name, original_sprites in self.original_sprites.items():
            scaled_sprites = pg.transform.scale_by(original_sprites, self.scale_factor)
            self.scaled_animations[name] = scaled_sprites

        self.idle_right_frame = ["facing_right"]
        self.idle_left_frame = ["facing_left"]

        self.walk_right_frames = [
            "walking_right1", "walking_right2", "walking_right3", "facing_right"
        ]
        self.walk_left_frames = [
            "walking_left1", "walking_left2", "walking_left3", "facing_left"
        ]
        self.jump_right_frames = [
            "jump_right1", "jump_right2", "jump_right2", "jump_right1"
        ]
        self.jump_left_frames = [
            "jump_left1", "jump_left2", "jump_left2", "jump_left1"
        ]
        self.attack_right_frames = [
            "right_attack1", "right_attack2", "right_attack3", "facing_right"
        ]
        self.attack_left_frames = [
            "left_attack1", "left_attack2", "left_attack3", "facing_left"
        ]

        self.current_animation_frames = self.idle_right_frame
        self.frame_index = 0
        self.animation_frame_counter = 0
        self.facing_direction = "right"

        self.current_image = self.scaled_animations[self.current_animation_frames[self.frame_index]]
        self.rect = self.current_image.get_rect()

        screen_rect = self.screen.get_rect()
        self.rect.bottom = screen_rect.bottom - 105
        self.ground_y = self.rect.bottom

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # Movement flags for character movement.
        self.moving_right = False
        self.moving_left = False
        self.jumping = False
        self.attacking = False

    def moving_bunny(self):
        """Move the bunny and update its animation frames."""
        self.prev_x = self.x  # Store previous x before moving
        self.prev_y = self.y  # Store previous y before moving
        previous_animation_frames = self.current_animation_frames
        screen_center = self.settings.screen_width // 2
        bunny_on_screen = int(self.x)

        # Prevent movement changes while attacking.
        if self.is_attacking:
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
            return

        # Handle jumping
        if self.jumping and self.on_ground:
            self.on_ground = False
            self.y_velocity = self.initial_jump_velocity
            if self.facing_direction == "right":
                self.current_animation_frames = self.jump_right_frames
            else:
                self.current_animation_frames = self.jump_left_frames

    # --- Always update animation based on movement flags ---
        if self.moving_right:
            self.facing_direction = "right"
            if self.on_ground:
                self.current_animation_frames = self.walk_right_frames
            else:
                self.current_animation_frames = self.jump_right_frames
            if bunny_on_screen < screen_center:
                self.x += self.speed
            elif self.rect.colliderect(self.obstacles.puddle_rect) and screen_center:
                self.speed = self.slower_speed
            else:
                self.settings.update_bg(True, False)
        elif self.moving_left:
            self.facing_direction = "left"
            if self.on_ground:
                self.current_animation_frames = self.walk_left_frames
            else:
                self.current_animation_frames = self.jump_left_frames
            if bunny_on_screen > 100:
                self.x -= self.speed
            else:
                self.settings.update_bg(False, True)
        else:
            if self.on_ground:
                if self.facing_direction == "right":
                    self.current_animation_frames = self.idle_right_frame
                else:
                    self.current_animation_frames = self.idle_left_frame
                self.frame_index = 0
                self.animation_frame_counter = 0

        if self.x < 0:
            self.x = 0

        # This tracks the jump and gravity.
        if not self.on_ground:
            self.y_velocity += self.gravity
            self.y += self.y_velocity
            

        # This handles the landing.
        if self.y + self.rect.height >= self.ground_y:
            self.y = self.ground_y - self.rect.height
            self.y_velocity = 0
            self.on_ground = True
            self.jumping = False

            if not (self.moving_right or self.moving_left):
                if self.facing_direction == "right":
                    self.current_animation_frames = self.idle_right_frame
                else:
                    self.current_animation_frames = self.idle_left_frame
                self.frame_index = 0
                self.animation_frame_counter = 0

        self.y_velocity += self.gravity
        self.y += self.y_velocity

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # This updates the animation frames.
        if self.current_animation_frames == previous_animation_frames:
            self.animation_frame_counter += 1
            if self.animation_frame_counter >= self.settings.bunny_animation_speed_frames:
                self.frame_index = (self.frame_index + 1) % len(self.current_animation_frames)
                self.animation_frame_counter = 0

        old_midbottom = self.rect.midbottom
        self.current_image = self.scaled_animations[self.current_animation_frames[self.frame_index]]
        self.rect = self.current_image.get_rect(midbottom=old_midbottom)

    def bunny_attack(self):
        """Make bunny attack and update position."""
        previous_animation_frames = self.current_animation_frames
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Start attack if requested and not already attacking
        if self.attacking and not self.is_attacking:
            self.is_attacking = True
            self.attack_start_x = self.x
            self.frame_index = 0
            self.animation_frame_counter = 0
            if self.facing_direction == "right":
                self.current_animation_frames = self.attack_right_frames
                self.attack_offset = 30
            else:
                self.current_animation_frames = self.attack_left_frames
                self.attack_offset = -30
            self.attacking = False
            self.x += self.attack_offset  # Move forward ONCE at start

        # Play attack animation if attacking
        if self.is_attacking:
            self.animation_frame_counter += 1
            if self.animation_frame_counter >= self.settings.bunny_animation_speed_frames:
                self.frame_index += 1
                self.animation_frame_counter = 0
                if self.frame_index >= len(self.current_animation_frames):
                    # Attack finished, reset
                    self.frame_index = 0
                    self.is_attacking = False
                    self.x = self.attack_start_x  # Move bunny back to original position
                    # Return to idle or jump animation
                    if self.on_ground:
                        if self.facing_direction == "right":
                            self.current_animation_frames = self.idle_right_frame
                        else:
                            self.current_animation_frames = self.idle_left_frame
                    else:
                        if self.facing_direction == "right":
                            self.current_animation_frames = self.jump_right_frames
                        else:
                            self.current_animation_frames = self.jump_left_frames

            # Update image and rect for attack
            old_midbottom = self.rect.midbottom
            self.current_image = self.scaled_animations[self.current_animation_frames[self.frame_index]]
            self.rect = self.current_image.get_rect(midbottom=old_midbottom)

        # Only animate idle/walk/jump if not attacking
        elif not self.is_attacking and self.current_animation_frames == previous_animation_frames:
            self.animation_frame_counter += 1
            if self.animation_frame_counter >= self.settings.bunny_animation_speed_frames:
                self.frame_index = (self.frame_index + 1) % len(self.current_animation_frames)
                self.animation_frame_counter = 0

            old_midbottom = self.rect.midbottom
            self.current_image = self.scaled_animations[self.current_animation_frames[self.frame_index]]
            self.rect = self.current_image.get_rect(midbottom=old_midbottom)

    def blitbunny(self, screen):
        """Draw the bunny and its attack rect (for debugging)."""
        self.screen.blit(self.current_image, self.rect)