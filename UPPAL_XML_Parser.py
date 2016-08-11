__author__ = 'roohitavaf'

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import re

#Utilities--------------------
#Preprocess Engine
def CorrectLocationsName (root): #add id as the name of location without name
    for template in root.iter('template'):
        templateName = template.find('name').text
        for location in template.iter('location'):
            nameElement = location.find('name')
            if nameElement is None:
                nElement = Element("name")
                location.insert(0, nElement)
            nameElement = location.find('name')
            if nameElement.text is None:
                nameElement.text = templateName + location.attrib['id']
            #nameElement.text = templateName + "_" + nameElement.text



# def UndoLocationName (root): #remove id_ from beginning of location names.
#     for template in root.iter('template'):
#         for location in template.iter('location'):
#             nameElement = location.find('name')
#             nameElement.text = RemoveId(nameElement.text)
#
# def RemoveIdList (l): #remove id_ from the beginning of a names in list
#     result = []
#     for i in l:
#         result.append(RemoveId(i))
#     return result
#
# def RemoveId(name): #remove id_ from the beginning of a name
#     return name[name.find("@")+1:]

#Location Engine
def GetLocationsName (root):
    l = []
    for template in root.iter('template'):
        for location in template.iter('location'):
            name = location.find('name')
            if name is not None : l.append(name.text)

    return l




def GetLocationNameById(root, id):
    for template in root.iter('template'):
        for location in template.iter('location'):
            if location.attrib['id'] == id: return location.find('name').text
    return -1

def GetLocationsID(root):
    l = []
    for template in root.iter('template'):
        for location in template.iter('location'):
            l.append(location.attrib['id'])

    return l

def GetLocationsOfTemplate (template):
    result = []
    for location in template.iter('location'):
        result.append(location)
    return result

def GetLocationId (root, name):
    for template in root.iter('template'):
        for location in template.iter('location'):
            if location.find('name').text == name:
                return location.attrib['id']
    return -1

def GetLocationTemplateByName (root, name):
    for template in root.iter('template'):
        for location in template.iter('location'):
            if location.find('name').text == name:
                return template
    return -1

def GetLocationTemplateById (root, id):
    for template in root.iter('template'):
        for location in template.iter('location'):
            if location.attrib['id'] == id:
                return template
    return -1

def GetLocationById(root, id):
    for template in root.iter('template'):
        for location in template.iter('location'):
            if location.attrib['id'] == id :  return location
    return -1

def IsUrgent (root, id):
    location = GetLocationById(root, id)
    if location.find('urgent') is not None or location.find('committed') is not None:
        return True
    return False

def GetInvolvingLocations (root, A):
    result = []
    for template in root.iter('template'):
        for transition in template.iter('transition'):
            source = transition.find('source').attrib['ref']
            assignment = GetAssignment(transition)
            assignmentList = GetLines(assignment)
            for a in assignmentList:
                if a in A and source not in result: result.append(GetLocationById(root,source).find('name').text)
    return result

def GetGuardOfLocations(root, locations):
    result = []
    for template in root.iter('template'):
        for transition in template.iter('transition'):
            source = transition.find('source').attrib['ref']
            if GetLocationById(root,source).find('name').text in locations:
                Guard = GetGuard(transition)
                if Guard != -1: result.append(Guard)
    return RemoveDuplicates(result)

def GetInvariant(location):
    for label in location.iter('label'):
        if (label.attrib['kind'] == 'invariant'): return label.text
    return -1

#Reachblity Engine
#REZA: finding predecessor of a location
'''
def predecessor (root, name):
    id = GetLocationId(root, name)
    for template in root.iter(tag="template"):
        for transition in template.iter('transition'):
            source = transition.find('source').attrib['ref']
            target = transition.find('target').attrib['ref']
            if target==id: return  GetLocationNameById(root, source)
    return -1
'''
def GetImPre (root, name):
    a = []
    id = GetLocationId(root, name)
    for template in root.iter('template'):
        for transition in template.iter('transition'):
            if transition.find('target').attrib['ref'] == id and (not transition.find('source').attrib['ref'] in a ):
                a.append(GetLocationNameById(root, transition.find('source').attrib['ref']))
    return a

