import pygame
import random
import sys
import math
import cmath

pygame.init()

WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Butterfly Effect FINAL V6")
clock = pygame.time.Clock()

# ------------------------------------------------------------
# Colors
# ------------------------------------------------------------
BG = (8, 12, 24)
PANEL = (22, 28, 46)
PANEL_2 = (27, 34, 58)
CARD = (30, 36, 60)
WHITE = (240, 245, 255)
GRAY = (170, 185, 210)
DARK_GRAY = (95, 105, 130)
CYAN = (0, 220, 255)
BLUE = (80, 130, 255)
GREEN = (70, 220, 140)
YELLOW = (255, 205, 80)
RED = (255, 95, 95)
PURPLE = (170, 110, 255)
ORANGE = (255, 150, 70)

# ------------------------------------------------------------
# Fonts - smaller than V5 to avoid overlapping
# ------------------------------------------------------------
TITLE = pygame.font.SysFont("arial", 34, True)
H1 = pygame.font.SysFont("arial", 26, True)
H2 = pygame.font.SysFont("arial", 20, True)
TEXT = pygame.font.SysFont("arial", 16)
SMALL = pygame.font.SysFont("arial", 14)
TINY = pygame.font.SysFont("arial", 12)

# ------------------------------------------------------------
# States
# ------------------------------------------------------------
MENU = "menu"
COUNTRY = "country"
PLAY = "play"
EVENT = "event"
TECH = "tech"
HELP = "help"
END = "end"

state = MENU
previous_state = PLAY

# ------------------------------------------------------------
# Core game data
# ------------------------------------------------------------
country = ""
year = 1
MAX_YEAR = 10
POINTS = 10

stats = {k: 50 for k in ["Environment", "Education", "Health", "Economy", "Stability"]}
alloc = {k: 0 for k in stats}
approval = 60

collapsed = False
rewind_used = False
history = None
future_cards = []

news = ["World initialized."]
timeline = []
message = "Allocate all 10 points."
last_event = ""
event_title = ""
event_desc = ""
event_choices = []

end_title = ""
end_text = ""
achievements = []
delayed_effects = []

last_quantum_status = "Coherent"
last_interference = "Neutral"
advisor_text = "Advisor: balance all systems to keep the future coherent."

# New player action data
action_points = 0
scan_used_this_year = False
campaign_used_this_year = False
resonance_charge = False

# Technology flags
tech_green_fusion = False
tech_ai_governance = False
tech_quantum_sensors = False
tech_social_shield = False

# ------------------------------------------------------------
# Rects / Buttons
# ------------------------------------------------------------
start_btn = pygame.Rect(500, 705, 280, 50)
restart_btn = pygame.Rect(930, 710, 220, 46)
observe_btn = pygame.Rect(1090, 710, 150, 48)
next_btn = pygame.Rect(1090, 710, 150, 48)
rewind_btn = pygame.Rect(920, 710, 150, 48)
help_btn = pygame.Rect(1040, 20, 200, 38)
back_btn = pygame.Rect(500, 700, 280, 52)

country_btns = [pygame.Rect(115 + i * 290, 300, 250, 90) for i in range(4)]
choice_rects = [
    pygame.Rect(390, 500, 500, 50),
    pygame.Rect(390, 570, 500, 50),
    pygame.Rect(390, 640, 500, 50),
]
tech_rects = [
    pygame.Rect(105, 315, 245, 68),
    pygame.Rect(385, 315, 245, 68),
    pygame.Rect(665, 315, 245, 68),
    pygame.Rect(945, 315, 245, 68),
]

scan_btn = pygame.Rect(500, 705, 120, 38)
campaign_btn = pygame.Rect(635, 705, 135, 38)
resonance_btn = pygame.Rect(785, 705, 125, 38)

plus_minus = []


# ------------------------------------------------------------
# Safe text and drawing utilities
# ------------------------------------------------------------
def clamp(value):
    return max(0, min(100, int(round(value))))


def remaining_points():
    return POINTS - sum(alloc.values()) - action_points


def draw_text(text, font, color, x, y):
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))


def draw_center(text, font, color, rect):
    surface = font.render(str(text), True, color)
    screen.blit(surface, surface.get_rect(center=(rect.centerx, rect.centery - 1)))


def draw_panel(rect, color=PANEL, border_color=None, radius=14):
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=radius)


def wrap_text_to_width(text, font, max_width):
    words = str(text).split()
    if not words:
        return [""]

    lines = []
    current = ""
    for word in words:
        test = word if current == "" else current + " " + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)
    return lines


def draw_wrapped(text, font, color, rect, line_height=20, max_lines=None, center=False):
    lines = wrap_text_to_width(text, font, rect.width)
    if max_lines is not None:
        lines = lines[:max_lines]
    y = rect.y

    for line in lines:
        surface = font.render(line, True, color)
        if center:
            x = rect.x + (rect.width - surface.get_width()) // 2
        else:
            x = rect.x
        screen.blit(surface, (x, y))
        y += line_height


def draw_button(rect, label, mouse, color=BLUE, disabled=False, font=TEXT):
    if disabled:
        fill = DARK_GRAY
    else:
        fill = CYAN if rect.collidepoint(mouse) else color

    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
    draw_center(label, font, WHITE, rect)


