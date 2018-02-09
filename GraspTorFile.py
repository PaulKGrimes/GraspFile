# A class to hold a parsed GRASP Tor File in a collection of objects
#
# Paul Grimes, 2018
#
# The data from the Tor file will be parsed by a pyparsing parser defined in GraspTorParser
# and stored in a GraspTorFile class derived from collections.OrderedDict, containing
# GraspTorObjects and Comments.

import GraspTorParser
from collections import OrderedDict

class GraspTorValue(self, torValue=None):
    """A container for values from GraspTorMember objects"""
    def __init__:
        self.value = None
        self.unit = None
        if torValue:
            self.fill(torValue)
    def fill(self, torValue):
        if len(torValue) > 1:
            self.value = torValue[0]
            self.unit = torValue[1]
        else:
            self.value = torValue


class GraspTorMember:
    """A container for the member parameter of an GraspTorObject """
    def __init__(self, torMember=None):
        self.name = None
        self.value = None
        if torMember:
            self.fill(torMember)
            
    def fill(torMember)
        self.name = torMember[0]
        self.value = GraspTorValue(torMember[1])
        

class GraspTorComment:
    """A container for comments from a GraspTorFile"""
    def __init__(self, torComment=None):
        self.name = None
        self.text = None
        self.location = None
        if torComment:
            self.fill(torComment)
            
    def fill(self, torComment):
        self.name = torComment._name
        self.location = int(torComment._name.lstrip("comment"))
        self.text = torComment.text

        
class GraspTorObject(OrderedDict):
    """A container for a GraspTorObject, that has a name, a type and a number of members.  Members are
    stored as an OrderedDict."""
    def __init__(self, torObj=None):
        if isinstance(torObj, __builtins__.str):
            self.readStr(torObj)
        elif isinstance(torObj, GraspTorParser.ParseResults):
            self.fill(torObj)
        else:
            pass
            
    def readStr(self, torStr):
        """Read the contents of the string into a torObject and then process the results"""
        res = GraspTorParser.torObjects.parseString(torStr)
        self.fill(res)
        
    def fill(self, torObj):
        """Fill the GraspTorObject using the pyparsing results"""
        self._name = torObj._name
        self._type = torObj._type
        for r in torObj[2:]:
            self[r[0]] = GraspTorMember(r)


class GraspTorFile(OrderedDict):
    """A container for objects read from a tor file.  Subclasses OrderedDict to provide a dict of torObjects
     keyed by name, and sorted by insertion order"""
    def __init__(self, fileLike=None):
        """Create a TorFile object, and if fileLike is specified, read the file"""
        OrderedDict.__init__()
        self._parser = GraspTorParser.torFile
        if fileLike:
            self.read(fileLike)
        
    def read(self, fileLike):
        """Read a list of torObjects and torComments from a fileLike object.  We use pyparsing.ParserElement's parseFile
        method, which can take either a file-like object or a filename to open.  If you wish to parse an existing string
        object, used StringIO to supply a file-like object containing the string."""
        # Parse the file
        res = self._parser.parseFile(fileLike)
        
        # Turn the parse results into objects
        self.fill(res)
        
    def fill(self, torFile):
        """Fill the GraspTorFile using the parser results in torFile"""
        for r in torFile:
            if r._type == "comment":
                self[r._name] = GraspTorComment(r)
            else:
                self[r._name] = GraspTorObject(r)
        
if __name__ == "__main__":
    import StringIO
    testFile = StringIO.StringIO(GraspTorParser.test_str)
    
    gtf = GraspTorFile(testFile)
    
    print(gtf)
    print(gtf.get_keys())