def IsReachable (root, id1, id2, checked, avoid): #returns true if id2 is reachable from id1 avoiding the avoid
    if id1 == id2:
        return True
    checked.append(id1)
    for template in root.iter('template'):
        for transition in template.iter('transition'):
            source = transition.find('source').attrib['ref']
            target = transition.find('target').attrib['ref']
            if (source == id1) and not (target in checked) and target != avoid:
                result = IsReachable(root, target, id2, checked, avoid)
                if result:
                    return True
    return False

def AllPathsReach (template, id1, id2, checked): #return true if all pathes from id1 reaches id2.
    if id1 == id2: return True
    nextStates = GetNextStates(template, id1)
    if nextStates.__len__() == 0: return False
    for location in nextStates:
        if location in checked: return False
        checked.append(location)
        if not AllPathsReach(template, location, id2, checked): return False

    return True



def GetNextStates (template, id1): #returns the id of the immidiates next states.
    result = []
    for transition in template.iter('transition'):
        if (transition.find('source').attrib['ref'] == id1) and not (transition.find('target').attrib['ref'] in result):
            result.append(transition.find('target').attrib['ref'])
    return result

#Text Engine
def GetLeftSide(s):
    if (s.find('=')):
        leftSide = s.partition('=')[0]
    elif (s.find('++')):
        leftSide = s[:s.find('++')]
    elif  (s.find('--')):
        leftSide = s[:s.find('--')]
    elif  (s.find('+=')):
        leftSide = s[:s.find('+=')]
    elif (s.find('-=')):
        leftSide = s[:s.find('-=')]
    elif (s.find('*=')):
        leftSide = s[:s.find('*=')]
    elif (s.find('/=')):
        leftSide = s[:s.find('/=')]
    leftSide = leftSide.replace (' ', '')
    return leftSide

def GetRightSide(s):
    rightSide = s.partition('=')[2]
    rightSide = rightSide.replace (' ', '')

    return rightSide

def GetAllAssignments(root):
    a = []
    for template in root.iter('template'):
        for transition in template.iter('transition'):
            if (GetAssignment(transition) != -1): a.append(GetAssignment(transition))
    result = []
    for assign in a:
        splited = re.split(",", assign)
        splited2 =[]
        for s in splited:
            s = s[s.find("\n")+1:]
            splited2.append(s)
        result = result + splited2
    return result

#REZA
def GetAllActions(root):
    a = []
    for template in root.iter('template'):
        for transition in template.iter('transition'):
            Actions = GetAction(transition)
            if (Actions != -1): 
                for item in Actions:
                    a.append(item)
    result = []
    for assign in a:
        splited = re.split(",", assign)
        splited2 =[]
        for s in splited:
            s = s[s.find("\n")+1:]
            splited2.append(s)
        result = result + splited2
    return result

#REZA
def GetAction (t):
    all_labels = []
    for label in t.iter('label'):
        all_labels.append(label.text)
    if len(all_labels) > 0: return all_labels
    return -1

def GetAssignment (t):
    for label in t.iter('label'):
        if (label.attrib['kind'] == 'assignment'): return label.text
    return -1

def GetGuard (t):
    for label in t.iter('label'):
        if (label.attrib['kind'] == 'guard'): return label.text
    return -1

def GetSyncLabel (t):
    for label in t.iter('label'):
        if (label.attrib['kind'] == 'synchronisation'): return label.text[:len(label.text)-1]
    return -1



