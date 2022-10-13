# This file is part of the WFC distribution.
# Copyright (c) 2022 Igor Marinescu (igor.marinescu@gmail.com).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
""" Wave Function Collapse Main """
import pygame

from . import tilesman

# ###############################################################################
# Main
# ###############################################################################
class WFC:
    """ Wave Function Collapse """

    def __init__(self, width, height, path):
        """ Init Module
        """
        self.width = width
        self.height = height
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption('WFC')
        #self.background = (25,32,49)
        #self.background = (17,43,52) #112b34
        self.background = (3,78,121) #034e79
        self.quit_flag = False

        # create tiles
        self.tiles_man = tilesman.TilesManager(path)
        self.tiles_man.load_tiles('/../resources/tiles_64x64_9.png', True, ty_cnt=9, tx_cnt=13)
        #self.tiles_man.printTiles()
        self.tiles_man.clear()

    def display(self):
        """ Draw scene on the surface.
        """
        # display background
        self.surface.fill(self.background)
        self.tiles_man.draw(self.surface)

    def run(self):
        """ Create a pygame surface until it is closed.
        """
        self.display()
        pygame.display.flip()

        # Initialize clock
        #clock = pygame.time.Clock()
        auto = False

        while not self.quit_flag:

            # Computes how many milliseconds have passed since previous call
            # The argument framerate makes the function to delay to keep the game running slower.
            # ex: clock.tick(60) -> doesn't run faster than 60 frames/sec (16ms)
            #clock.tick(60)
            #clock.tick(15)
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.quit_flag = True

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_flag = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.tiles_man.clear()
                    if event.key == pygame.K_q:
                        self.tiles_man.next_step()
                    if event.key == pygame.K_r:
                        self.tiles_man.clear()
                        self.tiles_man.set_cell(3, 3, 104)
                        self.tiles_man.set_cell(3, 4, 6)
                        self.tiles_man.set_cell(4, 3, 26)
                        self.tiles_man.set_cell(4, 4, 30 )

                        self.tiles_man.set_cell(9, 9, 48)
                        self.tiles_man.set_cell(9, 8, 46)

                    elif event.key == pygame.K_0:
                        auto = False
                    elif event.key == pygame.K_1:
                        auto = True
                    elif event.key == pygame.K_2:
                        self.tiles_man.generate()
                    elif event.key == pygame.K_DOWN:
                        self.tiles_man.shift_down()
                        self.tiles_man.generate()
                    elif event.key == pygame.K_UP:
                        self.tiles_man.shift_up()
                        self.tiles_man.generate()
                    elif event.key == pygame.K_s:
                        pygame.image.save(self.surface, 'out.png')

            if auto:
                auto = self.tiles_man.next_step()
            self.display()
            pygame.display.flip()
