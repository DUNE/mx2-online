CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC
#COMPILE_OPTIONS += -DTHREAD_ME
#COMPILE_OPTIONS += -DDEBUG_THREAD
COMPILE_OPTIONS += -DNO_THREAD
#COMPILE_OPTIONS += -DTIME_ME
#--DEBUG FLAGS--
#COMPILE_OPTIONS += -DDEBUG_VERBOSE 
#COMPILE_OPTIONS += -DDEBUG_BUFFERS
#COMPILE_OPTIONS += -DDEBUG_REPORT_EVENT
#--MULTI PC SETUP--
#COMPILE_OPTIONS += -DMULTIPC

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=event_builder

LDLIBS += -L$(DAQROOT)/lib -lhardware -levent_structure -L$(ET_LIBROOT)/lib -let
include $(DAQROOT)/Make.include

$(TARGET): $(OBJS)
	@echo $(OBJS)
	@echo $(LDLIBS)
	$(CXX) $(LDFLAGS) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../../bin;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm *.o; 