def Spliter(s):
    s2 = s.replace (' ' , '')
    s2 = s2.replace ('>=', '>')
    s2 = s2.replace ('and', '>')
    s2 = s2.replace ('or', '>')
    s2 = s2.replace ('==', '>')
    s2 = s2.replace ('<=', '>')
    s2 = s2.replace ('!=', '>')
    s2 = s2.replace ('<>', '>')
    s2 = s2.replace ('||', '>')
    s2 = s2.replace ('&&', '>')
    s2 = s2.replace ('%', '>')
    s2 = s2.replace ('-->', '>')
    s2 = s2.replace ('imply', '>')
    s2 = s2.replace ('A[]', '>')
    return re.split('\+|\-|<|>|<=|>=|=|==|\*|/|!=|<>|\(|\)|not|\[\]', s2) #ToDo> check all operator in UPPAAL

def GetLines (text):
    result = []
    lines = []
    if text != -1:  lines = re.split(",", text)
    for line in lines:
        line = line[line.find("\n")+1:]
        result.append(line)
    return result


def GetMultiLineLeftSideVariables (assign): #take a multi line assigment and returns all the variables used in the left side
    variables = []
    if assign ==  -1: return variables
    lines = re.split(",", assign)


    for line in lines:
        line = line[line.find("\n")+1:]
        variables = variables + Spliter(GetLeftSide(line))
    return variables

def GetMultiLineRightSideVariables (assign): #take a multi line assigment and returns all the variables used in the right side
    variables = []
    if assign ==  -1: return variables
    lines = re.split(",", assign)

    for line in lines:
        line = line[line.find("\n")+1:]
        variables = variables + Spliter(GetRightSide(line))
    return variables

def Projection(block, statements): #returns a projectio of the block on the statements
    result=[]
    assigments = GetLines(block)
    for assing in assigments:
        if assing in statements:
            result.append(assing)
    return result

# Clock Engine
def GetClocks (root):
    result = []
    text = root.find('declaration').text
    i = text.find('clock')
    while (i != -1):
        semiColon = text.find(';', i)
        clockName = text[i+6:semiColon]
        result.append(clockName)
        i = text.find('clock', i + 6)
    return result

def GetUsedClockOfState (template, id, clocks):
    result =[]
    location = GetLocationById(template, id)
    invariant = GetInvariant(location)
    variables = []
    if invariant != -1: variables = variables + Spliter(invariant)
    for clock in clocks:
        if clock in variables and not clock in result : result.append(clock)

    for transition in template.iter('transition'):
        source = transition.find('source').attrib['ref']
        target = transition.find('target').attrib['ref']
        if source == id:
            guard = GetGuard(transition)
            assignment = GetAssignment(transition)
            variables = []
            if guard != -1: variables = variables + Spliter(guard)
            variables = variables + GetMultiLineRightSideVariables(assignment)
            for clock in clocks:
                if clock in variables and not clock in result : result.append(clock)

    return  result



def IsReachableNotSetClock (root, id1, id2, checked, avoid, clocks): #returns true if id2 is reachable from id1 avoiding the avoid
    if id1 == id2:
        return True
    checked.append(id1)
    template = GetLocationTemplateById(root, id1)
    for transition in template.iter('transition'):
        assignment = GetAssignment(transition)
        variables = GetMultiLineLeftSideVariables(assignment)
        noChange = True
        for clock in clocks:
                if clock in variables: noChange = False
        if (noChange):
            source = transition.find('source').attrib['ref']
            target = transition.find('target').attrib['ref']
            if (source == id1) and not (target in checked) and target != avoid:
                result = IsReachable(root, target, id2, checked, avoid)
                if result:
                    return True
    return False

def IsAssigment (statement):
    if statement.find('>'): return False
    if statement.find('<'): return False
    if statement.find('=='): return False
    if statement.find('!'): return False
    return True

def Use(statement):
    if IsAssigment(statement):
        return Spliter(GetRightSide(statement))
    else:
        return Spliter(statement)


# Set Engine...
def Union(list1, list2):
    result = list1
    for l2 in list2:
        if l2 not in list1: result.append(l2)
    return result

def RemoveDuplicates (list):
    result = []
    for l in list:
        if l not in result: result.append(l)
    return result