def draw_bar(x, y, value, width=230, height=16):
    pygame.draw.rect(screen, (40, 45, 65), (x, y, width, height), border_radius=8)
    color = GREEN if value >= 70 else YELLOW if value >= 40 else RED
    pygame.draw.rect(screen, color, (x, y, int(value * width / 100), height), border_radius=8)


def add_news(text):
    news.append(text)
    if len(news) > 35:
        del news[0]


def add_achievement(name):
    if name not in achievements:
        achievements.append(name)


# ------------------------------------------------------------
# Quantum-inspired mechanics
# ------------------------------------------------------------
def normalize_amplitudes(raw):
    """
    Quantum-inspired normalization:
    possible futures are represented as complex amplitudes.
    Their observable probabilities are calculated as |A|^2.
    """
    total = sum(abs(a) ** 2 for a in raw.values())
    if total <= 0:
        return {k: complex(1 / math.sqrt(len(raw)), 0) for k in raw}

    factor = math.sqrt(total)
    return {k: a / factor for k, a in raw.items()}


def quantum_decoherence_level():
    """
    Decoherence in this game means the system loses stable possible futures.
    Bad balance, weak approval, and low indicators increase crisis-like outcomes.
    """
    low_values = [100 - v for v in stats.values() if v < 45]
    imbalance = max(stats.values()) - min(stats.values())
    approval_risk = max(0, 50 - approval)
    level = (sum(low_values) * 0.25) + (imbalance * 0.35) + (approval_risk * 0.4)

    if tech_quantum_sensors:
        level -= 12
    if tech_social_shield:
        level -= 6
    if resonance_charge:
        level -= 5

    return clamp(level)


def build_quantum_state():
    """
    Builds a quantum-inspired state vector for future outcomes.
    Player decisions affect amplitudes, phases, interference, and decoherence.
    """
    e = alloc["Environment"]
    d = alloc["Education"]
    h = alloc["Health"]
    ec = alloc["Economy"]
    s = alloc["Stability"]

    raw = {
        "Green Recovery": complex(1.0 + e * 0.16 + d * 0.08, 0.12 * d),
        "Economic Boom": complex(1.0 + ec * 0.16 + s * 0.06, 0.10 * ec),
        "Social Strain": complex(1.0 + (10 - h) * 0.12 + (10 - s) * 0.14, 0.15 * (10 - s)),
        "Quantum Leap": complex(0.65 + d * 0.08 + h * 0.05, 0.10 * (d + h)),
    }

    # Constructive interference: good combinations amplify positive futures.
    if e >= 3 and d >= 3:
        raw["Green Recovery"] += complex(0.55, 0.35)
    if d >= 3 and ec >= 3:
        raw["Quantum Leap"] += complex(0.45, 0.40)
    if h >= 3 and s >= 3:
        raw["Social Strain"] -= complex(0.35, 0.20)

    # Destructive interference: unsafe combinations create crisis amplitude.
    if ec >= 5 and s <= 1:
        raw["Economic Boom"] -= complex(0.30, 0.25)
        raw["Social Strain"] += complex(0.75, 0.25)
    if e <= 1 and ec >= 4:
        raw["Green Recovery"] -= complex(0.45, 0.10)
        raw["Social Strain"] += complex(0.35, 0.25)

    # Technologies modify amplitudes.
    if tech_green_fusion:
        raw["Green Recovery"] += complex(0.35, 0.20)
    if tech_ai_governance:
        raw["Economic Boom"] += complex(0.35, 0.25)
        raw["Social Strain"] += complex(0.18, 0.10)
    if tech_quantum_sensors:
        raw["Social Strain"] -= complex(0.35, 0.15)
        raw["Quantum Leap"] += complex(0.25, 0.20)
    if tech_social_shield:
        raw["Social Strain"] -= complex(0.25, 0.12)
        raw["Green Recovery"] += complex(0.12, 0.05)

    # New user feature: Resonance Boost.
    # It costs policy points and temporarily strengthens positive amplitudes.
    if resonance_charge:
        raw["Green Recovery"] += complex(0.40, 0.30)
        raw["Quantum Leap"] += complex(0.35, 0.28)
        raw["Social Strain"] -= complex(0.25, 0.10)

    decoherence = quantum_decoherence_level()
    if decoherence > 45:
        raw["Social Strain"] += complex(decoherence / 90, decoherence / 140)
        raw["Quantum Leap"] -= complex(decoherence / 220, 0)

    return normalize_amplitudes(raw)


def detect_interference():
    e = alloc["Environment"]
    d = alloc["Education"]
    h = alloc["Health"]
    ec = alloc["Economy"]
    s = alloc["Stability"]

    if e >= 3 and d >= 3:
        return "Constructive: Education amplifies Climate policy."
    if d >= 3 and ec >= 3:
        return "Constructive: Education amplifies Innovation."
    if ec >= 5 and s <= 1:
        return "Destructive: Growth without Stability."
    if e <= 1 and ec >= 4:
        return "Destructive: Economy damages Climate future."
    if h >= 3 and s >= 3:
        return "Stabilizing: Health and Stability reduce crisis."
    if resonance_charge:
        return "Resonance Boost: positive futures are amplified."
    return "Neutral: no strong interference pattern."


