from character import Character
from items import Item
from constants import TILE_SIZE

class World():
    def __init__(self):
        self.map_tiles = []
        self.obstacle_tiles = []
        self.exit_tile = None
        self.item_list = []
        self.enemy_list = []

    def process_data(self, data, tile_list, item_images, mob_animations):
        self.level_length = len(data)

        # Iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                image = tile_list[tile]
                image_rect = image.get_rect()
                image_x = x * TILE_SIZE
                image_y = y * TILE_SIZE
              
                image_rect.center = (image_x, image_y)
                
                tile_data = [image, image_rect, image_x, image_y]

                # A flag to mark if the tile should be replaced by a floor tile
                is_entity_tile = False

                if tile == 7: # Obstacle
                    self.obstacle_tiles.append(tile_data)
                elif tile == 8: # Exit
                    self.exit_tile = tile_data
                elif 9 <= tile <= 10: # Items
                    item_type = tile - 9  # 9 -> 0 (coin), 10 -> 1 (potion)
                    item = Item(image_x, image_y, item_type, item_images[item_type])
                    self.item_list.append(item)
                    is_entity_tile = True
                elif tile == 11: # Player
                    # This sets the player's position from the map.
                    # The main game loop should use this `world.player` instance.
                    self.player = Character(image_x, image_y, 100, mob_animations, 0, size = 0.8)
                    is_entity_tile = True
                elif 12 <= tile <= 16: # Enemies
                    enemy_type = tile - 11  # Tile 12 -> type 1 ("imp"), etc.
                    # Safeguard to prevent crashing if tile number is out of range.
                    if enemy_type < len(mob_animations):
                        enemy = Character(image_x, image_y, 100, mob_animations, enemy_type, size = 1)
                        self.enemy_list.append(enemy)
                    else:
                        print(f"Warning: Tile {tile} has an invalid enemy type and will be ignored.")
                    is_entity_tile = True
                elif tile == 17: # Boss
                    enemy = Character(image_x, image_y, 100, mob_animations, 6, size = 1.7, boss = True)
                    self.enemy_list.append(enemy)
                    is_entity_tile = True
                
                # If the tile was an entity (item, player, enemy), replace it with a floor tile.
                if is_entity_tile:
                    tile_data[0] = tile_list[1]
                    
                    

                # Add image data to main tiles list
                if tile >= 0:
                    self.map_tiles.append(tile_data)

    def update(self, screen_scroll):
        # Update tile positions based on screen scroll
        for tile in self.map_tiles:
            tile[2] += screen_scroll[0]
            tile[3] += screen_scroll[1]
            tile[1].center = (tile[2], tile[3])
                
    def draw(self, surface):
        for tile in self.map_tiles:
            surface.blit(tile[0], tile[1])
            
            
