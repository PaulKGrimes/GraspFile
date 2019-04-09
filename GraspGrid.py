# GraspGrid.py
#
# Paul Grimes, March 2009
#
# Module to read GRASP output grids into numpy arrays
# Ported from GRASP Reference Manual page F25
#
# The function stores each record as a list over datasets with the file
# the number of datasets is stored in nset
#
# Currently assumes that file is of type "formatted"


import numpy, math
import matplotlib.pyplot as pp

class GraspField:
    """Object holding a single dataset from a Grasp field on grid output file (*.grd)
    
    The filed is held in a complex numpy array of shape (gridN_x, gridN_y, ncomp)
    where gridN_x and gridN_y set the number of points in the grid and ncomp is the
    number of field components"""
    # This layout of array should mean that the polarisation components for a point 
    # are contiguous memory, allowing rapid calculation of stokes parameters, etc.
  
    def __init__(self):
        # initialize storage variables
        # Beam centre in [x,y] form
        self.beamCentre = [0.0,0.0]
    
        # Grid parameters
        self.gridMin_x = 0.0
        self.gridMin_y = 0.0
        self.gridMax_x = 0.0
        self.gridMax_y = 0.0
        self.gridN_x = 0
        self.gridN_y = 0
        self.kLimit = 0   # Is grid sparse (0=filled, 1=sparse)
    
        # the field object is numpy array of shape (gridN_x, gridN_y, ncomp)
        self.field = None

    def readGraspField(self, f, ncomp):
        """Reads the Grasp dataset from the file object passed in.  This assumes that
        it is being called from the graspGrid classes readGraspGrid(f) method, so that
        the file object is already at the start of the record"""
        
        # find the grid physical extents
        line = f.readline().split()
        self.gridMin_x = float(line[0])
        self.gridMin_y = float(line[1])
        self.gridMax_x = float(line[2])
        self.gridMax_y = float(line[3])
        self.ncomp = ncomp
    
        # find the number of points in the grid
        line = f.readline().split()
        self.gridN_x = int(line[0])
        self.gridN_y = int(line[1])
        self.kLimit = int(line[2])
        
        self.gridStep_x = (self.gridMax_x - self.gridMin_x) / (self.gridN_x - 1)
        self.gridStep_y = (self.gridMax_y - self.gridMin_y) / (self.gridN_y - 1)
        
        # We can now initialise the numpy arrays to hold the field data
        self.field = numpy.zeros(shape=(self.gridN_x, self.gridN_y, self.ncomp), dtype=numpy.complex)
        
        for j in range(self.gridN_y):
            # If kLimit is 1 then rows of grid are sparse (i.e. limited length)
            # read the limits from each line before reading in data
            if self.kLimit == 1:
                line = f.readline().split()
                i_s = int(line[0])-1
                i_e = int(line[1])-1
            else:
                i_s = 0
                i_e = self.gridN_x
      
            # Read in the data
            for i in range(i_s, i_e):
                line = f.readline().split()
                if self.ncomp == 2:
                    self.field[j,i,0] = complex(float(line[0]), float(line[1]))
                    self.field[j,i,1] = complex(float(line[2]), float(line[3]))
                else:
                    self.field[j,i,0] = complex(float(line[0]), float(line[1]))
                    self.field[j,i,1] = complex(float(line[2]), float(line[3]))
                    self.field[j,i,2] = complex(float(line[4]), float(line[5]))
  
        return 0
    
    def indexRadialDist(self, i, j):
        """Return radial distance from the beam center to an element of the field.
        
        Useful for calculating the integrated power in a beam within a certain radius."""
        pos_x = self.gridMin_x + self.gridStep_x * i
        pos_y = self.gridMin_y + self.gridStep_y * j
        
        off_x = pos_x - self.beamCentre[0]
        off_y = pos_y - self.beamCentre[1]
        
        return numpy.sqrt(off_x**2 + off_y**2)
        
    def gridPos(self):
        """Return meshed grids of the x and y positions of each point in the field"""
        return numpy.meshgrid(numpy.linspace(self.gridMin_x, self.gridMax_x, self.gridN_x), \
                            numpy.linspace(self.gridMin_y, self.gridMax_y, self.gridN_y))
    
    def radiusGrid(self, center=None):
        """Return an array holding the radiuses of each point from the beam centre"""
        grid_x, grid_y = self.gridPos()
        
        if center==None:
            center = self.beamCentre
        
        return numpy.sqrt((grid_x-center[0])**2 + (grid_y-center[1])**2)
        
    
# The main file object class
class GraspGrid:
    """Object holding the data in contained in a general Grasp grid field output"""
    def __init__(self):
        """Create empty variables or lists of attributes for haolding data for each dataset"""
        # Text Header
        self.header = ""
    
        # File Type parameters
        self.ktype = 0  # type of file format
        self.nset = 0   # number of datasets
        self.icomp = 0  # type of field components
        self.ncomp = 0  # number of field components
        self.igrid = 0  # grid type
    
        # List of field objects
        self.fields = []
    
    
    def readGraspGrid(self, fi):
        """Reads GRASP output grid files from file object and fills a number of variables 
        and numpy arrays with the data, befroe returning them as a tuple"""
    
        # Loop over initial lines before "++++" getting text
        self.header = ""
    
        while 1:
            line = fi.readline()
            if line[0:4] == "++++":
                break
            else:
                self.header = self.header + line

        # Parse the header to get the frequency information
        for line in self.header.split("\n"):
            term, arg, res = line.partition(":")
            # print term
            if term.strip() == "FREQUENCY":
                # print line
                first, arg, rest = res.partition(":")
                if first.strip() == "start_frequency":
                    # print rest
                    # We have a frequency range
                    start, stop, num_freq = rest.rsplit(",")
                    self.freqs = numpy.linspace(float(start.split()[0]), float(stop.split()[0]), int(num_freq))
                else:
                    # We probably have a list of frequencies
                    # print res
                    freqStrs = res.rsplit("'")
                    freqs = []
                    for f in freqStrs:
                        freqs.append(float(f.split()[0]))
                    self.freqs = numpy.array(freqs)
                break
        
        # We've now got through the header text and are ready to read the general
        # field type parameters
        self.ktype = int(fi.readline())
        line = fi.readline().split()
        self.nset = int(line[0])
        self.icomp = int(line[1])
        self.ncomp = int(line[2])
        self.igrid = int(line[3])
        
        self.beamCenters = []
        for i in range(self.nset):
            line = fi.readline().split()
            self.beamCenters.append([int(line[0]), int(line[1])])
            
        # field type parameters are now understood
        # we now start reading the individual fields
        for i in range(self.nset):
            dataset = GraspField()
            dataset.beamCenter = self.beamCenters[i]
            dataset.readGraspField(fi, self.ncomp)
            self.fields.append(dataset)

