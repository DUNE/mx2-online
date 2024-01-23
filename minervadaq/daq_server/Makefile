CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC

#COMPILE_OPTIONS += -DDEBUG_GENERAL 

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=daq_slave_service

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

