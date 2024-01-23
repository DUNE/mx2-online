CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC
LDFLAGS += -shared -Wl,-soname
CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=libcaeninterface.so

LDLIBS += -L$(DAQROOT)/lib -lhardware
include $(DAQROOT)/Make.include

$(TARGET): $(OBJS)
	@echo $(OBJS)
	@echo $(LDLIBS)
	$(CXX) $(LDFLAGS),$(TARGET) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../../lib;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(INCLUDE) -c $< -o $@

clean:
	rm *.o; 

