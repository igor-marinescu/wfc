# This file is part of the WFC distribution.
# Copyright (c) 2020 Igor Marinescu (igor.marinescu@gmail.com).
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
#-------------------------------------------------------------------------------
# Tiles:
# Tile is a small 64x64 pixels image. The final image is rendered using a set of tiles.
# Beside image, a tile contains also a definition, which allows the algorithm
# to decide how to correctly connect the tiles between them.
#
# Tile definition is a (T,R,B,L) tuple, where every element is the definition
# of the corresponding edge:
#       T=Top edge, R=Right edge, B=Bottom edge, L=Left edge:
#
#   T=0 +---+---+   T=1 +---+---+   T=2 +---+---+   T=3 +---+---+
#       | 0 | 0 |       | 1 | 0 |       | 0 | 1 |       | 1 | 1 |
#       +---+---+       +---+---+       +---+---+       +---+---+
#       | * | * |       | * | * |       | * | * |       | * | * |
#       +---+---+       +---+---+       +---+---+       +---+---+
#
#   R=0 +---+---+   R=1 +---+---+   R=2 +---+---+   R=3 +---+---+
#       | * | 0 |       | * | 1 |       | * | 0 |       | * | 1 |
#       +---+---+       +---+---+       +---+---+       +---+---+
#       | * | 0 |       | * | 0 |       | * | 1 |       | * | 1 |
#       +---+---+       +---+---+       +---+---+       +---+---+
#
#   B=0 +---+---+   B=1 +---+---+   B=2 +---+---+   B=3 +---+---+
#       | * | * |       | * | * |       | * | * |       | * | * |
#       +---+---+       +---+---+       +---+---+       +---+---+
#       | 0 | 0 |       | 1 | 0 |       | 0 | 1 |       | 1 | 1 |
#       +---+---+       +---+---+       +---+---+       +---+---+
#
#   L=0 +---+---+   L=1 +---+---+   L=2 +---+---+   L=3 +---+---+
#       | 0 | * |       | 1 | * |       | 0 | * |       | 1 | * |
#       +---+---+       +---+---+       +---+---+       +---+---+
#       | 0 | * |       | 0 | * |       | 1 | * |       | 1 | * |
#       +---+---+       +---+---+       +---+---+       +---+---+
# Example:
#   A Tile with definition (2,3,3,2) is a Tile which looks like:
#   +---+---+
#   | 0 | 1 |
#   +---+---+
#   | 1 | 1 |
#   +---+---+
#
# Two Tiles can be connected if they have the same opposite edges:
#   connected vertical:     Tile1.T == Tile2.B
#   connected hotizontal:   Tile1.R == Tile2.L
#
# Example, the following two Tiles can be connected horizontal:
#                  (T,R,B,L)         (T,R,B,L)
#            Tile1=(2,3,3,2),  Tile2=(1,2,3,3)
#
#                  +---+---+         +---+---+
#                  | 0 | 1 |  <----- | 1 | 0 |
#                  +---+---+         +---+---+
#                  | 1 | 1 |  <----- | 1 | 1 |
#                  +---+---+         +---+---+
#
# The definitions for all Tiles are stored in a list, where every element
# is a Tile defined by a (T,R,B,L) tuple:
#   tiles_def = [ (T0,R0,B0,L0), (T1,R1,B1,L1), (T2,R2,B2,L2), ... ]
#                 |<-  tile0  ->|<--  tile1  -->|<-- tile2 -->| ...
#
#-------------------------------------------------------------------------------
# Modification history:
#
# 03.08.2022 10:04:01 - pylint check and fixes
#
#-------------------------------------------------------------------------------
""" Tiles Manager Module. """

import os.path
import random
import time
from functools import wraps

import pygame

