import math
import os
import random
from pathlib import Path

import pygame

WIDTH, HEIGHT = 900, 600
FPS = 60

STAR_LAYERS = [
    {"count": 70, "speed": 38, "size": (1.0, 2.2), "alpha": 120},
    {"count": 55, "speed": 72, "size": (1.8, 3.2), "alpha": 180},
    {"count": 40, "speed": 135, "size": (2.4, 4.2), "alpha": 255},
]


class StarField:
    def __init__(self):
        self.stars = []
        for layer_index, layer in enumerate(STAR_LAYERS):
            for _ in range(layer["count"]):
                star = {
                    "pos": pygame.Vector2(
                        random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
                    ),
                    "speed": layer["speed"],
                    "size": random.uniform(*layer["size"]),
                    "alpha": layer["alpha"],
                    "layer": layer_index,
                }
                self.stars.append(star)

    def update(self, dt, speed_multiplier=1.0):
        for star in self.stars:
            star["pos"].y += star["speed"] * dt * speed_multiplier
            if star["pos"].y > HEIGHT:
                star["pos"].x = random.uniform(0, WIDTH)
                star["pos"].y -= HEIGHT + random.uniform(10, 60)

    def draw(self, surface):
        for star in self.stars:
            radius = star["size"]
            color = (
                min(255, 170 + star["layer"] * 38),
                min(255, 190 + star["layer"] * 30),
                255,
            )
            star_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(
                star_surf,
                (*color, star["alpha"]),
                (radius * 2, radius * 2),
                int(radius),
            )
            surface.blit(
                star_surf, star["pos"] - pygame.Vector2(radius * 2, radius * 2)
            )


class GlowOverlay:
    def __init__(self, size):
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        gradient_color = (40, 60, 110, 140)
        for y in range(size[1]):
            alpha = int(gradient_color[3] * (y / size[1]))
            pygame.draw.rect(
                self.surface,
                gradient_color[:3] + (alpha,),
                pygame.Rect(0, y, size[0], 1),
            )

    def draw(self, surface):
        surface.blit(self.surface, (0, 0), special_flags=pygame.BLEND_ADD)


class Laser(pygame.sprite.Sprite):
    def __init__(self, position, velocity, color=(90, 255, 150)):
        super().__init__()
        self.image = pygame.Surface((6, 26), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, pygame.Rect(2, 2, 2, 22))
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, 6, 26), 2)
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.damage = 1

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position
        if self.rect.bottom < -40 or self.rect.top > HEIGHT + 40:
            self.kill()


