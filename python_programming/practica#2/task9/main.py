import pygame
import sys
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def run_game():
    try:
        pygame.init()
        size = width, height = 800, 600
        speed = [2, 2]
        black = 0, 0, 0
        screen = pygame.display.set_mode(size)
        ball = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(ball, (255, 0, 0), (25, 25), 25)
        ballrect = ball.get_rect()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            ballrect = ballrect.move(speed)
            if ballrect.left < 0 or ballrect.right > width:
                speed[0] = -speed[0]
            if ballrect.top < 0 or ballrect.bottom > height:
                speed[1] = -speed[1]

            screen.fill(black)
            screen.blit(ball, ballrect)
            pygame.display.flip()
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    run_game()