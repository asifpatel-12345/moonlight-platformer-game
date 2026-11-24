# main.py
import pygame
import sys
import math
import array
from settings import *
from sprites import Player, Platform, Coin, SpikeGroup, Flag

# Initialize Pygame & Mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont("Segoe UI", 36, bold=True)
font_sub = pygame.font.SysFont("Segoe UI", 22, bold=True)
font_btn = pygame.font.SysFont("Segoe UI", 20, bold=True)
font_hud = pygame.font.SysFont("Consolas", 20, bold=True)
font_key = pygame.font.SysFont("Consolas", 15, bold=True)


# Generate Retro Sound Effects without external files
def make_beep(freq, duration_ms, volume=0.2):
    sample_rate = 22050
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        val = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)


snd_jump = make_beep(620, 85, 0.15)
snd_coin = make_beep(980, 90, 0.18)
snd_hurt = make_beep(180, 220, 0.25)
snd_win = make_beep(760, 300, 0.2)


# Play-Store Style Smooth Sky & Depth Layers (No Stars, No Moon Clutter)
def _build_playstore_backdrop():
    surf = pygame.Surface((WIDTH, HEIGHT))

    # Rich Twilight-to-Deep-Teal Gradient Sky
    top_c = (28, 37, 78)
    mid_c = (44, 72, 118)
    bot_c = (32, 56, 86)

    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.55:
            k = t / 0.55
            r = int(top_c[0] * (1 - k) + mid_c[0] * k)
            g = int(top_c[1] * (1 - k) + mid_c[1] * k)
            b = int(top_c[2] * (1 - k) + mid_c[2] * k)
        else:
            k = (t - 0.55) / 0.45
            r = int(mid_c[0] * (1 - k) + bot_c[0] * k)
            g = int(mid_c[1] * (1 - k) + bot_c[1] * k)
            b = int(mid_c[2] * (1 - k) + bot_c[2] * k)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # Soft Horizon Glow Band
    glow = pygame.Surface((WIDTH, 180), pygame.SRCALPHA)
    for i in range(180):
        alpha = int(36 * math.sin((i / 180) * math.pi))
        pygame.draw.line(glow, (125, 211, 252, alpha), (0, i), (WIDTH, i))
    surf.blit(glow, (0, 210))

    # Far Mountain Ridge (Smooth & Minimal)
    far_hills = [
        (-60, HEIGHT),
        (-60, 340),
        (160, 250),
        (390, 335),
        (640, 235),
        (890, 325),
        (WIDTH + 60, 265),
        (WIDTH + 60, HEIGHT),
    ]
    pygame.draw.polygon(surf, (36, 56, 94), far_hills)

    # Mid Valley Hills
    mid_hills = [
        (-60, HEIGHT),
        (-60, 415),
        (210, 355),
        (470, 430),
        (740, 360),
        (WIDTH + 60, 405),
        (WIDTH + 60, HEIGHT),
    ]
    pygame.draw.polygon(surf, (25, 43, 74), mid_hills)

    # Clean Pine Trees Silhouette along Mid Ridge
    tree_x_positions = [55, 115, 255, 325, 530, 595, 785, 855, 935]
    for idx, tx in enumerate(tree_x_positions):
        ty = 375 if idx % 2 == 0 else 395
        scale = 0.85 if idx % 3 == 0 else 1.05
        h1 = int(34 * scale)
        h2 = int(28 * scale)
        w1 = int(18 * scale)
        w2 = int(14 * scale)
        pygame.draw.polygon(surf, (19, 34, 60), [(tx, ty - h1 - h2), (tx - w2, ty - h1 + 6), (tx + w2, ty - h1 + 6)])
        pygame.draw.polygon(surf, (19, 34, 60), [(tx, ty - h1), (tx - w1, ty), (tx + w1, ty)])

    # Foreground Ground Base
    fg_hills = [
        (-60, HEIGHT),
        (-60, 495),
        (260, 465),
        (560, 505),
        (840, 470),
        (WIDTH + 60, 495),
        (WIDTH + 60, HEIGHT),
    ]
    pygame.draw.polygon(surf, (16, 27, 48), fg_hills)

    return surf


backdrop_surface = _build_playstore_backdrop()


def get_tier_name(level_num):
    if level_num <= 20:
        return "Moonlit Meadow"
    elif level_num <= 40:
        return "Spike Ridge"
    elif level_num <= 60:
        return "Sky Hopper"
    elif level_num <= 80:
        return "Castle Gauntlet"
    return "Shadow Master"


