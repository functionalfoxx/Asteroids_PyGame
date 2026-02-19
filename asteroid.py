import pygame, random
from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from logger import log_event

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "white",
            (int(self.position.x), int(self.position.y)),
            self.radius,
            LINE_WIDTH
        )

    def update(self, dt):
        self.position += self.velocity * dt

    ASTEROID_SCORE = {
        'small': 10,
        'medium': 20,
        'large': 30
    }

    def split(self):
        if self.radius <= ASTEROID_MIN_RADIUS:
            points = self.ASTEROID_SCORE['small']
            self.kill()
            return points  # small asteroids still give points

        self.kill()
        log_event("asteroid_split")
        angle = random.uniform(20, 50)

        vel1 = self.velocity.rotate(angle)
        vel2 = self.velocity.rotate(-angle)

        new_radius = self.radius - ASTEROID_MIN_RADIUS

        a1 = Asteroid(self.position.x, self.position.y, new_radius)
        a1.velocity = vel1 * 1.2

        a2 = Asteroid(self.position.x, self.position.y, new_radius)
        a2.velocity = vel2 * 1.2

        if self.radius >= ASTEROID_MIN_RADIUS * 3:
            points = self.ASTEROID_SCORE['large']
        elif self.radius >= ASTEROID_MIN_RADIUS * 2:
            points = self.ASTEROID_SCORE['medium']
        else:
            points = self.ASTEROID_SCORE['small']

        return points
