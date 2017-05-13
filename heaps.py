#(c) 2017 R. T. LGPL: part of heapsOstuff w.b. for FreeCAD

__title__="heaps module"
__author__="oddtopus"
__url__="github.com/oddtopus/heaps"
__license__="LGPL 3"

import xml.etree.ElementTree as et
from PySide.QtGui import *
from PySide.QtCore import *
from os import listdir,sep, environ
from os.path import abspath,dirname,join,sep
import FreeCAD, FreeCADGui

################# CLASSES ###################

class heap(object):
  '''heap(heapFile)
  \tThe heap object
  \tDefault heapFile = "../Mod/heaps/heaps/heapBase.xml"
  \tIf the path is not specified in the argument, it is changed to
  \t"../Mod/heaps/heaps/" by default'''
  def __init__(self,heapFile='heapBase.xml'):
    if dirname(heapFile):
      self.heapFile=heapFile
    else:
      self.heapFile=join(dirname(abspath(__file__)),'heaps',heapFile)
    self.heapRead()
  def heapWrite(self, fileName):
    '''heapWrite(fileName)
    \tWrites the .heap attribute to specified fileName'''
    self.heap.write(fileName)
  def heapRead(self):
    '''heapRead()
    \tUpdates the attribute .heap re-parsing the .xml file'''
    self.heap=et.parse(self.heapFile)
  def getStuff(self,cat=None):
    '''getStuff(cat)
    \tReturns the list of stuff (list of Element) in the .heap (ElementTree)
    \twhich category==cat'''
    if cat:
      return [s for s in self.heap.iter('stuff') if s.attrib['category']==cat]
    else:
      return [s for s in self.heap.iter('stuff')]
  def addStuff(self,cat='',where=''): #in progress
    '''Adds stuff to heap'''
    if not cat:
      reply=QInputDialog.getText(None,'Add stuff','Insert new \ncategory:')
      if reply[1]:
        cat=reply[0]
      else:
        return
    et.SubElement(self.heap.getroot(),'stuff',category=cat,where='')
    return cat
  def getThings(self,category):
    '''getThings(category)
    \tIf "category" is in the heap, returns the list of 
    \trelevant things (list of Element)
    '''
    things=list()
    for stuff in self.getStuff():
      if stuff.attrib['category']==category:
        things+=[t for t in stuff.iter('thing')  ]
    return things
  def addThings(self,cat=None): #in progress
    '''Adds things to stuff.
    Returns names list of things'''
    #if not cat: #temporary code: direct category input
    #  cat=QInputDialog.getItem(None,'Add things','Select the stuff of thing',[s.attrib['category'] for s in self.getStuff()])[0]
    stuff=self.getStuff(cat)[0]
    home=''
    try:
      home=environ['HOME']
    except:
      pass
    thingFiles=QFileDialog.getOpenFileNames(dir=home,filter='FC models (*.fcstd)')[0]
    names=list()
    where=stuff.attrib['where']
    if not where:
      if self.getThings(cat): 
        where=join(dirname(abspath(__file__)),'heaps')
      else: 
        where=dirname(thingFiles[0])
        stuff.attrib['where']=where
    for thingFile in thingFiles:
      if dirname(abspath(thingFile))==where:
        thingName=thingFile.split(sep)[-1].split('.')[-2]
        names.append(thingName)
        newThing=et.SubElement(stuff,'thing',name=thingName,file=thingName+'.fcstd')
        newThing.text='-- Add description here --'
        FreeCAD.Console.PrintMessage('"'+thingName+'" added to stuff "'+stuff.attrib['category']+'".\n')
      else:
        FreeCAD.Console.PrintError(thingFile+' is not inside directory '+where+'.\n')
        break
    return names

################# COMMANDS ##################

def generateHeap(fileName='heapBase.xml'):
  '''generateHeap(fileName='heapBase.xml')   
  Generates a sample heap in "../Mod/heaps/heaps/"'''
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
    #from os import environ
    home=''
    try:
      home=environ['HOME']
    except:
      pass
    fileToMerge=QFileDialog.getOpenFileName(dir=home,filter='FC models (*.fcstd)')[0]
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

def faces(selex=[]):
  '''returns the list of faces in the selection set'''
  selex=FreeCADGui.Selection.getSelectionEx()
  try:
    fcs=[f for sx in selex for so in sx.SubObjects for f in so.Faces]
  except:
    FreeCAD.Console.PrintError('\nNo valid selection.\n')
  return fcs