Numbers = ["0","1","2","3","4","5","6","7","8", "9"]
def RemoveDuplicatesandNumbers (list):
    result = []
    for l in list:
        if l not in result and l not in Numbers: result.append(l)
    return result


def intersect(a, b):
     return list(set(a) & set(b))


# Depenencies Engine......
def IsDataDep(s1, s2): #s1 is dependent on s2
    variables = Use(s1)
    v = GetLeftSide(s2)
    return v in variables

def IsControlDep(root, id1, id2): #return true if id1 is control dependent on id2
    C1 = False
    C2 = False
    template = GetLocationTemplateById(root, id1)

    nextStates= GetNextStates(template, id2)
    for location in nextStates :
        checked = [id2, location]
        if (not C1) and AllPathsReach(template, location, id1, checked):
            C1 = True
            break
            '''
    for location in nextStates:
        if not IsReachable(root, location, id1, [], id2):
            C2 = True
            break
            '''
    checked = [id2]
    if not AllPathsReach (template, id2, id1, checked): C2 = True
    if GetLocationNameById(root, id1) == "notify_now" and GetLocationNameById(root, id2) == "advancing_time" :
        for n in nextStates:
            print "nexState:", GetLocationNameById(root, n)
        print "C1:",  C1
        print "C2:",  C2

    return C1 and C2

def IsClockDep (root, id1, id2, clocks): #return true if l1 is clock dependent on l2
    template = GetLocationById(root, id1)
    for transition in template.iter('transition'):
        source = transition.find('source').attrib['ref']
        target = transition.find('target').attrib['ref']
        if source == id2:
            variables = []
            assignment = GetAssignment(transition)
            variables = GetMultiLineLeftSideVariables(assignment)
            usedClocks = GetUsedClockOfState(template,id1,clocks)

            for clock in usedClocks:
                checked = []
                clocks2 = [clock]
                if clock in variables and IsReachableNotSetClock(root,target,id1, checked,target,clocks2): return True
    return  False

def IsTimeDep (root, id1, id2):  #return true if l1 is time dependent on l2
    template = GetLocationTemplateById(root, id2)
    checked = []
    C1 = IsReachable(root, id2, id1, checked, id2)
    C2 = not IsUrgent(template, id2)
    return C1 and C2


def GetAllDependentLocations (root, R): #returns the list of all names of states which are dependent on location in R
    result = []
    clocks = GetClocks(root)
    for r in R:
        id1 = GetLocationId(root, r)
        template = GetLocationTemplateByName (root, r)
        locations = GetLocationsOfTemplate(template)
        for location in locations:
            locationId = location.attrib['id']
            if IsControlDep(root, id1, locationId) or IsClockDep(root, id1, locationId,clocks) or IsTimeDep(root, id1, locationId):
                result.append(location.find('name').text)

    return RemoveDuplicates(result)


def GetAllDependentStatements(root, A):
    result = []
    All_statements = GetAllAssignments(root)
    for s in All_statements:
        for a in A:
            if IsDataDep(a, s): result.append(s)
    return RemoveDuplicates(result)



def GetSyncDependentLocation (root, L):
    result = []
    for template in root.iter('template'):
        for transition in template.iter('transition'):
            source = transition.find('source').attrib['ref']
            label = GetSyncLabel(transition)
            if label in L: result.append(GetLocationById(root,source).find('name').text)
    return RemoveDuplicates(result)

def GetSyncLables(root, R):
    result = []
    for template in root.iter('template'):
        for transition in template.iter('transition'):
            source = transition.find('source').attrib['ref']
            label = GetSyncLabel(transition)
            if label != -1 and GetLocationById(root,source).find('name').text in R: result.append(label)
    return RemoveDuplicates(result)

#Mix Engine
def Qr (root, R):
    result = []
    ids = GetLocationsID(root)
    for id in ids:
        for r in R:
            r_id = GetLocationId(root, r)
            checked = []
            if IsReachable(root, id, r_id, checked, id):
                name = GetLocationNameById(root, id)
                if name not in result:
                    result.append(name)
    return RemoveDuplicates(result)

