import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1200, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Butterfly Effect")

# Colors
BG_COLOR = (18, 22, 34)
PANEL_COLOR = (30, 36, 52)
CARD_COLOR = (36, 44, 64)
TEXT_COLOR = (240, 240, 240)
MUTED_TEXT = (180, 190, 210)
ACCENT_COLOR = (100, 180, 255)
BUTTON_COLOR = (70, 120, 200)
BUTTON_HOVER = (90, 140, 220)
GOOD_COLOR = (90, 200, 140)
WARNING_COLOR = (230, 180, 80)
DANGER_COLOR = (220, 90, 90)

# Fonts
title_font = pygame.font.SysFont("arial", 42, bold=True)
subtitle_font = pygame.font.SysFont("arial", 26, bold=True)
text_font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 16)
label_font = pygame.font.SysFont("arial", 22, bold=True)

clock = pygame.time.Clock()

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_END = "end"

game_state = STATE_MENU

# Turn settings
year = 1
max_years = 10
points_per_turn = 10

# Indicators
indicator_names = ["Environment", "Education", "Health", "Economy", "Stability"]
indicators = {
    "Environment": 50,
    "Education": 50,
    "Health": 50,
    "Economy": 50,
    "Stability": 50,
}

allocations = {
    "Environment": 0,
    "Education": 0,
    "Health": 0,
    "Economy": 0,
    "Stability": 0,
}

# Message
message = "Allocate your resource points for this year."

# End result
end_title = ""
end_description = ""

# Buttons
start_button = pygame.Rect(480, 560, 240, 60)
observe_button = pygame.Rect(880, 660, 220, 55)
next_year_button = pygame.Rect(880, 660, 220, 55)
restart_button = pygame.Rect(480, 620, 240, 60)

# Future cards
future_cards = []

# State flags
turn_collapsed = False
plus_minus_buttons = []


def draw_text(text, font, color, surface, x, y):
    """Draw text on the screen."""
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))


def draw_button(rect, text, mouse_pos, active=True):
    """Draw a button with hover effect."""
    if not active:
        color = (80, 85, 95)
        border = (110, 115, 125)
    else:
        color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        border = ACCENT_COLOR

    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, border, rect, 2, border_radius=10)

    text_surface = text_font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def get_remaining_points():
    """Return remaining resource points for this turn."""
    return points_per_turn - sum(allocations.values())


def clamp_stat(value):
    """Keep indicator values between 0 and 100."""
    return max(0, min(100, value))


