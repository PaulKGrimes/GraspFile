#!/usr/bin/env python
#
# GRASP_cut.py
#
# P. Grimes, March 2009
#
# Class to read, write and manipulate GRASP cut files
#

import string
import GraspCut

class GraspCutFile:
    """Class for reading, holding, manipulating and writing GRASP 9.3 format 
    output cut files"""
    def __init__(self):
        self.filename = ""
        self.cuts = []
        self.cut_type = "spherical"
        
    def read(self, filename):
        '''Open filename, read the contents and parse into cut objects'''
        self.filename = filename
        file = open(self.filename)
        text = file.readlines()
        
        temp_text = []
        # Read through the file, splitting the lines into separate cuts
        for line in text:
            if len(line) < 10:
                # We have the start of a new cut
                # Have we already collected a cut?
                if temp_text != []:
                    # Create new cut
                    new_cut = GraspCut.GraspCut()
                    new_cut.read(temp_text)
                    self.cuts.append(new_cut)
                    temp_text = []
            
            temp_text.append(line)
        
        # Append the last cut to the file
        if temp_text !=[]:
            new_cut = GraspCut.GraspCut()
            new_cut.read(temp_text)
            self.cuts.append(new_cut)
            
        file.close()


    def selectPosRange(self, pos_min, pos_max):
        '''Return a new cut file object containing only the parts of 
        each cut between pos_min and pos_max inclusive'''
        newcf = GraspCutFile()
        newcf.filename = self.filename
        newcf.cut_type = "spherical"
        for cut in self.cuts:
            newcf.cuts.append(cut.selectPosRange(pos_min, pos_max))
            
        return newcf
