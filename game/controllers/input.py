import pygame


class InputController:
    def __init__(self):
        self.left = False
        self.right = False
        self.jump = False
        self.start = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.left = True
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.right = True
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.jump = True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.start = True

    def consume(self):
        data = (self.left, self.right, self.jump, self.start)
        self.left = False
        self.right = False
        self.jump = False
        self.start = False
        return data
