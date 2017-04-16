# heaps
"heaps" will be a Python module for FreeCAD aimed to simplify mergings of models into the active project. The relevant workbench will be "heapsOstuff".

To try the first features, after you have copied the content of the repository in FC's path, just type

	import heaps
	form=heaps.insertThingForm()

The basic idea is to gather into .xml files (called "heaps" in the slang of this module) the references to the files frequently imported ("things") and organized in categories ("stuff").
At the end you'll just need to pick a thing from the stuff of a heap and place it in your project.
