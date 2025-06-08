import pygame
from constants import (
    RED, SPRINT_SPEED_BOOST, SCALE, OFFSET,
    ANIMATION_COOLDOWN_IDLE, ANIMATION_COOLDOWN_RUN, ANIMATION_COOLDOWN_SPRINT, ATTACK_DIRECTION_COOLDOWN,
    MAX_STAMINA, STAMINA_DEPLETION_RATE, STAMINA_REGEN_IDLE_RATE, STAMINA_REGEN_RUN_RATE,
    STAMINA_COLOR_FULL, STAMINA_COLOR_SPRINTING, STAMINA_COLOR_REGENERATING, STAMINA_COLOR_DEPLETED,
    SPRINT_COOLDOWN_DURATION, STAMINA_COLOR_COOLDOWN, TILE_SIZE, SCREEN_WIDTH, SCROLL_THRESH, SCREEN_HEIGHT, ENEMY_SPEED, ENEMY_RANGE, # New constants
    # UI Feedback constants
    PLAYER_FLASH_DURATION, PLAYER_FLASH_COLOR
)
import math

class Character:
    def __init__(self, x, y, health, mob_animations, char_type, size, boss = False):
        # Boss settings
        self.boss = boss
        
        self.size = size
        self.flip = False
        self.rect = pygame.Rect(0, 0, TILE_SIZE * size, TILE_SIZE * size)
        self.rect.center = (x, y)
        self.char_type = char_type

        # Item settings
        self.score = 0

        # Health settings
        self.health = health
        self.is_alive = True
        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.last_attack_time = 0
        
        # Animation settings
        self.running = False
        self.action = 1 # Start with run animation if moving, will be updated
        self.animation_list = mob_animations[char_type]
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.action][self.frame_index]
        self.stunned = False
       
        # Movement state
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        self.sprinting = False

        # Stamina settings
        self.stamina = MAX_STAMINA
        self.stamina_text_color = STAMINA_COLOR_FULL
        self.sprint_cooldown_active = False
        self.sprint_cooldown_end_time = 0

    def handle_keydown(self, key):
        if key == pygame.K_a:
            self.moving_left = True
        if key == pygame.K_d:
            self.moving_right = True
        if key == pygame.K_w:
            self.moving_up = True
        if key == pygame.K_s:
            self.moving_down = True
        if key == pygame.K_LSHIFT:
            # Allow sprint only if stamina > 0 and not in cooldown
            if self.stamina > 0 and not self.sprint_cooldown_active:
                self.sprinting = True

    def handle_keyup(self, key):
        if key == pygame.K_a:
            self.moving_left = False
        if key == pygame.K_d:
            self.moving_right = False
        if key == pygame.K_w:
            self.moving_up = False
        if key == pygame.K_s:
            self.moving_down = False
        if key == pygame.K_LSHIFT:
            self.sprinting = False

    def handle_attack_direction(self, direction):
        self.last_attack_time = pygame.time.get_ticks()
        self.flip = direction

    def get_movement(self, base_speed):
        dx = 0
        dy = 0
        current_speed = base_speed
        
        is_effectively_sprinting = self.sprinting and self.stamina > 0

        if is_effectively_sprinting:
            current_speed += SPRINT_SPEED_BOOST

        if self.moving_right and not self.moving_left:
            dx = current_speed
        elif self.moving_left and not self.moving_right:
            dx = -current_speed
        if self.moving_down and not self.moving_up:
            dy = current_speed
        elif self.moving_up and not self.moving_down:
            dy = -current_speed
        
        if dx != 0 and dy != 0:
            dx *= (math.sqrt(2) / 2)
            dy *= (math.sqrt(2) / 2)
        return dx, dy

    def move(self, dx, dy, obstacle_tiles):
        # Screen scroll
        screen_scroll = [0, 0]
        self.running = False
        if dx != 0 or dy != 0:
            self.running = True
        
        # Set player direction based on movement, but only if not in attack cooldown
        if pygame.time.get_ticks() - self.last_attack_time > ATTACK_DIRECTION_COOLDOWN:
            if dx < 0:
                self.flip = True
            elif dx > 0:
                self.flip = False
        
       

        # Check for collisions with obstacle tiles
        self.rect.x += dx
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                # Check which side of the obstacle the character is colliding with
                if dx > 0:
                    self.rect.right = obstacle[1].left
                if dx < 0:
                    self.rect.left = obstacle[1].right
        
        self.rect.y += dy
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                if dy > 0:
                    self.rect.bottom = obstacle[1].top
                if dy < 0:
                    self.rect.top = obstacle[1].bottom

        # Scroll logic only applies to player
        if self.char_type == 0:
            # Update scroll based on player position
            # Move camera left and right
            if self.rect.right > SCREEN_WIDTH - SCROLL_THRESH:
                screen_scroll[0] = (SCREEN_WIDTH - SCROLL_THRESH) - self.rect.right
                self.rect.right = SCREEN_WIDTH - SCROLL_THRESH
            if self.rect.left < SCROLL_THRESH:
                screen_scroll[0] = SCROLL_THRESH - self.rect.left
                self.rect.left = SCROLL_THRESH
            # Move camera up and down
            if self.rect.bottom > SCREEN_HEIGHT - SCROLL_THRESH:
                screen_scroll[1] = (SCREEN_HEIGHT - SCROLL_THRESH) - self.rect.bottom
                self.rect.bottom = SCREEN_HEIGHT - SCROLL_THRESH
            if self.rect.top < SCROLL_THRESH:
                screen_scroll[1] = SCROLL_THRESH - self.rect.top
                self.rect.top = SCROLL_THRESH

        return screen_scroll

    def ai(self, player, obstacle_tiles, screen_scroll):
        clipped_line = ()

        stunned_cooldown = 150

        ai_dx = 0
        ai_dy = 0
        # Reposition mobs based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        # Create Enemy Line of Sight
        line_of_sight = ((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))
        
        # Check if line of sight is obstructed by obstacle tiles
        for obstacle in obstacle_tiles:
            if obstacle[1].clipline(line_of_sight):
                clipped_line = obstacle[1].clipline(line_of_sight)
                
        
        # Check if player is within range
        dist = math.sqrt(((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2))
        if not clipped_line and dist > ENEMY_RANGE:
            if self.rect.centerx > player.rect.centerx:
                ai_dx = -ENEMY_SPEED
            if self.rect.centerx < player.rect.centerx:
                ai_dx = ENEMY_SPEED
            if self.rect.centery > player.rect.centery:
                ai_dy = -ENEMY_SPEED
            if self.rect.centery < player.rect.centery:
                ai_dy = ENEMY_SPEED
            
        if not self.stunned:
            self.move(ai_dx, ai_dy, obstacle_tiles)

            # If enemy is within range, attack player
            if dist < ENEMY_RANGE and not self.hit and pygame.time.get_ticks() - self.last_hit > 1000:
                self.hit = False
                self.last_hit = pygame.time.get_ticks()
                player.health -= 10
                player.hit = True
                player.last_hit = pygame.time.get_ticks()
        
        # Check if hit
        if self.hit:
            self.hit = False
            self.last_hit = pygame.time.get_ticks()
            self.stunned = True
            self.running = False
            self.update_action(0)
        
        if (pygame.time.get_ticks() - self.last_hit > stunned_cooldown):
            self.stunned = False

    def update_stamina(self):
        # 1. Update Cooldown Status
        if self.sprint_cooldown_active and pygame.time.get_ticks() >= self.sprint_cooldown_end_time:
            self.sprint_cooldown_active = False

        # 2. Determine current sprint status for logic
        player_intends_sprint = self.sprinting and (self.stamina > 0 and not self.sprint_cooldown_active)
        is_depleting_stamina = player_intends_sprint and self.running

        # 3. Handle Stamina Depletion
        if is_depleting_stamina:
            self.stamina -= STAMINA_DEPLETION_RATE
            self.stamina = max(0, self.stamina)
            if self.stamina == 0:
                self.sprinting = False
                self.sprint_cooldown_active = True
                self.sprint_cooldown_end_time = pygame.time.get_ticks() + SPRINT_COOLDOWN_DURATION
        # 4. Handle Stamina Regeneration (only if not depleting and not currently intending to sprint)
        elif not player_intends_sprint: # Cooldown no longer blocks regeneration
            if self.running:
                self.stamina += STAMINA_REGEN_RUN_RATE
            else:  # Idle
                self.stamina += STAMINA_REGEN_IDLE_RATE
            self.stamina = min(MAX_STAMINA, self.stamina)

        # 5. Update Main Stamina Text Color (Simplified: Cooldown color is handled separately in main.py)
        if player_intends_sprint:
            self.stamina_text_color = STAMINA_COLOR_SPRINTING
        elif self.stamina == 0:
            self.stamina_text_color = STAMINA_COLOR_DEPLETED
        elif self.stamina == MAX_STAMINA:
            self.stamina_text_color = STAMINA_COLOR_FULL
        else: # Regenerating or partially full
            self.stamina_text_color = STAMINA_COLOR_REGENERATING

    
    
    def update_animation(self):

        # Check if character is alive
        if self.health <= 0:
            self.health = 0 
            self.is_alive = False

        self.update_action(1) if self.running else self.update_action(0)

        is_effectively_sprinting = self.sprinting and self.stamina > 0

        if self.action == 0: # Idle
            animation_cooldown = ANIMATION_COOLDOWN_IDLE
        elif self.action == 1: # Running
            if is_effectively_sprinting:
                animation_cooldown = ANIMATION_COOLDOWN_SPRINT
            else:
                animation_cooldown = ANIMATION_COOLDOWN_RUN
            
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0
                
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        image_to_draw = pygame.transform.flip(self.image, self.flip, False)

        # Check if the character is the player and if the flash duration is active
        if self.char_type == 0 and pygame.time.get_ticks() - self.last_hit < PLAYER_FLASH_DURATION:
            # Create a copy to avoid modifying the original animation frame
            image_to_draw = image_to_draw.copy()
            # Create a red surface to use as a color filter
            color_surface = pygame.Surface(image_to_draw.get_size()).convert_alpha()
            color_surface.fill(PLAYER_FLASH_COLOR)
            
            # Blend the red color onto the image copy using a MULTIPLY blend mode.
            # This mode multiplies the color values of each pixel, effectively tinting
            # the sprite with the specified color while preserving its alpha channel.
            image_to_draw.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Common drawing logic for both player and enemies
        if self.char_type == 0:
            surface.blit(image_to_draw, (self.rect.x, self.rect.y - SCALE * OFFSET))
        else:
            surface.blit(image_to_draw, self.rect)
            
        pygame.draw.rect(surface, RED, self.rect, 1)