class ThrusterParticle(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((14, 24), pygame.SRCALPHA)
        core_color = random.choice(
            [
                (255, 200, 90, 210),
                (140, 220, 255, 220),
                (255, 120, 120, 200),
            ]
        )
        pygame.draw.ellipse(
            self.image,
            core_color,
            pygame.Rect(2, 2, 10, 20),
        )
        pygame.draw.ellipse(
            self.image,
            (50, 90, 160, 120),
            pygame.Rect(0, 0, 14, 24),
            2,
        )
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(
            random.uniform(-45, 45), random.uniform(180, 260)
        )
        self.life = random.uniform(0.32, 0.52)
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt
        self.position += self.velocity * dt
        self.rect = self.image.get_rect(center=self.position)
        fade = max(0.0, 1.0 - self.timer / self.life)
        self.image.set_alpha(int(255 * fade))
        if self.timer >= self.life:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.frames = []
        for radius in range(14, 70, 10):
            frame = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                frame,
                (255, 160, 40, 220),
                (radius, radius),
                radius,
            )
            pygame.draw.circle(
                frame,
                (255, 240, 180, 140),
                (radius, radius),
                int(radius * 0.65),
            )
            pygame.draw.circle(
                frame,
                (255, 255, 240, 90),
                (radius, radius),
                int(radius * 0.35),
            )
            self.frames.append(frame)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=position)
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt * 18
        if self.timer >= 1:
            self.timer = 0
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.frames[self.index]
                self.rect = self.image.get_rect(center=center)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, explosion_group, difficulty=1.0):
        super().__init__()
        scale = random.uniform(0.7, 1.15)
        width, height = int(74 * scale), int(64 * scale)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self._draw_tie_fighter(self.image)
        spawn_x = random.uniform(60, WIDTH - 60)
        self.rect = self.image.get_rect(midtop=(spawn_x, -height))
        self.position = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(
            random.uniform(-35, 35), random.uniform(140, 200) * difficulty
        )
        self.explosions = explosion_group
        self.health = 2 + int(difficulty * 0.6)
        self.radius = width * 0.42
        self.zigzag_phase = random.uniform(0, math.tau)
        self.zigzag_speed = random.uniform(1.4, 2.2)
        self.zigzag_amplitude = random.uniform(60, 110)

    @staticmethod
    def _draw_tie_fighter(surface):
        w, h = surface.get_size()
        wing_color = (90, 120, 140)
        wing_dark = (40, 60, 90)
        core_color = (220, 220, 240)
        pygame.draw.rect(surface, wing_color, pygame.Rect(0, 0, int(w * 0.28), h), border_radius=6)
        pygame.draw.rect(surface, wing_color, pygame.Rect(w - int(w * 0.28), 0, int(w * 0.28), h), border_radius=6)
        pygame.draw.rect(surface, wing_dark, pygame.Rect(int(w * 0.04), int(h * 0.06), int(w * 0.2), int(h * 0.88)), width=2, border_radius=6)
        pygame.draw.rect(surface, wing_dark, pygame.Rect(w - int(w * 0.24), int(h * 0.06), int(w * 0.2), int(h * 0.88)), width=2, border_radius=6)
        pygame.draw.circle(surface, core_color, (w // 2, h // 2), int(h * 0.28))
        pygame.draw.circle(surface, (40, 40, 60), (w // 2, h // 2), int(h * 0.18))
        for offset in (-1, 1):
            pygame.draw.line(
                surface,
                core_color,
                (w // 2, h // 2),
                (w // 2 + offset * int(w * 0.35), h // 2),
                4,
            )

    def update(self, dt):
        self.zigzag_phase += self.zigzag_speed * dt
        sway = math.sin(self.zigzag_phase) * self.zigzag_amplitude * dt
        self.position.x += self.velocity.x * dt + sway
        self.position.y += self.velocity.y * dt
        self.rect.center = (self.position.x, self.position.y)
        if self.rect.top > HEIGHT + 80 or self.rect.right < -120 or self.rect.left > WIDTH + 120:
            self.kill()

    def hit(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            self.explosions.add(Explosion(self.rect.center))
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, laser_group, trail_group):
        super().__init__()
        self.lasers = laser_group
        self.trails = trail_group
        self.base_image = self._create_image()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 110))
        self.position = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2()
        self.acceleration = 650
        self.max_speed = 460
        self.drag = 4.2
        self.shoot_cooldown = 0.15
        self._shoot_timer = 0.0
        self.radius = 28
        self.shield = 3
        self.invulnerable_timer = 0.0
        self.roll_amount = 0.0
        self.roll_target = 0.0
        self.trail_timer = 0.0

    @staticmethod
    def _create_image():
        surf = pygame.Surface((84, 90), pygame.SRCALPHA)
        body_color = (220, 220, 230)
        accent = (255, 70, 60)
        glow = (130, 210, 255, 160)
        pygame.draw.polygon(
            surf,
            body_color,
            [(42, 4), (64, 30), (52, 82), (32, 82), (20, 30)],
        )
        pygame.draw.polygon(
            surf,
            (35, 35, 60),
            [(42, 10), (56, 34), (48, 68), (36, 68), (28, 34)],
        )
        pygame.draw.rect(surf, accent, pygame.Rect(34, 30, 6, 18))
        pygame.draw.rect(surf, accent, pygame.Rect(44, 30, 6, 18))
        for wing_offset in (-30, 30):
            pygame.draw.polygon(
                surf,
                body_color,
                [
                    (42 + wing_offset, 40),
                    (42 + int(wing_offset * 1.1), 64),
                    (42 + wing_offset, 84),
                    (42, 66),
                ],
                width=3,
            )
        pygame.draw.circle(surf, glow, (42, 18), 10)
        return surf

    def reset(self):
        self.position.update(WIDTH // 2, HEIGHT - 110)
        self.velocity.update(0, 0)
        self.rect.center = self.position
        self.shield = 3
        self.invulnerable_timer = 0.0
        self._shoot_timer = 0.0
        self.roll_amount = 0.0
        self.roll_target = 0.0
        self.trail_timer = 0.0

    def update(self, dt, keys):
        move = pygame.Vector2()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move.y += 1
        if move.length_squared() > 0:
            move = move.normalize()
            self.velocity += move * self.acceleration * dt
        else:
            self.velocity -= self.velocity * self.drag * dt

        if self.velocity.length_squared() > self.max_speed**2:
            self.velocity.scale_to_length(self.max_speed)

        self.position += self.velocity * dt
        self.position.x = max(48, min(WIDTH - 48, self.position.x))
        self.position.y = max(80, min(HEIGHT - 40, self.position.y))
        self.rect.center = self.position

        self.roll_target = -self.velocity.x / max(1, self.max_speed) * 18
        self.roll_amount += (self.roll_target - self.roll_amount) * min(1.0, dt * 8.5)
        rotated = pygame.transform.rotozoom(self.base_image, self.roll_amount, 1.0)
        prev_center = self.rect.center
        self.image = rotated
        self.rect = self.image.get_rect(center=prev_center)

        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
            flicker = (math.sin(self.invulnerable_timer * 22) + 1) / 2
            self.image.set_alpha(int(140 + flicker * 100))
        else:
            self.image.set_alpha(255)

        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        if keys[pygame.K_SPACE] or keys[pygame.K_LCTRL]:
            self.try_shoot()

        self.trail_timer += dt
        if self.trail_timer >= 0.035:
            self.trail_timer = 0.0
            thruster_offset = pygame.Vector2(0, 46)
            jitter = pygame.Vector2(random.uniform(-12, 12), random.uniform(-6, 6))
            spawn_point = self.position + thruster_offset + jitter
            self.trails.add(ThrusterParticle(spawn_point))

    def try_shoot(self):
        if self._shoot_timer > 0:
            return
        self._shoot_timer = self.shoot_cooldown
        offsets = [pygame.Vector2(-18, -30), pygame.Vector2(18, -30)]
        for offset in offsets:
            spread = pygame.Vector2(random.uniform(-20, 20), random.uniform(-10, 10))
            direction = pygame.Vector2(0, -780) + spread
            laser = Laser(self.rect.center + offset, direction)
            self.lasers.add(laser)

    def absorb_hit(self):
        if self.invulnerable_timer > 0:
            return True
        self.shield -= 1
        self.invulnerable_timer = 1.4
        self.velocity += pygame.Vector2(random.uniform(-220, 220), 260)
        return self.shield > 0


def draw_hud(surface, font, big_font, score, player, game_over=False):
    score_surf = font.render(f"Score  {int(score):07d}", True, (220, 235, 255))
    surface.blit(score_surf, (20, 18))

    shield_label = font.render("Shields", True, (120, 190, 255))
    surface.blit(shield_label, (20, 48))
    for i in range(3):
        color = (110, 200, 255) if i < max(player.shield, 0) else (30, 50, 90)
        pygame.draw.circle(surface, color, (24 + i * 26, 80), 10)
        pygame.draw.circle(surface, (12, 20, 40), (24 + i * 26, 80), 10, 2)

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 30, 130))
        surface.blit(overlay, (0, 0))
        title = big_font.render("MISSION FAILED", True, (255, 120, 120))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        tip = font.render("Press SPACE to fly again", True, (200, 220, 255))
        surface.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    pygame.display.set_caption("Star Wars: Rogue Run")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 22)
    big_font = pygame.font.SysFont("consolas", 54)

    starfield = StarField()
    glow = GlowOverlay((WIDTH, HEIGHT))

    lasers = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    trails = pygame.sprite.Group()
    player = Player(lasers, trails)
    player_group = pygame.sprite.GroupSingle(player)

    score = 0.0
    spawn_timer = 0.0
    game_over = False
    game_over_time = 0.0

    def reset_game_state():
        nonlocal score, spawn_timer, game_over, game_over_time
        lasers.empty()
        enemies.empty()
        explosions.empty()
        trails.empty()
        player.reset()
        score = 0.0
        spawn_timer = 0.0
        game_over = False
        game_over_time = 0.0

    running = True
    elapsed = 0.0
    auto_quit = 0.0
    try:
        auto_quit = float(os.getenv('STARWARS_AUTOQUIT', '0') or 0.0)
    except ValueError:
        auto_quit = 0.0

    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif game_over and event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                reset_game_state()

        keys = pygame.key.get_pressed()

        if auto_quit > 0 and elapsed >= auto_quit:
            running = False
            continue
        if not game_over:
            score += dt * 14
            starfield.update(dt)
            player_group.update(dt, keys)
            lasers.update(dt)
            trails.update(dt)
            enemies.update(dt)
            spawn_timer += dt
            spawn_interval = max(0.38, 1.1 - score / 2400)
            difficulty = 1.0 + score / 780
            if spawn_timer >= spawn_interval:
                spawn_timer = 0.0
                enemies.add(Enemy(explosions, difficulty=difficulty))

            collisions = pygame.sprite.groupcollide(enemies, lasers, False, True)
            for enemy, hits in collisions.items():
                destroyed = False
                for _ in hits:
                    prev_health = enemy.health
                    enemy.hit()
                    if not enemy.alive() and prev_health > 0:
                        score += 120
                        destroyed = True
                        break
                if not destroyed:
                    score += 18

            if player.invulnerable_timer <= 0:
                impacts = pygame.sprite.spritecollide(
                    player, enemies, True, pygame.sprite.collide_circle
                )
                if impacts:
                    for enemy in impacts:
                        explosions.add(Explosion(enemy.rect.center))
                    explosions.add(Explosion(player.rect.center))
                    if not player.absorb_hit():
                        game_over = True
                        game_over_time = 0.0
            else:
                pygame.sprite.spritecollide(
                    player, enemies, True, pygame.sprite.collide_circle
                )
        else:
            starfield.update(dt * 0.5)
            lasers.update(dt)
            trails.update(dt)
            game_over_time += dt

        explosions.update(dt)

        screen.fill((6, 8, 24))
        starfield.draw(screen)
        lasers.draw(screen)
        trails.draw(screen)
        enemies.draw(screen)
        player_group.draw(screen)
        explosions.draw(screen)
        glow.draw(screen)
        draw_hud(screen, font, big_font, score, player, game_over)

        hint = font.render("Arrows / WASD to move, Space to fire", True, (140, 200, 255))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 28)))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()


