#!/usr/bin/python2.4

# Author: C. Castromonte
# e-mail: cesarc@cbpf.br
# 04/30/10


import os.path, glob, sys
import string

import MySQLdb
import time, datetime

### ---------------------------- ###

def loc_2l_item(pattern, dir, type):
# retrieve the file information from a selected folder
# sort the files by last modified date/time and give the 2 latest files
    date_file_list = []
    for folder in glob.glob(dir):

        for file in glob.glob(folder + '/' + pattern):
            stats = os.stat(file)
            lastmod_date = time.localtime(stats[8])
            date_file_tuple = lastmod_date, file, stats[8]
            date_file_list.append(date_file_tuple)
    
    date_file_list.sort()

    if (type == "c"): pos = 1
    if (type == "p"): pos = 2

    loc_arr = date_file_list[len(date_file_list)-pos]

    loc_file = loc_arr[1]
    ftmp = loc_file.split("_")
    loc_run = int(ftmp[1])
    loc_srun = int(ftmp[2])
    loc_runt = ftmp[3]
    loc_etime = loc_arr[2]

    return loc_file,loc_run,loc_srun,loc_runt,loc_etime

### ---------------------------- ###

def loc_1_item(pattern, dir, p_run, p_srun):
# retrieve information from a selected file

    sam_file = "-"; sam_run = 0; sam_srun = 0

    for folder in glob.glob(dir):

        for file in glob.glob(folder + '/' + pattern):
            ftmp2 = file.split("_")
            trun = int(ftmp2[1])
            tsrun = int(ftmp2[2])

            if (p_run == trun and p_srun == tsrun):
               sam_file = file
               sam_run = trun
               sam_srun = tsrun

#    print sam_file,sam_run,sam_srun
    return sam_file,sam_run,sam_srun               

### ---------------------------- ###

def dq_chk(fname):
#    print fname
   
    ietime = 0; eetime = 0; ngates = 0

    infile = open(fname,'r')
    data =  infile.readlines()
    infile.close()

    fn_tmp = fname.split("/")
    type = fn_tmp[4]
#    print type

    if (type == "logs"): search_words = ['Starting MINERvA','Acquiring Gate','Total acquisition']
    if (type == "sam"): search_words = ['startTime','eventCount','endTime']

    for word in search_words:
 
        for line in data:

            if line.find(word) >= 0:
               results=line
    
               if (type == "logs"):
                  if word == 'Starting MINERvA':    
                     st_tmp = results.split()
                     ietime = int(st_tmp[0])

                  if word == 'Acquiring Gate': #num of gates
                     ag_tmp = results.split()
                     ngates = int(ag_tmp[6])

                  if word == 'Total acquisition':    
                     et_tmp = results.split()
                     eetime = int(et_tmp[0])

               if (type == "sam"):
                  if word == 'startTime': 
                     ietime = int(results.split("'")[1])

                  if word == 'eventCount':  #num of gates
                     evnt_tmp = results.split(",")
                     uelim = len(evnt_tmp[0])
                     ngates=int(evnt_tmp[0][11:uelim])
                  
                  if word == 'endTime': 
                     eetime = int(results.split("'")[1])

    return ngates,ietime,eetime
    
### ---------------------------- ###

class Table:
     def __init__(self,db,name):
          self.db = db
          self.name = name
          self.dbc = self.db.cursor()

     def __len__(self):
          self.dbc.execute("select count(*) from %s" %(self.name))
          l = int(self.dbc.fetchone()[0])
          return l

     def check_item(self,var1,var2):
          sql = "select RUN,SRUN,DAQSTAT from %s where RUN=%d and SRUN=%d" %(self.name,var1,var2)
          self.dbc.execute(sql)
          return

     def ins_check_item(self,var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11):
          sql = "insert into %s (IDATE,ITIME,RUN,SRUN,RUNT,NGATES,ETIME,DAQSTAT,ADATQUAL,DSTSTAT,MDATQUAL) values ('%s','%s',%d,%d,'%s',%d,%d,'%s','%s','%s','%s') " % (self.name,var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11)
          self.dbc.execute(sql)
          return

     def sel_last_item(self):
          sql = "select RUN,SRUN,RUNT from %s where RUN is not null order by ETIME desc limit 1" %(self.name)
          self.dbc.execute(sql)
          return

     def updt_last_item(self,var1,var2,var3,var4,var5):
          sql = "update %s set NGATES=%d, DAQSTAT='%s', ADATQUAL='%s' where RUN=%d and SRUN=%d" %(self.name,var1,var2,var3,var4,var5)
          self.dbc.execute(sql)
          return

     def updt_last_finished_item(self,var1,var2,var3):
          sql = "update %s set DAQSTAT='%s' where RUN=%d and SRUN=%d" %(self.name,var1,var2,var3)
          self.dbc.execute(sql)
          return

