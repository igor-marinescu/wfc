# WFC - Wavefunction Collapse Algorithm

![Alt Intro](/docs/wfc_demo.gif)

![Alt Intro](/docs/wfc_intro.png)

WFC is a simple implementation of a Wavefunction-Collapse algorithm. Written entirely in Python, it takes a set of Tiles as input and procedurally generates an output image. 

# Install and run

Download the code to your computer. (Be sure Python is installed. If not, install it.)   
Go to the project folder, create the virtual environment and install the requirements:
```sh
C:\test\wfc> python -m venv venv
C:\test\wfc> venv\Scripts\activate
C:\test\wfc> pip install -r requirements.txt
```
Run the algorithm:
```sh
C:\test\wfc> python -m wfc_src
```

## Controls

| Key | Function |
| --- | -------- |
| c | Clear the input set |
| 1 | Generate output image (slow/animation mode) |
| 2 | Generate output image (instant mode) |

# Algorithm breakdown

![Alt Tile-Definition](/docs/wfc_diagrams.png)

The algorithm generates an output image from a small number of predefined squares, called Tiles. Each Tile is a 64x64 pixel image (see Fig.1). The algorithm accepts as input the tile atlas - an image containing the complete set of Tiles. It analyzes the atlas and extracts all Tiles out of it. It parses, analyzes the markers and derives from them how Tiles are allowed to be arranged.

A Tile definition is a *(T,R,B,L)* set - the format of its four edges: top, right, bottom and left. The four markers (pixels) are used to specify the configuration of each edge (see Fig.2 and Fig.3). Two Tiles can be connected if their opposite edges have the same configuration (see Fig.4).

The algorithm starts by defining a NxM matrix of Cells. Every Cell is a placeholder for a Tile in the output image. Initially all Cells in the output image are in superposition - each can hold all possible Tiles. In process of collapsing the wave-function the Cells lose the entropy (the incompatible Tiles are removed from the list of possible placeholders) until the Cells collapse (only one possible Tile remains). See Fig.5.

![Alt Tile-Definition](/docs/wfc_collapse.png)

We initialize a wave-function. We collapse one Cell and propagate the consequences of this collapse throughout the rest of the Cells. The Cell neighbor of a collapsed Cell loses entropy (the Tiles which cannot be connected to the collapsed Cell are deleted from its list of possible Tiles). 

At each step we sequentially take not collapsed Cells (from lowest to highest entropy, see Fig.6) and delete the incompatible Tiles from their list. If no Tiles were deleted from any of the Cells in a step, the Cell with the lowest entropy collapses into a random Tile from its list of possibilities.

The process is repeated until every Cell's wave-function is collapsed (it has only one Tile possible for it) and the output image is generated.

## In a nutshell:

1. Parse Tile-atlas and extract all Tiles. Create a definition for each Tile based on markers.
2. Create an array of NxM Cells. It will result in an output image at the end. Every Cell has the highest entropy (a list of all possible Tiles). 
3. Collapse Cells from input set if defined, if not collapse a random Cell (select a random Tile for it).
4. Mark all Cells as not processed.
5. Select a not collapsed and not processed Cell with lowest entropy.
    - If all Cells are collapsed -> exit algorithm.
    - If no more not processed Cells -> jump to step 9
6. For each of the four neighbors of selected Cell: 
    - Remove the Tiles that are incompatible with the selected Cell. 
    - If the neighbor Cell has only one Tile left - it collapsed. 
7. Mark the selected Cell as processed.
8. Jump to step 5
9. If no Tiles have been removed since step 4:
    -  Select a Cell with lowest entropy and collapse it (set to a random Tile from its list of possibilities).
10. Jump to step 4.

# Author and license

Igor Marinescu  
GNU GPL3. See the [LICENSE.md](LICENSE.md) file for details.


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen.)

# Links and info

<https://robertheaton.com/2018/12/17/wavefunction-collapse-algorithm/>  
<https://github.com/mxgmn/WaveFunctionCollapse>  
<https://developer.mozilla.org/en-US/docs/Games/Techniques/Tilemaps>  
<https://www.pygame.org>
