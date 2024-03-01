import pygame as pg
from sys import exit
from os import path

# Pg init
pg.init()
display_surface = pg.display.set_mode((462, 258))
clock = pg.time.Clock()

# Player sprite data
player_frame = 0
player_frames_list = [
    pg.Rect(360, 0, 24, 24),
    pg.Rect(384, 0, 24, 24),
]
player_rect = pg.Rect(0, 0, 24, 24)

# Load sprite sheet
sprite_sheet_path = path.join('sprite_sheets', 'sprite_sheet.png')
sprite_sheet_surface = pg.image.load(sprite_sheet_path).convert_alpha()


while 1:
    # Max 60 fps
    clock.tick(60)

    # Window closed? quit
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

    # Get input

    # Clear display_surface
    display_surface.fill("blue4")

    # Update

    # Render
    display_surface.blit(
        sprite_sheet_surface,
        player_rect.topleft,
        player_frames_list[player_frame]
    )

    pg.display.update()
