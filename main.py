import pygame, sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, POINTS_FOR_EXTRA_LIFE, RESPAWN_INVULN_SECONDS, RESPAWN_COUNTDOWN_SECONDS
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot


def main():
    pygame.init()

    score = 0
    lives = 3
    next_extra_life = POINTS_FOR_EXTRA_LIFE
    respawn_timer = 0
    countdown_timer = 0

    font = pygame.font.SysFont(None, 36)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)
    Player.containers = (updatable, drawable)

    asteroid_field = AsteroidField()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    while True:
        log_state()

        dt = clock.tick(60) / 1000

        if respawn_timer > 0:
            respawn_timer -= dt

        if countdown_timer <= 0:
            updatable.update(dt)
        else:   
            countdown_timer -= dt


        for asteroid in asteroids:
            if respawn_timer <= 0 and asteroid.collides_with(player):
                log_event("player_hit")
                lives -= 1
                next_extra_life = score + POINTS_FOR_EXTRA_LIFE

                # Reset all asteroids immediately
                for a in list(asteroids):
                    a.kill()

                if lives <= 0:
                    print("Game over!")
                    sys.exit()

                # Reset player
                player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.velocity = pygame.Vector2(0, 0)

                # Start respawn countdown
                respawn_timer = RESPAWN_INVULN_SECONDS
                countdown_timer = RESPAWN_COUNTDOWN_SECONDS
                break


        for asteroid in asteroids:
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    points = asteroid.split() or 0
                    shot.kill()
                    score += points

                    while score >= next_extra_life:
                        lives += 1
                        next_extra_life += POINTS_FOR_EXTRA_LIFE

        screen.fill("black")

        
        if countdown_timer > 0:
            countdown_number = int(countdown_timer) + 1

            countdown_text = font.render(
                str(countdown_number), True, (255, 255, 255)
            )

            text_rect = countdown_text.get_rect(
                center=(
                    int(player.position.x),
                    int(player.position.y + player.radius + 40),
                )
            )

            screen.blit(countdown_text, text_rect)


        points_left = max(next_extra_life - score, 0)
        score_y = 10
        line_spacing = 28

        screen.blit(
            font.render(f"Score: {score}", True, (255, 255, 255)),
            (10, score_y),
        )

        screen.blit(
            font.render(
                f"Points Until Extra Life: {points_left}",
                True,
                (255, 255, 255),
            ),
            (10, score_y + line_spacing),
        )

        triangle_size = 10
        text_left_x = 10
        y = SCREEN_HEIGHT - 45

        start_x = text_left_x + triangle_size
        
        for i in range(lives):
            x = start_x + i * 25
            pygame.draw.polygon(
                screen,
                (255, 255, 255),
                [
                    (x, y - triangle_size),
                    (x - triangle_size, y + triangle_size),
                    (x + triangle_size, y + triangle_size),
                ],
            )

        for obj in drawable:
            obj.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        pygame.display.flip()


if __name__ == "__main__":
    main()
