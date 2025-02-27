import pygame
import math
import random
import time

pygame.init()
pygame.font.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("AsteroidGame")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

font_large = pygame.font.SysFont('Arial', 40)
font_medium = pygame.font.SysFont('Arial', 24)
font_small = pygame.font.SysFont('Arial', 16)

clock = pygame.time.Clock()

pygame.mixer.init()

try:
    shoot_sound = pygame.mixer.Sound('shoot.wav')
    explosion_sound = pygame.mixer.Sound('explosion.wav')
    thrust_sound = pygame.mixer.Sound.play
    level_up_sound = pygame.mixer.Sound.play
except:
    print("ERROR: Sound files are missing!")
    shoot_sound = pygame.mixer.Sound.play
    explosion_sound = pygame.mixer.Sound.play
    thrust_sound = pygame.mixer.Sound.play
    level_up_sound = pygame.mixer.Sound.play

stars = [(random.randint(0, screen_width), random.randint(0, screen_height), random.random())
         for _ in range(100)]

SMALL = 1
MEDIUM = 2
LARGE = 3

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(1, 3)
        self.lifetime = random.randint(20, 40)
        speed = random.uniform(0.5, 2.0)
        angle = random.uniform(0, 2 * math.pi)
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class Powerup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.type = random.choice(['shield', 'triple_shot', 'rapid_fire'])
        self.color = {
            'shield': (0, 191, 255),      # Deep sky blue
            'triple_shot': (255, 105, 180), # Hot pink
            'rapid_fire': (255, 215, 0)     # Gold
        }[self.type]
        self.lifetime = 600  # 10 seconds at 60 FPS

    def update(self):
        self.lifetime -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        if self.type == 'shield':
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 8, 2)
        elif self.type == 'triple_shot':
            pygame.draw.line(screen, WHITE, (self.x-5, self.y), (self.x+5, self.y), 2)
            pygame.draw.line(screen, WHITE, (self.x-5, self.y-5), (self.x+5, self.y+5), 2)
            pygame.draw.line(screen, WHITE, (self.x-5, self.y+5), (self.x+5, self.y-5), 2)
        elif self.type == 'rapid_fire':
            pygame.draw.line(screen, WHITE, (self.x-5, self.y), (self.x+5, self.y), 2)
            pygame.draw.line(screen, WHITE, (self.x, self.y-5), (self.x, self.y+5), 2)

class Asteroid:
    def __init__(self, size, x, y):
        self.size = size
        self.x = x
        self.y = y

        if size == SMALL:
            self.radius = 20
            self.hp = 1
            self.color = (0, 0, random.randint(200, 255))  # Shades of blue
            self.score_value = 100
            speed = random.uniform(3, 5)
        elif size == MEDIUM:
            self.radius = 40
            self.hp = 2
            self.color = (0, random.randint(200, 255), 0)  # Shades of green
            self.score_value = 50
            speed = random.uniform(2, 4)
        elif size == LARGE:
            self.radius = 60
            self.hp = 3
            self.color = (random.randint(200, 255), 0, 0)  # Shades of red
            self.score_value = 20
            speed = random.uniform(1, 3)

        angle = random.uniform(0, 2 * math.pi)
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)

        num_sides = random.randint(6, 10)
        self.points = []
        for i in range(num_sides):
            angle = 2 * math.pi * i / num_sides
            r = self.radius + random.uniform(-self.radius * 0.3, self.radius * 0.3)
            px = r * math.cos(angle)
            py = r * math.sin(angle)
            self.points.append((px, py))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rotation += self.rotation_speed

        if self.x < -self.radius:
            self.x = screen_width + self.radius
        elif self.x > screen_width + self.radius:
            self.x = -self.radius
        if self.y < -self.radius:
            self.y = screen_height + self.radius
        elif self.y > screen_height + self.radius:
            self.y = -self.radius

    def draw(self, screen):
        rot_rad = math.radians(self.rotation)
        translated_points = []
        for px, py in self.points:
            rx = px * math.cos(rot_rad) - py * math.sin(rot_rad)
            ry = px * math.sin(rot_rad) + py * math.cos(rot_rad)
            translated_points.append((self.x + rx, self.y + ry))

        pygame.draw.polygon(screen, self.color, translated_points)

        inner_color = [(255, 0, 0), (255, 255, 0), (0, 255, 0)][self.hp-1]
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), int(self.radius / 4))

