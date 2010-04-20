CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC

COMPILE_OPTIONS = -DTAKE_DATA 
#COMPILE_OPTIONS += -DTHREAD_ME
COMPILE_OPTIONS += -DNO_THREAD
COMPILE_OPTIONS += -DRECORD_EVENT
#COMPILE_OPTIONS += -DASSERT_INTERRUPT

#--DEBUG FLAGS--
#COMPILE_OPTIONS += -DTIME_ME
#COMPILE_OPTIONS += -DDEBUG_GENERAL
#COMPILE_OPTIONS += -DDEBUG_THREAD
#COMPILE_OPTIONS += -DDEBUG_SOCKETS
#COMPILE_OPTIONS += -DDEBUG_MIXEDMODE
COMPILE_OPTIONS += -DDEBUG_TIMING
COMPILE_OPTIONS += -DRUN_SLEEPY # This flag is required to for FEB digitization.  2009.Dec.16

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=minervadaq

LDLIBS += -L$(DAQROOT)/lib -lhardware -lminerva_acquire -lcaeninterface
include $(DAQROOT)/Make.include
include $(DAQROOT)/Make.options

$(TARGET): $(OBJS)
	@echo $(OBJS)
	@echo $(LDLIBS)
	$(CXX) $(LDFLAGS) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../bin;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm *.o; 

