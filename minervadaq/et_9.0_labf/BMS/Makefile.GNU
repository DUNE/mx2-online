# This defines things common to GNU compilation

CC  = gcc
CXX = g++

LD   = $(CXX)
DCC  = $(CC)  -MM -MT
DCXX = $(CXX) -MM -MT

CFLAGS   += -Wall -fPIC -D_GNU_SOURCE
CXXFLAGS += -Wall -fPIC -D_GNU_SOURCE

ifndef CODA_USE64BITS
  CFLAGS      += -m32
  CXXFLAGS    += -m32
  SHLIB_LD    += -m32
  LD_SO_FLAGS += -m32
  LDFLAGS     += -m32
endif
