import pygame
import math
import random
from constants import ARROW_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, FIREBALL_SPEED

class Weapon():
    def __init__(self, image, arrow_image):
        self.arrow_image = arrow_image
        self.original_image = image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.fired = False
        self.last_shot = pygame.time.get_ticks()

    def update(self, player):
        shot_cooldown = 300
        arrow = None
        firing_direction = None

        self.rect.center = player.rect.center

        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - self.rect.centerx
        y_dist = (pos[1] - self.rect.centery) * -1 # PyGame uses inverted Y-axis
        # Calculate angle
        self.angle = math.degrees(math.atan2(y_dist, x_dist))

        # Get mouse click
        if pygame.mouse.get_pressed()[0] and not self.fired and (pygame.time.get_ticks() - self.last_shot >= shot_cooldown):
            arrow = Arrow(self.arrow_image, self.rect.centerx, self.rect.centery, self.angle)
            self.fired = True
            self.last_shot = pygame.time.get_ticks()
            # Determine firing direction based on mouse position
            if pos[0] < player.rect.centerx:
                firing_direction = True # True for flip (face left)
            else:
                firing_direction = False # False for no flip (face right)

        if not pygame.mouse.get_pressed()[0]:
            self.fired = False
        
        return arrow, firing_direction
        

    def draw(self, surface):
        # Rotate image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width() / 2), self.rect.centery - int(self.image.get_height() / 2))))

class Arrow(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Calculate horizontal and vertical velocity based on angle
        self.dx = math.cos(math.radians(self.angle)) * ARROW_SPEED
        self.dy = math.sin(math.radians(self.angle)) * ARROW_SPEED * -1 # PyGame uses inverted Y-axis

    def update(self, obstacle_tiles, enemy_list, screen_scroll):
        # Reposition based on screen scroll
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy
        damage = 0
        damage_pos = None
        # Reposition based on velocity
        # self.rect.x += self.dx
        # self.rect.y += self.dy

        # Check if arrow is colliding with obstacle tiles
        for tile in obstacle_tiles:
            if tile[1].colliderect(self.rect):
                self.kill()
                break

        # Check if arrow is off screen
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            self.kill()

        # Check collision between arrow and enemy
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.is_alive:
                print("Arrow hit enemy")
                damage = 10 + random.randint(-5, 5)
                damage_pos = enemy.rect
                enemy.health -= damage
                enemy.hit = True
                self.kill()
                break
        return damage, damage_pos
                
        

    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width() / 2), self.rect.centery - int(self.image.get_height() / 2))))

class Fireball(pygame.sprite.Sprite):
    def __init__(self, image, x, y, target_x, target_y):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        x_dist = target_x - x
        y_dist = (target_y - y) * -1 # PyGame uses inverted Y-axis
        self.angle = math.degrees(math.atan2(y_dist, x_dist))
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Calculate horizontal and vertical velocity based on angle
        self.dx = math.cos(math.radians(self.angle)) * FIREBALL_SPEED
        self.dy = math.sin(math.radians(self.angle)) * FIREBALL_SPEED * -1 # PyGame uses inverted Y-axis

    def update(self, player, screen_scroll):
        # Reposition based on screen scroll
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy
        damage = 0
        damage_pos = None
        # Reposition based on velocity
        # self.rect.x += self.dx
        # self.rect.y += self.dy



        # Check if fireball is off screen
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            self.kill()

        # Check collision between fireball and player
        if player.rect.colliderect(self.rect) and not player.hit:
            player.hit = True
            player.last_hit = pygame.time.get_ticks()
            player.health -= 10
            self.kill()

        
       
                
        

    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width() / 2), self.rect.centery - int(self.image.get_height() / 2))))
