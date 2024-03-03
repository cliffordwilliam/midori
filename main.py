import pygame
import sys
from os import path
import json
from datetime import datetime

# Constants
NATIVE_WIDTH = 432
NATIVE_HEIGHT = 288
NATIVE_SIZE = (NATIVE_WIDTH, NATIVE_HEIGHT)

RESOLUTION_SCALE = 4

WINDOW_WIDTH = NATIVE_WIDTH * RESOLUTION_SCALE
WINDOW_HEIGHT = NATIVE_HEIGHT * RESOLUTION_SCALE
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

TILE_WIDTH = 6
TILE_HEIGHT = 6
TILE_SIZE = (TILE_WIDTH, TILE_HEIGHT)

BLOCK_TILE_WIDTH = TILE_WIDTH * 3
BLOCK_TILE_HEIGHT = TILE_HEIGHT * 3
BLOCK_TILE_SIZE = (BLOCK_TILE_WIDTH, BLOCK_TILE_HEIGHT)

ACTOR_TILE_WIDTH = TILE_WIDTH * 4
ACTOR_TILE_HEIGHT = TILE_HEIGHT * 4
ACTOR_TILE_SIZE = (ACTOR_TILE_WIDTH, ACTOR_TILE_HEIGHT)

SPRITE_SHEET_PATH = path.join('sprite_sheets', 'sprite_sheet.png')

ROOMS_DIR_NAME = "rooms"

# Initialize
pygame.init()

# For dt and fps limiter
clock = pygame.time.Clock()

# Blit things here, then blit this to window_surface
native_surface = pygame.Surface(NATIVE_SIZE)

# This is as big as the window
window_surface = pygame.display.set_mode(WINDOW_SIZE)

# Only 1 scene at a time
current_scene = None

# Helper


def get_mouse_position_tuple():
    # Get based on window
    mouse_pos = pygame.mouse.get_pos()

    # Turn to based on native
    scaled_pos = (
        mouse_pos[0] // RESOLUTION_SCALE,
        mouse_pos[1] // RESOLUTION_SCALE
    )

    return scaled_pos


def get_mouse_position_vector():
    # Get based on window
    mouse_position = pygame.mouse.get_pos()

    # Turn to based on native
    scaled_position = (
        mouse_position[0] // RESOLUTION_SCALE,
        mouse_position[1] // RESOLUTION_SCALE
    )

    # Tuple to vector
    vector_position = pygame.math.Vector2(scaled_position)

    return vector_position


def snap_to_block_tile_grid_vector(position_vector, block_tile_width, block_tile_height):
    snapped_x = position_vector.x // block_tile_width * block_tile_width
    snapped_y = position_vector.y // block_tile_height * block_tile_height
    return pygame.Vector2(snapped_x, snapped_y)


def add_camera_offset(position_vector, camera_vector):
    position_vector_with_offset = pygame.math.Vector2()
    position_vector_with_offset.x = position_vector.x + camera_vector.x
    position_vector_with_offset.y = position_vector.y + camera_vector.y
    return pygame.Vector2(position_vector_with_offset.x, position_vector_with_offset.y)


def minus_camera_offset(position_vector, camera_vector):
    position_vector_with_offset = pygame.math.Vector2()
    position_vector_with_offset.x = position_vector.x - camera_vector.x
    position_vector_with_offset.y = position_vector.y - camera_vector.y
    return pygame.Vector2(position_vector_with_offset.x, position_vector_with_offset.y)


class Sprite(pygame.sprite.Sprite):
    """Anything with a sprite and rect"""

    def __init__(self, groups, sprite_sheet_surface, rect, regions_list):
        super().__init__(groups)
        self.image = sprite_sheet_surface

        # Move this one
        self.rect = self.image.get_frect()

        # Do collision check with this one
        self.real_rect = rect

        self.frame_index = 0
        self.regions_list = regions_list


class Group(pygame.sprite.Group):
    """Special render to camera offset"""

    def __init__(self):
        super().__init__()

    def draw(self, native_surface, camera_vector):
        for sprite in self:
            # Bring real rect to default rect
            sprite.real_rect.topleft = sprite.rect.topleft

            # Turn sprite rect into vector
            sprite_rect_position_vector = pygame.math.Vector2(
                sprite.rect.left, sprite.rect.top)

            # Add camera off set to sprite rect vector
            sprite_rect_position_vector_with_offset = add_camera_offset(
                sprite_rect_position_vector,
                camera_vector
            )

            # Get current sprite region rect with its frame index
            sprite_region = sprite.regions_list[sprite.frame_index]

            # Render the sprite with camera offset
            native_surface.blit(
                sprite.image,
                sprite_rect_position_vector_with_offset,
                sprite_region,
            )


