import pygame
import random
from character import Character
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG, SPEED, SCALE, WEAPON_SCALE, PANEL, PANEL_BORDER, WHITE, TILE_SIZE, TILE_TYPES, # Existing constants
    MAX_STAMINA, STAMINA_FONT_PATH, STAMINA_FONT_SIZE, STAMINA_TEXT_PADDING, # Stamina constants
    STAMINA_COLOR_COOLDOWN, # Cooldown color constant
    # Regeneration Note constants
    REGEN_NOTE_TEXT, REGEN_NOTE_FONT_SIZE, REGEN_NOTE_COLOR, REGEN_NOTE_PADDING_BOTTOM,
    # Damage text constants
    DAMAGE_TEXT_FONT_PATH, DAMAGE_TEXT_FONT_SIZE, DAMAGE_TEXT_COLOR, 
    # Item constants
    ITEM_SCALE, POTION_SCALE, FIREBALL_SCALE,
    # World constants
    ROWS, COLS,
    # Screen scroll constants
    SCROLL_THRESH,
    # UI Feedback constants
    HEART_WIGGLE_DURATION, HEART_WIGGLE_STRENGTH,
)
from weapon import Weapon
from items import Item
from world import World
import csv
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

# Create clock for maintaining a consistent frame rate
clock = pygame.time.Clock()

# Define game variables
level = 3
screen_scroll = [0, 0]
heart_wiggle_active = False
heart_wiggle_start_time = 0
 
# Helper function to scale images
def scale_image(image, scale_factor):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (int(w * scale_factor), int(h * scale_factor)))

# Load heart images
heart_empty = scale_image(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), ITEM_SCALE)
heart_half = scale_image(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), ITEM_SCALE)
heart_full = scale_image(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), ITEM_SCALE)

# Load coin images
coin_images = []
for i in range(4):
    img = scale_image(pygame.image.load(f"assets/images/items/coin_f{i}.png").convert_alpha(), ITEM_SCALE)
    coin_images.append(img)

# Load potion image
potion_image = scale_image(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), POTION_SCALE)

# Combine item images
item_images = []
item_images.append(coin_images)
item_images.append(potion_image)

# Load weapon images
bow_image = scale_image(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), WEAPON_SCALE)
arrow_image = scale_image(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), WEAPON_SCALE)
fireball_image = scale_image(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), FIREBALL_SCALE)

# Load tile images
tile_list = []
for i in range(TILE_TYPES):
    tile_image = pygame.image.load(f"assets/images/tiles/{i}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))
    tile_list.append(tile_image)

# Load character images
mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]

for mob in mob_types:
    animation_types = ["idle", "run"]
    animation_list = []
    for animation in animation_types:
        # Reset temporary list of images
        temp_list = []
        for i in range(4):
            images = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            image = scale_image(images, SCALE)
            temp_list.append(image)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)

# Define font
damage_text_font = pygame.font.Font(DAMAGE_TEXT_FONT_PATH, DAMAGE_TEXT_FONT_SIZE)
score_font = pygame.font.Font(STAMINA_FONT_PATH, 24)
# Function to output text to the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function for displaying game info
def draw_info():
    # --- Heart Wiggle Calculation ---
    wiggle_offset_x, wiggle_offset_y = 0, 0
    global heart_wiggle_active, heart_wiggle_start_time # Use global to modify these variables

    if heart_wiggle_active:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - heart_wiggle_start_time

        if elapsed_time < HEART_WIGGLE_DURATION:
            # Calculate decay (1.0 at start, 0.0 at end)
            decay = 1 - (elapsed_time / HEART_WIGGLE_DURATION)
            # Apply decay to strength
            current_strength = HEART_WIGGLE_STRENGTH * decay
            # Generate random offset
            wiggle_offset_x = random.randint(-int(current_strength), int(current_strength))
            wiggle_offset_y = random.randint(-int(current_strength), int(current_strength))
        else:
            heart_wiggle_active = False # End the wiggle


    # Draw panel
    pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 60))
    pygame.draw.line(screen, PANEL_BORDER, (0, 60), (SCREEN_WIDTH, 60), 2)
    # Draw hearts
    half_heart_drawn = False
    for i in range(5):
        heart_x = 10 + (i * (heart_full.get_width() + 5)) + wiggle_offset_x
        heart_y = 10 + wiggle_offset_y
        if player.health >= ((i + 1) * 20):
            screen.blit(heart_full, (heart_x, heart_y))
        elif (player.health % 20) > 0 and not half_heart_drawn:
            screen.blit(heart_half, (heart_x, heart_y))
            half_heart_drawn = True
        else:
            screen.blit(heart_empty, (heart_x, heart_y))

    # Draw score
    draw_text(f"{player.score}", score_font, WHITE, SCREEN_WIDTH - 695, 20)
    # Draw Level
    draw_text(f"Level: {level}", score_font, WHITE, 400, 20)

