import pygame
import random
from asteroid import Asteroid
from shot import Shot
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from titleart import TITLE_ART
from fauxplayer import FauxPlayer

class StartScreen:
    def __init__(self):
        self.faux_player = FauxPlayer(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.behavior_timer = 0
        self.behavior_interval = 2.0
        self.current_behavior = "roam"
        self.velocity = pygame.Vector2(0, 0)

        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        for _ in range(random.randint(3,5)):
            pos = pygame.Vector2(random.uniform(0, SCREEN_WIDTH), random.uniform(0, SCREEN_HEIGHT))
            radius = random.randint(15, 35)
            asteroid = Asteroid(pos.x, pos.y, radius)
            asteroid.velocity = pygame.Vector2(random.uniform(-60,60), random.uniform(-60,60))
            asteroid.containers = (self.asteroids,)
            self.asteroids.add(asteroid)

        self.title_surface = self._render_title(TITLE_ART)
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    def _render_title(self, ascii_art):
        lines = ascii_art.splitlines()
        font = pygame.font.SysFont("Courier", 16, bold=True)
        widths = [font.size(line)[0] for line in lines]
        max_width = max(widths)
        surf = pygame.Surface((max_width, len(lines) * font.get_linesize()), pygame.SRCALPHA)
        y = 0
        for line in lines:
            text_surf = font.render(line, True, (255,255,255))
            surf.blit(text_surf, (0, y))
            y += font.get_linesize()
        return surf

    def update(self, dt, mouse_pos):
        self.behavior_timer -= dt
        if self.behavior_timer <= 0:
            self._choose_behavior(mouse_pos)
            self.behavior_timer = self.behavior_interval

        self._update_faux_player(dt, mouse_pos)
        self._update_asteroids(dt)
        self._update_shots(dt)

    def _choose_behavior(self, mouse_pos):
        choice = random.choice(["roam", "toward_mouse", "shoot_asteroids"])
        self.current_behavior = choice
        if choice == "roam":
            angle = random.uniform(0, 360)
            speed = random.uniform(100, 200)
            self.velocity = pygame.Vector2(0, 1).rotate(angle) * speed
            self.faux_player.rotation = angle
        elif choice == "toward_mouse":
            direction = pygame.Vector2(mouse_pos) - self.faux_player.position
            if direction.length() > 0:
                self.velocity = direction.normalize() * random.uniform(150, 200)
                self.faux_player.rotation = direction.angle_to(pygame.Vector2(0,1))
        elif choice == "shoot_asteroids":
            self.velocity = pygame.Vector2(0,0)

    def _update_faux_player(self, dt, mouse_pos):
        if self.current_behavior in ["toward_mouse","shoot_asteroids"]:
            direction = pygame.Vector2(mouse_pos) - self.faux_player.position
            if direction.length() > 0:
                target_angle = direction.angle_to(pygame.Vector2(0,1))
                current_angle = self.faux_player.rotation
                angle_diff = (target_angle - current_angle + 180) % 360 - 180
                self.faux_player.rotation += max(-180*dt, min(180*dt, angle_diff))

        self.faux_player.position += self.velocity * dt

        if self.faux_player.position.x < -50:
            self.faux_player.position.x = SCREEN_WIDTH + 50
        if self.faux_player.position.x > SCREEN_WIDTH + 50:
            self.faux_player.position.x = -50
        if self.faux_player.position.y < -50:
            self.faux_player.position.y = SCREEN_HEIGHT + 50
        if self.faux_player.position.y > SCREEN_HEIGHT + 50:
            self.faux_player.position.y = -50

        if self.faux_player.shoot_timer > 0:
            self.faux_player.shoot_timer -= dt
        if self.current_behavior in ["toward_mouse","shoot_asteroids"] and self.faux_player.shoot_timer <= 0:
            if random.random() < 0.3:
                self._faux_shoot(mouse_pos)
            self.faux_player.shoot_timer = random.uniform(0.5, 1.0)

    def _faux_shoot(self, target):
        direction = pygame.Vector2(target) - self.faux_player.position
        if direction.length() > 0:
            direction_norm = direction.normalize()
            self.faux_player.rotation = direction.angle_to(pygame.Vector2(0,1))
            new_shot = Shot(self.faux_player.position.x, self.faux_player.position.y)
            new_shot.velocity = direction_norm * 300
            new_shot.containers = (self.shots,)
            self.shots.add(new_shot)

    def _update_shots(self, dt):
        for shot in list(self.shots):
            shot.update(dt)
            for asteroid in list(self.asteroids):
                if asteroid.collides_with(shot):
                    asteroid.split()
                    shot.kill()
            if (shot.position.x < -50 or shot.position.x > SCREEN_WIDTH + 50 or
                shot.position.y < -50 or shot.position.y > SCREEN_HEIGHT + 50):
                shot.kill()

    def _update_asteroids(self, dt):
        for asteroid in self.asteroids:
            asteroid.position += asteroid.velocity * dt
            if asteroid.position.x < -50:
                asteroid.position.x = SCREEN_WIDTH + 50
            if asteroid.position.x > SCREEN_WIDTH + 50:
                asteroid.position.x = -50
            if asteroid.position.y < -50:
                asteroid.position.y = SCREEN_HEIGHT + 50
            if asteroid.position.y > SCREEN_HEIGHT + 50:
                asteroid.position.y = -50

    def draw(self, screen):
        for asteroid in self.asteroids:
            asteroid.draw(screen)
        for shot in self.shots:
            shot.draw(screen)
        self.faux_player.draw(screen)
        screen.blit(self.title_surface, self.title_rect)
