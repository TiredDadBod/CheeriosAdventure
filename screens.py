# This Section will house the:
# Main Menu (Button to show Credit Screen and Start Game),
# Level Complete (1 Star = 33%, 2 Stars = 66%, 3 Stars = 100%),
# Pause Menu (Button to Resume Game or Quit to Main Menu),
# and Game Over Screens (Button to Restart Game or Quit to Main Menu)
import pygame as pg
from settings import Settings
from bunny import Bunny
from pathlib import Path


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.settings = Settings()
        self.font = pg.font.Font('fonts/Peas & Carrots.ttf', 80)
        self.title = self.font.render("Cheerio's Adventure", True, (0, 0, 0))
        self.start_button = pg.Rect(700, 350, 200, 50)
        self.start_button_text = self.font.render("Start Game", True, (255, 255, 255))
        self.credits_button = pg.Rect(700, 450, 200, 50)
        self.credits_button_text = self.font.render("Credits", True, (255, 255, 255))

    def draw(self):
        self.settings.blitbg(self.screen)
        self.screen.blit(self.title, (525, 200))
        self.screen.blit(self.start_button_text, (650, 350))
        self.screen.blit(self.credits_button_text, (700, 450))

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.settings = Settings()
        self.font = pg.font.Font('fonts/Peas & Carrots.ttf', 80)
        self.pause_text = self.font.render("Game Paused", True, (0, 0, 255))
        self.resume_button = pg.Rect(700, 350, 200, 50)
        self.resume_button_text = self.font.render("Resume", True, (255, 255, 255))
        self.quit_button = pg.Rect(700, 450, 200, 50)
        self.quit_button_text = self.font.render("Quit to Main Menu", True, (255, 255, 255))

    def draw(self):
        self.settings.blitbg(self.screen)
        self.screen.blit(self.pause_text, (625, 200))
        self.screen.blit(self.resume_button_text, (700, 350))
        self.screen.blit(self.quit_button_text, (550, 450))

class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.settings = Settings()
        self.font = pg.font.Font('fonts/Peas & Carrots.ttf', 80)
        self.game_over_text = self.font.render("Game Over", True, (255, 0, 0))
        self.restart_button = pg.Rect(700, 350, 200, 50)
        self.restart_button_text = self.font.render("Restart", True, (255, 255, 255))
        self.quit_button = pg.Rect(700, 450, 200, 50)
        self.quit_button_text = self.font.render("Quit to Main Menu", True, (255, 255, 255))

    def draw(self):
        self.settings.blitbg(self.screen)
        self.screen.blit(self.game_over_text, (650, 200))
        self.screen.blit(self.restart_button_text, (700, 350))
        self.screen.blit(self.quit_button_text, (550, 450))

class LevelCompleteScreen:
    def __init__(self, screen, stars_earned, stats):
        self.screen = screen
        self.settings = Settings()
        self.stats = stats
        self.font = pg.font.Font('fonts/Peas & Carrots.ttf', 80)
        self.level_complete_text = self.font.render("Level Complete!", True, (0, 255, 0))
        self.star = pg.image.load("images/sss.png")
        self.stars_earned = stars_earned
        self.restart_button = pg.Rect(700, 550, 200, 50)
        self.restart_button_text = self.font.render("Restart Level", True, (255, 255, 255))
        self.quit_button = pg.Rect(700, 650, 200, 50)
        self.quit_button_text = self.font.render("Quit to Main Menu", True, (255, 255, 255))

    def draw(self):
        screen_rect = self.screen.get_rect()
        self.settings.blitbg(self.screen)
        self.screen.blit(self.level_complete_text, (600, 50))
        for i in range(self.stars_earned):
            star_x = screen_rect.centerx - (self.star.get_width() * self.stars_earned) // 2 + i * (self.star.get_width() + 10)
            star_y = 200
            self.screen.blit(self.star, (star_x, star_y))
        big_font = pg.font.Font('fonts/Peas & Carrots.ttf', 65)
        big_score_text = big_font.render(f"Score: {self.stats.score}", True, (0, 0, 0))
        self.screen.blit(big_score_text, (screen_rect.centerx - big_score_text.get_width() // 2, 400))
        self.screen.blit(self.restart_button_text, (625, 550))
        self.screen.blit(self.quit_button_text, (550, 650))

class Stats:
    def __init__(self, screen, bunny, carrots):
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.screen_width = self.screen_rect.width
        self.screen_height = self.screen_rect.height
        self.bunny = bunny
        self.carrots = carrots
        self.score = 0
        self.settings = Settings()
        self.font = pg.font.Font('fonts/Peas & Carrots.ttf', 40)
        self.health_rect = pg.Rect(self.screen_width - 150, self.screen_height - 50, 200, 50)
        self.health_icon = pg.image.load("images/heart_animation_16x16_trans.png")
        self.health_icon = pg.transform.scale_by(self.health_icon, 2)
        self.health_icon_rect = self.health_icon.get_rect()
        self.health_text = self.font.render(f"Health:", True, (255, 255, 255), (0, 0, 0, 0.2))
        self.lives_rect = pg.Rect(50, self.screen_height - 50, 200, 50)
        self.lives_icon = pg.transform.scale_by(self.bunny.original_sprites['facing_right'], 2)
        self.lives_icon_rect = self.lives_icon.get_rect()
        self.lives_text = self.font.render(f"Lives:", True, (255, 255, 255), (0, 0, 0, 0.2))
        self.score_rect = pg.Rect(self.screen_width - 150, 50, 200, 50)
        self.score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.carrot_rect = pg.Rect(50, 50, 200, 20)
        self.carrots_collected = 0
        self.carrot_text = self.font.render(f"Carrots: {self.carrots_collected} / {len(self.carrots.collectibles)}", True, (0, 0, 0))
        self.timer = pg.time.Clock()
        self.timer_text = self.font.render(f"Time: {self.timer.get_time() // 1000}", True, (0, 0, 0))
        self.timer_rect = pg.Rect(self.screen_width // 2, 50, 200, 20)

    def draw(self):
        screen_rect = self.screen.get_rect()

        self.carrot_text = self.font.render(f"Carrots: {self.carrots_collected} / {len(self.carrots.collectibles)}", True, (0, 0, 0))
        elapsed_seconds = pg.time.get_ticks() // 1000
        self.timer_text = self.font.render(f"Time: {elapsed_seconds}", True, (0, 0, 0))
        self.score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))

        # Draw the timer in the top center
        self.screen.blit(self.timer_text, (screen_rect.centerx - self.timer_rect.width // 2, screen_rect.top + 50))

        # Draw health in bottom right corner
        self.screen.blit(self.health_text, (screen_rect.right - 275, screen_rect.bottom - 50))
        for i in range(self.bunny.health):
            icon_x = screen_rect.right - 150 + i * (self.health_icon_rect.width + 5)
            icon_y = screen_rect.bottom - 45
            self.screen.blit(self.health_icon, (icon_x, icon_y))
        
        # Draw lives in bottom left corner
        self.screen.blit(self.lives_text, (screen_rect.left + 50, screen_rect.bottom - 50))
        for i in range(self.bunny.bunny_lives):
            self.screen.blit(self.lives_icon, (screen_rect.left + 150 + i * (self.lives_icon_rect.width + 5), screen_rect.bottom - 70))

        # Draw score in top right corner
        score_x = screen_rect.right - self.score_text.get_width() - 50
        score_y = screen_rect.top + 50
        self.screen.blit(self.score_text, (score_x, score_y))

        # Draw carrots collected in top left corner
        self.screen.blit(self.carrot_text, (screen_rect.left + 50, screen_rect.top + 50)) 