def futures():
    global last_quantum_status, last_interference

    q = build_quantum_state()
    decoherence = quantum_decoherence_level()
    last_quantum_status = (
        "Coherent" if decoherence < 35
        else "Decoherence Risk" if decoherence < 65
        else "Unstable / Decohered"
    )
    last_interference = detect_interference()

    data = {
        "Green Recovery": {
            "color": GREEN,
            "effects": {"Environment": 11, "Education": 4, "Health": 4, "Economy": 1, "Stability": 3},
            "desc": "Sustainable systems reinforce each other.",
        },
        "Economic Boom": {
            "color": YELLOW,
            "effects": {"Environment": -6, "Economy": 12, "Stability": 2, "Education": 1, "Approval": 2},
            "desc": "Rapid growth, but environmental pressure rises.",
        },
        "Social Strain": {
            "color": RED,
            "effects": {"Health": -8, "Economy": -5, "Stability": -11, "Approval": -5},
            "desc": "Weak systems collapse into public pressure.",
        },
        "Quantum Leap": {
            "color": PURPLE,
            "effects": {"Education": 7, "Health": 3, "Economy": 5, "Stability": -2, "Approval": 3},
            "desc": "Innovation opens a new timeline with mixed risks.",
        },
    }

    cards = []
    for title, amplitude in q.items():
        probability = abs(amplitude) ** 2
        phase = math.degrees(cmath.phase(amplitude))
        cards.append({
            "title": title,
            "amplitude": amplitude,
            "amp_text": f"{amplitude.real:.2f}+{amplitude.imag:.2f}i",
            "phase": round(phase),
            "prob_value": probability,
            "prob": round(probability * 100),
            "weight": probability,
            "decoherence": decoherence,
            **data[title],
        })

    total_percent = sum(c["prob"] for c in cards)
    if total_percent != 100 and cards:
        cards[0]["prob"] += 100 - total_percent

    return cards


def apply_entanglement():
    """
    Entanglement matrix: indicators are not independent.
    A change in one area creates secondary effects elsewhere.
    """
    global approval

    changes = {k: 0 for k in stats}
    approval_change = 0

    if stats["Education"] >= 65:
        changes["Economy"] += 2
        changes["Stability"] += 1
    if stats["Education"] < 35:
        changes["Economy"] -= 2
        changes["Stability"] -= 1
        delayed_effects.append((2, "Delayed effect: low education reduced economic resilience.", {"Economy": -4}))

    if stats["Environment"] < 35:
        changes["Health"] -= 3
        delayed_effects.append((2, "Delayed effect: pollution created health problems.", {"Health": -4, "Approval": -2}))
    if stats["Environment"] >= 70:
        changes["Health"] += 2

    if stats["Health"] >= 70:
        approval_change += 2
    if stats["Health"] < 35:
        approval_change -= 3
        changes["Stability"] -= 1

    if stats["Stability"] < 35:
        changes["Economy"] -= 3
        approval_change -= 2
    if stats["Stability"] >= 70:
        changes["Economy"] += 1
        approval_change += 1

    if tech_social_shield and stats["Stability"] < 50:
        changes["Stability"] += 2
        approval_change += 1

    applied = []
    for k, v in changes.items():
        if v != 0:
            stats[k] = clamp(stats[k] + v)
            applied.append(f"{k} {v:+d}")

    if approval_change != 0:
        approval = clamp(approval + approval_change)
        applied.append(f"Approval {approval_change:+d}")

    if applied:
        add_news("Entanglement effect: " + ", ".join(applied))


def process_delayed_effects():
    global approval, delayed_effects
    remaining = []

    for turns_left, text, effects in delayed_effects:
        turns_left -= 1
        if turns_left <= 0:
            for k, v in effects.items():
                if k == "Approval":
                    approval = clamp(approval + v)
                else:
                    stats[k] = clamp(stats[k] + v)
            add_news(text)
        else:
            remaining.append((turns_left, text, effects))

    delayed_effects = remaining


# ------------------------------------------------------------
# Gameplay functions
# ------------------------------------------------------------
def set_country(index):
    global country, stats, approval, state, news, future_cards
    opts = ["Developed Nation", "Island State", "Tech Superpower", "Developing Nation"]
    country = opts[index]
    stats = {k: 50 for k in stats}
    approval = 60

    if index == 0:
        stats["Economy"] = 65
        stats["Education"] = 65
        stats["Environment"] = 40
    elif index == 1:
        stats["Environment"] = 72
        stats["Economy"] = 35
        stats["Health"] = 55
    elif index == 2:
        stats["Economy"] = 72
        stats["Education"] = 76
        stats["Stability"] = 40
        stats["Environment"] = 42
    elif index == 3:
        stats["Stability"] = 65
        stats["Health"] = 40
        stats["Economy"] = 42

    news = [country + " selected.", "Quantum policy simulator activated."]
    future_cards = futures()
    state = PLAY


