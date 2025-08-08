import sys;
import pygame as pg;
from pathlib import Path;
from settings import Settings;
from bunny import Bunny;
from obstacles import Obstacles;
from obstacles import Carrots;
from enemies import Snake, WolfBoss;
from screens import MainMenu, PauseMenu, GameOverScreen, LevelCompleteScreen, Stats;
from pygame import mixer;

class Cheerios_Adventure:
    def __init__(self):
        """Initialize game instance of cheerio's adventure."""
        pg.init()
        self.clock = pg.time.Clock()
        self.settings = Settings()
        self.running = True

        self.screen = pg.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pg.display.set_caption("Cheerio's Adventure")

        self.bunny = Bunny(self.settings, self.screen)
        self.obstacles = Obstacles(self.settings, self.screen)
        self.carrots = Carrots(self.settings, self.screen)
        self.snakes = Snake(self.settings, self.screen, self.obstacles, self.carrots)
        self.main_menu = MainMenu(self.screen)
        self.pause_menu = PauseMenu(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)
        self.stats = Stats(self.screen, self.bunny, self.carrots)
        self.wolf_boss = WolfBoss(self.settings, self.screen, self.bunny)
        self.level_complete_screen = LevelCompleteScreen(self.screen, 0, self.stats)

        self.world_offset = 0  # Track how far the world has scrolled

    def run_game(self):
        """Start main loop for the game."""
        mixer.music.load('audio/Woodland Fantasy.mp3')
        mixer.music.play(-1)
        mixer.music.set_volume(0.3)
        self.show_main_menu()

        while True:
            self._check_events()
            if not self.bunny.alive:
                self.show_game_over_screen()
                continue
            self.bunny.moving_bunny()
            if self.wolf_boss.health == 0 or (self.bunny.x >= self.settings.level_length):
                self.show_level_complete_screen()
            if self.bunny.invincibility_timer:
                self.bunny.invincibility_timer += 1
                if self.bunny.invincibility_timer >= self.bunny.invincibility_duration:
                    self.bunny.invincible = False
                    self.bunny.invincibility_timer = 0
            self.bunny.bunny_attack()
            # Update world_offset when background scrolls
            if self.bunny.moving_right and int(self.bunny.x) >= self.settings.screen_width // 2:
                self.world_offset += self.settings.bg_speed3  # Use your ground layer speed
            elif self.bunny.moving_left and int(self.bunny.x) <= 100:
                self.world_offset -= self.settings.bg_speed3
            self.obstacles.update(self.world_offset)
            self.carrots.update(self.world_offset)
            self.snakes.update()
            self.wolf_boss.attack_phase(world_offset=self.world_offset)
            self._check_collision_events()
            self._check_boss_collision()

            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse clicks."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pg.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pg.K_d:
            self.bunny.moving_right = True
        elif event.key == pg.K_a:
            self.bunny.moving_left = True
        elif event.key == pg.K_w:
            self.bunny.jumping = True
            jump = pg.mixer.Sound('audio/qubodup-cfork-ccby3-jump.ogg')
            jump.set_volume(0.1)
            jump.play()
        elif event.key == pg.K_SPACE:
            self.bunny.moving_left = False
            self.bunny.moving_right = False
            self.bunny.attacking = True
        elif event.key == pg.K_p:
            self.show_pause_menu()
        elif event.key == pg.K_q:
            sys.exit()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pg.K_d:
            self.bunny.moving_right = False
        elif event.key == pg.K_a:
            self.bunny.moving_left = False
        elif event.key == pg.K_w:
            self.bunny.jumping = False
        elif event.key == pg.K_SPACE:
            self.bunny.attacking = False

    def show_main_menu(self):
        """Display the main menu and wait for user to start the game."""
        while True:
            self.main_menu.draw()
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.main_menu.start_button.collidepoint(event.pos):
                        return
                    elif self.main_menu.credits_button.collidepoint(event.pos):
                        credits = Path("credits.txt")
                        pull_credits = credits.read_text() if credits.exists() else "Credits file not found."
                        credits_font = pg.font.Font(None, 24)
                        split_credits = pull_credits.splitlines()
                        self.screen.fill((0, 0, 0))  # Clear the screen
                        for i, line in enumerate(split_credits):
                            display_credits = credits_font.render(line, True, (255, 255, 255))
                            self.screen.blit(display_credits, (20, 20 + i * 40))
                        pg.display.flip()
                        pg.time.wait(5000)  # Display credits for 5 seconds
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            sys.exit()

    def show_pause_menu(self):
        """Display the pause menu and wait for user to resume or quit."""
        paused = True
        while paused:
            self.pause_menu.draw()
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.pause_menu.resume_button.collidepoint(event.pos):
                        paused = False
                        return
                    elif self.pause_menu.quit_button.collidepoint(event.pos):
                        self.show_main_menu()
                        return
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        paused = False

    def show_game_over_screen(self):
        """Display the game over screen and wait for user to restart or quit."""
        self.game_over_screen.draw()
        pg.display.flip()
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.game_over_screen.restart_button.collidepoint(event.pos):
                        self.__init__()  # Reinitialize the game
                        self.run_game()  # Restart the game
                        return
                    elif self.game_over_screen.quit_button.collidepoint(event.pos):
                        self.show_main_menu()
                        return

    def show_level_complete_screen(self):
        """Display the level complete screen and wait for user to continue or quit."""
        self._calculate_final_score()  # Calculate stars based on carrots collected
        self.level_complete_screen.draw()
        pg.display.flip()
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.level_complete_screen.restart_button.collidepoint(event.pos):
                        self.__init__()
                        self.run_game()  # Restart the game
                        return
                    elif self.level_complete_screen.quit_button.collidepoint(event.pos):
                        self.show_main_menu()
                        return

    def _check_collision_events(self):
        """Check for collisions with obstacles."""
        self.bunny.speed = self.bunny.normal_speed  # Reset speed to normal
        bunny_rect = self.bunny.rect
        on_rock = False
        in_any_puddle = False
        bunny_world_x = self.bunny.x + self.world_offset
        bunny_world_y = self.bunny.y

        for obs in self.obstacles.obstacles:
            if obs['type'] == 'rock':
                # Check if bunny is landing on top of the rock
                if bunny_rect.colliderect(obs['rect']):
                    # Check if bunny is falling onto the rock (feet above rock, moving down)
                    if self.bunny.y_velocity >= 0 and bunny_rect.bottom - obs['rect'].top < 20:
                        self.bunny.y = obs['rect'].top - bunny_rect.height
                        self.bunny.y_velocity = 0
                        self.bunny.on_ground = True
                        on_rock = True
                    elif bunny_rect.right > obs['rect'].left and bunny_rect.left < obs['rect'].left:
                    # Colliding from left
                        self.bunny.x = obs['rect'].left - bunny_rect.width
                    elif bunny_rect.left < obs['rect'].right and bunny_rect.right > obs['rect'].right:
                    # Colliding from right
                        self.bunny.x = obs['rect'].right

            elif obs['type'] == 'puddle':
                puddle_rect = obs['rect'].copy()
                puddle_rect.x = obs['x']
                puddle_rect.y = obs['y']

                bunny_run_rect = bunny_rect.copy()
                bunny_run_rect.x = bunny_world_x
                bunny_run_rect.y = bunny_world_y                

                
                if bunny_run_rect.colliderect(puddle_rect):
                    #print(f"Bunny ({bunny_world_x}, {bunny_world_y}) in puddle at {puddle_rect.x}, {puddle_rect.y}")
                    in_any_puddle = True
                    if in_any_puddle:
                        self.bunny.speed = self.bunny.slower_speed
                    else:
                        self.bunny.speed = self.bunny.normal_speed

        for carrot in self.carrots.collectibles:
            if carrot['type'] == 'carrot':
                # Check if bunny collides with carrot
                if bunny_rect.colliderect(carrot['rect']):
                    self.carrots.collectibles.remove(carrot)
                    self.stats.carrots_collected += 1
                    self.stats.score += 10

        # If not on any rock, set ground to normal ground level
        if not on_rock and self.bunny.y + bunny_rect.height >= self.bunny.ground_y:
            self.bunny.y = self.bunny.ground_y - bunny_rect.height
            self.bunny.y_velocity = 0
            self.bunny.on_ground = True

        for snake in self.snakes.snakes[:]:
            snake_world_rect = snake['rect'].copy()
            snake_world_rect.x = snake['x']
            snake_world_rect.y = snake['y']

            # Always use is_attacking for attack logic
            if self.bunny.is_attacking:
                attack_rect = bunny_rect.copy()
                attack_rect.x = bunny_world_x
                attack_rect.y = bunny_world_y
                if self.bunny.facing_direction == 'right':
                    attack_rect.width += 10
                else:
                    attack_rect.x -= 30
                    attack_rect.width += 10
            else:
                attack_rect = bunny_rect.copy()
                attack_rect.x = bunny_world_x
                attack_rect.y = bunny_world_y

            if attack_rect.colliderect(snake_world_rect.copy()):
                if self.bunny.is_attacking:
                    pg.mixer.Sound('audio/steam hisses - Marker #1.wav').play()
                    self.snakes.snakes.remove(snake)
                    self.stats.score += 20
                elif not self.bunny.invincible:
                    self.bunny.health -= 1
                    self.stats.score -= 10
                    self.bunny.invincible = True
                    self.bunny.invincibility_timer = 1
                    self.bunny.invincibility_duration = 120  # 2 seconds at 60 FPS
                    if self.bunny.health <= 0:
                        self.bunny.bunny_lives -= 1
                        self.stats.score -= 50
                        if self.bunny.bunny_lives <= 0:
                            self.show_game_over_screen()
                        else:
                            self._reset_level()
                            self.bunny.health = 3
                            return
                        
    def _check_boss_collision(self):
        """Check for collisions with the wolf boss."""
        bunny_rect = self.bunny.rect.copy()
        bunny_rect.x += self.world_offset
        bunny_rect.y = self.bunny.y

        if self.wolf_boss.rect.colliderect(bunny_rect):
            if self.bunny.is_attacking and not self.wolf_boss.invincible:
                self.wolf_boss.invincible = True
                self.wolf_boss.invincibility_timer = 1
                self.wolf_boss.invincibility_duration = 120
                self.wolf_boss.health -= 2
                self.stats.score += 50
                if self.wolf_boss.health <= 0:
                    self.wolf_boss.health = 0
                    self.wolf_boss.is_attacking = False
                    self.wolf_boss.invincible = True
                    self.wolf_boss.kill()
                    self.wolf_boss.remove()
                    self.stats.score += 200
            elif self.wolf_boss.is_attacking and not self.bunny.invincible:
                self.bunny.health -= 1
                self.stats.score -= 30
                self.bunny.invincible = True
                self.bunny.invincibility_timer = 1
                self.bunny.invincibility_duration = 120  # 2 seconds at 60 FPS
                if self.bunny.health <= 0:
                    self.bunny.bunny_lives -= 1
                    self.stats.score -= 50
                    if self.bunny.bunny_lives <= 0:
                        self.show_game_over_screen()
                    else:
                        self._reset_level()
                        self.bunny.health = 3
                    return
                        
    def _display_stats(self):
        """Display the stats on the screen."""
        self.stats.draw()
        pg.display.flip()

    def _calculate_final_score(self):
        """Calculate the final score based on carrots collected and time taken."""
        if self.stats.carrots_collected == 20:
            self.level_complete_screen.stars_earned = 3
        elif self.stats.carrots_collected >= 13:
            self.level_complete_screen.stars_earned = 2
        elif self.stats.carrots_collected >= 6:
            self.level_complete_screen.stars_earned = 1
        elapsed_time = pg.time.get_ticks() // 1000
        time_bonus = max(0, 60 - elapsed_time) * 5
        final_score = self.stats.score + time_bonus
        self.stats.score = final_score
        return final_score

    def _reset_level(self):
        """Reset the bunny and obstacles to the starting position."""
        self.bunny.x = 100
        self.bunny.y = self.bunny.ground_y - self.bunny.rect.height
        self.bunny.y_velocity = 0
        self.bunny.on_ground = True
        self.bunny.moving_right = False
        self.bunny.moving_left = False
        self.bunny.jumping = False
        self.bunny.attacking = False
        self.world_offset = 0

    def _update_screen(self):
        """Update images on the screen and flip to the new screen."""
        self.settings.blitbg(self.screen)
        self.obstacles.blit_obstacles()
        self.carrots.blit_carrots()
        self.snakes.blit_snakes(world_offset=self.world_offset)
        self.wolf_boss.draw(self.screen, world_offset=self.world_offset)
        self.bunny.blitbunny(self.screen)
        self._display_stats()

        pg.display.flip()

if __name__ == '__main__':
    ca = Cheerios_Adventure()
    ca.run_game()