# Create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# Load in level data
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


# Create world object
world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)

# create player
player = world.player

# Damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = damage_text_font.render(str(damage), True, DAMAGE_TEXT_COLOR)
        self.rect = self.image.get_rect()
        
        # Add random initial offset
        self.rect.centerx = x + random.randint(-10, 10)
        self.rect.centery = y
        
        # Add random initial velocities
        self.velocity_x = random.uniform(-0.5, 0.5)  # Random horizontal velocity
        self.velocity_y = random.uniform(-2.0, -1.0)  # Random upward velocity
        self.gravity = 0.1  # Gravity effect to create arc
        
        # Add random rotation
        self.rotation = random.uniform(-2, 2)  # Reduced rotation range for less tilt
        self.original_image = self.image
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        
        # Fade settings
        self.alpha = 255
        self.fade_speed = random.uniform(6, 10)  # Increased fade speed for shorter visibility
       
    def update(self, screen_scroll):
        # Reposition damage text based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        # Apply gravity to vertical velocity
        self.velocity_y += self.gravity
        
        # Update position based on velocities
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Fade out the damage text
        self.alpha -= self.fade_speed
        self.image.set_alpha(max(0, int(self.alpha)))
        
        # Remove the damage text when it's fully faded out
        if self.alpha <= 0:
            self.kill()



# Create player weapon
bow = Weapon(bow_image, arrow_image)



# Create sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score_coin = Item(SCREEN_WIDTH - 710, 30, -1, coin_images)
item_group.add(score_coin)

# Add items from level data
for item in world.item_list:
    item_group.add(item)

enemy_list = []
# Add enemies from level data
enemy_list.extend(world.enemy_list)






# Load fonts
stamina_font = pygame.font.Font(STAMINA_FONT_PATH, STAMINA_FONT_SIZE)
regen_note_font = pygame.font.Font(STAMINA_FONT_PATH, REGEN_NOTE_FONT_SIZE) # Font for the regen note