def Qphi (root, R, Q_r):
    result = []
    Q = GetLocationsName(root)
    diff = list(set(Q) - set(Q_r))
    print "diff: ", diff
    for q in diff:
        Pre = GetImPre(root, q)
        if (q == "Init2"):
            print "Init2 Pre:", Pre
            print "Init2 Pre & Q_r: ", (list(set(Pre) & set(Q_r)))
            #print "Q_r:", Q_r
        
        if list(set(Pre) & set(Q_r)): 
            result.append(q)
            print "q is added :", q
    return RemoveDuplicates(R + result)


#Builidng Engine
from xml.etree import ElementTree
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def SlicedTemplate(root, oldTemplate, Q_r, Q_phi, A):
    newTemplate  = Element('template')

    name =  oldTemplate.find('name')
    if name != None: newTemplate.append(name)

    parameter =  oldTemplate.find('parameter')
    if parameter != None: newTemplate.append(parameter)

    declaration =  oldTemplate.find('declaration')
    if declaration != None: newTemplate.append(declaration)

    #locations....
    noLocation = True
    for location in oldTemplate.iter('location'):
        name = location.find('name').text
        if name in Q_phi:
            # for label in location.iter('label'):
            #     if label.attrib['kind'] == "invariant":
            #         label.text = ",\n".join(Projection(label.text, A))
            noLocation = False
            newTemplate.append(location)
    if noLocation: return -1
    #initial location......
    inital_id = oldTemplate.find('init').attrib['ref']
    inital_name = GetLocationNameById(root, inital_id)
    initalElement = Element('init')
    newInitId = inital_id
    if inital_name not in Q_phi :
        checked = [inital_id]
        newInitId = GetFirstInQ_phi (root, oldTemplate, inital_id, Q_phi, checked)
        if newInitId == -1 : return -1
    initalElement.attrib['ref'] = newInitId
    newTemplate.append(initalElement)

    #transitions....
    QirIDs = [] # :D
    for location in oldTemplate.iter('location'):
        name = location.find('name').text
        if name in list(set(Q_phi) & set(Q_r)): QirIDs.append(location.attrib['id'])

    for q in QirIDs:
        for transition in oldTemplate.iter('transition'):
            source = transition.find('source').attrib['ref']
            target = transition.find('target').attrib['ref']

            if source == q:
                newTransition = Element('transition')
                newTransition.append(transition.find('source')) #copying source

                finalTarget = target
                checked = [source]
                if GetLocationNameById(root, finalTarget) not in Q_phi:
                    finalTarget = GetFirstInQ_phi(root, oldTemplate, target, Q_phi, checked)
                    if finalTarget == -1: continue
                newTarget = transition.find('target')
                newTarget.attrib['ref'] = finalTarget
                newTransition.append(newTarget)        #adding target

                for label in transition.iter('label'):
                    if label.attrib['kind'] == "synchronisation":  #copying synchronization labels
                        newTransition.append(label)
                    if label.attrib['kind'] == "guard":
                        label.text = ",\n".join(Projection(label.text, A)) #adding gurad
                        newTransition.append(label)
                    if label.attrib['kind'] == "assignment":
                        label.text = ",\n".join(Projection(label.text, A)) #adding assignment
                        newTransition.append(label)
                for nail in transition.iter('nail'):
                    newTransition.append(nail)
                newTemplate.append(newTransition)

    return newTemplate

def GetFirstInQ_phi(root, oldTemplate, startId, Q_phi, checked):
    name = GetLocationNameById(root, startId)
    if name in Q_phi: return startId
    checked.append(startId)
    for transition in oldTemplate.iter('transition'):
            source = transition.find('source').attrib['ref']
            target = transition.find('target').attrib['ref']
            if (source == startId) and not (target in checked):
                result = GetFirstInQ_phi(root, oldTemplate, target, Q_phi, checked)
                if result != -1:
                    return result
    print("GetFirsInQ: -1")
    print "checked: ", checked
    print "name: ", name
    return -1

