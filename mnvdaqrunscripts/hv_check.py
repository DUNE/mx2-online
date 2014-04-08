#!/usr/bin/env python

#TODO FOR ANNE::
#--Write in names of the the options to make the output easier to read
#--test to make sure the input files work correctly
#--add a help mennu?? 

import re
from itertools import izip
from optparse import OptionParser
import optparse
import sys

mand = OptionParser()
mand.add_option('-o','--old_file', dest="file1", help='Previous HWCFG File Name')
mand.add_option('-n','--new_file', dest="file2", help='New HWCFG File Name')

(options, args) = mand.parse_args()
            
to_check=[0,1,2,3,4,5,6,7,8,9,10,13,14,19,20,21,22,23,24,25,26,27,30,31,32,33,34,36,37,40,43,45,46,47,48,49,50,51,52]


print options.file1
print options.file2

for line1, line2 in izip(open(options.file1),open(options.file2)):
   if re.match(r'FPGA(.*)',line1) and re.match(r'FPGA(.*)',line2):
      #print(line1 + line2)
      FPGA_num = line1.split(':')
      file1_test=line1.split(',')
      file2_test=line2.split(',')
      for item in to_check:
         if file1_test[item]!=file2_test[item]:
            tmp1=file1_test[3].split(":")
            tmp2=file2_test[3].split(":")
           # print (str(item) + file1_test[item] + "  "+ file1_test[0] + file1_test[1] +   file1_test[2]  + " old file  " + file1_test[item]+ " new file " + file2_test[item] )
            print (str(item) +" "+ FPGA_num[1] + " old file  " + file1_test[item]+ " new file " + file2_test[item] )
            # check to find the differences between the target voltages. 
            if item==25 :
               hex1_part1 = file1_test[item+1].replace("'","")
               hex1_part2 = file1_test[item].replace("'","")
               hex1 = hex1_part1+hex1_part2
               hex1_new = hex1.replace(" ","")

               hex2_part1 = file2_test[item+1].replace("'","")
               hex2_part2 = file2_test[item].replace("'","")
               hex2 =  hex2_part1+hex2_part2
               hex2_new = hex2.replace(" ","")
               print (FPGA_num[1] +"  "+str((int(hex2_new,16)-int(hex1_new,16))*0.0170213))
                     
