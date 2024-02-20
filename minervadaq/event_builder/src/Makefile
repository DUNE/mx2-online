# Use one of these two lines, but not both
# CPPFLAGS  = -g -fno-inline -O0  # debugging & no optimization
CPPFLAGS  = -O3                 # all optimizations, combine with GOFAST

#CPPFLAGS  = -Wall -Werror -DLINUX -fPIC
CPPFLAGS  = -Wall -DLINUX -fPIC

#--DEBUG FLAGS--
COMPILE_OPTIONS += -DGOFAST  # comment this out to get full logging back


CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=event_builder

LDLIBS += -L$(DAQROOT)/lib -lhardware -levent_structure -L$(ET_LIBROOT)/lib -let
include $(DAQROOT)/Make.include
include $(DAQROOT)/Make.options

$(TARGET): $(OBJS)
	@echo $(OBJS)
	@echo $(LDLIBS)
	$(CXX) $(LDFLAGS) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../../bin;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm -f *.o; 
	cd $(DAQROOT)/bin; rm -f $(TARGET)

