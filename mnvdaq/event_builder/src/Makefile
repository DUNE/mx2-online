CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC
#COMPILE_OPTIONS = -Dv65 
COMPILE_OPTIONS = -Dv81 
COMPILE_OPTIONS += -DREPORT_EVENT
#COMPILE_OPTIONS += -DTHREAD_ME
#COMPILE_OPTIONS += -DDEBUG_THREAD
COMPILE_OPTIONS += -DNO_THREAD
#COMPILE_OPTIONS += -DDEBUG_ME
#COMPILE_OPTIONS += -DTIME_ME
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

