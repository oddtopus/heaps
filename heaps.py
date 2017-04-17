#(c) 2017 R. T. LGPL: part of heapsOstuff w.b. for FreeCAD

__title__="heaps module"
__author__="oddtopus"
__url__="github.com/oddtopus/heaps"
__license__="LGPL 3"

import xml.etree.ElementTree as et
from PySide.QtGui import QFileDialog as qfd
from os import listdir
from os.path import abspath,dirname,join
from PySide.QtGui import QInputDialog as inputs
import FreeCAD, FreeCADGui

################# CLASSES ###################

class heap():
  '''heap(heapDir,heapFile)
  \tThe heap object
  \tDefault heapDir = "./heaps"
  \tDefault heapFile = "heapBase.xml"'''
  def __init__(self,heapDir=None,heapFile='heapBase.xml'):
    if not heapDir:
      heapDir=join(dirname(abspath(__file__)),'heaps')    
    self.heapDir=heapDir
    self.heapFile=heapFile
    self.heapUpdate()
  def heapWrite(self, fileName):
    '''heapWrite(fileName)
    \tWrites the .heap attribute to specified fileName'''
    self.heap.write(join(self.heapDir,fileName))
  def heapUpdate(self):
    '''heapUpdate()
    \tupdates the attribute .heap'''
    self.heap=et.parse(join(self.heapDir,self.heapFile))
  def getStuff(self):
    '''getStuff()
    \tReturns the list of stuff (list of Element) in the .heap (ElementTree)'''
    return [s for s in self.heap.iter('stuff')]
  def addStuff(self,cat='',where=''): #in progress
    '''Adds stuff to heap'''
    cat=inputs.getText(None,'Add stuff','Insert new \ncategory')
    if cat[1]:
      et.SubElement(self.heap.getroot(),'stuff',category=cat[0],where='')
  def getThings(self,category):
    '''getThings(category)
    \tIf "category" is in the heap, returns the list of 
    relevant things (list of Element)
    '''
    things=list()
    for stuff in self.getStuff():
      if stuff.attrib['category']==category:
        things+=[t for t in stuff.iter('thing')  ]
    return things
  def addThings(self,cat=None,thingFiles=[],names=[]): #in progress
    '''Adds things to stuff'''
    if len(thingFiles)!=len(names):
      FreeCAD.Console.PrintError("Files and names lists don't match\n")
      return 0
    #temporary code: direct category input
    if not cat:
      cat=inputs.getItem(None,'Add things','Select the stuff of thing',[s.attrib['category'] for s in self.getStuff()])[0]
    stuff=[s for s in self.heap.iter('stuff')][0]
    thingFiles=qfd.getOpenFileNames()[0]
    for thingFile in thingFiles:
      #temporary code: preliminary check
      if dirname(abspath(thingFile))==stuff.attrib['where']:
        FreeCAD.Console.PrintMessage(thingFile+' can be added to stuff '+stuff.attrib['category']+'.\n')
      else:
        FreeCAD.Console.PrintError(thingFile+' is outside '+stuff.attrib['where']+'.\n')
    return len(thingFiles)

################# COMMANDS ##################

def generateHeap(fileName='heapBase.xml',heapDir=None):
  '''generateHeap(fileName='heapBase.xml',heapDir=None)   
  Generates a sample heap'''
  if not heapDir:
    heapDir=join(dirname(abspath(__file__)),'heaps') #'[..]/.FreeCAD/Mod/heapsOstuff/heaps/'
  heapEl=et.Element('heap',type='baseStuff')
  stuff1=et.Element('stuff',category='things1',where='/home/path/number/1')
  stuff2=et.Element('stuff',category='otherThings',where='/home/path/number/2')
  things=[et.Element('thing',name=t,file='') for t in ['thing'+str(i) for i in [1,2,3,4,5,6]]]
  for t in things[:3]:
    stuff1.append(t)
  heapEl.append(stuff1)
  for t in things[3:]:
    stuff2.append(t)
  heapEl.append(stuff2)
  et.dump(heapEl)
  et.ElementTree(heapEl).write(join(heapDir,fileName))

def importAndMove(fileToMerge='',pos=FreeCAD.Vector(0,0,0)):
  '''importAndMove(fileToMerge='',pos=FreeCAD.Vector(0,0,0))
  \tMerges one .fcstd file into the project
  \tand moves it to pos
  \tIf no file is specified, uses getOpenFileName()'''
  n=len(FreeCAD.ActiveDocument.Objects)
  if not fileToMerge:
    from os import environ
    home=''
    try:
      home=environ['HOME']
    except:
      pass
    fileToMerge=qfd.getOpenFileName(dir=home,filter='FC models (*.fcstd)')[0]
  if fileToMerge:
    FreeCADGui.ActiveDocument.mergeProject(fileToMerge)
    l=[o.Name for o in FreeCAD.ActiveDocument.Objects[n:]]
    if pos.Length!=0:
      for name in l:
        FreeCAD.ActiveDocument.getObject(name).Placement.move(pos)
    return l

