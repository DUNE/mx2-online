CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=daq_master

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

