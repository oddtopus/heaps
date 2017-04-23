#(c) 2017 R. T. LGPL: part of heapsOstuff w.b. for FreeCAD

__title__="heapsOstuff toolbar"
__author__="oddtopus"
__url__="github.com/oddtopus/heaps"
__license__="LGPL 3"

# import FreeCAD modules
import FreeCAD, FreeCADGui,inspect, os

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

class mergeThing:
  '''
  Simple dialog to merge .fcstd files in documents.
  '''
  def Activated (self):
    import heaps
    heapsForm=heaps.mergeThingForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","merge.svg"),'MenuText':'Merge things','ToolTip':'Open heap -> select stuff -> merge thing.'}

class heapsManager:
  '''
  Simple dialog to create heaps, add stuff to heaps 
  or add things to stuff.
  '''
  def Activated (self):
    import heaps
    heapsForm=heaps.HeapsManagerForm()
  def GetResources(self):
    return{'Pixmap':os.path.join(os.path.dirname(os.path.abspath(__file__)),"icons","manager.svg"),'MenuText':'Heaps manager','ToolTip':'Actions on heaps'}

#---------------------------------------------------------------------------
# Adds the commands to the FreeCAD command manager
#---------------------------------------------------------------------------
addCommand('mergeThing',mergeThing())
addCommand('heapsManager',heapsManager())