class TestScene():
    """Segregate the main loop"""

    def __init__(self):
        # Load sprite sheet
        self.sprite_sheet_surface = pygame.image.load(
            SPRITE_SHEET_PATH
        ).convert_alpha()

        # Groups
        self.all_sprites = pygame.sprite.Group()

        # Instance Player
        self.player_frame = 0
        self.player_regions_list = [
            pygame.FRect(360, 0, 24, 24),
            pygame.FRect(384, 0, 24, 24),
        ]
        self.player_rect = pygame.FRect(0, 0, 24, 24)
        self.player = Sprite(
            self.all_sprites,
            self.sprite_sheet_surface,
            self.player_rect,
            self.player_regions_list
        )

    def input(self, event):
        pass

    def update(self, native_surface, dt):
        # Clear native_surface
        native_surface.fill("black")
        self.all_sprites.draw(native_surface)


class LevelMakerScene():
    """Segregate the main loop"""

    # TODO: The input logic is horrible, you check where the mouse is and then handle clicks - set a state on where a mouse is and use that to segregate input

    # TODO: The data you save is not useful, why save the size of the sprite sheet? save the sprite sheet that is being used and the size of the tile, region, and maybe add animation too

    def __init__(self):
        # Menu data
        self.sprite_sheet_data_list = [
            {
                "regions_list": [
                    pygame.FRect(
                        7 * BLOCK_TILE_WIDTH,
                        2 * BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    )
                ],
                "rect": pygame.FRect(
                    0,
                    0,
                    BLOCK_TILE_HEIGHT,
                    BLOCK_TILE_HEIGHT
                ),
                "type": "Normal"
            },
            {
                "regions_list": [
                    pygame.FRect(
                        7 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    )
                ],
                "rect": pygame.FRect(
                    0,
                    0,
                    BLOCK_TILE_HEIGHT,
                    BLOCK_TILE_HEIGHT
                ),
                "type": "Normal"
            },
            {
                "regions_list": [
                    pygame.FRect(
                        9 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    )
                ],
                "rect": pygame.FRect(
                    0,
                    0,
                    BLOCK_TILE_HEIGHT,
                    BLOCK_TILE_HEIGHT
                ),
                "type": "Normal"
            },

            # Grass autotile
            {
                "regions_list": [
                    pygame.FRect(
                        0,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        4 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        5 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        4 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        5 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                ],
                "rect": pygame.FRect(
                    0,
                    0,
                    6 * BLOCK_TILE_WIDTH,
                    8 * BLOCK_TILE_HEIGHT
                ),
                "type": "Autotile",
                "bitmasks": {
                    (
                        (0, 0, 0),
                        (0, 1, 0),
                        (0, 0, 0)
                    ): 0,
                    (
                        (0, 0, 0),
                        (0, 1, 1),
                        (0, 0, 0)
                    ): 1,
                    (
                        (0, 0, 0),
                        (1, 1, 1),
                        (0, 0, 0)
                    ): 2,
                    (
                        (0, 0, 0),
                        (1, 1, 0),
                        (0, 0, 0)
                    ): 3,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (1, 1, 0)
                    ): 4,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (0, 1, 1)
                    ): 5,
                    (
                        (0, 0, 0),
                        (0, 1, 0),
                        (0, 1, 0)
                    ): 6,
                    (
                        (0, 0, 0),
                        (0, 1, 1),
                        (0, 1, 1)
                    ): 7,
                    (
                        (0, 0, 0),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 8,
                    (
                        (0, 0, 0),
                        (1, 1, 0),
                        (1, 1, 0)
                    ): 9,
                    (
                        (1, 1, 0),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 10,
                    (
                        (0, 1, 1),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 11,
                    (
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 1, 0)
                    ): 12,
                    (
                        (0, 1, 1),
                        (0, 1, 1),
                        (0, 1, 1)
                    ): 13,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 14,
                    (
                        (1, 1, 0),
                        (1, 1, 0),
                        (1, 1, 0)
                    ): 15,
                    (
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 0, 0)
                    ): 16,
                    (
                        (0, 1, 1),
                        (0, 1, 1),
                        (0, 0, 0)
                    ): 17,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (0, 0, 0)
                    ): 18,
                    (
                        (1, 1, 0),
                        (1, 1, 0),
                        (0, 0, 0)
                    ): 19,
                }
            },

            # Dirt autotile
            {
                "regions_list": [
                    pygame.FRect(
                        0,
                        2 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        2 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        2 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        2 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        4 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        5 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        3 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        3 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        3 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        3 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        4 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        5 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                ],
                "rect": pygame.FRect(
                    0,
                    0,
                    6 * BLOCK_TILE_WIDTH,
                    8 * BLOCK_TILE_HEIGHT
                ),
                "type": "Autotile",
                "bitmasks": {
                    (
                        (0, 0, 0),
                        (0, 1, 0),
                        (0, 0, 0)
                    ): 0,
                    (
                        (0, 0, 0),
                        (0, 1, 1),
                        (0, 0, 0)
                    ): 1,
                    (
                        (0, 0, 0),
                        (1, 1, 1),
                        (0, 0, 0)
                    ): 2,
                    (
                        (0, 0, 0),
                        (1, 1, 0),
                        (0, 0, 0)
                    ): 3,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (1, 1, 0)
                    ): 4,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (0, 1, 1)
                    ): 5,
                    (
                        (0, 0, 0),
                        (0, 1, 0),
                        (0, 1, 0)
                    ): 6,
                    (
                        (0, 0, 0),
                        (0, 1, 1),
                        (0, 1, 1)
                    ): 7,
                    (
                        (0, 0, 0),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 8,
                    (
                        (0, 0, 0),
                        (1, 1, 0),
                        (1, 1, 0)
                    ): 9,
                    (
                        (1, 1, 0),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 10,
                    (
                        (0, 1, 1),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 11,
                    (
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 1, 0)
                    ): 12,
                    (
                        (0, 1, 1),
                        (0, 1, 1),
                        (0, 1, 1)
                    ): 13,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 14,
                    (
                        (1, 1, 0),
                        (1, 1, 0),
                        (1, 1, 0)
                    ): 15,
                    (
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 0, 0)
                    ): 16,
                    (
                        (0, 1, 1),
                        (0, 1, 1),
                        (0, 0, 0)
                    ): 17,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (0, 0, 0)
                    ): 18,
                    (
                        (1, 1, 0),
                        (1, 1, 0),
                        (0, 0, 0)
                    ): 19,
                }
            },

            # Snow autotile
            {
                "regions_list": [
                    pygame.FRect(
                        0,
                        4 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        4 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        4 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        4 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        4 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        5 * BLOCK_TILE_WIDTH,
                        0,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        5 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        5 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        5 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        5 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        4 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        5 * BLOCK_TILE_WIDTH,
                        1 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        6 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        0,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        1 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        2 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                    pygame.FRect(
                        3 * BLOCK_TILE_WIDTH,
                        7 * BLOCK_TILE_WIDTH,
                        BLOCK_TILE_HEIGHT,
                        BLOCK_TILE_HEIGHT
                    ),
                ],
                "rect": pygame.FRect(
                    0,
                    0,
                    6 * BLOCK_TILE_WIDTH,
                    8 * BLOCK_TILE_HEIGHT
                ),
                "type": "Autotile",
                "bitmasks": {
                    (
                        (0, 0, 0),
                        (0, 1, 0),
                        (0, 0, 0)
                    ): 0,
                    (
                        (0, 0, 0),
                        (0, 1, 1),
                        (0, 0, 0)
                    ): 1,
                    (
                        (0, 0, 0),
                        (1, 1, 1),
                        (0, 0, 0)
                    ): 2,
                    (
                        (0, 0, 0),
                        (1, 1, 0),
                        (0, 0, 0)
                    ): 3,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (1, 1, 0)
                    ): 4,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (0, 1, 1)
                    ): 5,
                    (
                        (0, 0, 0),
                        (0, 1, 0),
                        (0, 1, 0)
                    ): 6,
                    (
                        (0, 0, 0),
                        (0, 1, 1),
                        (0, 1, 1)
                    ): 7,
                    (
                        (0, 0, 0),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 8,
                    (
                        (0, 0, 0),
                        (1, 1, 0),
                        (1, 1, 0)
                    ): 9,
                    (
                        (1, 1, 0),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 10,
                    (
                        (0, 1, 1),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 11,
                    (
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 1, 0)
                    ): 12,
                    (
                        (0, 1, 1),
                        (0, 1, 1),
                        (0, 1, 1)
                    ): 13,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (1, 1, 1)
                    ): 14,
                    (
                        (1, 1, 0),
                        (1, 1, 0),
                        (1, 1, 0)
                    ): 15,
                    (
                        (0, 1, 0),
                        (0, 1, 0),
                        (0, 0, 0)
                    ): 16,
                    (
                        (0, 1, 1),
                        (0, 1, 1),
                        (0, 0, 0)
                    ): 17,
                    (
                        (1, 1, 1),
                        (1, 1, 1),
                        (0, 0, 0)
                    ): 18,
                    (
                        (1, 1, 0),
                        (1, 1, 0),
                        (0, 0, 0)
                    ): 19,
                }
            },
        ]

        # Preview cursor on grid
        self.selected_item = 0

        # Load sprite sheet
        self.sprite_sheet_surface = pygame.image.load(
            SPRITE_SHEET_PATH
        ).convert_alpha()

        # Groups
        self.groups = [
            Group()
        ]
        self.layer = Group()
        self.current_layer_index = 0

        # Things are drawn relative to this
        self.camera_vector = pygame.math.Vector2()

        # Initial mouse pos for panning
        self.initial_mouse_position_vector = pygame.math.Vector2()

        # Grid color
        self.grid_color = "grey5"
        self.grid_color_secondary = "grey15"

        # Ruler text
        self.ruler_text_color = "white"

        # Ruler card
        self.ruler_card_color = "blue4"
        self.ruler_card_padding = 2

        # Menu button
        self.menu_button_color = "white"
        self.menu_button_border_color = "blue4"
        self.menu_button_padding = 6
        self.menu_button_border_width = 2

        # Origin dot
        self.origin_dot_radius = 2
        self.origin_dot_color = "red"
        self.origin_dot_width = 1

        # Text
        self.font_height = 5
        self.font = pygame.font.Font("cg-pixel-3x5.ttf", self.font_height)

        # States
        self.state = 0
        # 0 - normal
        # 1 - panning

        # Remember last frame mouse input
        self.old_mouse_buttons_pressed_list = [False, False, False]

        # Creation data
        self.creation_data = []

        self.clicked = False

    def input(self, event):
        pass

    def update(self, native_surface, dt):
        # Get mouse button pressed states
        mouse_buttons_pressed_list = pygame.mouse.get_pressed()
        is_left_mouse_button_pressed = mouse_buttons_pressed_list[0]
        is_middle_mouse_button_pressed = mouse_buttons_pressed_list[1]
        is_right_mouse_button_pressed = mouse_buttons_pressed_list[2]

        if self.old_mouse_buttons_pressed_list[0] == True and is_left_mouse_button_pressed == False:
            self.clicked = False

        # Get mouse position - many people needs this - GLOBAL
        mouse_position_vector = get_mouse_position_vector()

        # Get mouse position with camera offset - GAME WORLD
        mouse_position_vector_with_camera_offset = minus_camera_offset(
            mouse_position_vector,
            self.camera_vector
        )

        # Get mouse position with camera offset snapped to grid - GAME WORLD SNAPPED
        mouse_position_vector_with_camera_offset_snapped = snap_to_block_tile_grid_vector(
            mouse_position_vector_with_camera_offset,
            BLOCK_TILE_WIDTH,
            BLOCK_TILE_HEIGHT
        )

        # Normal state
        if self.state == 0:
            # Exit
            if pygame.mouse.get_pressed()[1]:
                self.change_state(1)

        # Panning state
        elif self.state == 1:
            # Find displacement
            displacement = mouse_position_vector - self.initial_mouse_position_vector
            self.camera_vector = displacement

            # Exit
            if not pygame.mouse.get_pressed()[1]:
                self.change_state(0)

        # Clear native_surface
        native_surface.fill("black")

        # Draw grid lines
        self.draw_vertical_grid_lines(
            native_surface,
            BLOCK_TILE_WIDTH,
            self.grid_color,
        )
        self.draw_horizontal_grid_lines(
            native_surface,
            BLOCK_TILE_HEIGHT,
            self.grid_color,
        )

        # Draw secondary grid lines
        self.draw_vertical_grid_lines(
            native_surface,
            NATIVE_WIDTH,
            self.grid_color_secondary,
        )
        self.draw_horizontal_grid_lines(
            native_surface,
            NATIVE_HEIGHT,
            self.grid_color_secondary,
        )

        # Draw tiles
        for group in self.groups:
            group.draw(native_surface, self.camera_vector)

        # Draw origin
        pygame.draw.circle(
            native_surface,
            self.origin_dot_color,
            self.camera_vector,
            self.origin_dot_radius,
            self.origin_dot_width
        )

        # Create a copy of the sprite_sheet_surface
        copied_surface = self.sprite_sheet_surface.copy()

        # Add alpha to it - translucent
        copied_surface.set_alpha(100)

        # Render the preview_cursor_surface
        preview_cursor_surface_region = self.sprite_sheet_data_list[
            self.selected_item]["regions_list"][0]
        native_surface.blit(
            copied_surface,
            add_camera_offset(
                mouse_position_vector_with_camera_offset_snapped,
                self.camera_vector
            ),
            preview_cursor_surface_region,
        )

        # Draw sprite
        # native_surface.blit(
        #     self.sprite_sheet_surface,
        #     (0 + self.camera_vector.x, 0 + self.camera_vector.y),
        #     pygame.FRect(0, 0, BLOCK_TILE_HEIGHT, BLOCK_TILE_HEIGHT),
        # )

        # Draw grid ruler card
        card_width = self.font_height + self.ruler_card_padding * 2
        pygame.draw.rect(
            native_surface,
            self.ruler_card_color,
            pygame.FRect(0, 0, card_width, NATIVE_HEIGHT)
        )
        card_height = self.font_height + self.ruler_card_padding * 2
        pygame.draw.rect(
            native_surface,
            self.ruler_card_color,
            pygame.FRect(0, 0, NATIVE_WIDTH, card_height)
        )

        # Draw grid ruler
        self.draw_vertical_grid_ruler(
            native_surface,
            BLOCK_TILE_WIDTH,
            self.ruler_text_color
        )
        self.draw_horizontal_grid_ruler(
            native_surface,
            BLOCK_TILE_HEIGHT,
            self.ruler_text_color
        )

        # Draw grid ruler card corner
        card_width = self.font_height + self.ruler_card_padding * 2
        card_height = self.font_height + self.ruler_card_padding * 2
        pygame.draw.rect(
            native_surface,
            self.ruler_text_color,
            pygame.FRect(0, 0, card_width, card_height)
        )

        # Get add layer button rect
        add_layer_rect = pygame.FRect(
            0,
            0,
            BLOCK_TILE_WIDTH,
            BLOCK_TILE_HEIGHT
        )

        # Move to top right of window
        add_layer_rect.topright = (NATIVE_WIDTH - BLOCK_TILE_WIDTH * 2, 0)

        # Draw the add layer rect
        pygame.draw.rect(
            native_surface,
            "white",
            add_layer_rect,
        )

        # Draw the layer rect border
        pygame.draw.rect(
            native_surface,
            "blue",
            add_layer_rect,
            1
        )

        # Prepare the add layer text
        add_layer_text_surface = self.font.render(
            "Add",
            False,
            "blue"
        )
        add_layer_text_rect = add_layer_text_surface.get_frect()

        # Position the layer text on the layer rect
        add_layer_text_rect.center = add_layer_rect.center

        # Render the text
        native_surface.blit(
            add_layer_text_surface,
            add_layer_text_rect
        )

        # Handle layer item clicks
        if self.clicked == False:
            # Mouse position is on this layer item?
            if add_layer_rect.collidepoint(mouse_position_vector):
                # Handle left is just pressed
                if is_left_mouse_button_pressed and mouse_buttons_pressed_list != self.old_mouse_buttons_pressed_list:
                    # Add new group
                    self.groups.append(Group())

                    # Move the current selected layer to the new one
                    self.current_layer_index = len(self.groups) - 1

                    self.clicked = True

        # Get del layer button rect
        del_layer_rect = pygame.FRect(
            0,
            0,
            BLOCK_TILE_WIDTH,
            BLOCK_TILE_HEIGHT
        )

        # Move to top right of window
        del_layer_rect.topright = (NATIVE_WIDTH - BLOCK_TILE_WIDTH * 3, 0)

        # Draw the del layer rect
        pygame.draw.rect(
            native_surface,
            "white",
            del_layer_rect,
        )

        # Draw the layer rect border
        pygame.draw.rect(
            native_surface,
            "blue",
            del_layer_rect,
            1
        )

        # Prepare the del layer text
        del_layer_text_surface = self.font.render(
            "Del",
            False,
            "blue"
        )
        del_layer_text_rect = del_layer_text_surface.get_frect()

        # Position the layer text on the layer rect
        del_layer_text_rect.center = del_layer_rect.center

        # Render the text
        native_surface.blit(
            del_layer_text_surface,
            del_layer_text_rect
        )

        # Handle layer item clicks
        if self.clicked == False:
            # Mouse position is on this layer item?
            if del_layer_rect.collidepoint(mouse_position_vector):
                # Handle left is just pressed
                if is_left_mouse_button_pressed and mouse_buttons_pressed_list != self.old_mouse_buttons_pressed_list:
                    # Make sure not to delete the last layer
                    if len(self.groups) > 1:
                        # About to delete current layer? move it back first
                        if len(self.groups) - 1 == self.current_layer_index:
                            self.current_layer_index -= 1

                        # Delete the latest layer
                        self.groups.pop()

                    self.clicked = True

        # Read layers
        for layer_group_index, group in enumerate(self.groups):
            # Get layer rect
            layer_rect = pygame.FRect(
                0,
                0,
                BLOCK_TILE_WIDTH * 2,
                BLOCK_TILE_HEIGHT
            )

            # Move to top right of window
            layer_rect.topright = (NATIVE_WIDTH, 0)

            # Place next layer to the bottom of the old one
            layer_rect.top += layer_group_index * BLOCK_TILE_HEIGHT

            # Active layer?
            if self.current_layer_index == layer_group_index:
                # Draw the layer rect
                pygame.draw.rect(
                    native_surface,
                    "red",
                    layer_rect,
                )

                # Draw the layer rect border
                pygame.draw.rect(
                    native_surface,
                    "white",
                    layer_rect,
                    1
                )
            else:
                # Draw the layer rect
                pygame.draw.rect(
                    native_surface,
                    "grey40",
                    layer_rect,
                )

                # Draw the layer rect border
                pygame.draw.rect(
                    native_surface,
                    "grey50",
                    layer_rect,
                    1
                )

            # Prepare the layer text

            # Active layer?
            if self.current_layer_index == layer_group_index:
                layer_number_text_surface = self.font.render(
                    f"Layer {layer_group_index}",
                    False,
                    "white"
                )
            else:
                layer_number_text_surface = self.font.render(
                    f"Layer {layer_group_index}",
                    False,
                    "white"
                )
            layer_number_text_rect = layer_number_text_surface.get_frect()

            # Position the layer text on the layer rect
            layer_number_text_rect.center = layer_rect.center

            # Render the text
            native_surface.blit(
                layer_number_text_surface,
                layer_number_text_rect
            )

            # Handle layer item clicks
            if self.clicked == False:
                # Mouse position is on this layer item?
                if layer_rect.collidepoint(mouse_position_vector):
                    # Handle left is just pressed
                    if is_left_mouse_button_pressed and mouse_buttons_pressed_list != self.old_mouse_buttons_pressed_list:
                        self.current_layer_index = layer_group_index
                        self.clicked = True

        # Read available menu items
        for menu_data_index, menu_data in enumerate(self.sprite_sheet_data_list):
            # Get button rect
            button_rect = pygame.FRect(
                0,
                0,
                BLOCK_TILE_HEIGHT,
                BLOCK_TILE_WIDTH
            )

            # Move to bottom left of window
            button_rect.bottomleft = (0, NATIVE_HEIGHT)

            # Place next button to the right of the old one
            button_rect.left += menu_data_index * BLOCK_TILE_WIDTH

            # Create another rect for the button icon
            button_icon_rect = button_rect.copy().inflate(
                -self.menu_button_padding,
                -self.menu_button_padding
            )

            # Draw the button rect
            pygame.draw.rect(
                native_surface,
                self.menu_button_color,
                button_rect,
            )

            # Draw the button rect border
            pygame.draw.rect(
                native_surface,
                self.menu_button_border_color,
                button_rect,
                self.menu_button_border_width
            )

            # Extract sprite from sprite sheet with this item region data
            region_surface = self.sprite_sheet_surface.subsurface(
                menu_data["regions_list"][0]
            )

            # Scale sprite to be icon sized
            scaled_region_surface = pygame.transform.scale(
                region_surface, button_icon_rect.size
            )

            # Render the icon on button_icon_rect
            native_surface.blit(
                scaled_region_surface,
                button_icon_rect
            )
            # Handle menu item clicks
            if self.clicked == False:
                # Mouse position is on this menu?
                if button_icon_rect.collidepoint(mouse_position_vector):
                    # Handle left is just pressed
                    if is_left_mouse_button_pressed and mouse_buttons_pressed_list != self.old_mouse_buttons_pressed_list:
                        self.selected_item = menu_data_index
                        self.clicked = True

        # Handle grid clicks
        if self.clicked == False:
            # Handle is left pressed
            if is_left_mouse_button_pressed:
                # Check local storage if this cell is occupied
                is_occupied = False

                for sprite in self.groups[self.current_layer_index]:
                    if sprite.rect.topleft == mouse_position_vector_with_camera_offset_snapped:
                        is_occupied = True
                        break

                if is_occupied == False:
                    # Grab item data from menu
                    menu_item = self.sprite_sheet_data_list[self.selected_item]
                    group = self.groups[self.current_layer_index]
                    rect = menu_item["rect"]
                    regions_list = menu_item["regions_list"]
                    tile_type = menu_item["type"]

                    # Instance tile
                    tile = Sprite(
                        group,
                        self.sprite_sheet_surface,
                        rect,
                        regions_list
                    )

                    # Set the tile position to mouse
                    tile.rect.topleft = mouse_position_vector_with_camera_offset_snapped

                    # Prepare data to be saved
                    to_be_added_sprite_data = {
                        "instance": tile,  # removed this later, do not save
                        "layer": self.current_layer_index,
                        "left": tile.rect.left,
                        "top": tile.rect.top,
                        "width": tile.rect.width,
                        "height": tile.rect.height,
                        "type": tile_type
                    }

                    # Store it locally
                    self.creation_data.append(to_be_added_sprite_data)

                    # Handle autotile
                    self.handle_autotile(to_be_added_sprite_data)

            # Handle is right pressed
            elif is_right_mouse_button_pressed:
                # Check local storage if this cell is occupied
                to_be_killed_sprite_data = None
                for sprite_data in self.creation_data:
                    if sprite_data["layer"] == self.current_layer_index:
                        if pygame.math.Vector2(sprite_data["left"], sprite_data["top"]) == mouse_position_vector_with_camera_offset_snapped:
                            sprite_data["instance"].kill()
                            self.creation_data = list(filter(lambda data: data["layer"] != self.current_layer_index or pygame.math.Vector2(
                                data["left"], data["top"]) != mouse_position_vector_with_camera_offset_snapped, self.creation_data))
                            to_be_killed_sprite_data = sprite_data
                            break

                # Handle autotile
                if to_be_killed_sprite_data:
                    self.handle_autotile(to_be_killed_sprite_data)

        # Update for next frame
        self.old_mouse_buttons_pressed_list = mouse_buttons_pressed_list

        # Save button
        if pygame.key.get_just_pressed()[pygame.K_a]:
            # Remove instance
            modified_creation_data = [{k: v for k, v in data.items(
            ) if k != "instance"} for data in self.creation_data]

            # Generate file name
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"room_{current_time}.json"
            file_path = path.join(ROOMS_DIR_NAME, filename)

            # Save to json
            with open(file_path, "x") as json_file:
                json.dump(modified_creation_data, json_file)

    def change_state(self, state):
        # Get mouse position - many people needs this
        mouse_position_vector = get_mouse_position_vector()

        # Remember state
        old_state = self.state
        new_state = state

        # Update state
        self.state = state

        # Normal -> Panning
        if old_state == 0 and new_state == 1:
            # Set initial_mouse_position_vector
            self.initial_mouse_position_vector = mouse_position_vector - \
                self.camera_vector

        # Panning -> Normal
        if old_state == 1 and new_state == 2:
            # Reset initial_mouse_position_vector
            self.initial_mouse_position_vector = pygame.math.Vector2()

    # Helpers

    def handle_autotile(self, to_be_added_or_removed_spirte_data):
        # Handle extra autotile logic
        if to_be_added_or_removed_spirte_data["type"] == "Autotile":
            for sprite_data in self.creation_data:
                # prepare this tile data
                instance = sprite_data["instance"]
                layer = sprite_data["layer"]
                left = sprite_data["left"]
                top = sprite_data["top"]
                tile_type = sprite_data["type"]

                if tile_type == "Autotile" and layer == self.current_layer_index:
                    # Prepare mask
                    mask = [
                        [0, 0, 0],
                        [0, 1, 0],
                        [0, 0, 0]
                    ]

                    for other_sprite_data in self.creation_data:
                        # Get other sprite data
                        other_layer = other_sprite_data["layer"]
                        other_left = other_sprite_data["left"]
                        other_top = other_sprite_data["top"]
                        other_tile_type = other_sprite_data["type"]

                        if layer == other_layer and other_tile_type == "Autotile":
                            # OTHER rel to THIS
                            dx = (other_left -
                                  left) // BLOCK_TILE_WIDTH
                            dy = (other_top -
                                  top) // BLOCK_TILE_HEIGHT

                            # Update THIS mask based on ALL OTHER
                            possible_neighbour_positions = [
                                [(-1, -1), (0, -1), (1, -1),],
                                [(-1, 0), (0, 0), (1, 0),],
                                [(-1, 1), (0, 1), (1, 1)]
                            ]

                            for y, row in enumerate(possible_neighbour_positions):
                                for x, possible_position in enumerate(row):
                                    if possible_position == (dx, dy):
                                        mask[y][x] = 1

                    # handle TL
                    if mask[0][0] == 1:
                        if mask[0][1] == 0 or mask[1][0] == 0:
                            mask[0][0] = 0

                    # handle TR
                    if mask[0][2] == 1:
                        if mask[0][1] == 0 or mask[1][2] == 0:
                            mask[0][2] = 0

                    # handle BL
                    if mask[2][0] == 1:
                        if mask[1][0] == 0 or mask[2][1] == 0:
                            mask[2][0] = 0

                    # handle BR
                    if mask[2][2] == 1:
                        if mask[1][2] == 0 or mask[2][1] == 0:
                            mask[2][2] = 0

                    # Turn list to tuple
                    tuple_key = tuple(map(tuple, mask))

                    # Use tuple as key to get frame index value
                    menu_item = self.sprite_sheet_data_list[self.selected_item]
                    frame_index = menu_item["bitmasks"].get(
                        tuple_key,
                        0
                    )

                    # Update  frame index
                    instance.frame_index = frame_index

    def draw_vertical_grid_lines(self, native_surface, cell_width, grid_color):
        # Calculate lines amount to be drawn
        columns = NATIVE_WIDTH // cell_width

        # To be used for offseting collumn for loop
        camera_position_snapped_to_block_tile_grid = snap_to_block_tile_grid_vector(
            self.camera_vector, cell_width, cell_width
        )
        camera_x_position_snapped_to_block_tile_grid = camera_position_snapped_to_block_tile_grid.x

        # Loop over amount to draw vertically
        for column in range(columns):
            # Vertical line always start at most top of window frame
            column_start_y = 0

            # Vertical line always end at most bottom of window frame
            column_end_y = WINDOW_HEIGHT

            # Convert index to position
            column_x_position = (column * cell_width)

            # Before rendering apply camera offset
            column_x_position += self.camera_vector.x

            # Keep whole grid within view by offseting using
            column_x_position -= camera_x_position_snapped_to_block_tile_grid

            # Draw the vertical lines
            pygame.draw.line(
                native_surface,
                grid_color,
                (column_x_position, column_start_y),
                (column_x_position, column_end_y)
            )

            # Get the column number
            column -= int(camera_x_position_snapped_to_block_tile_grid) // cell_width

    def draw_vertical_grid_ruler(self, native_surface, cell_width, ruler_text_color):
        # Calculate lines amount to be drawn
        columns = NATIVE_WIDTH // cell_width

        # To be used for offseting collumn for loop
        camera_position_snapped_to_block_tile_grid = snap_to_block_tile_grid_vector(
            self.camera_vector, cell_width, cell_width
        )
        camera_x_position_snapped_to_block_tile_grid = camera_position_snapped_to_block_tile_grid.x

        # Loop over amount to draw vertically
        for column in range(columns):
            # Vertical line always start at most top of window frame
            column_start_y = 0

            # Convert index to position
            column_x_position = (column * cell_width)

            # Before rendering apply camera offset
            column_x_position += self.camera_vector.x

            # Keep whole grid within view by offseting using
            column_x_position -= camera_x_position_snapped_to_block_tile_grid

            # Get the column number
            column -= int(camera_x_position_snapped_to_block_tile_grid) // cell_width

            # Get column number surface
            text_surface = self.font.render(
                str(column),
                False,
                ruler_text_color
            )

            # Get column number rect
            text_rect = text_surface.get_rect()

            # Position column number rect
            text_rect.topleft = (column_x_position, column_start_y)
            text_rect.top += self.ruler_card_padding

            # Render column number surface on column number rect
            native_surface.blit(text_surface, text_rect)

    def draw_horizontal_grid_lines(self, native_surface, cell_height, grid_color):
        # Calculate lines amount to be drawn
        rows = NATIVE_HEIGHT // cell_height

        # To be used for offsetting row for loop
        camera_position_snapped_to_block_tile_grid = snap_to_block_tile_grid_vector(
            self.camera_vector, cell_height, cell_height
        )
        camera_y_position_snapped_to_block_tile_grid = camera_position_snapped_to_block_tile_grid.y

        # Loop over amount to draw horizontally
        for row in range(rows):
            # Horizontal line always start at most left of window frame
            row_start_x = 0

            # Horizontal line always end at most right of window frame
            row_end_x = WINDOW_WIDTH

            # Convert index to position
            row_y_position = (row * cell_height)

            # Before rendering apply camera offset
            row_y_position += self.camera_vector.y

            # Keep whole grid within view by offsetting using camera position
            row_y_position -= camera_y_position_snapped_to_block_tile_grid

            # Draw the horizontal lines
            pygame.draw.line(
                native_surface,
                grid_color,
                (row_start_x, row_y_position),
                (row_end_x, row_y_position)
            )

            # Get the row number
            row -= int(camera_y_position_snapped_to_block_tile_grid) // cell_height

    def draw_horizontal_grid_ruler(self, native_surface, cell_height, ruler_text_color):
        # Calculate lines amount to be drawn
        rows = NATIVE_HEIGHT // cell_height

        # To be used for offsetting row for loop
        camera_position_snapped_to_block_tile_grid = snap_to_block_tile_grid_vector(
            self.camera_vector, cell_height, cell_height
        )
        camera_y_position_snapped_to_block_tile_grid = camera_position_snapped_to_block_tile_grid.y

        # Loop over amount to draw horizontally
        for row in range(rows):
            # Horizontal line always start at most left of window frame
            row_start_x = 0

            # Convert index to position
            row_y_position = (row * cell_height)

            # Before rendering apply camera offset
            row_y_position += self.camera_vector.y

            # Keep whole grid within view by offsetting using camera position
            row_y_position -= camera_y_position_snapped_to_block_tile_grid

            # Get the row number
            row -= int(camera_y_position_snapped_to_block_tile_grid) // cell_height

            # Get column number surface
            text_surface = self.font.render(
                str(row),
                False,
                ruler_text_color
            )

            # Get column number rect
            text_surface = pygame.transform.rotate(text_surface, -90)
            text_rect = text_surface.get_rect()

            # Position column number rect
            text_rect.topleft = (row_start_x, row_y_position)
            text_rect.left += self.ruler_card_padding

            # Render column number surface on column number rect
            native_surface.blit(text_surface, text_rect)


# Set the starting scene
current_scene = LevelMakerScene()

# Main loop
while 1:
    # 60 fps and dt
    dt = clock.tick() / 1000

    # Handle closing window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Pass event to current scene
        current_scene.input(event)

    # Update current_scene
    current_scene.update(native_surface, dt)

    # Scale native_surface to window_surface
    pygame.transform.scale_by(native_surface, RESOLUTION_SCALE, window_surface)

    # Update window_surface
    pygame.display.update()