def wrap_text(text, max_chars):
    """Split text into simple wrapped lines."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines


def generate_futures():
    """
    Generate three possible futures.
    This is the 'superposition' layer:
    multiple possible outcomes exist before observation.
    """
    env = allocations["Environment"]
    edu = allocations["Education"]
    health = allocations["Health"]
    eco = allocations["Economy"]
    stab = allocations["Stability"]

    # Future 1: Green Recovery
    green_weight = 25 + env * 4 + edu * 2 + health * 2 - eco
    green_effects = {
        "Environment": 8 + env,
        "Education": 3 + edu // 2,
        "Health": 4 + health // 2,
        "Economy": -2 + eco // 3,
        "Stability": 3 + stab // 2,
    }

    # Future 2: Economic Boom
    boom_weight = 25 + eco * 4 + stab * 2 + edu - env
    boom_effects = {
        "Environment": -4 + env // 3,
        "Education": 2 + edu // 2,
        "Health": 1 + health // 3,
        "Economy": 9 + eco,
        "Stability": 3 + stab // 2,
    }

    # Future 3: Social Strain
    strain_weight = 20 + (points_per_turn - health) * 2 + (points_per_turn - stab) * 2 + random.randint(0, 6)
    strain_effects = {
        "Environment": -3 + env // 3,
        "Education": -2 + edu // 3,
        "Health": -7 + health // 2,
        "Economy": -3 + eco // 2,
        "Stability": -8 + stab // 2,
    }

    futures = [
        {
            "title": "Green Recovery",
            "description": "Sustainable policies improve resilience and long-term balance.",
            "weight": max(1, green_weight),
            "effects": green_effects,
            "color": GOOD_COLOR,
        },
        {
            "title": "Economic Boom",
            "description": "Growth accelerates, but environmental pressure may increase.",
            "weight": max(1, boom_weight),
            "effects": boom_effects,
            "color": WARNING_COLOR,
        },
        {
            "title": "Social Strain",
            "description": "Weak support systems increase instability and public stress.",
            "weight": max(1, strain_weight),
            "effects": strain_effects,
            "color": DANGER_COLOR,
        },
    ]

    total_weight = sum(future["weight"] for future in futures)
    for future in futures:
        future["probability"] = round((future["weight"] / total_weight) * 100)

    return futures


def apply_future(selected_future):
    """
    Collapse one future into reality.
    This represents quantum measurement / collapse.
    """
    global message, turn_collapsed

    for stat_name, change in selected_future["effects"].items():
        indicators[stat_name] = clamp_stat(indicators[stat_name] + change)

    turn_collapsed = True
    message = f"Observed future: {selected_future['title']}"


def reset_allocations():
    """Reset resource allocation for the next turn."""
    for key in allocations:
        allocations[key] = 0


def next_turn():
    """Move to the next year."""
    global year, future_cards, turn_collapsed, message
    year += 1
    reset_allocations()
    future_cards = generate_futures()
    turn_collapsed = False
    message = "Allocate your resource points for this year."


def evaluate_world():
    """
    Evaluate final world state based on indicators.
    Returns a result title and description.
    """
    avg = sum(indicators.values()) / len(indicators)

    env = indicators["Environment"]
    stab = indicators["Stability"]
    eco = indicators["Economy"]

    if env < 30:
        return "Ecological Collapse", "Environmental systems have critically failed."
    if stab < 30:
        return "Unstable Society", "Social instability has led to fragmentation."
    if avg > 70:
        return "Sustainable Future", "Balanced development created a stable and thriving world."
    if eco > 75 and env < 50:
        return "Growth Without Balance", "Economic success came at environmental cost."

    return "Mixed Outcome", "The world developed unevenly with both progress and risks."

def reset_game():
    """Reset the entire game to the initial state."""
    global year, indicators, allocations, future_cards, turn_collapsed
    global message, game_state, end_title, end_description

    year = 1

    indicators = {
        "Environment": 50,
        "Education": 50,
        "Health": 50,
        "Economy": 50,
        "Stability": 50,
    }

    allocations = {
        "Environment": 0,
        "Education": 0,
        "Health": 0,
        "Economy": 0,
        "Stability": 0,
    }

    future_cards = generate_futures()
    turn_collapsed = False
    message = "Allocate your resource points for this year."
    end_title = ""
    end_description = ""
    game_state = STATE_MENU

def draw_progress_bar(x, y, width, height, value):
    """Draw a progress bar for indicators."""
    pygame.draw.rect(screen, (55, 60, 75), (x, y, width, height), border_radius=8)

    if value >= 70:
        fill_color = GOOD_COLOR
    elif value >= 40:
        fill_color = WARNING_COLOR
    else:
        fill_color = DANGER_COLOR

    fill_width = int((value / 100) * width)
    pygame.draw.rect(screen, fill_color, (x, y, fill_width, height), border_radius=8)
    pygame.draw.rect(screen, ACCENT_COLOR, (x, y, width, height), 2, border_radius=8)


def draw_menu(mouse_pos):
    """Draw main menu."""
    screen.fill(BG_COLOR)

    draw_text("Quantum Butterfly Effect", title_font, TEXT_COLOR, screen, 340, 130)
    draw_text("A quantum-inspired game about sustainable futures", subtitle_font, ACCENT_COLOR, screen, 285, 200)

    intro_lines = [
        "In this prototype, the player manages global development year by year.",
        "Each decision creates several possible futures.",
        "When the player observes the future, one outcome becomes reality.",
        "This represents the quantum ideas of superposition and collapse.",
    ]

    y_offset = 300
    for line in intro_lines:
        draw_text(line, text_font, TEXT_COLOR, screen, 290, y_offset)
        y_offset += 38

    draw_button(start_button, "Start Prototype", mouse_pos)


def draw_playing(mouse_pos):
    """Draw the main gameplay screen."""
    screen.fill(BG_COLOR)

    # Header
    draw_text("Quantum Butterfly Effect", title_font, TEXT_COLOR, screen, 30, 20)
    draw_text(f"Year {year} / {max_years}", subtitle_font, ACCENT_COLOR, screen, 30, 75)
    draw_text(f"Remaining Points: {get_remaining_points()}", label_font, TEXT_COLOR, screen, 950, 30)

    # Left panel
    pygame.draw.rect(screen, PANEL_COLOR, (30, 120, 470, 590), border_radius=16)
    draw_text("Global Indicators", subtitle_font, TEXT_COLOR, screen, 50, 140)

    base_y = 190
    plus_minus_buttons.clear()

    for index, name in enumerate(indicator_names):
        stat_y = base_y + index * 100

        draw_text(name, label_font, TEXT_COLOR, screen, 50, stat_y)
        draw_text(f"State: {indicators[name]}", text_font, MUTED_TEXT, screen, 50, stat_y + 30)
        draw_progress_bar(50, stat_y + 58, 250, 22, indicators[name])

        draw_text(f"Allocated: {allocations[name]}", text_font, TEXT_COLOR, screen, 320, stat_y + 12)

        minus_rect = pygame.Rect(320, stat_y + 45, 40, 35)
        plus_rect = pygame.Rect(370, stat_y + 45, 40, 35)

        plus_minus_buttons.append((name, "minus", minus_rect))
        plus_minus_buttons.append((name, "plus", plus_rect))

        draw_button(minus_rect, "-", mouse_pos, active=True)
        draw_button(plus_rect, "+", mouse_pos, active=True)

    # Right top panel
    pygame.draw.rect(screen, PANEL_COLOR, (530, 120, 640, 260), border_radius=16)
    draw_text("Possible Futures", subtitle_font, TEXT_COLOR, screen, 550, 140)
    draw_text("Before observation, these futures exist in superposition.", small_font, MUTED_TEXT, screen, 550, 175)

    card_width = 185
    card_height = 150
    start_x = 550
    card_y = 205

    for i, future in enumerate(future_cards):
        card_x = start_x + i * 205
        pygame.draw.rect(screen, CARD_COLOR, (card_x, card_y, card_width, card_height), border_radius=14)
        pygame.draw.rect(screen, future["color"], (card_x, card_y, card_width, card_height), 2, border_radius=14)

        draw_text(future["title"], label_font, future["color"], screen, card_x + 12, card_y + 12)
        draw_text(f"{future['probability']}%", subtitle_font, TEXT_COLOR, screen, card_x + 12, card_y + 48)

        description_lines = wrap_text(future["description"], 24)
        line_y = card_y + 90
        for line in description_lines[:3]:
            draw_text(line, small_font, MUTED_TEXT, screen, card_x + 12, line_y)
            line_y += 20

    # Right bottom panel
    pygame.draw.rect(screen, PANEL_COLOR, (530, 410, 640, 300), border_radius=16)
    draw_text("Turn Status", subtitle_font, TEXT_COLOR, screen, 550, 430)

    status_lines = wrap_text(message, 52)
    msg_y = 475
    for line in status_lines[:4]:
        draw_text(line, text_font, TEXT_COLOR, screen, 550, msg_y)
        msg_y += 30

    if not turn_collapsed:
        observe_active = get_remaining_points() == 0
        draw_button(observe_button, "Observe Future", mouse_pos, active=observe_active)
    else:
        draw_button(next_year_button, "Next Year", mouse_pos, active=True)


def draw_end_screen(mouse_pos):
    """Draw final result screen."""
    screen.fill(BG_COLOR)

    draw_text("Final Outcome", title_font, TEXT_COLOR, screen, 420, 100)
    draw_text(end_title, subtitle_font, ACCENT_COLOR, screen, 420, 170)

    lines = wrap_text(end_description, 60)
    y = 230
    for line in lines:
        draw_text(line, text_font, TEXT_COLOR, screen, 280, y)
        y += 30

    draw_text("Final Indicators", subtitle_font, TEXT_COLOR, screen, 420, 330)

    y = 390
    for name in indicator_names:
        draw_text(f"{name}: {indicators[name]}", text_font, TEXT_COLOR, screen, 460, y)
        y += 40

    draw_button(restart_button, "Restart Game", mouse_pos, active=True)   

future_cards = generate_futures()

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    if game_state == STATE_MENU:
        draw_menu(mouse_pos)
    elif game_state == STATE_PLAYING:
        draw_playing(mouse_pos)
    elif game_state == STATE_END:
        if restart_button.collidepoint(event.pos):
            reset_game()
        draw_end_screen(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == STATE_MENU:
                if start_button.collidepoint(event.pos):
                    game_state = STATE_PLAYING
                    reset_allocations()
                    future_cards = generate_futures()
                    message = "Allocate all 10 resource points, then observe the future."

            elif game_state == STATE_PLAYING:
                # Allocation buttons
                for stat_name, action, rect in plus_minus_buttons:
                    if rect.collidepoint(event.pos):
                        if action == "plus" and get_remaining_points() > 0:
                            allocations[stat_name] += 1
                            future_cards = generate_futures()
                        elif action == "minus" and allocations[stat_name] > 0:
                            allocations[stat_name] -= 1
                            future_cards = generate_futures()

                # Observe future
                if not turn_collapsed and observe_button.collidepoint(event.pos):
                    if get_remaining_points() == 0:
                        selected_future = random.choices(
                            future_cards,
                            weights=[future["weight"] for future in future_cards],
                            k=1
                        )[0]
                        apply_future(selected_future)

                # Next year
                if turn_collapsed and next_year_button.collidepoint(event.pos):
                    if year < max_years:
                        next_turn()
                    else:
                        end_title, end_description = evaluate_world()
                        game_state = STATE_END

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()