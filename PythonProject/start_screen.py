import pygame
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def show_start_screen(screen, WIDTH, HEIGHT):
    font_big = pygame.font.SysFont(None, 60)
    font_small = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    selected_players = 0
    use_ai = False
    stage = 0

    while True:
        screen.fill(WHITE)

        if stage == 0:
            welcome_text = font_big.render("Καλωσήρθες στο παιχνίδι!", True, BLACK)
            screen.blit(welcome_text, welcome_text.get_rect(center=(WIDTH//2, 100)))

            prompt_text = font_small.render("Επίλεξε αριθμό παικτών (1–4):", True, BLACK)
            screen.blit(prompt_text, prompt_text.get_rect(center=(WIDTH//2, 180)))

            buttons = []
            for i in range(1, 5):
                rect = pygame.Rect(WIDTH//2 - 150 + (i-1)*80, 230, 60, 40)
                pygame.draw.rect(screen, (180, 220, 180), rect)
                btn_text = font_small.render(str(i), True, BLACK)
                screen.blit(btn_text, btn_text.get_rect(center=rect.center))
                buttons.append((rect, i))

        elif stage == 1:
            question_text = font_small.render("Θες να προσθέσεις AI παίκτες; (Ναι/Όχι)", True, BLACK)
            screen.blit(question_text, question_text.get_rect(center=(WIDTH//2, 180)))

            yes_btn = pygame.Rect(WIDTH//2 - 100, 230, 80, 40)
            no_btn = pygame.Rect(WIDTH//2 + 20, 230, 80, 40)

            pygame.draw.rect(screen, (180, 220, 255), yes_btn)
            pygame.draw.rect(screen, (255, 200, 200), no_btn)

            screen.blit(font_small.render("Ναι", True, BLACK), font_small.render("Ναι", True, BLACK).get_rect(center=yes_btn.center))
            screen.blit(font_small.render("Όχι", True, BLACK), font_small.render("Όχι", True, BLACK).get_rect(center=no_btn.center))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if stage == 0:
                    for rect, value in buttons:
                        if rect.collidepoint(pos):
                            selected_players = value
                            stage = 1
                elif stage == 1:
                    if yes_btn.collidepoint(pos):
                        return selected_players, True
                    elif no_btn.collidepoint(pos):
                        return selected_players, False