def update_and_draw_background(dt, pulse_t, player_x=0):
    # Smooth subtle camera pan so the world feels alive without visual noise
    shift_x = int((player_x - WIDTH // 2) * -0.03)
    screen.fill((16, 27, 48))
    screen.blit(backdrop_surface, (shift_x, 0))


def draw_heart(surface, x, y, filled=True):
    color = HEART_RED if filled else (71, 85, 105)
    pygame.draw.circle(surface, color, (x + 6, y + 6), 6)
    pygame.draw.circle(surface, color, (x + 16, y + 6), 6)
    pygame.draw.polygon(surface, color, [(x, y + 8), (x + 22, y + 8), (x + 11, y + 20)])


def draw_star(surface, cx, cy, outer_r, inner_r, filled=True):
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        px = cx + math.cos(angle) * r
        py = cy + math.sin(angle) * r
        points.append((px, py))

    if filled:
        pygame.draw.circle(surface, (120, 95, 15), (int(cx), int(cy)), outer_r + 7)
        pygame.draw.polygon(surface, GOLD, points)
        pygame.draw.polygon(surface, GOLD_SHINE, points, 2)
    else:
        pygame.draw.polygon(surface, (45, 58, 78), points)
        pygame.draw.polygon(surface, (90, 106, 128), points, 2)


def draw_hud(lives, coins, score, level_idx):
    lvl_num = min(level_idx + 1, TOTAL_LEVELS)
    tier = get_tier_name(lvl_num)

    for i in range(3):
        draw_heart(screen, 25 + i * 30, 20, filled=(i < lives))

    pygame.draw.circle(screen, GOLD, (36, 62), 11)
    pygame.draw.circle(screen, GOLD_SHINE, (36, 62), 7, 2)
    coin_txt = font_hud.render(f"COINS: {coins}", True, WHITE)
    screen.blit(coin_txt, (56, 51))

    score_txt = font_hud.render(f"SCORE: {score:05d} | LVL {lvl_num}/{TOTAL_LEVELS}", True, WHITE)
    screen.blit(score_txt, (WIDTH - score_txt.get_width() - 25, 20))

    tier_txt = font_hud.render(f"ZONE: {tier}", True, GOLD)
    screen.blit(tier_txt, (WIDTH - tier_txt.get_width() - 25, 48))


def load_level(level_idx):
    data = LEVELS[level_idx]
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    spikes = pygame.sprite.Group()

    for p in data["platforms"]:
        platforms.add(Platform(*p))
    for c in data["coins"]:
        coins.add(Coin(*c))
    for s in data["spikes"]:
        spikes.add(SpikeGroup(*s))

    flag = Flag(*data["flag"])
    spawn_x, spawn_y = data["spawn"]
    player = Player(spawn_x, spawn_y)
    return player, platforms, coins, spikes, flag


def _draw_key_pill(surface, cx, cy, label, accent=(251, 191, 36)):
    w = max(44, font_key.size(label)[0] + 18)
    h = 28
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    shadow = rect.move(0, 3)
    pygame.draw.rect(surface, (10, 15, 28), shadow, border_radius=7)
    pygame.draw.rect(surface, (51, 65, 85), rect, border_radius=7)
    pygame.draw.rect(surface, accent, rect, 2, border_radius=7)
    txt = font_key.render(label, True, WHITE)
    surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))


