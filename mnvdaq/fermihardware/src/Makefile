CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC
LDFLAGS += -shared -Wl,-soname
#COMPILE_OPTIONS = -Dv65 #-DDEBUG_FEB 
COMPILE_OPTIONS = -Dv81 -DDEBUG -DDEBUG_FEB 
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
#	$(CXX) $(CPPFLAGS) $(INCLUDE) -DDEBUG_FRAME_BASE -c $< -o $@
#	$(CXX) $(CPPFLAGS) $(INCLUDE) -DDEBUG_FEB -c $< -o $@
#	$(CXX) $(CPPFLAGS) $(INCLUDE) -DDEBUG_CHANNELS -c $< -o $@
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm *.o; 

