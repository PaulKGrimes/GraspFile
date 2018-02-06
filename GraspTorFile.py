# A class to parse a GRASP Tor File
#
# Paul Grimes, 2018
#
# Since Tor file The data from the Tor file will be parsed into nested dictionaries
# Since I don't know if the order of the keys matters to GRASP, the dictionaries will
# be OrderedDicts so that order in the file is maintained for writing out.  No file
# should be so large that the performance hit of this is a concern.
#
# A typical entry in the tor file looks like this:
#
# SMA200_GaussianHorn_Output_cut  spherical_cut  
# (
#   coor_sys         : ref(Primary_coor),
#   theta_range      : struct(start: -1.0, end: 1.0, np: 1601),
#   phi_range        : struct(start: 0.0, end: 180.0, np: 9),
#   polarisation_modification : struct(status: on, coor_sys: ref(SMA200_Output_Beam_coor)),
#   near_dist        : 0.0 mm,
#   file_name        : " ",
#   frequency        : ref(Frequencies)
# )
#
# The first line consists of the name of the object, then the type.  The parameters of the object
# are contained between brackets.
#
# Comments in the file start with //


from collections import OrderedDict as odict


class GraspTorFile:
    """A class for parsing, storing and writing out GRASP Tor files"""
    def __init__(self, file=None):
        if file != None:
            self.read(file)
        else:
            pass
            
    def read(self, file):
        self._oDict = odict()
        
        commentID = 1
        
        # read file line by line
        while True:
            # Get line
            try:
                line = file.readline()
            except IOError:
                break
            
            # skip lines with only whitespace
            if line.strip():
                continue
            
            # Test to see if we have a comment or an object
            if line[0:2] == "//":
                # Create a comment and add to oDict
                commentObj = {"_type":"comment", "_text":line[2,]}
                self._oDict["comment{:s}".format(commentID)] = commentObj
                commentID += 1
            else:
                # We have the start of an object
                # Get the object name and type from first line
                newObj = {"_name":line.split()[0].strip(), "_type":line.split()[1].strip()}
                objectText = []
                while True:
                    line = file.readline()
                    if line[0] == "(":
                        # Start of object
                        continue
                    elif line[0] == ")":
                        # End of object
                        break
                    else:
                        objectText.append(line)
                        
                objectParm = self.parseObjectText(objectText)
                for key in objectParm.keys():
                    newObj[key] = objectParm[key]
                
                self._oDict[newObj["_name"]] = newObj
                
    def parseObjectText(self, oText):
        """Parse object text from between brackets, returning an oDict of keys and values.
        
        This method is intended to work both for multiline text and single line text, so it can
        be used recursively for structs, sequences, etc."""
        while True:
            # Get next parameter name
            parName, arg, res = oText.partion(":")
            # Check if parameter value is reference, struct or sequence
            if res[0:3] == "ref" | res[0:6] == "struct" | res[0:8] == "sequence":
                type, arg, res = res.partition("(")
                