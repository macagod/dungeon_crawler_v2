import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, animation_list ):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        if not isinstance(animation_list, list):  # If animation list is provided, use it
            self.animation_list = [animation_list]
        else:
            self.animation_list = animation_list
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, screen_scroll=None, player=None):
        # Reposition item based on screen scroll, but not for HUD items like score_coin (item_type == -1)
        if screen_scroll and self.item_type != -1:
            self.rect.x += screen_scroll[0]
            self.rect.y += screen_scroll[1]
        # Check if item overlaps with player
        if player and self.rect.colliderect(player.rect):
            # Item is coin
            if self.item_type == 0:
                player.score += 1
            # Item is potion
            elif self.item_type == 1:
                player.health += 10
                # Check if player has full health
                if player.health > 100:
                    player.health = 100
            self.kill()

        animation_cooldown = 160
        # Update image
        self.image = self.animation_list[self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            # If the animation is complete, reset the frame index
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)