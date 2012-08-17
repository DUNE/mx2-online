from commands import *
#import commands

#et_file    = raw_input('Enter ET file name:\n')
#n_febs     = raw_input('Enter the number of FEBs:\n')
#n_gates    = raw_input('Enter the number of gates:\n')
#mode       = raw_input('Enter the run mode:\n')
#run        = raw_input('Enter the run number:\n')
#subrun     = raw_input('Enter the subrun number:\n')

get_date = 'date -u +%y%m%d%k%M'
date = getoutput(get_date)

NFEBS=4
NGATES=10
RUNMODE=0
RUN=1337
SUB=391

ETNAME = 'MN_%08d_%04d_numib_v04_%s' % (int(RUN),int(SUB),date)
#ETNAME=testme
print ETNAME

launch_daq = 'MN_%08d_%04d_numib_v04_%s' % (int(RUN),int(SUB),date)

blah = './start_daq_singleton -et %s -f %s -g %s -m %s -r %s -s %s' % (ETNAME,NFEBS,NGATES,RUNMODE,RUN,SUB)
print blah

#blah = raw_input('Enter a unix command:\n')
#print blah
#print type(blah)
#print getstatusoutput(blah)
print getoutput(blah)