def draw_popup_card(
    title,
    subtitle="",
    cta_text="PRESS SPACE OR ENTER",
    stars_earned=None,
    show_controls=False,
    accent_color=(250, 204, 21),
    pulse_t=0.0,
):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 28, 175))
    screen.blit(overlay, (0, 0))

    card_w = 560
    card_h = 350 if stars_earned is not None else (315 if show_controls else 245)
    card = pygame.Rect(WIDTH // 2 - card_w // 2, HEIGHT // 2 - card_h // 2, card_w, card_h)

    pygame.draw.rect(screen, (5, 8, 18), card.move(0, 8), border_radius=24)
    pygame.draw.rect(screen, (23, 33, 56), card, border_radius=24)
    inner = card.inflate(-10, -10)
    pygame.draw.rect(screen, (33, 47, 77), inner, border_radius=20)
    pygame.draw.rect(screen, accent_color, card, 3, border_radius=24)

    header_h = 58
    header_rect = pygame.Rect(card.x + 12, card.y + 12, card_w - 24, header_h)
    pygame.draw.rect(screen, (15, 23, 42), header_rect, border_radius=15)
    pygame.draw.rect(screen, accent_color, header_rect, 2, border_radius=15)

    t_surf = font_title.render(title, True, accent_color)
    if t_surf.get_width() > header_rect.width - 24:
        scale = (header_rect.width - 24) / t_surf.get_width()
        t_surf = pygame.transform.smoothscale(
            t_surf, (int(t_surf.get_width() * scale), int(t_surf.get_height() * scale))
        )
    screen.blit(
        t_surf,
        (header_rect.centerx - t_surf.get_width() // 2, header_rect.centery - t_surf.get_height() // 2),
    )

    cursor_y = header_rect.bottom + 24

    if stars_earned is not None:
        for i in range(3):
            sx = card.centerx + (i - 1) * 92
            bob = math.sin(pulse_t * 4.5 + i * 0.9) * 4 if i < stars_earned else 0
            draw_star(screen, sx, cursor_y + 24 + bob, 27, 12, filled=(i < stars_earned))
        cursor_y += 66

    if subtitle:
        sub_surf = font_sub.render(subtitle, True, (226, 232, 240))
        screen.blit(sub_surf, (card.centerx - sub_surf.get_width() // 2, cursor_y))
        cursor_y += 42

    if show_controls:
        _draw_key_pill(screen, card.x + 95, cursor_y + 14, "A / D  or  ← →")
        lbl1 = font_key.render("Move", True, (186, 230, 253))
        screen.blit(lbl1, (card.x + 165, cursor_y + 5))

        _draw_key_pill(screen, card.x + 285, cursor_y + 14, "SPACE / ↑", accent=(52, 211, 153))
        lbl2 = font_key.render("Jump", True, (186, 230, 253))
        screen.blit(lbl2, (card.x + 340, cursor_y + 5))

        _draw_key_pill(screen, card.x + 445, cursor_y + 14, "P", accent=(148, 163, 184))
        lbl3 = font_key.render("Pause", True, (186, 230, 253))
        screen.blit(lbl3, (card.x + 468, cursor_y + 5))
        cursor_y += 48

    btn_w = 310
    btn_h = 44
    pulse_offset = int(math.sin(pulse_t * 5.0) * 2)
    btn_rect = pygame.Rect(card.centerx - btn_w // 2, card.bottom - 64 + pulse_offset, btn_w, btn_h)
    pygame.draw.rect(screen, (15, 118, 110), btn_rect.move(0, 3), border_radius=22)
    pygame.draw.rect(screen, (16, 185, 129), btn_rect, border_radius=22)
    pygame.draw.rect(screen, (167, 243, 208), btn_rect, 2, border_radius=22)

    btn_txt = font_btn.render(cta_text, True, WHITE)
    screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width() // 2, btn_rect.centery - btn_txt.get_height() // 2))


def main():
    game_state = "START"  # START, PLAYING, LEVEL_COMPLETE, PAUSED, GAMEOVER, VICTORY
    level_idx = 0
    lives = 3
    completed_stars = 0
    coins_collected = 0
    score = 0
    pulse_t = 0.0

    player, platforms, coins, spikes, flag = load_level(level_idx)

    while True:
        dt = clock.tick(FPS) / 1000.0
        pulse_t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_state == "START":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_state = "PLAYING"

                elif game_state == "PLAYING":
                    if event.key in (pygame.K_UP, pygame.K_SPACE, pygame.K_w):
                        player.queue_jump()
                    elif event.key == pygame.K_p:
                        game_state = "PAUSED"
                    elif event.key == pygame.K_n:
                        level_idx = (level_idx + 1) % TOTAL_LEVELS
                        lives = 3
                        player, platforms, coins, spikes, flag = load_level(level_idx)

                elif game_state == "LEVEL_COMPLETE":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        level_idx += 1
                        if level_idx < TOTAL_LEVELS:
                            lives = 3
                            player, platforms, coins, spikes, flag = load_level(level_idx)
                            game_state = "PLAYING"
                        else:
                            game_state = "VICTORY"

                elif game_state == "PAUSED":
                    if event.key == pygame.K_p:
                        game_state = "PLAYING"

                elif game_state in ("GAMEOVER", "VICTORY"):
                    if event.key == pygame.K_r or event.key == pygame.K_RETURN:
                        level_idx = 0
                        lives = 3
                        completed_stars = 0
                        coins_collected = 0
                        score = 0
                        player, platforms, coins, spikes, flag = load_level(level_idx)
                        game_state = "PLAYING"

            if event.type == pygame.KEYUP and game_state == "PLAYING":
                if event.key in (pygame.K_UP, pygame.K_SPACE, pygame.K_w):
                    player.cut_jump()

        update_and_draw_background(dt, pulse_t, player.rect.centerx)

        if game_state == "START":
            platforms.draw(screen)
            coins.draw(screen)
            screen.blit(flag.image, flag.rect)
            screen.blit(player.image, player.rect)
            draw_hud(lives, coins_collected, score, level_idx)
            draw_popup_card(
                title="MOONLIGHT QUEST",
                subtitle="100 Levels of Castle Adventure!",
                cta_text="▶  PLAY NOW (SPACE)",
                show_controls=True,
                accent_color=(250, 204, 21),
                pulse_t=pulse_t,
            )

        elif game_state == "PLAYING":
            did_jump = player.update(platforms)
            if did_jump:
                snd_jump.play()
            coins.update()

            hit_coins = pygame.sprite.spritecollide(player, coins, True)
            if hit_coins:
                snd_coin.play()
                coins_collected += len(hit_coins)
                score += len(hit_coins) * 100

            if player.invincible_timer == 0 and pygame.sprite.spritecollide(player, spikes, False):
                snd_hurt.play()
                lives -= 1
                player.invincible_timer = 75
                player.vel_y = -11
                if lives <= 0:
                    game_state = "GAMEOVER"

            if player.rect.top > HEIGHT:
                snd_hurt.play()
                lives -= 1
                if lives <= 0:
                    game_state = "GAMEOVER"
                else:
                    sx, sy = LEVELS[level_idx]["spawn"]
                    player.rect.topleft = (sx, sy)
                    player.vel_y = 0

            if player.rect.colliderect(flag.rect):
                snd_win.play()
                completed_stars = max(1, min(3, lives))
                score += 500 + (completed_stars * 100)
                game_state = "LEVEL_COMPLETE"

            platforms.draw(screen)
            coins.draw(screen)
            spikes.draw(screen)
            screen.blit(flag.image, flag.rect)
            player.draw_particles(screen)
            screen.blit(player.image, player.rect)
            draw_hud(lives, coins_collected, score, level_idx)

        elif game_state == "LEVEL_COMPLETE":
            platforms.draw(screen)
            coins.draw(screen)
            spikes.draw(screen)
            screen.blit(flag.image, flag.rect)
            screen.blit(player.image, player.rect)
            draw_hud(lives, coins_collected, score, level_idx)
            draw_popup_card(
                title="CONGRATULATIONS!",
                subtitle=f"Level {level_idx + 1} Cleared  •  Score: {score}",
                cta_text="NEXT LEVEL (SPACE)",
                stars_earned=completed_stars,
                accent_color=(250, 204, 21),
                pulse_t=pulse_t,
            )

        elif game_state == "PAUSED":
            platforms.draw(screen)
            coins.draw(screen)
            spikes.draw(screen)
            screen.blit(flag.image, flag.rect)
            screen.blit(player.image, player.rect)
            draw_hud(lives, coins_collected, score, level_idx)
            draw_popup_card(
                title="GAME PAUSED",
                subtitle="Take a quick breather!",
                cta_text="RESUME GAME (P)",
                accent_color=(56, 189, 248),
                pulse_t=pulse_t,
            )

        elif game_state == "GAMEOVER":
            draw_hud(0, coins_collected, score, level_idx)
            draw_popup_card(
                title="GAME OVER",
                subtitle=f"Reached Level {level_idx + 1}/{TOTAL_LEVELS}  •  Score: {score}",
                cta_text="PLAY AGAIN (R / ENTER)",
                accent_color=(248, 113, 113),
                pulse_t=pulse_t,
            )

        elif game_state == "VICTORY":
            draw_hud(lives, coins_collected, score, TOTAL_LEVELS - 1)
            draw_popup_card(
                title="CHAMPION OF 100 LEVELS!",
                subtitle=f"Total Score: {score}  •  Coins: {coins_collected}",
                cta_text="PLAY AGAIN (R / ENTER)",
                stars_earned=3,
                accent_color=(250, 204, 21),
                pulse_t=pulse_t,
            )

        pygame.display.flip()


if __name__ == "__main__":
    main()