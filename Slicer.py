from fileinput import filename
import sys
import operator
import sys, os, traceback
from os.path import join, getsize
import datetime
import copy
import re

import xml.etree.cElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from UPPAL_XML_Parser import *

#tree = ET.parse("bit_protocol_6.xml")
#tree = ET.parse("prod_cons_b_revisd2.xml")
#tree = ET.parse("test.xml")
tree = ET.parse("initiator_target_nb_revised.xml")
root = tree.getroot()

# some requirements for the model to have a correct result:
# 1- any state which is ungent should be marked urgent in the UPPAAL model
# 2- any template should have initial state.



CorrectLocationsName(root)
'''
id1 = GetLocationId(root, "wait_for_delta")
id2 = GetLocationId(root, "notify_now")
check = []
id3 = GetLocationId(root, "advancing_time")
print IsReachable(root, id1, id2, check, id3)
exit()
'''
#creating initial states----------------------------


A_init = []
All_assigments = GetAllAssignments(root)
#phi = "A[] not (Sender.snd_init) || (s_bit==r_bit)"
#phi = "(Init.L1||Init2.L6) --> ((Init.L4 || Init2.L9) and x>=delay1)"
#phi = "consumer_consume.mon_start1 --> consumer_consume.mon_end1"
#phi = "SchedulerTemplate.evaluate --> SchedulerTemplate.execute" #liveness
#phi = "A[] SchedulerTemplate.update imply readyprocs==0" #imply
#phi = "A[] SchedulerTemplate.evaluate imply (not SchedulerTemplate.execute)"
#phi = "E<> SchedulerTemplate.execute" #reachability
#phi = "SchedulerTemplate.execute --> SchedulerTemplate.evaluate"
#phi = "A[] ((myfifo_write.fifow4) &&  (myfifo_read.fifo_r4)) imply w_pos == r_pos"
#phi = "A[] (w_pos + 1)%3 == r_pos"
#phi = "E<> Initiator_free.Init_free1"
phi = "Initiator_thread_process.Init_thread_process20 --> Target_nb_transport_fw.nb_fw1"



#----correction of phi
for template in root.iter('template'):
    templateName = template.find("name").text
    phi = phi.replace(templateName + ".", '')
print "ffff ", phi


for a in All_assigments:
    for v in Spliter(phi):
        #if (v in Spliter(GetLeftSide(a))) and not a in A_init: A_init.append(a)
        if (v in Spliter(GetLeftSide(a))) and a not in A_init :
            A_init.append(a) #REZA


print "    Phi: ", phi

print "    A_init: ", A_init


R_init = []
elements = Spliter(phi)
print "ssss, ", elements
All_locations = GetLocationsName (root)
for element in elements:
    if element in All_locations:
        R_init.append(element)


#REZA
R_init_prime = []
for r in R_init:
    pre = GetImPre(root, r)
    for p in pre:
        R_init_prime.append(p)
for r in R_init_prime:
    R_init.append(r)

R_init = RemoveDuplicates(R_init)
print "    R_init: ", R_init




#Calculating Q_r and Q_phi--------------------------------------------------

R = R_init
A = A_init
L = []

R1 = []
A1 = []
L1 = [1] # set to [1] to insure that the while loop will run for the first time.


while (R1 != R or A1 != A or L1 != L):
    R1 = R
    A1 = A
    L1 = L

    A2 = RemoveDuplicates(A + GetGuardOfLocations(root, GetAllDependentLocations(root, R) + GetInvolvingLocations(root, A)))
    A = RemoveDuplicates(A2 + GetAllDependentStatements(root, A2))

    R2 = RemoveDuplicates(R + GetInvolvingLocations(root, A) )
    R = RemoveDuplicates(R2 + GetAllDependentLocations(root, R2) + GetSyncDependentLocation(root, L))

    L = GetSyncLables (root, R)

print("    R: {}".format(R))
print("    A: {}".format(A))



Q_r = Qr(root, R)
Q_phi = Qphi (root, R, Q_r)

print("  Q_r: {}".format(Q_r))
print("Q_phi: {}".format(Q_phi))
print "Q_phi:", Q_phi


#REZA
#################################################################################################
All_actions = RemoveDuplicates(GetAllActions(root))
left = []
right =[]
for action in All_actions:
	right_temp = GetMultiLineRightSideVariables(action)
	for item in right_temp:
		right.append(item)
	left_temp = GetMultiLineLeftSideVariables(action)
	for item in left_temp:
		left.append(item)
for item in right:
	left.append(item)

left_A = []
right_A = []
right_temp_A = []
left_temp_A = []
for action in A:
	right_temp_A = GetMultiLineRightSideVariables(action)
	for item in right_temp_A:
		right_A.append(item)
	left_temp_A = GetMultiLineLeftSideVariables(action)
	for item in left_temp_A:
		left_A.append(item)
for item in right_A:
	left_A.append(item)

print "No. of locations: ", len(All_locations), ", No. of relevant locations: ", len(Q_phi)
print "No. of variables in original model: ", len(RemoveDuplicatesandNumbers(left)), ", No. of variables in sliced model: ", len(RemoveDuplicatesandNumbers(left_A))
print "Original Vars :", RemoveDuplicatesandNumbers(left)
print "Sliced Vars :", RemoveDuplicatesandNumbers(left_A)
#################################################################################################


# for transition in root.find('template').iter('transition'):
#     source = transition.find('source').attrib['ref']
#     target = transition.find('target').attrib['ref']
#     if source == 'id2':
#         assign = GetAssignment(transition)
#         print(GetMultiLineRightSideVariables (assign))


#Creating the sliced program------------------------------------
newRoot = Element('nta')

declaration =  root.find('declaration')
if declaration != None: newRoot.append(declaration)

#Copy templates
for template in root.iter('template'):
    newTemplate = SlicedTemplate(root, template, Q_r, Q_phi, A)
    #if newTemplate.find("location") != None and newTemplate.find("init").attrib['ref'] != -1: newRoot.append(newTemplate)
    if newTemplate != -1: newRoot.append(newTemplate)

system = root.find('system')
if system != None: newRoot.append(system)

queries = root.find('queries')
if queries != None: newRoot.append(queries)

f = open('result.xml', 'w')
f.write(tostring(newRoot))