def trigger_event():
    global state, event_title, event_desc, event_choices, last_event

    state = EVENT
    events = [
        (
            "Pandemic",
            "Hospitals are overloaded and public fear is rising.",
            [
                ("Lockdown", {"Health": 8, "Economy": -6, "Approval": -2}),
                ("Balanced", {"Health": 4, "Economy": -2, "Stability": 2}),
                ("Open", {"Health": -6, "Economy": 5, "Approval": -4}),
            ],
        ),
        (
            "Floods",
            "Coastal cities are under water after extreme weather.",
            [
                ("Green Aid", {"Environment": 7, "Approval": 2}),
                ("Relief", {"Stability": 4, "Health": 2}),
                ("Ignore", {"Approval": -7, "Environment": -3}),
            ],
        ),
        (
            "Scandal",
            "A corruption scandal is damaging public trust.",
            [
                ("Reform", {"Stability": 8, "Approval": 2}),
                ("Control Media", {"Approval": 2, "Stability": -4}),
                ("Do Nothing", {"Approval": -8, "Stability": -4}),
            ],
        ),
        (
            "Quantum Misinformation",
            "False predictions about the future spread online.",
            [
                ("Teach Media Literacy", {"Education": 6, "Stability": 3}),
                ("AI Fact Checking", {"Economy": 3, "Stability": 3, "Approval": 1}),
                ("Censor Panic", {"Stability": -5, "Approval": -5}),
            ],
        ),
        (
            "Energy Shock",
            "Energy prices rise and industry demands immediate action.",
            [
                ("Invest Green", {"Environment": 6, "Economy": -2}),
                ("Subsidize Industry", {"Economy": 5, "Environment": -4}),
                ("Ration Energy", {"Stability": -3, "Approval": -4, "Environment": 3}),
            ],
        ),
        (
            "Climate Migration",
            "A nearby region becomes unlivable and refugees need support.",
            [
                ("Open Support", {"Stability": -2, "Health": 3, "Approval": 2}),
                ("International Aid", {"Economy": -3, "Stability": 4}),
                ("Close Borders", {"Stability": 2, "Approval": -6}),
            ],
        ),
    ]

    available = [x for x in events if x[0] != last_event]
    chosen = random.choice(available)
    last_event = chosen[0]
    event_title, event_desc, event_choices = chosen


def apply_choice(index):
    global state, approval, future_cards

    for k, v in event_choices[index][1].items():
        if k == "Approval":
            approval = clamp(approval + v)
        else:
            stats[k] = clamp(stats[k] + v)

    add_news(event_title + " handled: " + event_choices[index][0])
    apply_entanglement()
    future_cards = futures()
    state = PLAY


def apply_future(future):
    global collapsed, history, message, state, approval, future_cards, resonance_charge

    history = {
        "year": year,
        "stats": stats.copy(),
        "approval": approval,
        "alloc": alloc.copy(),
        "news": news.copy(),
        "timeline": timeline.copy(),
        "delayed_effects": delayed_effects.copy(),
        "action_points": action_points,
        "resonance_charge": resonance_charge,
    }

    for k, v in future["effects"].items():
        if k == "Approval":
            approval = clamp(approval + v)
        else:
            stats[k] = clamp(stats[k] + v)

    collapsed = True
    message = "Reality collapsed into " + future["title"]
    timeline.append(f"Y{year}: {future['title']} ({future['prob']}%)")
    add_news(message)
    add_news("Measured amplitude: " + future["amp_text"] + f", phase {future['phase']}°")

    if resonance_charge:
        add_news("Resonance Boost discharged during observation.")
        resonance_charge = False

    apply_entanglement()

    event_chance = 0.32 + quantum_decoherence_level() / 190
    if random.random() < event_chance:
        trigger_event()

    if state != EVENT and year in [3, 6, 8] and (stats["Education"] >= 62 or future["title"] == "Quantum Leap"):
        state = TECH

    future_cards = futures()


def next_year():
    global year, collapsed, future_cards, message, state
    global action_points, scan_used_this_year, campaign_used_this_year

    year += 1
    process_delayed_effects()

    if year in [4, 8] and approval < 40:
        set_ending("LOST ELECTION", "Citizens voted you out because public approval collapsed.")
        return

    if stats["Environment"] <= 10:
        set_ending("ECOLOGICAL COLLAPSE", "The environment crossed a critical threshold before the decade ended.")
        return
    if stats["Stability"] <= 10:
        set_ending("FRAGMENTED WORLD", "Institutions failed and the world split into unstable blocs.")
        return
    if stats["Economy"] <= 10:
        set_ending("ECONOMIC BREAKDOWN", "The economy failed and long-term development became impossible.")
        return

    for k in alloc:
        alloc[k] = 0

    action_points = 0
    scan_used_this_year = False
    campaign_used_this_year = False
    collapsed = False
    future_cards = futures()
    message = "Allocate all 10 points."

    if year > MAX_YEAR:
        finish()


def set_ending(title, text):
    global state, end_title, end_text
    end_title = title
    end_text = text
    state = END


def choose_technology(index):
    global state
    global tech_green_fusion, tech_ai_governance, tech_quantum_sensors, tech_social_shield

    used = [tech_green_fusion, tech_ai_governance, tech_quantum_sensors, tech_social_shield][index]
    if used:
        return

    if index == 0:
        tech_green_fusion = True
        stats["Environment"] = clamp(stats["Environment"] + 10)
        stats["Economy"] = clamp(stats["Economy"] + 5)
        add_news("Green Fusion deployed: climate amplitude strengthened.")
        add_achievement("Fusion Pioneer")
    elif index == 1:
        tech_ai_governance = True
        stats["Economy"] = clamp(stats["Economy"] + 12)
        stats["Stability"] = clamp(stats["Stability"] - 5)
        add_news("AI Governance activated: growth rises, stability risk appears.")
        add_achievement("AI Governor")
    elif index == 2:
        tech_quantum_sensors = True
        stats["Health"] = clamp(stats["Health"] + 5)
        stats["Stability"] = clamp(stats["Stability"] + 5)
        add_news("Quantum Sensors deployed: decoherence risk reduced.")
        add_achievement("Quantum Observer")
    elif index == 3:
        tech_social_shield = True
        stats["Stability"] = clamp(stats["Stability"] + 8)
        approval = globals()["approval"]
        globals()["approval"] = clamp(approval + 5)
        add_news("Social Shield deployed: public trust and stability improved.")
        add_achievement("Social Architect")

    apply_entanglement()
    state = PLAY


