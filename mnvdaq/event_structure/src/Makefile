CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC
LDFLAGS += -shared -Wl,-soname

#--DEBUG FLAGS--
#COMPILE_OPTIONS += -DDEBUG_HEADERS
#COMPILE_OPTIONS += -DDEBUG_MAKEDATABLOCK # CAREFUL!  This dumps a lot of txt to std out.

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=libevent_structure.so

include $(DAQROOT)/Make.include

$(TARGET): $(OBJS)
	@echo $(OBJS)
	$(CXX) $(LDFLAGS),$(TARGET) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../../lib;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm *.o; 

