# settings.py
import random

# Screen Settings
WIDTH = 1000
HEIGHT = 600
FPS = 60
TITLE = "Moonlight Castle Adventure - 100 Levels"
TOTAL_LEVELS = 100

# Colors (RGB)
SKY_TOP = (15, 23, 54)
SKY_BOTTOM = (45, 58, 115)
MOON_COLOR = (235, 245, 255)
CASTLE_COLOR = (22, 28, 58)
GRASS_GREEN = (46, 204, 113)
GRASS_DARK = (39, 174, 96)
DIRT_BROWN = (110, 71, 43)
DIRT_DARK = (82, 50, 28)
GOLD = (255, 215, 0)
GOLD_SHINE = (255, 250, 180)
RED_HOODIE = (220, 38, 38)
SKIN_COLOR = (255, 218, 185)
HAIR_BROWN = (74, 44, 24)
PANTS_BLUE = (30, 58, 138)
SPIKE_GRAY = (203, 213, 225)
WHITE = (255, 255, 255)
BLACK = (15, 23, 42)
HEART_RED = (239, 68, 68)

# Snappy Platformer Physics (Play-Store Game Feel)
GRAVITY = 1.15
FALL_GRAVITY = 1.55
PLAYER_SPEED = 6.8
JUMP_STRENGTH = -18.5
MAX_FALL_SPEED = 20


def _clamp(val, low, high):
    return max(low, min(high, val))


def generate_level(level_idx):
    """Generates a playable, interesting level for any index from 0 to 99 (Levels 1..100)."""
    lvl_num = level_idx + 1
    rng = random.Random(lvl_num * 9973 + 17)

    # Tier difficulty scaling across 100 levels
    if lvl_num <= 20:
        num_islands = rng.randint(3, 4)
        min_w, max_w = 185, 290
        min_gap, max_gap = 65, 115
        spike_chance = 0.45
        max_spikes = 2
    elif lvl_num <= 40:
        num_islands = rng.randint(4, 5)
        min_w, max_w = 165, 255
        min_gap, max_gap = 75, 125
        spike_chance = 0.65
        max_spikes = 3
    elif lvl_num <= 60:
        num_islands = rng.randint(4, 5)
        min_w, max_w = 145, 230
        min_gap, max_gap = 85, 135
        spike_chance = 0.72
        max_spikes = 3
    elif lvl_num <= 80:
        num_islands = rng.randint(5, 6)
        min_w, max_w = 130, 205
        min_gap, max_gap = 85, 140
        spike_chance = 0.80
        max_spikes = 4
    else:
        num_islands = rng.randint(5, 6)
        min_w, max_w = 120, 190
        min_gap, max_gap = 90, 145
        spike_chance = 0.88
        max_spikes = 4

    platforms = []
    coins = []
    spikes = []

    # Starting safe island
    start_w = rng.randint(170, 220)
    start_y = rng.randint(440, 500)
    start_x = 35
    platforms.append((start_x, start_y, start_w, 45))
    coins.append((start_x + start_w - 40, start_y - 55))

    curr_x = start_x + start_w
    curr_y = start_y

    # Reserve space on the right for the final island + flag
    right_margin_for_flag = 175

    for i in range(num_islands - 1):
        gap = rng.randint(min_gap, max_gap)
        next_x = curr_x + gap

        # Keep vertical step comfortably jumpable (-85px up to +70px down)
        delta_y = rng.randint(-82, 68)
        next_y = _clamp(curr_y + delta_y, 230, 510)

        avail_w = (WIDTH - right_margin_for_flag) - next_x
        if avail_w < 110:
            break

        w = _clamp(rng.randint(min_w, max_w), 110, avail_w)
        platforms.append((next_x, next_y, w, 45))

        # Place coins above platform
        coin_count = rng.randint(1, 3)
        for c_idx in range(coin_count):
            cx = int(next_x + ((c_idx + 1) / (coin_count + 1)) * w)
            cy = next_y - rng.randint(52, 85)
            coins.append((cx, cy))

        # Place spikes on wider middle islands, leaving safe landing/takeoff room
        if w >= 150 and rng.random() < spike_chance:
            spike_count = rng.randint(1, min(max_spikes, max(1, (w - 90) // 24)))
            spike_width = spike_count * 20
            min_sx = next_x + 36
            max_sx = next_x + w - spike_width - 36
            if max_sx > min_sx:
                sx = rng.randint(min_sx, max_sx)
                sy = next_y - 25
                spikes.append((sx, sy, spike_count))
                # Reward coin above spikes
                coins.append((sx + spike_width // 2, sy - 52))

        curr_x = next_x + w
        curr_y = next_y

    # Final goal island with Finish Flag
    goal_gap = rng.randint(min_gap, min(max_gap, 125))
    goal_x = _clamp(curr_x + goal_gap, 680, WIDTH - 175)
    goal_y = _clamp(curr_y + rng.randint(-70, 55), 210, 460)
    goal_w = min(155, WIDTH - goal_x - 20)
    if goal_w < 110:
        goal_x = WIDTH - 145
        goal_w = 125

    platforms.append((goal_x, goal_y, goal_w, 45))
    coins.append((goal_x + 28, goal_y - 55))
    flag_pos = (goal_x + goal_w - 52, goal_y - 70)

    return {
        "platforms": platforms,
        "coins": coins,
        "spikes": spikes,
        "flag": flag_pos,
        "spawn": (start_x + 35, start_y - 65),
    }


LEVELS = [generate_level(i) for i in range(TOTAL_LEVELS)]