def run_quantum_scan():
    global advisor_text, scan_used_this_year, future_cards

    if scan_used_this_year:
        advisor_text = "Advisor: quantum scan already used this year."
        return

    weakest = min(stats, key=stats.get)
    decoherence = quantum_decoherence_level()
    highest_future = max(future_cards, key=lambda f: f["prob"])

    advisor_text = (
        f"Advisor: weakest system is {weakest}. "
        f"Current dominant future is {highest_future['title']} ({highest_future['prob']}%). "
        f"Decoherence is {decoherence}%."
    )
    add_news("Quantum Scan completed: " + weakest + " is the weakest indicator.")
    scan_used_this_year = True
    add_achievement("Quantum Analyst")


def run_public_campaign():
    global approval, action_points, campaign_used_this_year, future_cards, message

    if collapsed:
        message = "Campaign is only available before observation."
        return
    if campaign_used_this_year:
        message = "Public Campaign already used this year."
        return
    if remaining_points() < 2:
        message = "Public Campaign needs 2 available points."
        return

    action_points += 2
    approval = clamp(approval + 5)
    stats["Stability"] = clamp(stats["Stability"] + 1)
    campaign_used_this_year = True
    message = "Public Campaign improved approval."
    add_news("Public Campaign used: Approval +5, Stability +1.")
    future_cards = futures()


def run_resonance_boost():
    global resonance_charge, action_points, future_cards, message

    if collapsed:
        message = "Resonance Boost is only available before observation."
        return
    if resonance_charge:
        message = "Resonance Boost is already charged."
        return
    if remaining_points() < 3:
        message = "Resonance Boost needs 3 available points."
        return

    action_points += 3
    resonance_charge = True
    message = "Resonance Boost charged for next observation."
    add_news("Resonance Boost charged: positive amplitudes amplified.")
    add_achievement("Resonance Engineer")
    future_cards = futures()


def finish():
    avg = sum(stats.values()) / 5
    balance = max(stats.values()) - min(stats.values())
    decoherence = quantum_decoherence_level()

    if avg >= 76 and balance <= 28 and decoherence < 45:
        set_ending(
            "SUSTAINABLE QUANTUM FUTURE",
            "You maintained coherence between development, climate, health, economy, and institutions.",
        )
        add_achievement("Coherent World Builder")
    elif stats["Economy"] > 85 and stats["Environment"] < 45:
        set_ending("CORPORATE DYSTOPIA", "The economy boomed, but the climate and society paid the price.")
        add_achievement("Economic Titan")
    elif stats["Environment"] >= 80 and stats["Economy"] < 45:
        set_ending("GREEN BUT FRAGILE WORLD", "Ecology recovered, but weak economic foundations created social pressure.")
        add_achievement("Climate Protector")
    elif stats["Stability"] > 82 and approval < 45:
        set_ending("AUTHORITARIAN STABILITY", "Institutions survived, but public freedom and trust declined.")
        add_achievement("Iron Order")
    elif decoherence >= 65:
        set_ending("DECOHERED FUTURE", "The system became too unstable: possible futures collapsed into chaotic outcomes.")
        add_achievement("Chaos Witness")
    else:
        set_ending("UNCERTAIN FUTURE", "The world survived, but its long-term trajectory remains unstable.")

    if not rewind_used:
        add_achievement("No Rewind Timeline")
    if len(timeline) >= 10:
        add_achievement("Decade Completed")


def reset_game():
    global country, year, stats, alloc, approval, collapsed, rewind_used, history, future_cards
    global news, timeline, message, last_event, event_title, event_desc, event_choices
    global end_title, end_text, achievements, delayed_effects, state
    global last_quantum_status, last_interference, advisor_text
    global action_points, scan_used_this_year, campaign_used_this_year, resonance_charge
    global tech_green_fusion, tech_ai_governance, tech_quantum_sensors, tech_social_shield

    country = ""
    year = 1
    stats = {k: 50 for k in ["Environment", "Education", "Health", "Economy", "Stability"]}
    alloc = {k: 0 for k in stats}
    approval = 60
    collapsed = False
    rewind_used = False
    history = None
    news = ["World initialized."]
    timeline = []
    message = "Allocate all 10 points."
    last_event = ""
    event_title = ""
    event_desc = ""
    event_choices = []
    end_title = ""
    end_text = ""
    achievements = []
    delayed_effects = []
    last_quantum_status = "Coherent"
    last_interference = "Neutral"
    advisor_text = "Advisor: balance all systems to keep the future coherent."
    action_points = 0
    scan_used_this_year = False
    campaign_used_this_year = False
    resonance_charge = False
    tech_green_fusion = False
    tech_ai_governance = False
    tech_quantum_sensors = False
    tech_social_shield = False
    future_cards = futures()
    state = MENU


