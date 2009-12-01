CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC
COMPILE_OPTIONS = -DTAKE_DATA 
#COMPILE_OPTIONS += -DTHREAD_ME
COMPILE_OPTIONS += -DNO_THREAD
COMPILE_OPTIONS += -DDEBUG_ME 
#COMPILE_OPTIONS += -DDEBUG_THREAD
COMPILE_OPTIONS += -DRECORD_EVENT
COMPILE_OPTIONS += -Dv81
#COMPILE_OPTIONS += -Dv65
#COMPILE_OPTIONS += -DASSERT_INTERRUPT
COMPILE_OPTIONS += -DKEEP_DATA
#COMPILE_OPTIONS += -DTIME_ME
COMPILE_OPTIONS += -DSINGLE_PC
#COMPILE_OPTIONS += -DMULTI_PC
#COMPILE_OPTIONS += -DMASTER

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=minervadaq

LDLIBS += -L$(DAQROOT)/lib -lhardware -lminerva_acquire -lcaeninterface
include $(DAQROOT)/Make.include

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

