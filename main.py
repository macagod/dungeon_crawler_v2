import pygame
from character import Character
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG, SPEED, SCALE, WEAPON_SCALE, # Existing constants
    MAX_STAMINA, STAMINA_FONT_PATH, STAMINA_FONT_SIZE, STAMINA_TEXT_PADDING, # Stamina constants
    STAMINA_COLOR_COOLDOWN, # Cooldown color constant
    # Regeneration Note constants
    REGEN_NOTE_TEXT, REGEN_NOTE_FONT_SIZE, REGEN_NOTE_COLOR, REGEN_NOTE_PADDING_BOTTOM 
)
from weapon import Weapon

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

# Create clock for maintaining a consistent frame rate
clock = pygame.time.Clock()

# Helper function to scale images
def scale_image(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))

# Load weapon images
bow_image = scale_image(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), WEAPON_SCALE)
arrow_image = scale_image(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), WEAPON_SCALE)

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
arrow_group = pygame.sprite.Group()
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
        arrow.update()
    
    print(arrow_group)
    

    # Draw character
    player.draw(screen)
    bow.draw(screen)
    for arrow in arrow_group: # Draw arrows
        arrow.draw(screen)
    for enemy in enemy_list: # Draw enemies
        enemy.draw(screen)
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
        cooldown_rect.topright = (SCREEN_WIDTH - STAMINA_TEXT_PADDING, stamina_rect.bottom + 5)
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