# ------------------------------------------------------------
# Drawing functions
# ------------------------------------------------------------
def draw_menu(mouse):
    screen.fill(BG)

    draw_text("QUANTUM BUTTERFLY EFFECT", TITLE, CYAN, 285, 150)

    draw_wrapped(
        "A quantum-inspired strategy game about sustainability, uncertainty, and possible futures.",
        TEXT,
        GRAY,
        pygame.Rect(310, 235, 660, 60),
        22,
        center=True,
    )

    draw_text("ABOUT THE GAME", H1, CYAN, 420, 360)

    intro = (
        "Every policy decision creates several possible futures. "
        "Before observation, these futures exist as quantum-inspired states. "
        "When you press OBSERVE, one future collapses into reality."
    )

    draw_wrapped(
        intro,
        TEXT,
        WHITE,
        pygame.Rect(420, 410, 470, 100),
        24,
        max_lines=4
    )

    draw_text("GOAL", H2, PURPLE, 420, 535)
    draw_text("Balance society for 10 years and reach a sustainable future.", SMALL, WHITE, 420, 565)

    draw_text("MAIN RULES", H2, PURPLE, 420, 605)
    draw_text("Spend all 10 points, observe the future, survive crises and elections.", SMALL, WHITE, 420, 635)

    draw_button(start_btn, "START GAME", mouse, BLUE, font=H2)


def draw_country(mouse):
    screen.fill(BG)

    draw_text("SELECT STARTING NATION", TITLE, CYAN, 325, 150)
    draw_wrapped(
        "Each country starts with different strengths and weaknesses, which changes the quantum state of future outcomes.",
        TEXT,
        GRAY,
        pygame.Rect(330, 215, 620, 60),
        22,
        center=True,
    )

    names = ["Developed", "Island", "Tech Power", "Developing"]
    descriptions = [
        "Strong education, weaker climate resilience.",
        "Strong environment, weaker economy.",
        "High tech and economy, unstable society.",
        "Stable institutions, but weak health.",
    ]
    colors = [BLUE, GREEN, PURPLE, YELLOW]

    for i, rect in enumerate(country_btns):
        draw_button(rect, names[i], mouse, colors[i], font=H2)
        draw_wrapped(descriptions[i], SMALL, GRAY, pygame.Rect(rect.x, rect.y + 105, rect.width, 50), 18, center=True)


def draw_stat_panel(mouse):
    panel = pygame.Rect(20, 105, 430, 665)
    draw_panel(panel)
    draw_text("Policy Allocation", H1, CYAN, 40, 125)
    draw_wrapped(message, SMALL, GRAY, pygame.Rect(40, 160, 370, 40), 18, max_lines=2)

    y = 205
    plus_minus.clear()

    for stat in stats:
        draw_text(stat, H2, WHITE, 40, y)
        draw_text(str(stats[stat]), TEXT, GRAY, 270, y + 2)
        draw_text("alloc " + str(alloc[stat]), SMALL, PURPLE, 335, y + 4)
        draw_bar(40, y + 32, stats[stat], 245, 16)

        minus_rect = pygame.Rect(320, y + 25, 34, 30)
        plus_rect = pygame.Rect(365, y + 25, 34, 30)
        plus_minus.append((stat, "-", minus_rect))
        plus_minus.append((stat, "+", plus_rect))
        draw_button(minus_rect, "-", mouse, BLUE, font=H2)
        draw_button(plus_rect, "+", mouse, BLUE, font=H2)

        y += 105


