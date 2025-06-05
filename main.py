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
    ITEM_SCALE, POTION_SCALE,
    # World constants
    ROWS, COLS,
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
level = 1

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

# Load weapon images
bow_image = scale_image(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), WEAPON_SCALE)
arrow_image = scale_image(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), WEAPON_SCALE)

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
            image = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            image = scale_image(image, SCALE)
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


    # Draw panel
    pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 60))
    pygame.draw.line(screen, PANEL_BORDER, (0, 60), (SCREEN_WIDTH, 60), 2)
    # Draw hearts
    half_heart_drawn = False
    for i in range(5):
        if player.health >= ((i + 1) * 20):
            screen.blit(heart_full, (10 + (i * (heart_full.get_width() + 5)), 10))
        elif (player.health % 20) > 0 and not half_heart_drawn:
            screen.blit(heart_half, (10 + (i * (heart_half.get_width() + 5)), 10))
            half_heart_drawn = True
        else:
            screen.blit(heart_empty, (10 + (i * (heart_full.get_width() + 5)), 10))

    # Draw score
    draw_text(f"{player.score}", score_font, WHITE, SCREEN_WIDTH - 695, 20)

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
world.process_data(world_data, tile_list)


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
       
    def update(self):
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


# Create character
player = Character(100, 100, 100, mob_animations, 0)

# Create enemy
enemy = Character(200, 300, 100, mob_animations, 1)

# Create player weapon
bow = Weapon(bow_image, arrow_image)

# Create empty enemy list
enemy_list = []
enemy_list.append(enemy)

# Create sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()

score_coin = Item(SCREEN_WIDTH - 710, 30, -1, coin_images)
item_group.add(score_coin)

potion = Item(200, 200, 1, [potion_image])
item_group.add(potion)

coin = Item(400, 400, 0, coin_images)
item_group.add(coin)


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

    # Draw info
    draw_info()

    # Draw damage text
    damage_text_group.draw(screen)

    
    # Calculate player movement
    dx, dy = player.get_movement(SPEED)
    player.move(dx, dy)

    # Update enemy
    for enemy in enemy_list:
        enemy.update_animation()
    # Update stamina
    player.update_stamina()

    # Update player animation
    player.update_animation()
    
    # Update bow
    arrow = bow.update(player)
    if arrow:
        arrow_group.add(arrow)
    
    # Update arrows
    for arrow in arrow_group:
        damage, damage_pos = arrow.update(enemy_list)
        if damage != 0:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), DAMAGE_TEXT_COLOR)
            damage_text_group.add(damage_text)

    
    # Update damage text
    damage_text_group.update()

    # Update collectable items
    item_group.update(player)

    # Update HUD coin
    score_coin.update()

    # Draw world
    world.draw(screen)

    # Draw character
    player.draw(screen)
    bow.draw(screen)
    for arrow in arrow_group: # Draw arrows
        arrow.draw(screen)
    for enemy in enemy_list: # Draw enemies
        enemy.draw(screen)

    score_coin.draw(screen)
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

    # --- Draw Regeneration Hint Note ---
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

