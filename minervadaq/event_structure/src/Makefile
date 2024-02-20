# Use one of these two lines, but not both
#CPPFLAGS  = -g -fno-inline -O0  # debugging & no optimization
CPPFLAGS  = -O3                 # all optimizations, combine with GOFAST
#--DEBUG FLAGS--
COMPILE_OPTIONS += -DGOFAST  # comment this OUT to get full logging back

#CPPFLAGS += -Werror -Wall -DLINUX -fPIC
CPPFLAGS += -Wall -DLINUX -fPIC

LDFLAGS  += -shared -Wl,-soname

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
	rm -f *.o; 
	cd $(DAQROOT)/lib; rm -f $(TARGET)
