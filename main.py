import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Butterfly Effect")

# Colors
BG_COLOR = (18, 22, 34)
PANEL_COLOR = (30, 36, 52)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (100, 180, 255)
BUTTON_COLOR = (70, 120, 200)
BUTTON_HOVER = (90, 140, 220)

# Fonts
title_font = pygame.font.SysFont("arial", 38, bold=True)
subtitle_font = pygame.font.SysFont("arial", 24, bold=True)
text_font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 16)

clock = pygame.time.Clock()

# Game state
year = 1
max_years = 10
running = True


def draw_text(text, font, color, surface, x, y):
    """Draw text on the screen."""
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))


def draw_button(rect, text, mouse_pos):
    """Draw a button with hover effect."""
    color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, ACCENT_COLOR, rect, 2, border_radius=10)

    text_surface = text_font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


start_button = pygame.Rect(430, 500, 240, 60)

while running:
    mouse_pos = pygame.mouse.get_pos()
    screen.fill(BG_COLOR)

    # Title
    draw_text("Quantum Butterfly Effect", title_font, TEXT_COLOR, screen, 300, 120)
    draw_text("A quantum-inspired game about sustainable futures", subtitle_font, ACCENT_COLOR, screen, 240, 180)

    # Intro text
    intro_lines = [
        "In this prototype, the player manages global development year by year.",
        "Each decision creates several possible futures.",
        "When the player observes the future, one outcome becomes reality.",
        "This represents the quantum ideas of superposition and collapse."
    ]

    y_offset = 270
    for line in intro_lines:
        draw_text(line, text_font, TEXT_COLOR, screen, 220, y_offset)
        y_offset += 35

    draw_button(start_button, "Start Prototype", mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                print("Prototype started!")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()