################# FORMS #####################

class prototypeHeapForm(QWidget):
  def __init__(self,winTitle='Title', startHeap='heapBase.xml', icon=''):
    '''
    __init__(self, winTitle='Title', startHeap='heapBase.xml', icon='')
       
    '''
    super(prototypeHeapForm,self).__init__()
    # Main properties
    FreeCAD.__activeHeap__=heap(heapFile=startHeap)
    self.currentStuff=''
    self.currentThing=''
    self.stuff=dict() 
    self.things=dict()
    w=140
    # Widgets
    self.move(QPoint(100,250))
    self.setWindowFlags(Qt.WindowStaysOnTopHint)
    self.setWindowTitle(winTitle)
    self.setMaximumWidth(2*w)
    self.setMaximumHeight(3*w)
    if icon:
      iconPath=join(dirname(abspath(__file__)),"icons",icon)
      Icon=QIcon()
      Icon.addFile(iconPath)
      self.setWindowIcon(Icon)
    self.currentHeapLab=QLabel()
    self.currentDirLab=QLabel('Place: (directory of stuff)')
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
    self.grid.addWidget(self.currentDirLab,1,0,1,2)
    self.grid.addWidget(self.stuffList,2,0)
    self.grid.addWidget(self.thingsList,2,1)
    self.grid.addWidget(self.btn1,3,0)
    self.grid.addWidget(self.btn2,3,1)
    self.grid.addWidget(self.text,4,0,1,2)
    self.show()
  def openHeap(self, heap2open=None):
    if not heap2open:
      reply=QFileDialog.getOpenFileName(self,dir=join(dirname(abspath(__file__)),"heaps"),filter='Heap file (*.xml)')
      if reply[1]:
        heap2open=reply[0]
        del reply
      else:
        del reply
        return
    FreeCAD.__activeHeap__=heap(heapFile=heap2open)
    self.currentHeapLab.setText('Heap: %s' %FreeCAD.__activeHeap__.heapFile.split(sep)[-1])
    self.stuff.clear()
    self.things.clear()
    self.text.clear()
    self.thingsList.clear()
    self.stuffList.clear()
    for s in FreeCAD.__activeHeap__.getStuff():
      self.stuff[s.attrib['category']]=s.attrib['where']
    self.stuffList.addItems(self.stuff.keys())
  def changeStuff(self):
    self.currentStuff=self.stuffList.currentItem().text()
    self.things.clear()
    place=self.stuff[self.currentStuff]
    if not place: place='(default or not defined)'
    elif len(place)>30: place=".."+place[-28:]
    self.currentDirLab.setText('Place: %s' %place)
    for thing in FreeCAD.__activeHeap__.getThings(self.currentStuff):
      description=''
      if thing.text: description+=thing.text.strip()
      if thing.tail: description+='\n'+thing.tail.strip()
      self.things[thing.attrib['name']]=[thing.attrib['file'],description]
    self.thingsList.clear()
    things=self.things.keys()
    things.sort()
    self.thingsList.addItems(things)
  def changeThing(self):
    self.currentThing=self.thingsList.currentItem().text()
    self.text.setText(self.things[self.currentThing][1])
    