def edges():
  '''returns the list of edges in the selection set'''
  selex=FreeCADGui.Selection.getSelectionEx()
  try:
    eds=[e for sx in selex for so in sx.SubObjects for e in so.Edges]
  except:
    FreeCAD.Console.PrintError('\nNo valid selection.\n')
  return eds

################# FORMS #####################

from PySide.QtCore import *
from PySide.QtGui import *

class prototypeHeapForm(QWidget):
  def __init__(self,winTitle='Title', startHeap='heapBase.xml', icon=''):
    '''
    __init__(self, winTitle='Title', startHeap='heapBase.xml', icon='')
       
    '''
    # Main properties
    self.heap=heap(heapFile=startHeap)
    self.currentStuff=''
    self.currentThing=''
    self.stuff=dict() 
    self.things=dict()
    w=140
    # Widgets
    super(prototypeHeapForm,self).__init__()
    self.move(QPoint(100,250))
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    self.setMaximumWidth(2*w)
    self.setMaximumHeight(3*w)
    if icon:
      iconPath=join(dirname(abspath(__file__)),"icons",icon)
      from PySide.QtGui import QIcon
      Icon=QIcon()
      Icon.addFile(iconPath)
      self.setWindowIcon(Icon) 
    self.currentHeapLab=QLabel('Heap: %s' %self.heap.heapFile.rstrip('.xml'))
    self.thingsList=QListWidget()
    self.thingsList.itemClicked.connect(self.changeThing)
    self.stuffList=QListWidget()
    self.stuffList.itemClicked.connect(self.changeStuff)
    self.btn1=QPushButton('btn1')
    self.btn2=QPushButton('btn2')
    self.text=QTextEdit()
    self.text.setMaximumHeight(self.height()/5)
    self.openHeap(join(dirname(abspath(__file__)),"heaps",startHeap))
    # Draw the dialog
    self.grid=QGridLayout()
    self.setLayout(self.grid)
    self.grid.addWidget(self.currentHeapLab,0,0,1,2)
    self.grid.addWidget(self.stuffList,1,0)
    self.grid.addWidget(self.thingsList,1,1)
    self.grid.addWidget(self.btn1,2,0)
    self.grid.addWidget(self.btn2,2,1)
    self.grid.addWidget(self.text,3,0,1,2)
    self.show()
  def openHeap(self, heap2open=None):
    if not heap2open:
      reply=qfd.getOpenFileName(self,dir=join(dirname(abspath(__file__)),"heaps"),filter='Heap file (*.xml)')
      if reply[1]:
        heap2open=reply[0]
        del reply
      else:
        del reply
        return
    self.heap=heap(heapFile=heap2open)
    self.stuff.clear()
    self.things.clear()
    self.text.clear()
    self.thingsList.clear()
    self.stuffList.clear()
    for s in self.heap.getStuff():
      self.stuff[s.attrib['category']]=s.attrib['where']
    self.stuffList.addItems(self.stuff.keys())
  def changeStuff(self):
    self.currentStuff=self.stuffList.currentItem().text()
    self.things.clear()
    for thing in self.heap.getThings(self.currentStuff):
      self.things[thing.attrib['name']]=[thing.attrib['file'],thing.text.strip()+'\n'+thing.tail.strip()]
    self.thingsList.clear()
    things=self.things.keys()
    things.sort()
    self.thingsList.addItems(things)
  def changeThing(self):
    self.currentThing=self.thingsList.currentItem().text()
    self.text.setText(self.things[self.currentThing][1])
    
class insertThingForm(prototypeHeapForm):
  '''Form to merge a model from one heap into the ActiveDocument
  '''
  def __init__(self,winTitle='Merge a thing', startHeap='heapBase.xml', icon=''):
    # Widgets
    super(insertThingForm,self).__init__(winTitle,startHeap,icon)
    self.btn1.setText('Insert thing')
    self.btn1.clicked.connect(self.insertThing)
    self.btn2.setText('Open heap')
    self.btn2.clicked.connect(self.openHeap)
  def insertThing(self):
    if FreeCAD.ActiveDocument:
      if self.currentStuff:
        directory=self.stuff[self.currentStuff]
      else:
        FreeCAD.Console.PrintError('Select somestuff before.\n')
        return
      if not directory:
        directory=self.heap.heapDir
      if self.currentThing: #main block
        FreeCAD.ActiveDocument.openTransaction('Merge a file')
        file2merge=join(directory,self.things[self.thingsList.currentItem().text()][0])
        positions=list()
        selex=FreeCADGui.Selection.getSelectionEx()
        if selex:
          if edges():
            positions=[edge.centerOfCurvatureAt(0) for edge in edges() if edge.curvatureAt(0)]
          else:
            subobjects=[so for sx in selex for so in sx.SubObjects]
            positions=[v.Point for so in subobjects for v in so.Vertexes]
        if positions:
          for pos in positions:
            importAndMove(file2merge,pos)
        else:
          importAndMove(file2merge)
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
      else:
        FreeCAD.Console.PrintError('Select something before.\n')
    else:
      FreeCAD.Console.PrintError('Open one file before.\n')
