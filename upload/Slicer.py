#!/usr/bin/python



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


#print "\n############################################################################"
#print "some requirements for the model to have a correct result: \n"
#print "     1- any state which is ungent needs to be marked urgent in the UPPAAL model"
#print "     2- any template should have initial state."
#print  "############################################################################ \n\n"

if __name__ == '__main__':

    try:
        #tree = ET.parse("bit_protocol.xml")
        tree = ET.parse(sys.argv[1])
        root = tree.getroot()
        CorrectLocationsName(root)


        #creating initial states----------------------------
        A_init = []
        All_assigments = GetAllAssignments(root)
        phi = sys.argv[2]


        #----correction of phi
        for template in root.iter('template'):
            templateName = template.find("name").text
            phi = phi.replace(templateName + ".", '')


        for a in All_assigments:
            for v in Spliter(phi):
                if (v in Spliter(GetLeftSide(a))) and a not in A_init :
                    A_init.append(a) 


        print "    Phi: ", phi

        print "    A_init: ", A_init


        R_init = []
        elements = Spliter(phi)
        All_locations = GetLocationsName (root)
        for element in elements:
            if element in All_locations:
                R_init.append(element)


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

        print("    Q_r: {}".format(Q_r))
        print("    Q_phi: {}".format(Q_phi))



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

        print "    No. of locations in the original model: ", len(All_locations), ", No. of relevant locations: ", len(Q_phi)
        print "    No. of variables in original model: ", len(RemoveDuplicatesandNumbers(left)), ", No. of variables in sliced model: ", len(RemoveDuplicatesandNumbers(left_A))

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




    except:
        traceback.print_exc()
        print "\n################################################################################"
        print "THE \"TA MODEL\" AND \"PROPERTY TO BE VERIFIED\" ARE NOT SPECIFIED!"
        print "AN EXAMPLE FOR THE INPUT IS:"
        print "     ./Slicer.py bit_protocol.xml \"A[] not (Sender.snd_init) || (s_bit==r_bit)\""
        print  "################################################################################ \n\n"
        pass
