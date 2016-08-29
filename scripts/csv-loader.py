# import_csv.py
# import comma separated values from a file into Flying Logic
# supports comma, tab and semicolon as delimiters and quoted values
# creates entities, groups and edges, but not junctors
# Copyright 2013,2014 Sciral
# Java classes needed to create the UI and read files
from java.io import InputStreamReader, BufferedReader, FileInputStream
from java.nio.charset import Charset
from javax.swing import Box, BoxLayout, JLabel, JCheckBox, JComboBox,
JTextField
# required variable that provides the label for the item in Flying Logic
import menu
importMenuLabel = "Import Diagram from CSV File"
# importLine: a subroutine to process a line
# returns an array of values found in the line
def importLine(line, delimiter):
    cols = []
    stage = 0
    quoted = False
    for c in line:
        if stage == 0:
            if c == '"':
                quoted = True
                stage = 1
                s = []
            elif c == delimiter:
                cols.append('')
            elif not c.isspace():
                quoted = False
stage = 1
                s = [c]
        elif stage == 1:
            if c == '"':
                if quoted:
                    stage = 2
                else:
                    s.append(c)
            elif c == delimiter:
                if quoted:
                    s.append(c)
                else:
                    cols.append(''.join(s).strip())
                    stage = 0
            else:
                s.append(c)
        elif stage == 2:
            if c == '"':
                s.append(c)
                stage = 1
            elif c == delimiter:
                cols.append(''.join(s))
                stage = 0
            elif not c.isspace():
                """ bad format """
                break
if stage != 0:
    cols.append(''.join(s))
return cols
# this function nicely adds an annotation from plain text
def setAnnotation(elem, text):
    editor = elem.annotationEditor
    editor.insert(text, { })
    editor.flush()
# importDocument: required function for an importer
# parameters
#      file: filename of the file to import
def importDocument(file):
    # create a dialog using Java to collect details about the imported file
    masterBox = Box(BoxLayout.Y_AXIS)
    # text encoding
    controlBox = Box(BoxLayout.X_AXIS)
    controlBox.add(JLabel("Text Encoding: "))
    encodingsComboBox = JComboBox(['Windows/Latin-1/ISO-8859-1', 'UTF-8',
'ASCII (US)'])
    controlBox.add(encodingsComboBox)
    masterBox.add(controlBox)
# delimiter
    controlBox = Box(BoxLayout.X_AXIS)
    controlBox.add(JLabel("Column separator: "))
    columnSepComboBox = JComboBox(["Commas", "Tabs", "Semicolon"])
    controlBox.add(columnSepComboBox)
    masterBox.add(controlBox)
# header row?
    controlBox = Box(BoxLayout.X_AXIS)
    headerCheckbox = JCheckBox("Has header row")
    controlBox.add(headerCheckbox)
    controlBox.add(Box.createHorizontalGlue())
    masterBox.add(controlBox)
    # create new document? (default is to import into current document)
    controlBox = Box(BoxLayout.X_AXIS)
    newDocCheckbox = JCheckBox("Create new document")
    controlBox.add(newDocCheckbox)
    controlBox.add(Box.createHorizontalGlue())
    masterBox.add(controlBox)
    # display dialog and collect options
    if 0 == Application.request("CSV Import Settings", masterBox, ("Cancel",
"OK")):
        return
    createNewDocument = newDocCheckbox.isSelected()
knownEncodings = ['ISO-8859-1', 'UTF-8', 'US-ACSII']
    encoding = knownEncodings[encodingsComboBox.selectedIndex]
    columnDelimiter = ','
    if columnSepComboBox.selectedIndex == 1:
        columnDelimiter = '\t'
if columnSepComboBox.selectedIndex == 2:
    columnDelimiter = ';'
    hasHeader = headerCheckbox.isSelected()
    theDoc = document
    if createNewDocument:
        theDoc = Application.newDocument()
    # open input file
    reader = BufferedReader( InputStreamReader( FileInputStream( file ),
encoding ) )
firstLine = True
    vertexList = []
    indexMap = {}
    row = 0
    # process file line by line
    while True:
        line = reader.readLine()
        if line == None:
break
row = row + 1
        # collect values in line
        columns = importLine(line, columnDelimiter)
        numColumns = len(columns)
        # if first line, ask user to identify meaning if each column
        if firstLine:
            firstLine = False
            columnNames = ['Not used']
            indexNames = ['First row is index 1', 'First row is index 0']
            if hasHeader:
                columnNames = columnNames + columns
                indexNames = indexNames + columns
            else:
                for i in range(numColumns):
        columnNames.append('Column ' + str(i + 1))
        indexNames.append('Column ' + str(i + 1))