class Spaceship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.dx = 0
        self.dy = 0
        self.max_speed = 5
        self.points = [(-10, -10), (20, 0), (-10, 10), (0, 0)]
        self.lives = 3
        self.shield = 0
        self.shield_strength = 100
        self.respawn_timer = 0
        self.invulnerable_timer = 0
        self.fire_cooldown = 0
        self.rapid_fire = 0
        self.triple_shot = 0
        self.thrust_particles = []

    def update(self):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            return

        if left_pressed:
            self.angle -= 5
        if right_pressed:
            self.angle += 5
        if up_pressed:
            rad = math.radians(self.angle)
            self.dx += 0.2 * math.cos(rad)
            self.dy += 0.2 * math.sin(rad)

            if random.random() < 0.3:
                thrust_rad = math.radians(self.angle + 180)
                offset_x = -10 * math.cos(rad)
                offset_y = -10 * math.sin(rad)
                color = random.choice([YELLOW, RED])
                self.thrust_particles.append(
                    Particle(self.x + offset_x, self.y + offset_y, color)
                )

        self.dx *= 0.98
        self.dy *= 0.98

        speed = math.hypot(self.dx, self.dy)
        if speed > self.max_speed:
            self.dx = self.dx / speed * self.max_speed
            self.dy = self.dy / speed * self.max_speed

        self.x += self.dx
        self.y += self.dy

        if self.x < 0:
            self.x = screen_width
        elif self.x > screen_width:
            self.x = 0
        if self.y < 0:
            self.y = screen_height
        elif self.y > screen_height:
            self.y = 0

        self.angle %= 360
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        if self.shield > 0:
            self.shield -= 1
        if self.rapid_fire > 0:
            self.rapid_fire -= 1
        if self.triple_shot > 0:
            self.triple_shot -= 1

        for particle in self.thrust_particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.thrust_particles.remove(particle)

    def draw(self, screen):
        if self.respawn_timer > 0:
            return

        if up_pressed:
            rad = math.radians(self.angle)
            thruster_points = []
            for i in range(3):
                angle = self.angle + 180 + random.randint(-20, 20)
                length = random.randint(10, 20)
                rad_p = math.radians(angle)
                tx = -15 * math.cos(rad) - length * math.cos(rad_p)
                ty = -15 * math.sin(rad) - length * math.sin(rad_p)
                thruster_points.append((self.x + tx, self.y + ty))
            pygame.draw.polygon(screen, YELLOW, thruster_points)

        for particle in self.thrust_particles:
            particle.draw(screen)

        rad = math.radians(self.angle)
        rotated_points = []
        for px, py in self.points:
            rx = px * math.cos(rad) - py * math.sin(rad)
            ry = px * math.sin(rad) + py * math.cos(rad)
            rotated_points.append((self.x + rx, self.y + ry))

        if self.invulnerable_timer > 0 and self.invulnerable_timer % 10 >= 5:
            pass
        else:
            pygame.draw.polygon(screen, WHITE, rotated_points)

        if self.shield > 0:
            shield_intensity = min(255, int(255 * self.shield_strength / 100))
            shield_color = (0, shield_intensity, 255)
            pygame.draw.circle(screen, shield_color, (int(self.x), int(self.y)), 25, 2)

        power_y = self.y - 30
        if self.rapid_fire > 0:
            txt = font_small.render("RF", True, YELLOW)
            screen.blit(txt, (self.x - 20, power_y))
        if self.triple_shot > 0:
            txt = font_small.render("TS", True, (255, 105, 180))
            screen.blit(txt, (self.x + 5, power_y))

    def fire(self, bullets):
        if self.respawn_timer > 0:
            return

        if self.fire_cooldown <= 0:
            rad = math.radians(self.angle)
            tip_x = self.x + 20 * math.cos(rad)
            tip_y = self.y + 20 * math.sin(rad)

            if self.triple_shot > 0:
                bullets.append(Bullet(tip_x, tip_y, self.angle))
                bullets.append(Bullet(tip_x, tip_y, self.angle - 15))
                bullets.append(Bullet(tip_x, tip_y, self.angle + 15))
            else:
                bullets.append(Bullet(tip_x, tip_y, self.angle))

            if self.rapid_fire > 0:
                self.fire_cooldown = 5
            else:
                self.fire_cooldown = 15

            try:
                pygame.mixer.Sound.play(shoot_sound)
            except:
                pass

    def hit(self):
        if self.respawn_timer > 0 or self.invulnerable_timer > 0:
            return False

        if self.shield > 0:
            self.shield_strength -= 0
            if self.shield_strength <= 0:
                self.shield = 0
            return False

        self.lives -= 1
        if self.lives > 0:
            self.respawn_timer = 120  # 2 seconds
            self.invulnerable_timer = 180  # 3 seconds of invulnerability after respawn
        return True

    def respawn(self):
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.dx = 0
        self.dy = 0
        self.angle = 0

    def activate_powerup(self, powerup_type):
        if powerup_type == 'shield':
            self.shield = 600  # 10 seconds
            self.shield_strength = 100
        elif powerup_type == 'triple_shot':
            self.triple_shot = 300  # 5 seconds
        elif powerup_type == 'rapid_fire':
            self.rapid_fire = 300  # 5 seconds

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        speed = 10
        rad = math.radians(angle)
        self.dx = speed * math.cos(rad)
        self.dy = speed * math.sin(rad)
        self.lifetime = 60  # Disappears after 60 frames
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        
        if self.x < 0:
            self.x = screen_width
        elif self.x > screen_width:
            self.x = 0
        if self.y < 0:
            self.y = screen_height
        elif self.y > screen_height:
            self.y = 0

    def draw(self, screen):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * i / len(self.trail))
            radius = 1 + i / 2
            trail_color = (alpha, alpha, 255)
            pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), int(radius))

        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 2)

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.spaceship = Spaceship(screen_width // 2, screen_height // 2)
        self.asteroids = []
        self.bullets = []
        self.particles = []
        self.powerups = []
        self.score = 0
        self.level = 1
        self.state = "start"
        self.level_timer = 0
        self.message = ""
        self.message_timer = 0

    def start_level(self):
        self.asteroids = []
        for _ in range(2 + self.level):
            x = random.choice([random.randint(0, 100), random.randint(700, 800)])
            y = random.choice([random.randint(0, 100), random.randint(500, 600)])
            self.asteroids.append(Asteroid(LARGE, x, y))
        for _ in range(self.level):
            x = random.choice([random.randint(0, 100), random.randint(700, 800)])
            y = random.choice([random.randint(0, 100), random.randint(500, 600)])
            self.asteroids.append(Asteroid(MEDIUM, x, y))
        self.state = "playing"

    def show_message(self, text, duration=120):
        self.message = text
        self.message_timer = duration

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1

        if self.state == "start":
            pass
        elif self.state == "level_complete":
            self.level_timer -= 1
            if self.level_timer <= 0:
                self.level += 1
                self.start_level()
                self.show_message(f"Level {self.level}")
                if game.spaceship.lives <= 996:
                    game.spaceship.lives += 3
                try:
                    pygame.mixer.Sound.play(level_up_sound)
                except:
                    pass
        elif self.state == "game_over":
            pass
        elif self.state == "playing":
            if self.spaceship.respawn_timer <= 0:
                self.spaceship.update()

                if len(self.asteroids) == 0:
                    self.state = "level_complete"
                    self.level_timer = 120  # 2 seconds
                    self.show_message("Level Complete!")
            else:
                self.spaceship.respawn_timer -= 1
                if self.spaceship.respawn_timer == 0:
                    self.spaceship.respawn()

            for asteroid in self.asteroids:
                asteroid.update()

            for bullet in self.bullets[:]:
                bullet.update()
                if bullet.lifetime <= 0:
                    self.bullets.remove(bullet)

            for particle in self.particles[:]:
                particle.update()
                if particle.lifetime <= 0:
                    self.particles.remove(particle)

            for powerup in self.powerups[:]:
                powerup.update()
                if powerup.lifetime <= 0:
                    self.powerups.remove(powerup)

            self.check_collisions()

            if len(self.powerups) < 1 and random.random() < 0.001:
                self.powerups.append(
                    Powerup(random.randint(50, screen_width-50),
                           random.randint(50, screen_height-50))
                )

    def check_collisions(self):
        asteroids_to_add = []

        for bullet in self.bullets[:]:
            hit = False
            for asteroid in self.asteroids[:]:
                dist = math.hypot(bullet.x - asteroid.x, bullet.y - asteroid.y)
                if dist < asteroid.radius:

                    for _ in range(10):
                        self.particles.append(
                            Particle(asteroid.x, asteroid.y, asteroid.color)
                        )

                    asteroid.hp -= 1
                    self.score += 10
                    hit = True

                    if asteroid.hp <= 0:
                        self.score += asteroid.score_value
                        try:
                            pygame.mixer.Sound.play(explosion_sound)
                        except:
                            pass

                        if asteroid.size == LARGE:
                            for _ in range(2):
                                asteroids_to_add.append(
                                    Asteroid(MEDIUM, asteroid.x, asteroid.y)
                                )
                        elif asteroid.size == MEDIUM:
                            for _ in range(2):
                                asteroids_to_add.append(
                                    Asteroid(SMALL, asteroid.x, asteroid.y)
                                )

                        for _ in range(20):
                            self.particles.append(
                                Particle(asteroid.x, asteroid.y, asteroid.color)
                            )
                        
                        if random.random() < 0.2:
                            self.powerups.append(
                                Powerup(asteroid.x, asteroid.y)
                            )

                        self.asteroids.remove(asteroid)
                    break

            if hit and bullet in self.bullets:
                self.bullets.remove(bullet)

        self.asteroids.extend(asteroids_to_add)

        if self.spaceship.respawn_timer <= 0:
            for asteroid in self.asteroids:
                dist = math.hypot(self.spaceship.x - asteroid.x,
                                 self.spaceship.y - asteroid.y)
                if dist < asteroid.radius + 15:
                    if self.spaceship.hit():

                        for _ in range(30):
                            color = random.choice([WHITE, YELLOW, RED])
                            self.particles.append(
                                Particle(self.spaceship.x, self.spaceship.y, color)
                            )
                        try:
                            explosion_sound()
                        except:
                            pass

                        if self.spaceship.lives <= 0:
                            self.state = "game_over"
                            self.show_message("Game Over", 300)
                    break

        for powerup in self.powerups[:]:
            dist = math.hypot(self.spaceship.x - powerup.x,
                             self.spaceship.y - powerup.y)
            if dist < powerup.radius + 15:
                self.spaceship.activate_powerup(powerup.type)
                self.powerups.remove(powerup)
                self.show_message(f"{powerup.type.replace('_', ' ').title()} activated!")

    def draw(self, screen):
        screen.fill(BLACK)
        for x, y, brightness in stars:
            size = 1 if brightness < 0.5 else 2
            color = (int(255 * brightness),
                    int(255 * brightness),
                    int(255 * brightness))
            pygame.draw.circle(screen, color, (int(x), int(y)), size)

        for asteroid in self.asteroids:
            asteroid.draw(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

        for particle in self.particles:
            particle.draw(screen)

        for powerup in self.powerups:
            powerup.draw(screen)

        if self.state != "game_over":
            self.spaceship.draw(screen)

        self.draw_ui(screen)

    def draw_ui(self, screen):
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        level_text = font_medium.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (10, 40))

        lives_text = font_medium.render(f"Lives: {self.spaceship.lives}", True, WHITE)
        screen.blit(lives_text, (screen_width - 100, 10))

        if self.message and self.message_timer > 0:
            text = font_large.render(self.message, True, WHITE)
            text_rect = text.get_rect(center=(screen_width//2, screen_height//2))
            screen.blit(text, text_rect)

        if self.state == "start":
            title = font_large.render("AsteroidGame", True, WHITE)
            title_rect = title.get_rect(center=(screen_width//2, screen_height//2 - 50))
            screen.blit(title, title_rect)

            instruction = font_medium.render("Press SPACE to start", True, WHITE)
            instruction_rect = instruction.get_rect(center=(screen_width//2, screen_height//2 + 50))
            screen.blit(instruction, instruction_rect)

            controls = font_small.render("Arrow keys to move, E to shoot", True, WHITE)
            controls_rect = controls.get_rect(center=(screen_width//2, screen_height//2 + 100))
            screen.blit(controls, controls_rect)

        elif self.state == "game_over":
            if self.message_timer <= 0:
                gameover = font_large.render("GAME OVER", True, RED)
                gameover_rect = gameover.get_rect(center=(screen_width//2, screen_height//2 - 50))
                screen.blit(gameover, gameover_rect)

                score = font_medium.render(f"Final Score: {self.score}", True, WHITE)
                score_rect = score.get_rect(center=(screen_width//2, screen_height//2))
                screen.blit(score, score_rect)

                restart = font_medium.render("Press SPACE to restart", True, WHITE)
                restart_rect = restart.get_rect(center=(screen_width//2, screen_height//2 + 50))
                screen.blit(restart, restart_rect)

game = Game()

left_pressed = False
right_pressed = False
up_pressed = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_LEFT:
                left_pressed = True
            elif event.key == pygame.K_RIGHT:
                right_pressed = True
            elif event.key == pygame.K_UP:
                up_pressed = True
                try:
                    pygame.mixer.Sound.play(thrust_sound)
                except:
                    pass
            elif event.key == pygame.K_SPACE:
                if game.state == "start":
                    game.start_level()
                elif game.state == "game_over":
                    game.reset()
            elif event.key == pygame.K_e:
                if game.state == "playing":
                    game.spaceship.fire(game.bullets)
            elif event.key == pygame.K_c:
                game.spaceship.lives = 999
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left_pressed = False
            elif event.key == pygame.K_RIGHT:
                right_pressed = False
            elif event.key == pygame.K_UP:
                up_pressed = False

    game.update()
    game.draw(screen)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
