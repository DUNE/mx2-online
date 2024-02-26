"""
  shelf2to3.py:
  Script to regenerate db files produced by shelve in python2 
  into a db file compatible with python3

  Usage:
  python shelf2to3.py <python2 .db file> <new .db file>
  
   Original author: A. Hart (alhart@fnal.gov)
                    Feb. 2024
"""
import shelve
import dbm.gnu
import sys

def gdbm_shelve(filename,flag="c"):
    return shelve.Shelf(dbm.gnu.open(filename,flag))

def main(argv):
    out_shelf=gdbm_shelve(argv[1])
    in_shelf=shelve.open(argv[0])

    key_list=list(in_shelf.keys())
    print(key_list)
    for key in key_list:
        out_shelf[key]=in_shelf[key]

    out_shelf.close()
    in_shelf.close()

if __name__ == "__main__":
   main(sys.argv[1:])