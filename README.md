This Python package contains modules for reading and writing data files from/to TICRA GRASP.  The package is believed to work with at least GRASP 19 to 21.

This package is not affiliated with TICRA in any way.

I've not been able to actively maintain this project since ~2019, but if it is useful to you, please fork it and feel free to open issues and pull requests for
incorporation into the main project.  The latest version of GRASP that I have access to is 21.0, so I cannot check compatibility with more recent versions.

# Usage

Example usage, pulled from one of my Jupyter notebooks set up for analysing GRASP results

## Grids
```
import fileinput as fi
import matplotlib.pyplot as plt
import numpy as np

from GraspFile import GraspGrid

with fi.input("filename.grd") as gridFile:
  grid = GraspGrid.GraspGrid()
  grid.readGraspGrid(gridFile)

# pick which field from the file to display
#
# Grid objects contain a list of fields. Each field object contains a numpy array of the field data (.field), plus metadata.
# The metadata name is roughly consistent with that given for the file formats in the GRASP manual, but has been pythonized
# and somewhat converted to camelCase.
field = grid.fields[n]

# pick polarization component to display
#
# The third index of the field's field numpy array is the polarization
component = 0

# Plot a 2d image of the field
#
# Use the field metadata to set the size of the image plot.
plt.imshow((20*np.log10(abs(field.field[:,:,component]))), extent=[field.gridMin_x, field.gridMax_x, field.gridMin_y, field.gridMax_y])
```