class mergeThingForm:#(prototypeHeapForm):
  '''Form to merge a model from one heap into the ActiveDocument
  '''
  def __init__(self,winTitle='Merge a thing', startHeap='heapBase.xml', icon=''):
    # Main properties
    FreeCAD.__activeHeap__=heap(heapFile=startHeap)
    self.currentStuff=''
    self.currentThing=''
    self.stuff=dict() 
    self.things=dict()
    # Widgets
    self.form=FreeCADGui.PySideUic.loadUi(join(dirname(abspath(__file__)),"dialogs","merge.ui"))
    #super(mergeThingForm,self).__init__(winTitle,startHeap,icon)
    #self.btn1.setText('Merge thing')
    #self.btn1.clicked.connect(self.insertThing)
    #self.btn2.setText('Open heap')
    self.form.btn2.clicked.connect(self.openHeap)
    self.form.stuffCombo.currentIndexChanged.connect(self.changeStuff)
    self.form.thingsList.itemClicked.connect(self.changeThing)
    self.openHeap(join(dirname(abspath(__file__)),"heaps","heapBase.xml"))
  def changeStuff(self):
    self.currentStuff=self.form.stuffCombo.currentText()
    self.things.clear()
    #place=self.stuff[self.currentStuff]
    #print place
    #if not place: place='(default or not defined)'
    #elif len(place)>30: place=".."+place[-28:]
    for thing in FreeCAD.__activeHeap__.getThings(self.currentStuff):
      description=''
      if thing.text: description+=thing.text.strip()
      if thing.tail: description+='\n'+thing.tail.strip()
      self.things[thing.attrib['name']]=[thing.attrib['file'],description]
    self.form.thingsList.clear()
    things=self.things.keys()
    things.sort()
    self.form.thingsList.addItems(things)
  def changeThing(self):
    self.currentThing=self.form.thingsList.currentItem().text()
    self.form.text.setText(self.things[self.currentThing][1])
  def openHeap(self, heap2open=None):
    if not heap2open:
      reply=QFileDialog.getOpenFileName(dir=join(dirname(abspath(__file__)),"heaps"),filter='Heap file (*.xml)')
      if reply[1]:
        heap2open=reply[0]
        del reply
      else:
        del reply
        return
    FreeCAD.__activeHeap__=heap(heapFile=heap2open)
    self.stuff.clear()
    self.things.clear()
    self.form.text.clear()
    self.form.thingsList.clear()
    self.form.stuffCombo.clear()
    for s in FreeCAD.__activeHeap__.getStuff():
      self.stuff[s.attrib['category']]=s.attrib['where']
    self.form.stuffCombo.addItems(self.stuff.keys())
  def accept(self):#insertThing(self):
    if FreeCAD.ActiveDocument:
      directory=''
      if self.currentStuff:
        directory=self.stuff[self.currentStuff]
      else:
        FreeCAD.Console.PrintError('Select somestuff before.\n')
        return
      if not directory:
        directory=dirname(FreeCAD.__activeHeap__.heapFile)
      if self.currentThing: #main block
        FreeCAD.ActiveDocument.openTransaction('Merge a file')
        file2merge=join(directory,self.things[self.form.thingsList.currentItem().text()][0])
        positions=list()
        selex=FreeCADGui.Selection.getSelectionEx()
        if selex:
          if faces():
            positions=[face.CenterOfMass for face in faces()]
          elif edges():
            positions=[edge.centerOfCurvatureAt(0) for edge in edges() if edge.curvatureAt(0)]
          else:
            subobjects=[so for sx in selex for so in sx.SubObjects]
            positions=[v.Point for so in subobjects for v in so.Vertexes]
        if positions:
          for pos in positions:
            importAndMove(file2merge,pos)
        else:
          FreeCAD.Console.PrintMessage(file2merge+'\n')
          importAndMove(file2merge)
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
      else:
        FreeCAD.Console.PrintError('Select something before.\n')
    else:
      FreeCAD.Console.PrintError('Open one file before.\n')

class HeapsManagerForm(prototypeHeapForm):
  '''Form to manage the heaps
  '''
  def __init__(self,winTitle='Heaps Manager', startHeap='heapBase.xml', icon=''):
    # Widgets
    super(HeapsManagerForm,self).__init__(winTitle,startHeap,icon)
    self.btn1.setText('Add stuff')
    self.btn1.clicked.connect(self.moreStuff)#(lambda: FreeCAD.__activeHeap__.addStuff())
    self.btn2.setText('Open heap')
    self.btn2.clicked.connect(self.openHeap)
    self.grid.addWidget(self.text,5,0,2,2)
    self.btn3=QPushButton('Add things')
    self.btn3.clicked.connect(self.moreThings)
    self.btn4=QPushButton('Create heap')
    self.grid.addWidget(self.btn3,4,0)
    self.grid.addWidget(self.btn4,4,1)
  def moreStuff(self):
    self.stuffList.addItem(FreeCAD.__activeHeap__.addStuff())
    FreeCAD.__activeHeap__.heapWrite(FreeCAD.__activeHeap__.heapFile)
  def moreThings(self):
    if self.stuffList.selectedItems():
      newThings=FreeCAD.__activeHeap__.addThings(self.currentStuff) # names' list
      for thingName in newThings:
        self.things[thingName]=[thingName+'.fcstd','-- Add description here --'] #add new things to the dictionary
      self.thingsList.addItems(newThings) #add new things to the list-box
      FreeCAD.__activeHeap__.heapWrite(FreeCAD.__activeHeap__.heapFile)
      FreeCAD.__activeHeap__.heapRead()
    
