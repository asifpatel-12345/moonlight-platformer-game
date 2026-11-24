# sprites.py
import pygame
import math
import random
from settings import *


class DustParticle:
    def __init__(self, x, y, vx, vy, radius=5, color=(226, 232, 240)):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.life = 18

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.radius = max(0.5, self.radius - 0.22)
        self.life -= 1

    def draw(self, surface):
        if self.life > 0 and self.radius > 0.5:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 38
        self.height = 52
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.invincible_timer = 0

        # Pro Platformer Jump Feel Timers (in frames @ 60 FPS)
        self.coyote_timer = 0        # ~0.10s grace after leaving a ledge
        self.jump_buffer_timer = 0   # ~0.12s early jump press buffer
        self.particles = []

        self.draw_character()

    def draw_character(self):
        self.image.fill((0, 0, 0, 0))
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        # Hair & Head
        pygame.draw.rect(self.image, HAIR_BROWN, (8, 2, 22, 10), border_radius=4)
        pygame.draw.rect(self.image, SKIN_COLOR, (9, 8, 20, 16), border_radius=4)

        # Eyes
        eye_x = 22 if self.facing_right else 12
        pygame.draw.circle(self.image, BLACK, (eye_x, 15), 2)

        # Red Hoodie Body
        pygame.draw.rect(self.image, RED_HOODIE, (7, 24, 24, 16), border_radius=5)
        pygame.draw.line(self.image, WHITE, (16, 25), (16, 32), 2)
        pygame.draw.line(self.image, WHITE, (21, 25), (21, 32), 2)

        # Blue Pants & Shoes
        if not self.on_ground:
            pygame.draw.rect(self.image, PANTS_BLUE, (8, 40, 9, 8), border_radius=2)
            pygame.draw.rect(self.image, PANTS_BLUE, (21, 38, 9, 8), border_radius=2)
        else:
            pygame.draw.rect(self.image, PANTS_BLUE, (10, 40, 7, 10))
            pygame.draw.rect(self.image, PANTS_BLUE, (21, 40, 7, 10))

        # White Sneakers
        pygame.draw.rect(self.image, WHITE, (9, 48, 9, 4))
        pygame.draw.rect(self.image, WHITE, (20, 48, 9, 4))

    def spawn_jump_dust(self):
        for _ in range(7):
            vx = random.uniform(-2.4, 2.4)
            vy = random.uniform(-1.8, -0.3)
            self.particles.append(DustParticle(self.rect.centerx, self.rect.bottom - 2, vx, vy))

    def queue_jump(self):
        # Store jump request for 7 frames (~116ms) for instant response
        self.jump_buffer_timer = 7

    def cut_jump(self):
        # Variable jump height: releasing jump early trims upward velocity
        if self.vel_y < -6:
            self.vel_y *= 0.52

    def update(self, platforms):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True

        # Horizontal Movement & Collision
        self.rect.x += self.vel_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right

        # Snappy Gravity (faster when falling)
        current_gravity = FALL_GRAVITY if self.vel_y > 0 else GRAVITY
        self.vel_y += current_gravity
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.rect.y += self.vel_y
        was_on_ground = self.on_ground
        self.on_ground = False

        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

        # Coyote Time tracking
        if self.on_ground:
            self.coyote_timer = 6
            if not was_on_ground:
                self.spawn_jump_dust()
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        # Execute buffered jump if grounded or within coyote window
        jumped = False
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.coyote_timer = 0
            self.jump_buffer_timer = 0
            self.spawn_jump_dust()
            jumped = True

        # Update dust particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        self.draw_character()
        return jumped

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h + 15), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, w, h)

        points = [(6, 12), (w - 6, 12), (w - 22, h + 10), (w // 2, h + 15), (22, h + 10)]
        pygame.draw.polygon(self.image, DIRT_BROWN, points)
        pygame.draw.polygon(self.image, DIRT_DARK, points, 3)

        pygame.draw.rect(self.image, GRASS_GREEN, (0, 0, w, 16), border_radius=8)
        pygame.draw.rect(self.image, GRASS_DARK, (0, 11, w, 5), border_radius=4)

        for gx in range(10, w - 10, 18):
            pygame.draw.polygon(self.image, GRASS_GREEN, [(gx, 14), (gx + 5, 22), (gx + 10, 14)])


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_y = y
        self.angle = 0
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.angle += 0.1
        width_scale = max(4, int(abs(math.cos(self.angle)) * 24))
        self.image.fill((0, 0, 0, 0))
        self.rect.centery = self.base_y + math.sin(self.angle) * 4

        coin_rect = pygame.Rect(14 - width_scale // 2, 2, width_scale, 24)
        pygame.draw.ellipse(self.image, GOLD, coin_rect)
        pygame.draw.ellipse(self.image, (200, 150, 0), coin_rect, 2)
        if width_scale > 10:
            inner_rect = pygame.Rect(14 - (width_scale - 6) // 2, 6, width_scale - 6, 16)
            pygame.draw.ellipse(self.image, GOLD_SHINE, inner_rect, 1)


class SpikeGroup(pygame.sprite.Sprite):
    def __init__(self, x, y, count):
        super().__init__()
        spike_w = 20
        spike_h = 25
        total_w = count * spike_w
        self.image = pygame.Surface((total_w, spike_h), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, total_w, spike_h)

        for i in range(count):
            sx = i * spike_w
            pts = [(sx, spike_h), (sx + spike_w // 2, 0), (sx + spike_w, spike_h)]
            pygame.draw.polygon(self.image, SPIKE_GRAY, pts)
            pygame.draw.polygon(self.image, (100, 116, 139), pts, 2)


class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((45, 70), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, 45, 70)

        pygame.draw.rect(self.image, (226, 232, 240), (4, 5, 5, 65), border_radius=2)
        pygame.draw.circle(self.image, GOLD, (6, 5), 5)
        pygame.draw.polygon(self.image, RED_HOODIE, [(9, 10), (42, 22), (9, 34)])