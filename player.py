from settings import *
import pygame as pg
import math

class Player:
    def __init__(self, game, pos, angle):
        self.game = game
        self.x, self.y = pos
        self.angle = angle
        self.color = 'green'
        self.diag_move_corr = 1 / math.sqrt(2)
        self.shot = False
        self.did_shot = False
        self.health = 0
        self.alive = True
        self.rel = 0
        self.base_speed = PLAYER_SPEED
        self.current_speed = PLAYER_SPEED
        self.speed_boost_end_time = 0
        self.speed_boost_duration = 5000  # 5 seconds in milliseconds
        self.rockets = 0
        self.using_rocket = False

    def update(self):
        if self.alive:
            self.movement()
            self.mouse_control()
            self.update_speed_boost()
        else:
            self.shot = False
            self.did_shot = False

    def single_fire_event(self, event):
        if not self.alive or not self.game.started or self.game.enemy_disconnected:
            return
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.turret.reloading:
                self.shot = True
                self.did_shot = True
                self.using_rocket = (self.rockets > 0)

                if self.using_rocket:
                    self.game.sounds.rocket_sound.play()
                    self.rockets -= 1
                else:
                    self.game.sounds.shoot_sound.play()

                self.game.turret.reloading = True

    def update_speed_boost(self):
        current_time = pg.time.get_ticks()
        if current_time > self.speed_boost_end_time:
            self.current_speed = self.base_speed
        else:
            # Optional: Add visual feedback for speed boost
            pass

    def apply_speed_boost(self):
        self.current_speed = self.base_speed + 0.002  # Add speed boost
        self.speed_boost_end_time = pg.time.get_ticks() + self.speed_boost_duration
        print(f"Speed boost activated! New speed: {self.current_speed}")

    def movement(self):
        if not self.game.started or self.game.enemy_disconnected:
            return
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = self.current_speed * self.game.delta_time  # Use current_speed instead of constant
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()
        num_key_pressed = -1
        if keys[pg.K_w]:
            num_key_pressed += 1
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            num_key_pressed += 1
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            num_key_pressed += 1
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            num_key_pressed += 1
            dx += -speed_sin
            dy += speed_cos

        if num_key_pressed:
            dx *= self.diag_move_corr
            dy *= self.diag_move_corr

        self.check_wall_collision(dx, dy)

        self.angle %= math.tau

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def draw(self):
        # pg.draw.line(self.game.screen, 'yellow' if self.color == 'green' else 'orange', (self.x * 100, self.y * 100), (self.x * 100 + WIDTH * math.cos(self.angle), self.y * 100 + WIDTH * math.sin(self.angle)), 2)
        pg.draw.circle(self.game.screen, self.color, (self.x * 100, self.y * 100), 15)

    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)