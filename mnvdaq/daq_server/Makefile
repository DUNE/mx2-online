CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC

#--DEBUG FLAGS--
#COMPILE_OPTIONS += -DDEBUG_GENERAL 

# daq_server does not appear to use any of these...
# Time to start slowly trimming them away...
COMPILE_OPTIONS = -DTAKE_DATA 
COMPILE_OPTIONS += -DNO_THREAD
COMPILE_OPTIONS += -DRECORD_EVENT

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=daq_slave_service

#include $(DAQROOT)/Make.include

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