# ##############################################################################
def timethis(func):
    '''
    Decorator that reports the execution time.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result
    return wrapper

TY_OUT = 12 #8
TX_OUT = 12 #8

# ##############################################################################
class Cell:
    """ Tiles Cell definition """

    def __init__(self, p_list, changed = False):
        self.processed = False          # the cell has been processed
        self.changed = changed          # the cell has been changed
        self.poss_list = list(p_list)   # list of possibilities for this cell

    def get_entropy(self):
        ''' Return Cell's entropy (number of possible Tiles for this Cell).
        '''
        return len(self.poss_list)

# ##############################################################################
class TilesManager:
    """ Tiles Manager """

    def __init__(self, path):
        """ Init Tales Manager """
        self.path = path

        self.tiles_def = []     # Tiles Definitions
        self.tiles_img = []     # Tiles Images
        self.disp_idx = [[0    for x in range(TX_OUT)] for y in range(TY_OUT)]
        self.disp_img = [[None for x in range(TX_OUT)] for y in range(TY_OUT)]
        self.img_many = None
        self.img_none = None
        self.img_last = None
        self.img_entr = []      # Entropy image
        self.val_entr = []      # Entropy value
        self.last_y = None
        self.last_x = None

        self.tl_idx_list = []     # List of Tiles Definitions Indexes

        # Generate an empty array (all cells have all possibilities)
        self.cell_arr = [[Cell(self.tl_idx_list) for x in range(TX_OUT)] for y in range(TY_OUT)]

        pygame.font.init() # you have to call this at the start, if you want to use this module.
        self.myfont = pygame.font.SysFont('Courier New', 16)

        self.color_dict = {}

    def get_color_idx(self, surface, x_pos, y_pos):
        ''' Get color index from surface at a specified position (x_pos, y_pos).
        If color not already in the dictionary, add it and assign a index.'''

        color_test = tuple(surface.get_at((x_pos, y_pos)))
        if color_test not in self.color_dict:
            # Color not in dictionary, add it and assign a index (length)
            self.color_dict[color_test] = len(self.color_dict)
            print("Color added: ", color_test, self.color_dict[color_test])
        return self.color_dict[color_test]

    def decode_tile(self, j, i, surface):
        """ Decode a Tile """
        # Tile (T, R, B, L) definitions
        tile = [0, 0, 0, 0]

        color_idx = self.get_color_idx(surface, 1, 1)
        if color_idx != 0:
            tile[0] += (8 * color_idx) # Top
            tile[3] += (8 * color_idx) # Left

        color_idx = self.get_color_idx(surface, 1, 62)
        if color_idx != 0:
            tile[2] += (8 * color_idx)  # Bottom
            tile[3] += (1 * color_idx)  # Left

        color_idx = self.get_color_idx(surface, 62, 1)
        if color_idx != 0:
            tile[0] += (1 * color_idx)  # Top
            tile[1] += (8 * color_idx)  # Right

        color_idx = self.get_color_idx(surface, 62, 62)
        if color_idx != 0:
            tile[1] += (1 * color_idx)  # Right
            tile[2] += (1 * color_idx)  # Bottom

        self.tiles_def.append(tuple(tile))
        self.tiles_img.append(surface)
        print(len(self.tiles_def), j, i, tile)

    def load_tiles(self, filename, special_img, ty_cnt, tx_cnt):
        """ Load all Tiles from image file, decode them and append to existing list """

        # open image
        fullname = os.path.join('', self.path + filename)
        try:
            img_surface = pygame.image.load(fullname)
        except pygame.error as message:
            print('Cannot load image:', fullname)
            raise SystemExit(message)

        img_surface = img_surface.convert()
        #img_rect = img_surface.get_rect()

        # get reference colorkey (point 0, 0)
        ref_colorkey = img_surface.get_at((0, 0))
        img_surface.set_colorkey(ref_colorkey, pygame.RLEACCEL)

        # How many full 64x64 Tiles are in the image
        #ty_cnt = 9  #int(imgRect[3]/64)
        #tx_cnt = 10 #int(imgRect[2]/64)

        # Extract every 64x64 Tile from image
        for j in range(ty_cnt):
            for i in range(tx_cnt):

                # Tile image
                surface = pygame.Surface((64, 64))
                surface.blit(img_surface, (0, 0), ((i * 64), (j * 64), 64, 64))
                surface.set_colorkey((0, 0, 0))
                self.decode_tile(j, i, surface)

                surface = pygame.transform.flip(surface, True, False)
                surface = pygame.transform.rotate(surface, 90)
                self.decode_tile(j, i, surface)

        print("Total colors:", len(self.color_dict))
        self.tl_idx_list = list(range(len(self.tiles_def)))

        # Extract special images
        if special_img:
            # many possibilities
            surface = pygame.Surface((64, 64))
            surface.blit(img_surface, (0, 0), ((0 * 64), (9 * 64), 64, 64))
            surface.set_colorkey((0, 0, 0))
            self.img_many = surface
            # no possibilities
            surface = pygame.Surface((64, 64))
            surface.blit(img_surface, (0, 0), ((0 * 64), (9 * 64), 64, 64))
            surface.set_colorkey((0, 0, 0))
            self.img_none = surface
            # last processed
            surface = pygame.Surface((64, 64))
            surface.blit(img_surface, (0, 0), ((1 * 64), (9 * 64), 64, 64))
            surface.set_colorkey((0, 0, 0))
            self.img_last = surface
            # entropy images
            for i in range(5):
                surface = pygame.Surface((64, 64))
                surface.blit(img_surface, (0, 0), (((i + 2) * 64), (9 * 64), 64, 64))
                surface.set_colorkey((0, 0, 0))
                self.img_entr.append(surface)
                # calculate threshold for every entropy image
                self.val_entr.append(int(len(self.tiles_def)/5) * (i + 1))

    def process_neighbor_cell(self, y_pos, x_pos, y_rel, x_rel, side_idx, main_set):
        """ Process neighbor cell. Generate the list of new possible Tiles
            for this neighbor cell based on set of possible sides of the main cell.
            y_pos - y-position of the main cell
            x_pos - x-position of the main cell
            y_rel - y-relative-position of the neighbor cell
            x_rel - x-relative-position of the neighbor cell
            side_idx - index of the neighbor side to be cheked (0=top, 1=right, 2=bottom, 3=left)
            main_set - set of possible sides for the main cell
        """
        cell = self.cell_arr[y_pos + y_rel][x_pos + x_rel]
        # get the list of all possible Tiles for neighbor cell
        lst0 = cell.poss_list
        len0 = len(lst0)
        # process only cells with more than one possibility
        if len0 > 1:
            # create a new list, but only with Tiles which can be connected to main cell
            lst1 = [x for x in lst0 if self.tiles_def[x][side_idx] in main_set]
            # deadend detected? (no more valid possibilities)
            if len(lst1) == 0:
                # create "artificially" the null-cell
                lst1 = [0]
                print("Deadend: ", y_pos, x_pos, y_rel, x_rel, side_idx, main_set)
            # set the new list as possibilities for the neighbor cell
            cell.poss_list = lst1
            # mark neighbor as changed if list of possible Tiles for this cell changed
            if not cell.changed:
                cell.changed = (len0 != len(lst1))

    def process_cell(self, y_idx:int, x_idx:int):
        ''' Process cell with coordinates y_idx, x_idx .
            Create sets for every side with all possible Tiles for this cell.
            Check four neighbor cells (top, right, bottom, left) and remove Tiles
            which cannot be connected to this (center) cell.
        '''
        # list of all possible Tiles for this cell
        cell = self.cell_arr[y_idx][x_idx]
        lst = cell.poss_list

        # create sets with all possibilities for all sides
        u_set = {self.tiles_def[tile_idx][0] for tile_idx in lst}
        r_set = {self.tiles_def[tile_idx][1] for tile_idx in lst}
        b_set = {self.tiles_def[tile_idx][2] for tile_idx in lst}
        l_set = {self.tiles_def[tile_idx][3] for tile_idx in lst}

        # check neighbor cell on top side (j-1,i+0)
        # main cell top side (u_set) vs neighbor cell bottom side (2)
        if y_idx > 0:
            self.process_neighbor_cell(y_idx, x_idx, -1, 0, 2, u_set)

        # check neighbor cell on right side (j+0,i+1)
        # main cell right side (r_set) vs neighbor cell left side (3)
        if x_idx < (TX_OUT - 1):
            self.process_neighbor_cell(y_idx, x_idx, 0, 1, 3, r_set)

        # check neighbor cell on bottom side (j+1,i+0)
        # main cell bottom side (b_set) vs neighbor cell top side (0)
        if y_idx < (TY_OUT - 1):
            self.process_neighbor_cell(y_idx, x_idx, 1, 0, 0, b_set)

        # check neighbor cell on left side (j+0,i-1)
        # main cell left side (l_set) vs neighbor cell right side (1)
        if x_idx > 0:
            self.process_neighbor_cell(y_idx, x_idx, 0, -1, 1, l_set)

        # mark cell as processed
        cell.processed = True

    def find_min_entropy_cell(self, changed):
        ''' Find not processed cell with min entropy (min possible Tiles for it).
        '''
        # initially: set min to max entropy (= length of list of all Tiles)
        min_e = len(self.tiles_def)
        min_y = None
        min_x = None
        for j in range(TY_OUT):
            for i in range(TX_OUT):
                # if value less than min and not processed
                cell = self.cell_arr[j][i]
                if (min_e >= cell.get_entropy()) and not cell.processed and (cell.changed == changed):
                    min_e = cell.get_entropy()
                    min_y = j
                    min_x = i
        return min_y, min_x

    def mark_not_processed(self):
        ''' Mark all not-collapsed cells (with more than one possible Tile) as not processed.
        '''
        for lst in self.cell_arr:
            for cell in lst:
                # if Cell not collapsed, mark cell as not processed and not changed
                if cell.get_entropy() > 1:
                    cell.changed = False
                    cell.processed = False

    def next_step(self):
        ''' Next step in collapsing the wave-function.
        '''
        # Find next not processed and unchanged cell with minimal entropy
        min_y, min_x = self.find_min_entropy_cell(changed = True)
        if (min_y is not None) and (min_x is not None):
            # and process that cell
            self.process_cell(min_y, min_x)
            self.last_x = min_x
            self.last_y = min_y
        else:
            # No more possibilities.
            # Mark all cells with >1 possibilities as not processed.
            self.mark_not_processed()
            # Find cell with minimal number of possibilities
            # and collapse it (select a random Tile for it).
            min_y, min_x = self.find_min_entropy_cell(changed = False)
            if (min_y is not None) and (min_x is not None):
                cell = self.cell_arr[min_y][min_x]
                val_r = random.choice(cell.poss_list)
                cell.poss_list = [val_r]
                cell.changed = True
            else:
                print("Finish!")
                self.last_x = None
                self.last_y = None
                return False
        return True

    # ##########################################################################
    # Extern methods
    # ##########################################################################

    def clear(self):
        """ Clear all cells
        """
        self.cell_arr = [[Cell(self.tl_idx_list) for x in range(TX_OUT)] for y in range(TY_OUT)]

    def set_cell(self, y_pos, x_pos, val):
        """ Set value for a cell at specified position
        """
        cell = self.cell_arr[y_pos][x_pos]
        cell.poss_list = [val]
        cell.changed = True
        cell.processed = False

    @timethis
    def generate(self):
        """ Generate
        """
        while self.next_step():
            pass

    def shift_down(self):
        """ Shift all cells one row down, the bottom row is lost,
        a new row appears on top.
        """
        del self.cell_arr[-1]
        self.cell_arr.insert(0, [Cell(self.tl_idx_list) for x in range(TX_OUT)])
        # mark all cells as not processed
        for cell in self.cell_arr[1]:
            cell.processed = False

    def shift_up(self):
        """ Shift all cells one row up, the upper row is lost,
        a new row appears on bottom.
        """
        del self.cell_arr[0]
        self.cell_arr.append([Cell(self.tl_idx_list) for x in range(TX_OUT)])
        # mark all cells as not processed
        for cell in self.cell_arr[-2]:
            cell.processed = False

    # ##########################################################################
    def get_entropy_image(self, entropy):
        ''' Get Cell image based on its entropy. 
        '''
        if entropy < self.val_entr[0]:
            return self.img_entr[0]
        if entropy < self.val_entr[1]:
            return self.img_entr[1]
        if entropy < self.val_entr[2]:
            return self.img_entr[2]
        if entropy < self.val_entr[3]:
            return self.img_entr[3]
        return self.img_entr[4]

    def draw(self, surface):
        """ Draw all Tiles on a surface
        """
        for j in range(TY_OUT):
            for i in range(TX_OUT):
                cell = self.cell_arr[j][i]
                lst = cell.poss_list
                lst_len = len(lst)
                img = None
                if lst_len == 0:
                    img = self.img_none
                elif lst_len > 1:
                    #img = self.img_many
                    img = self.get_entropy_image(lst_len)
                else:
                    img = self.tiles_img[lst[0]]
                if img is not None:
                    surface.blit(img, ((i * 64), (j * 64)))

                # Last processed
                if (self.last_x is not None) and (self.last_y is not None):
                    surface.blit(self.img_last, ((self.last_x * 64), (self.last_y * 64)))

                # text: possibilities
                #textsurface = self.myfont.render(str(lst_len), False, (200, 200, 200))
                #if lst_len <= 0:
                #    textsurface = self.myfont.render("X", False, (200, 200, 200))
                #elif lst_len > 1:
                #    textsurface = self.myfont.render("?", False, (200, 200, 200))
                #else:
                #    textsurface = self.myfont.render(str(lst[0]), False, (200, 200, 200))
                #surface.blit(textsurface, ((i * 64) + 4, (j * 64)))

                # text: processed
                #if(cell.processed):
                #    textsurface = self.myfont.render("P", False, (150, 150, 150))
                #    surface.blit(textsurface, ((i * 64), (j * 64) + 16))

                # text: changed
                #if(cell.changed):
                #    textsurface = self.myfont.render("C", False, (150, 150, 150))
                #    surface.blit(textsurface, ((i * 64), (j * 64) + 32))
