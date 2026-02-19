import pygame, sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, POINTS_FOR_EXTRA_LIFE, RESPAWN_INVULN_SECONDS, RESPAWN_COUNTDOWN_SECONDS
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

def draw_button(screen, rect, text, font, color=(255,255,255), bg_color=(0,0,0)):
    pygame.draw.rect(screen, bg_color, rect)
    pygame.draw.rect(screen, color, rect, 2)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def main():
    pygame.init()

    # --- Game states ---
    STATE_START_SCREEN = "start_screen"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"
    game_state = STATE_START_SCREEN

    # --- Game variables ---
    score = 0
    lives = 3
    next_extra_life = POINTS_FOR_EXTRA_LIFE
    respawn_timer = 0
    countdown_timer = 0

    font = pygame.font.SysFont(None, 36)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0

    # --- Sprite groups ---
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

    # --- Main loop ---
    while True:
        dt = clock.tick(60) / 1000
        screen.fill("black")
        log_state()

        mouse_pos = pygame.mouse.get_pos()

        # --- Buttons ---
        if game_state == STATE_START_SCREEN:
            start_button = pygame.Rect(SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 25, 160, 50)
            if start_button.collidepoint(mouse_pos):
                draw_button(screen, start_button, "START", font, color=(0,0,0), bg_color=(255,255,255))
            else:
                draw_button(screen, start_button, "START", font)

        elif game_state == STATE_GAME_OVER:
            restart_button = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 25, 300, 50)
            if restart_button.collidepoint(mouse_pos):
                draw_button(screen, restart_button, "GAME OVER", font, color=(0,0,0), bg_color=(255,255,255))
            else:
                draw_button(screen, restart_button, "GAME OVER", font)

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if game_state == STATE_START_SCREEN and event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_state = STATE_PLAYING
                    # Reset game variables
                    score = 0
                    lives = 3
                    next_extra_life = POINTS_FOR_EXTRA_LIFE
                    respawn_timer = 0
                    countdown_timer = 0
                    player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    player.velocity = pygame.Vector2(0, 0)
                    for a in list(asteroids):
                        a.kill()

            elif game_state == STATE_GAME_OVER and event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    game_state = STATE_START_SCREEN

        # --- Gameplay ---
        if game_state == STATE_PLAYING:
            if respawn_timer > 0:
                respawn_timer -= dt

            # Countdown freeze
            if countdown_timer > 0:
                countdown_number = int(countdown_timer) + 1
                countdown_text = font.render(str(countdown_number), True, (255,255,255))
                text_rect = countdown_text.get_rect(
                    center=(int(player.position.x), int(player.position.y + player.radius + 40))
                )
                screen.blit(countdown_text, text_rect)
                countdown_timer -= dt
            else:
                updatable.update(dt)

            # --- Draw UI ---
            score_y = 10
            line_spacing = 28
            score_text = font.render(f"Score: {score}", True, (255,255,255))
            screen.blit(score_text, (10, score_y))

            points_left = max(next_extra_life - score, 0)
            extra_text = font.render(f"Points Until Extra Life: {points_left}", True, (255,255,255))
            screen.blit(extra_text, (10, score_y + line_spacing))

            # Lives triangles aligned with score
            triangle_size = 10
            start_x = 10 + triangle_size
            y = SCREEN_HEIGHT - 45
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

            # --- Collisions ---
            for asteroid in asteroids:
                if respawn_timer <= 0 and asteroid.collides_with(player):
                    log_event("player_hit")
                    lives -= 1
                    next_extra_life = score + POINTS_FOR_EXTRA_LIFE
                    # Reset asteroids
                    for a in list(asteroids):
                        a.kill()
                    if lives <= 0:
                        game_state = STATE_GAME_OVER
                    else:
                        player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        player.velocity = pygame.Vector2(0, 0)
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

            for drawable_obj in drawable:
                drawable_obj.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()