# Game loop
run = True
while run:
    # Maintain a consistent frame rate
    clock.tick(FPS)

    # Clear screen
    screen.fill(BG)
    # Draw world
    world.draw(screen)

    

    # Draw damage text
    damage_text_group.draw(screen)

    
    # Calculate player movement
    dx, dy = player.get_movement(SPEED)
    screen_scroll = player.move(dx, dy, world.obstacle_tiles)
 

    # Update world
    world.update(screen_scroll)
    # Update enemy
    for enemy in enemy_list:
        fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
        if fireball:
            fireball_group.add(fireball)
        if enemy.is_alive:
            enemy.update_animation()

    # --- Check for player getting hit to trigger UI feedback ---
    if player.hit:
        heart_wiggle_active = True
        heart_wiggle_start_time = pygame.time.get_ticks()
        player.hit = False # Reset the hit flag so it only triggers once

    # Update stamina
    player.update_stamina()

    # Update player animation
    player.update_animation()
    
    # Update bow
    arrow, firing_direction = bow.update(player)
    if arrow:
        arrow_group.add(arrow)
    if firing_direction is not None:
        player.handle_attack_direction(firing_direction)
    
    # Update arrows
    for arrow in arrow_group:
        damage, damage_pos = arrow.update(world.obstacle_tiles, enemy_list, screen_scroll)
        if damage != 0:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), DAMAGE_TEXT_COLOR)
            damage_text_group.add(damage_text)

    # Update fireballs
    fireball_group.update(player, screen_scroll)
    # Update damage text
    damage_text_group.update(screen_scroll)

    # Update collectable items
    item_group.update(screen_scroll, player)

    # Update HUD coin
    score_coin.update()

   

    # Draw characters
    player.draw(screen)
    bow.draw(screen)
    for arrow in arrow_group: # Draw arrows
        arrow.draw(screen)
    for fireball in fireball_group: # Draw fireballs
        fireball.draw(screen)
    for enemy in enemy_list: # Draw enemies
        enemy.draw(screen)
    
    # Draw items
    item_group.draw(screen)

   

    # Draw info
    draw_info() 
    score_coin.draw(screen) # Draw score coin
    # --- Draw Stamina UI ---
    # Main Stamina Text
    stamina_display_text = f"Stamina: {int(player.stamina)}/{MAX_STAMINA}"
    stamina_surface = stamina_font.render(stamina_display_text, True, player.stamina_text_color)
    stamina_rect = stamina_surface.get_rect()
    stamina_rect.topright = (SCREEN_WIDTH - STAMINA_TEXT_PADDING, STAMINA_TEXT_PADDING)
    screen.blit(stamina_surface, stamina_rect)

    # Sprint Cooldown Subtitle (if active)
    if player.sprint_cooldown_active:
        remaining_cooldown_seconds = (player.sprint_cooldown_end_time - pygame.time.get_ticks()) / 1000
        remaining_cooldown_seconds = max(0, remaining_cooldown_seconds) # Clamp at 0
        cooldown_text = f"Cooldown: {remaining_cooldown_seconds:.1f}s"
        cooldown_surface = stamina_font.render(cooldown_text, True, STAMINA_COLOR_COOLDOWN)
        cooldown_rect = cooldown_surface.get_rect()
        cooldown_rect.topright = (SCREEN_WIDTH - STAMINA_TEXT_PADDING, stamina_rect.bottom + 1)
        screen.blit(cooldown_surface, cooldown_rect)

    # --- Draw Regeneration Hint Nodte ---
    # Conditions to display the note:
    # 1. Stamina is regenerating (not full, not zero)
    # 2. Player is running (not idle)
    # 3. Player is not intending to sprint (sprinting is False or no stamina or on sprint cooldown)
    # 4. Sprint ability is not on cooldown (this specific note is about *optimizing* regen, not about when regen occurs)
    
    player_intends_sprint = player.sprinting and player.stamina > 0 and not player.sprint_cooldown_active
    
    show_regen_note = (
        player.stamina > 0 and 
        player.stamina < MAX_STAMINA and 
        player.running and 
        not player_intends_sprint
    )

    if show_regen_note:
        note_surface = regen_note_font.render(REGEN_NOTE_TEXT, True, REGEN_NOTE_COLOR)
        note_rect = note_surface.get_rect()
        note_rect.centerx = SCREEN_WIDTH / 2
        note_rect.bottom = SCREEN_HEIGHT - REGEN_NOTE_PADDING_BOTTOM
        screen.blit(note_surface, note_rect)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Take keyboard input
        if event.type == pygame.KEYDOWN:
            player.handle_keydown(event.key)
        if event.type == pygame.KEYUP:
            player.handle_keyup(event.key)
                
    # Update display
    pygame.display.update()
pygame.quit()

