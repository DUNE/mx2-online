CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC
LDFLAGS += -shared -Wl,-soname
COMPILE_OPTIONS = #-DDEBUG -DDEBUG_FEB
COMPILE_OPTIONS += -DDEBUG_VERBOSE
CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=libhardware.so

include $(DAQROOT)/Make.include

$(TARGET): $(OBJS)
	@echo $(OBJS)
	$(CXX) $(LDFLAGS),$(TARGET) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../../lib;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	@echo $(INCLUDE)
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm *.o; 