def draw_quantum_cards():
    panel = pygame.Rect(470, 105, 505, 290)
    draw_panel(panel)
    draw_text("Quantum Futures", H1, CYAN, 490, 125)
    draw_text("Chance is calculated from squared amplitude: |A|²", TINY, GRAY, 490, 158)

    for i, future in enumerate(future_cards):
        x = 490 + (i % 2) * 235
        y = 190 + (i // 2) * 92
        rect = pygame.Rect(x, y, 215, 76)

        draw_panel(rect, CARD, BLUE, radius=10)
        draw_text(future["title"], SMALL, WHITE, x + 8, y + 8)
        draw_text(str(future["prob"]) + "%", H2, WHITE, x + 158, y + 6)
        draw_text("A=" + future["amp_text"], TINY, GRAY, x + 8, y + 38)
        draw_text("phase " + str(future["phase"]) + "°", TINY, GRAY, x + 8, y + 56)


def draw_monitor():
    panel = pygame.Rect(995, 105, 260, 290)
    draw_panel(panel)
    draw_text("Quantum Monitor", H2, CYAN, 1015, 125)

    status_color = GREEN if last_quantum_status == "Coherent" else YELLOW if "Risk" in last_quantum_status else RED

    draw_text("Status:", SMALL, WHITE, 1015, 168)
    draw_text(last_quantum_status, SMALL, status_color, 1070, 168)

    decoherence = quantum_decoherence_level()
    draw_text("Decoherence: " + str(decoherence) + "%", SMALL, WHITE, 1015, 205)
    draw_bar(1015, 232, decoherence, 205, 14)

    draw_text("Interference:", SMALL, WHITE, 1015, 270)
    draw_wrapped(last_interference, TINY, PURPLE, pygame.Rect(1015, 296, 215, 60), 16, max_lines=4)

    charge = "ON" if resonance_charge else "OFF"
    draw_text("Resonance: " + charge, SMALL, CYAN if resonance_charge else GRAY, 1015, 362)


def draw_news_and_timeline():
    news_panel = pygame.Rect(470, 415, 505, 250)
    draw_panel(news_panel)
    draw_text("News Feed", H2, CYAN, 490, 435)

    y = 468
    for item in news[-6:]:
        lines = wrap_text_to_width("- " + item, SMALL, 460)
        for line in lines[:2]:
            draw_text(line, SMALL, WHITE, 490, y)
            y += 17
        y += 3
        if y > 640:
            break

    timeline_panel = pygame.Rect(995, 415, 260, 250)
    draw_panel(timeline_panel)
    draw_text("Timeline Map", H2, CYAN, 1015, 435)

    y = 472
    if not timeline:
        draw_wrapped("No collapsed futures yet.", SMALL, GRAY, pygame.Rect(1015, y, 215, 40), 18)
    else:
        for item in timeline[-7:]:
            draw_wrapped(item, SMALL, WHITE, pygame.Rect(1015, y, 215, 22), 18, max_lines=1)
            y += 25


def draw_player_actions(mouse):
    panel = pygame.Rect(470, 665, 785, 110)
    draw_panel(panel)

    draw_text("Actions", SMALL, CYAN, 490, 678)

    draw_button(scan_btn, "SCAN", mouse, CYAN, disabled=scan_used_this_year, font=SMALL)

    draw_button(campaign_btn, "CAMPAIGN", mouse, GREEN,
    disabled=campaign_used_this_year or collapsed or remaining_points() < 2,
    font=SMALL)

    draw_button(resonance_btn, "BOOST", mouse, PURPLE,
    disabled=resonance_charge or collapsed or remaining_points() < 3,
    font=SMALL)

    short_advisor = advisor_text[:85] + "..." if len(advisor_text) > 85 else advisor_text

    draw_wrapped(
        short_advisor,
        TINY,
        GRAY,
        pygame.Rect(500, 760, 520, 15),
        14,
        max_lines=1
    )


def draw_play(mouse):
    screen.fill(BG)

    draw_text(country, TEXT, PURPLE, 20, 12)
    draw_text("Year " + str(year) + "/10", H1, WHITE, 20, 42)
    draw_text("Approval " + str(approval), H2, WHITE, 810, 22)
    draw_text("Points " + str(remaining_points()), H2, WHITE, 810, 56)

    draw_button(help_btn, "QUANTUM HELP", mouse, PURPLE, font=SMALL)

    draw_stat_panel(mouse)
    draw_quantum_cards()
    draw_monitor()
    draw_news_and_timeline()
    draw_player_actions(mouse)

    # Warnings are compact and do not overlap with buttons.
    warning_y = 650
    if approval < 45:
        draw_text("Low approval!", SMALL, RED, 1000, warning_y)
        warning_y += 20
    if year in [3, 7]:
        draw_text("Election next year", SMALL, YELLOW, 1000, warning_y)
        warning_y += 20
    if stats["Stability"] < 35:
        draw_text("Stability critical", SMALL, RED, 1000, warning_y)
        warning_y += 20
    if quantum_decoherence_level() > 60:
        draw_text("High decoherence risk", SMALL, RED, 1000, warning_y)

    if not collapsed:
        draw_button(observe_btn, "OBSERVE", mouse, BLUE, font=H2)
    else:
        draw_button(next_btn, "NEXT YEAR", mouse, BLUE, font=H2)

    if history and not rewind_used:
        draw_button(rewind_btn, "REWIND", mouse, PURPLE, font=H2)


def draw_event(mouse):
    screen.fill(BG)

    panel = pygame.Rect(250, 115, 780, 610)
    draw_panel(panel)
    draw_text("GLOBAL EVENT", H1, RED, 515, 160)

    title_rect = pygame.Rect(320, 225, 640, 45)
    draw_wrapped(event_title, TITLE, CYAN, title_rect, 36, max_lines=1, center=True)

    draw_wrapped(event_desc, TEXT, WHITE, pygame.Rect(330, 320, 620, 70), 22, max_lines=3, center=True)
    draw_wrapped(
        "Choose a response. Your decision will affect entangled systems and may shift future amplitudes.",
        SMALL,
        GRAY,
        pygame.Rect(350, 425, 580, 45),
        18,
        max_lines=2,
        center=True,
    )

    for i, rect in enumerate(choice_rects):
        draw_button(rect, event_choices[i][0], mouse, BLUE, font=TEXT)


def draw_tech(mouse):
    screen.fill(BG)

    draw_text("TECHNOLOGY UNLOCKED", TITLE, CYAN, 360, 145)
    draw_wrapped(
        "Choose one technology. Each one changes the quantum state of possible future outcomes.",
        TEXT,
        GRAY,
        pygame.Rect(310, 210, 660, 55),
        22,
        center=True,
    )

    labels = ["Green Fusion", "AI Governance", "Quantum Sensors", "Social Shield"]
    descriptions = [
        "Boosts climate and economy; strengthens Green Recovery amplitude.",
        "Boosts economy but creates stability risk; mixed interference.",
        "Improves health and stability; reduces crisis and decoherence.",
        "Improves public trust and reduces social instability.",
    ]
    colors = [GREEN, PURPLE, CYAN, ORANGE]
    used = [tech_green_fusion, tech_ai_governance, tech_quantum_sensors, tech_social_shield]

    for i, rect in enumerate(tech_rects):
        label = labels[i] + (" USED" if used[i] else "")
        draw_button(rect, label, mouse, DARK_GRAY if used[i] else colors[i], disabled=used[i], font=SMALL)
        draw_wrapped(descriptions[i], SMALL, GRAY, pygame.Rect(rect.x, rect.y + 88, rect.width, 70), 17, max_lines=4, center=True)


def draw_help(mouse):
    screen.fill(BG)

    panel = pygame.Rect(170, 70, 940, 620)
    draw_panel(panel)
    draw_text("QUANTUM HELP", TITLE, CYAN, 480, 105)

    sections = [
        ("Superposition", "Before observation, several futures exist at the same time as possible game states."),
        ("Amplitudes", "Each future has a complex amplitude A. The game shows A and phase on each future card."),
        ("Collapse", "When you press OBSERVE, one future becomes real. Its chance is calculated as |A|²."),
        ("Interference", "Policy combinations can amplify or weaken futures. Education plus Environment strengthens Green Recovery."),
        ("Entanglement", "Indicators are connected. Education can affect Economy, Environment can affect Health, and Stability can affect Approval."),
        ("Decoherence", "If the world becomes unstable or unbalanced, crisis timelines become more likely."),
        ("Player Actions", "Scan gives advice, Campaign improves approval, and Resonance Boost temporarily amplifies positive futures."),
        ("Quantum Rewind", "Once per game, you may restore the previous timeline before collapse consequences continue."),
    ]

    y = 165
    for title, body in sections:
        draw_text(title, H2, PURPLE, 215, y)
        draw_wrapped(body, SMALL, WHITE, pygame.Rect(430, y + 1, 600, 45), 18, max_lines=2)
        y += 62

    draw_button(back_btn, "BACK", mouse, BLUE, font=H2)


def draw_end(mouse):
    screen.fill(BG)

    draw_text("FINAL OUTCOME", TITLE, CYAN, 430, 90)
    draw_wrapped(end_title, H1, WHITE, pygame.Rect(300, 165, 680, 40), 30, max_lines=1, center=True)
    draw_wrapped(end_text, TEXT, GRAY, pygame.Rect(300, 225, 680, 55), 22, max_lines=2, center=True)

    panel = pygame.Rect(250, 325, 780, 250)
    draw_panel(panel)
    draw_text("Final Indicators", H1, CYAN, 300, 350)

    y = 400
    for stat, value in stats.items():
        draw_text(stat, SMALL, WHITE, 300, y)
        draw_text(value, SMALL, GRAY, 430, y)
        draw_bar(500, y, value, 220, 14)
        y += 34

    draw_text("Approval " + str(approval), SMALL, WHITE, 760, 400)
    draw_text("Decoherence " + str(quantum_decoherence_level()) + "%", SMALL, WHITE, 760, 430)

    y = 600

    short_achievements = achievements[-4:]

    for achievement in short_achievements:
        draw_text("• " + achievement, SMALL, YELLOW, 420, y)
        y += 20

    draw_button(restart_btn, "RESTART", mouse, BLUE, font=H2)


# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------
future_cards = futures()
running = True

while running:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == MENU:
                if start_btn.collidepoint(event.pos):
                    state = COUNTRY

            elif state == COUNTRY:
                for i, rect in enumerate(country_btns):
                    if rect.collidepoint(event.pos):
                        set_country(i)

            elif state == PLAY:
                if help_btn.collidepoint(event.pos):
                    previous_state = PLAY
                    state = HELP
                    continue

                for stat, action, rect in plus_minus:
                    if rect.collidepoint(event.pos) and not collapsed:
                        if action == "+" and remaining_points() > 0:
                            alloc[stat] += 1
                        elif action == "-" and alloc[stat] > 0:
                            alloc[stat] -= 1
                        future_cards = futures()

                if scan_btn.collidepoint(event.pos):
                    run_quantum_scan()

                elif campaign_btn.collidepoint(event.pos):
                    run_public_campaign()

                elif resonance_btn.collidepoint(event.pos):
                    run_resonance_boost()

                elif history and not rewind_used and rewind_btn.collidepoint(event.pos):
                    year = history["year"]
                    stats = history["stats"].copy()
                    approval = history["approval"]
                    alloc = history["alloc"].copy()
                    news = history["news"].copy()
                    timeline = history["timeline"].copy()
                    delayed_effects = history["delayed_effects"].copy()
                    action_points = history["action_points"]
                    resonance_charge = history["resonance_charge"]
                    collapsed = False
                    rewind_used = True
                    add_news("Quantum Rewind used: previous timeline restored.")
                    add_achievement("Timeline Rewound")
                    future_cards = futures()

                elif not collapsed and observe_btn.collidepoint(event.pos):
                    if remaining_points() == 0:
                        pick = random.choices(future_cards, weights=[x["weight"] for x in future_cards], k=1)[0]
                        apply_future(pick)
                    else:
                        message = "Spend all 10 points before observation."

                elif collapsed and next_btn.collidepoint(event.pos):
                    next_year()

            elif state == EVENT:
                for i, rect in enumerate(choice_rects):
                    if rect.collidepoint(event.pos):
                        apply_choice(i)

            elif state == TECH:
                for i, rect in enumerate(tech_rects):
                    if rect.collidepoint(event.pos):
                        choose_technology(i)

            elif state == HELP:
                if back_btn.collidepoint(event.pos):
                    state = previous_state

            elif state == END:
                if restart_btn.collidepoint(event.pos):
                    reset_game()

    if state == MENU:
        draw_menu(mouse)
    elif state == COUNTRY:
        draw_country(mouse)
    elif state == PLAY:
        draw_play(mouse)
    elif state == EVENT:
        draw_event(mouse)
    elif state == TECH:
        draw_tech(mouse)
    elif state == HELP:
        draw_help(mouse)
    elif state == END:
        draw_end(mouse)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
