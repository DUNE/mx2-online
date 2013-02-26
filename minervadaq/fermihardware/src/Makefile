CPPFLAGS  = -g -fno-inline -O0 -Wall -DLINUX -fPIC
CPPFLAGS += -Werror -fno-inline
LDFLAGS  += -shared -Wl,-soname

#--DEBUG FLAGS--
#COMPILE_OPTIONS += -DDEBUG 
COMPILE_OPTIONS += -DDEBUG_FEB
#COMPILE_OPTIONS += -DDEBUG_CROC
#COMPILE_OPTIONS += -DDEBUG_VERBOSE
#COMPILE_OPTIONS += -DDEBUG_CRIM
#COMPILE_OPTIONS += -DDEBUG_CHPREVIEW

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=libhardware.so

include $(DAQROOT)/Make.include
include $(DAQROOT)/Make.options

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
	cd $(DAQROOT)/lib; rm $(TARGET)
