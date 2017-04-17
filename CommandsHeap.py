#(c) 2017 R. T. LGPL: part of heapsOstuff w.b. for FreeCAD

__title__="heapsOstuff toolbar"
__author__="oddtopus"
__url__="github.com/oddtopus/heaps"
__license__="LGPL 3"

# import FreeCAD modules
import FreeCAD, FreeCADGui,inspect

# helper -------------------------------------------------------------------

def addCommand(name,cmdObject):
  (list,num) = inspect.getsourcelines(cmdObject.Activated)
  pos = 0
  # check for indentation
  while(list[1][pos] == ' ' or list[1][pos] == '\t'):
    pos += 1
  source = ""
  for i in range(len(list)-1):
    source += list[i+1][pos:]
  FreeCADGui.addCommand(name,cmdObject,source)

#---------------------------------------------------------------------------
# The command classes
#---------------------------------------------------------------------------

class insertThing:
  '''
  Simple dialog to merge .fcstd files in documents.
  '''
  def Activated (self):
    import heaps
    heapsForm=heaps.insertThingForm()
  def GetResources(self):
    return{'Pixmap':'Std_Tool1','MenuText':'Merge things','ToolTip':'Open heap, select stuff, pick thing.'}

#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('insertThing',insertThing())

