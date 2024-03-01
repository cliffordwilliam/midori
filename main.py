import pygame as pg
from sys import exit
from random import randint
import time


class Quadtree:
    def __init__(self, capacity, boundary_rect):
        self.capacity = capacity
        self.boundary_rect = boundary_rect
        self.rects_list = []
        self.tl_quadtree = None
        self.tr_quadtree = None
        self.bl_quadtree = None
        self.br_quadtree = None

    def subdivide(self):
        x, y, w, h = self.boundary_rect
        half_w = w // 2
        half_h = h // 2

        tl_rect = pg.Rect(x, y, half_w, half_h)
        tr_rect = pg.Rect(x + half_w, y, half_w, half_h)
        bl_rect = pg.Rect(x, y + half_h, half_w, half_h)
        br_rect = pg.Rect(x + half_w, y + half_h, half_w, half_h)

        self.tl_quadtree = Quadtree(self.capacity, tl_rect)
        self.tr_quadtree = Quadtree(self.capacity, tr_rect)
        self.bl_quadtree = Quadtree(self.capacity, bl_rect)
        self.br_quadtree = Quadtree(self.capacity, br_rect)

        for i in range(len(self.rects_list)):
            self.tl_quadtree.insert(self.rects_list[i])
            self.tr_quadtree.insert(self.rects_list[i])
            self.bl_quadtree.insert(self.rects_list[i])
            self.br_quadtree.insert(self.rects_list[i])

    def insert(self, rect):
        if not self.boundary_rect.collidepoint(rect.center):
            return False

        if len(self.rects_list) < self.capacity and self.tl_quadtree is None:
            self.rects_list.append(rect)
            return True

        else:
            if self.tl_quadtree is None:
                self.subdivide()

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
        rects_in_range = []

        if not self.boundary_rect.colliderect(given_rect):
            return rects_in_range

        for rect in self.rects_list:
            if given_rect != rect and given_rect.colliderect(rect):
                rects_in_range.append(rect)

        if self.tl_quadtree is not None:
            rects_in_range.extend(self.tl_quadtree.query_range(given_rect))
            rects_in_range.extend(self.tr_quadtree.query_range(given_rect))
            rects_in_range.extend(self.bl_quadtree.query_range(given_rect))
            rects_in_range.extend(self.br_quadtree.query_range(given_rect))

        return rects_in_range

    def reset(self):
        if self.tl_quadtree is not None:
            self.tl_quadtree = None
            self.tr_quadtree = None
            self.bl_quadtree = None
            self.br_quadtree = None


pg.init()
display_surface = pg.display.set_mode((800, 600))
clock = pg.time.Clock()


class Actor:
    def __init__(self):
        self.velocity = [randint(-5, 5), randint(-5, 5)]
        x = randint(0, 800 - 16)
        y = randint(0, 600 - 16)
        self.rect = pg.Rect(randint(0, 800 - 16), randint(0, 600 - 16), 16, 16)


actors_list = []
for _ in range(20):
    actors_list.append(Actor())

quadtree = Quadtree(4, pg.Rect(0, 0, 800, 600))

while True:
    clock.tick(60)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

    display_surface.fill("black")

    for actor in actors_list:
        quadtree.insert(actor.rect)

    for actor in actors_list:
        actor.rect.x += actor.velocity[0]
        actor.rect.y += actor.velocity[1]

        actor.rect.left = max(0, min(actor.rect.left, 800 - actor.rect.width))
        actor.rect.top = max(0, min(actor.rect.top, 600 - actor.rect.height))

        if actor.rect.left == 0 or actor.rect.right == 800:
            actor.velocity[0] *= -1
        if actor.rect.top == 0 or actor.rect.bottom == 600:
            actor.velocity[1] *= -1

        collisions = quadtree.query_range(actor.rect)
        for collision in collisions:
            if actor.rect.colliderect(collision):
                actor.rect.x -= actor.velocity[0]
                actor.rect.y -= actor.velocity[1]

                actor.velocity[0] *= -1
                actor.velocity[1] *= -1

    quadtree.reset()

    for actor in actors_list:
        pg.draw.rect(display_surface, actor.color, actor.rect)

    pg.display.update()
