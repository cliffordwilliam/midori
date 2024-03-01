import pygame as pg
from sys import exit
from random import randint


class Quadtree:
    def __init__(self, capacity, boundary_rect):
        # Limit before division
        self.capacity = capacity

        # My rect
        self.boundary_rect = boundary_rect

        # Holds actors in me
        self.rects_list = []

        # My kids
        self.tl_quadtree = None
        self.tr_quadtree = None
        self.bl_quadtree = None
        self.br_quadtree = None

    def subdivide(self):
        # Get size
        x, y, w, h = self.boundary_rect
        half_w = w // 2
        half_h = h // 2

        # Prepare kids rects
        tl_rect = pg.Rect(x, y, half_w, half_h)
        tr_rect = pg.Rect(x + half_w, y, half_w, half_h)
        bl_rect = pg.Rect(x, y + half_h, half_w, half_h)
        br_rect = pg.Rect(x + half_w, y + half_h, half_w, half_h)

        # Instance kids
        self.tl_quadtree = Quadtree(self.capacity, tl_rect)
        self.tr_quadtree = Quadtree(self.capacity, tr_rect)
        self.bl_quadtree = Quadtree(self.capacity, bl_rect)
        self.br_quadtree = Quadtree(self.capacity, br_rect)

        # Recurssive based on actors in me
        for i in range(len(self.rects_list)):
            # Add each actors in me to kids
            self.tl_quadtree.insert(self.rects_list[i])
            self.tr_quadtree.insert(self.rects_list[i])
            self.bl_quadtree.insert(self.rects_list[i])
            self.br_quadtree.insert(self.rects_list[i])

    def insert(self, rect):
        # Actor not in me? False
        if not self.boundary_rect.collidepoint(rect.center):
            return False

        # Still under capacity? No kids? Add actor to list
        if len(self.rects_list) < self.capacity and self.tl_quadtree is None:
            self.rects_list.append(rect)
            return True
        # Capacity alr full?
        else:
            # Make kids
            if self.tl_quadtree is None:
                self.subdivide()
            # Pass actor to kids
            if self.tl_quadtree.insert(rect):
                return True
            if self.tr_quadtree.insert(rect):
                return True
            if self.bl_quadtree.insert(rect):
                return True
            if self.br_quadtree.insert(rect):
                return True
            return False

    def query_range(self, given_rect):
        # Container
        rects_in_range = []

        # Actor not in me? return []
        if not self.boundary_rect.colliderect(given_rect):
            return rects_in_range

        # Fill container with actors in my list that are close to given actor
        for rect in self.rects_list:
            if given_rect != rect and given_rect.colliderect(rect):
                rects_in_range.append(rect)

        # Got kids? add their container to mine
        if self.tl_quadtree is not None:
            rects_in_range.extend(self.tl_quadtree.query_range(given_rect))
            rects_in_range.extend(self.tr_quadtree.query_range(given_rect))
            rects_in_range.extend(self.bl_quadtree.query_range(given_rect))
            rects_in_range.extend(self.br_quadtree.query_range(given_rect))

        return rects_in_range

    def show(self, surface):
        # Draw my border
        pg.draw.rect(surface, pg.Color("white"), self.boundary_rect, 1)
        # Got kids? draw theirs too
        if self.tl_quadtree is not None:
            self.tl_quadtree.show(surface)
            self.tr_quadtree.show(surface)
            self.bl_quadtree.show(surface)
            self.br_quadtree.show(surface)


# Pygame init
pg.init()
display_surface = pg.display.set_mode((800, 600))
clock = pg.time.Clock()


class Actor:
    def __init__(self):
        self.velocity = [randint(-5, 5), randint(-5, 5)]
        x = randint(0, 800 - 16)
        y = randint(0, 600 - 16)
        self.rect = pg.Rect(randint(0, 800 - 16), randint(0, 600 - 16), 16, 16)


# Create 20 actors
actors_list = []
for _ in range(20):
    actors_list.append(Actor())


while True:
    # Get dt + limit fps
    clock.tick(60)

    # Windox closed? quit
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

    # Create a Quadtree for collision detection
    quadtree = Quadtree(4, pg.Rect(0, 0, 800, 600))

    # Clear the display_surface
    display_surface.fill("black")

    # Insert all actor rectangles into the Quadtree
    quadtree.rects_list = []
    for actor in actors_list:
        quadtree.insert(actor.rect)

    # Move the actors
    for actor in actors_list:
        # Update pos with velocity
        actor.rect.x += actor.velocity[0]
        actor.rect.y += actor.velocity[1]

        # Clamp pos to always stay in window
        actor.rect.left = max(0, min(actor.rect.left, 800 - actor.rect.width))
        actor.rect.top = max(0, min(actor.rect.top, 600 - actor.rect.height))

        # Pos at boundary? Flip velocity
        if actor.rect.left == 0 or actor.rect.right == 800:
            actor.velocity[0] *= -1
        if actor.rect.top == 0 or actor.rect.bottom == 600:
            actor.velocity[1] *= -1

        # Add actors rect to quadtree query
        collisions = quadtree.query_range(actor.rect)

        # Quadtree collisions (less than looping over each actors against each other)
        for collision in collisions:
            # Collided?
            if actor.rect.colliderect(collision):
                # Undo previous frame displacement
                actor.rect.x -= actor.velocity[0]
                actor.rect.y -= actor.velocity[1]
                # Flip velocity
                actor.velocity[0] *= -1
                actor.velocity[1] *= -1

    # Show Quadtree structure (boundaries)
    quadtree.show(display_surface)

    # Render actors
    for actor in actors_list:
        pg.draw.rect(display_surface, "red", actor.rect)

    pg.display.update()
