"""
  shelf2to3.py:
  Script to regenerate db files produced by shelve in python2 
  into a db file compatible with python3

  Needs to be run in Python2!

  Usage:
  To write to new file:
  python2 shelf2to3.py <python2 .db file> <new .db file>
  To overwrite original file:
  python2 shelf2to3.py <python2 .db file>
   Original author: A. Hart (alhart@fnal.gov)
                    Feb. 2024
"""
import shelve
import gdbm
import sys
import os

def gdbm_shelve(filename,flag="c"):
    return shelve.Shelf(gdbm.open(filename,flag))

def main(argv):
    outpath = ""
    if(len(argv)==1):
        outpath = argv[0]+"_tmp"
    elif (len(argv==2)):
        outpath = argv[1]
    else:
        print("Requires 1 or 2 arguments!")
        return

    out_shelf=gdbm_shelve(outpath)
    in_shelf=shelve.open(argv[0])


    key_list=in_shelf.keys()
    print(key_list)
    for key in key_list:
        out_shelf[key]=in_shelf[key]

    out_shelf.close()
    in_shelf.close()
    if(len(argv)==1):
        os.rename(outpath, argv[0])


if __name__ == "__main__":
   main(sys.argv[1:])