import pygame

class FauxPlayer:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.radius = 15
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.shoot_timer = 0

    def draw(self, screen):
        tip = self.position + pygame.Vector2(0, -self.radius).rotate(-self.rotation)
        left = self.position + pygame.Vector2(-self.radius//2, self.radius).rotate(-self.rotation)
        right = self.position + pygame.Vector2(self.radius//2, self.radius).rotate(-self.rotation)
        pygame.draw.polygon(screen, (255, 255, 255), [tip, left, right])