# make Java dialog
masterBox = Box(BoxLayout.Y_AXIS)
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Please match attributes with columns:"))
controlBox.add(Box.createHorizontalGlue())
masterBox.add(controlBox)
masterBox.add(Box.createVerticalStrut(20))
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Element Title: "))
titleColumnComboBox = JComboBox(columnNames)
controlBox.add(titleColumnComboBox)
controlBox.add(Box.createHorizontalGlue())
masterBox.add(controlBox)
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Entity Class: "))
classColumnComboBox = JComboBox(columnNames)
controlBox.add(classColumnComboBox)
controlBox.add(Box.createHorizontalGlue())
masterBox.add(controlBox)
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Connections: "))
linkColumnComboBox = JComboBox(columnNames)
controlBox.add(linkColumnComboBox)
predColumnComboBox = JComboBox(['Predecessors', 'Successors'])
controlBox.add(predColumnComboBox)
controlBox.add(Box.createHorizontalGlue())
masterBox.add(controlBox)
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Children: "))
childColumnComboBox = JComboBox(columnNames)
controlBox.add(childColumnComboBox)
controlBox.add(Box.createHorizontalGlue())
masterBox.add(controlBox)
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Internal separator: "))
rowSepTextField = JTextField(5)
controlBox.add(rowSepTextField)
controlBox.add(Box.createHorizontalGlue())
masterBox.add(controlBox)
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Row Index: ")),
indexColumnComboBox = JComboBox(indexNames)
controlBox.add(indexColumnComboBox)
            controlBox.add(Box.createHorizontalGlue())
            masterBox.add(controlBox)
            controlBox = Box(BoxLayout.X_AXIS)
            controlBox.add(JLabel("Annotation: "))
            noteColumnComboBox = JComboBox(columnNames)
            controlBox.add(noteColumnComboBox)
            controlBox.add(Box.createHorizontalGlue())
            masterBox.add(controlBox)
            if 0 == Application.request("CSV Column Interpretation",
masterBox, ("Cancel", "OK")):
                if createNewDocument:
                    theDoc.closeDocument(False)
return
            titleColumn = titleColumnComboBox.selectedIndex - 1
            classColumn = classColumnComboBox.selectedIndex - 1
            linkColumn = linkColumnComboBox.selectedIndex - 1
            childrenColumn = childColumnComboBox.selectedIndex - 1
            isSuccessor = (predColumnComboBox.selectedIndex == 1)
            indexColumn = indexColumnComboBox.selectedIndex - 2
            noteColumn = noteColumnComboBox.selectedIndex - 1
            rowDelimiter = rowSepTextField.text.strip()
            if len(rowDelimiter) == 0:
                rowDelimiter = ' '
            # if first line is a header, skip line
            if hasHeader:
                continue
    # default entity and group attributes
    entityTitle = 'untitled'
        entityClass = 'Generic'
        entityLinks = ''
        groupChildren = ''
        annotation = None
        # match values with identified attributes
        if titleColumn >= 0 and titleColumn < numColumns:
            entityTitle = columns[titleColumn]
if classColumn >= 0 and classColumn < numColumns:
    entityClass = columns[classColumn]
        if linkColumn >= 0 and linkColumn < numColumns:
            entityLinks = columns[linkColumn]
    if childrenColumn >= 0 and childrenColumn < numColumns:
        groupChildren = columns[childrenColumn]
        if noteColumn >= 0 and noteColumn < numColumns:
            annotation = columns[noteColumn]
            if len(annotation) == 0:
                annotation = None
# create index mapping based on user choice of one-based, zero-based or by
column value
indexRow = row
    if indexColumn >= 0:
        indexRow = int(columns[indexColumn])
        elif indexColumn == -1:
            indexRow = row - 1
    indexMap[indexRow] = row
        # either handle as group or entity -- no junctors yet
        if groupChildren != '':
            group = theDoc.newGroup(None)[0]
            if entityTitle != 'untitled':
                group.title = entityTitle
            if annotation != None:
                setAnnotation(group, annotation)
            vertexList.append( (group, None, groupChildren) )
        else:
            entity = theDoc.addEntityToTarget(None)[0] # no need to
clearSelection each iteration
            entity.title = entityTitle
            eCls = theDoc.getEntityClassByName(entityClass)
            if eCls != None:
                entity.entityClass = eCls
            if annotation != None:
                setAnnotation(entity, annotation)
            vertexList.append( (entity, entityLinks, None) )
# generate new elements from collected vertex data
for data in vertexList:
    if data[1] != None:
        predList = data[1].split(rowDelimiter)
            for pred in predList:
                if len(pred) > 0:
                    index = indexMap[int(pred)] - 1
                    if hasHeader:
                        index = index - 1
                    if index >= 0 and index < len(vertexList):
                        if isSuccessor:
                            theDoc.connect(data[0], vertexList[index][0])
                        else:
                            theDoc.connect(vertexList[index][0], data[0])
    if data[2] != None:
        childList = data[2].split(rowDelimiter)
            for child in childList:
                if len(child) > 0:
index = indexMap[int(child)] - 1
                    if hasHeader:
                        index = index - 1
                    if index >= 0 and index < len(vertexList):
			vertexList[index][0].parent = data[0]
return theDoc
