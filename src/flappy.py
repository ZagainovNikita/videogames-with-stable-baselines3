import asyncio
import sys

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from .entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window


class Flappy:
    def __init__(self, fps=90000):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=fps,
            window=window,
            images=images,
            sounds=Sounds(),
        )

    def start(self):
        while True:
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.player = Player(self.config)
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            self.score = Score(self.config)
            self.play()
            self.game_over()

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    def play(self):
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)

        while True:
            if self.player.collided(self.pipes, self.floor):
                return 1

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    self.player.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()

            pygame.display.update()
            # await asyncio.sleep(0)
            self.config.tick()
            
    def reset(self):
        # Recreate game objects
        self.background = Background(self.config)
        self.floor = Floor(self.config)
        self.player = Player(self.config)
        self.welcome_message = WelcomeMessage(self.config)
        self.game_over_message = GameOver(self.config)
        self.pipes = Pipes(self.config)
        self.score = Score(self.config)
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)
        
        self.background.tick()
        self.floor.tick()
        self.pipes.tick()
        self.score.tick()
        self.player.tick()

        pygame.display.update()
        # await asyncio.sleep(0)
        self.config.tick()
    
        # Process any pending events
        pygame.event.get()
        
        # Update display
        pygame.display.update()
        
        # Return observation
        obs = pygame.surfarray.array3d(self.config.screen)
        return obs, {}
            
    def step(self, action):
        # Reset done flag
        done = False
        reward = 0
        
        # Check if player crossed a pipe
        for i, pipe in enumerate(self.pipes.upper):
            if self.player.crossed(pipe):
                self.score.add()
                reward += 10

        # Perform action
        if action == 1:
            self.player.flap()

        # Move game objects
        self.background.tick()
        self.floor.tick()
        self.pipes.tick()
        self.score.tick()
        self.player.tick()

        # Update display
        pygame.display.update()
        self.config.tick()
        
        obs = pygame.surfarray.array3d(self.config.screen)
        
        # Check if player collided
        if self.player.collided(self.pipes, self.floor):
            # self.game_over_env()
            return obs, -100, True, {}
            
        # Return observation, reward, done flag, and additional info
        return obs, reward, done, {}

    def game_over(self):
        """crashes the player down and shows gameover image"""

        self.player.set_mode(PlayerMode.CRASH)
        self.pipes.stop()
        self.floor.stop()

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.game_over_message.tick()

            self.config.tick()
            pygame.display.update()
            # await asyncio.sleep(0)
            