### ---------------------------- ###

# test variables for database access  
HOST = 'fnalmysqldev.fnal.gov'
USER = 'fmindet_write'
PASSWD = 'write_fm99'
DATABASE = 'fmindet'
PORT = 3336

# Open database connection
db = MySQLdb.connect(
     host=HOST,
     port=PORT,
     user=USER,
     passwd=PASSWD,
     db=DATABASE)

### ---------------------------- ###

# test variables for database access  
#HOST = '152.84.101.153'
#USER = 'minerva'
#PASSWD = 'axial'
#DATABASE = 'fmindet'

# Open database connection
#db = MySQLdb.connect(
#     host=HOST,
#     user=USER,
#     passwd=PASSWD,
#     db=DATABASE)

### ---------------------------- ###

tab = Table(db,"DATA1")

logpath='/mnvonline0/work/data/logs'
sampath='/mnvonline0/work/data/sam'

# locate the current log file
l_cfname,l_crun,l_csrun,l_crunt,l_cet = loc_2l_item('*0Log.*',logpath,"c")
#print l_cfname,l_crun,l_csrun,l_crunt

# Does log current run exist in DB?  
tab.check_item(l_crun,l_csrun)
results = tab.dbc.fetchall()

db_crun = -1
db_csrun = -1
db_cdstat = "-"
for row1 in results:
    db_crun=row1[0]
    db_csrun=row1[1]
    db_cdstat=row1[2]
#print db_crun,db_csrun,db_cdstat

if (db_crun == -1 and db_csrun == -1):  # New entry

   # Perform data quality check on previous subrun and update the DB info
   l_pfname,l_prun,l_psrun,l_prunt,l_pet = loc_2l_item('*0Log.*',logpath,"p")
   l_pngates,l_pietime,l_peetime = dq_chk(l_pfname)
#   print l_pngates,l_pietime,l_peetime

   # Look for last entry in DB 
   tab.sel_last_item()
   results2 = tab.dbc.fetchall()

   db_prun = -1
   db_psrun = -1
   for row2 in results2:
       db_prun=row2[0]
       db_psrun=row2[1]  
#   print db_prun,db_psrun

   prun = l_prun; psrun = l_psrun; 
   prunt = l_prunt; pngates = 0; prqual = "No SAM"

   ngcut = 10

   if (db_prun == l_prun and db_psrun == l_psrun): #is last DB entry = log previous run? => look for sam file 

      s_pngates = 0; s_pietime = 0; s_peetime = 0

      s_pfname,s_prun,s_psrun = loc_1_item('*.py',sampath,l_prun,l_psrun)  
#      print s_pfname,s_prun,s_psrun

      if (s_pfname != "-"): # if sam file exists then do data quality check
         s_pngates,s_pietime,s_peetime = dq_chk(s_pfname)
#         print s_pngates,s_pietime,s_peetime

         if (abs(l_pietime - s_pietime)<10): # very close epoch time
            pngates = l_pngates; 
            prqual = "Bad"
            if pngates >= ngcut: prqual = "Good"

#   print "Entry updated: ",prun,psrun,prunt,prqual,pngates
   tab.updt_last_item(pngates,"Finished",prqual,prun,psrun)

   ### .................. ###

   # Update current info file in DB  
   if os.path.isfile(l_cfname):
#      print l_cfname

      l_cngates = 0
      l_cetime = 0

      infile = open(l_cfname,'r')
      data =  infile.readlines()
      infile.close()

      search_words = ['Starting MINERvA','Total Gates']

      for word in search_words:

          for line in data:

              if line.find(word) >= 0:
                 results=line
      
                 if word == 'Starting MINERvA':    
                    sm_tmp = results.split()
                    l_cetime = int(sm_tmp[0])
                    idatetime = datetime.datetime.fromtimestamp(l_cetime)
                    l_cidate = idatetime.date()
                    l_citime = idatetime.time()

                 if word == 'Total Gates':    
                    tg_tmp = results.split()
                    l_cngates = int(tg_tmp[7])

#   print "New entry: ",l_cidate,l_citime,l_crun,l_csrun,l_crunt,l_cngates,l_cetime
   tab.ins_check_item(l_cidate,l_citime,l_crun,l_csrun,l_crunt,l_cngates,l_cetime,"Current","-","-","-")

else:
 
  ce_time = int(time.time())

  if ( db_cdstat == "Current" and  (ce_time - l_cet) > 1200 ):
     tab.updt_last_finished_item("Finished",db_crun,db_csrun)
     
db.close()


