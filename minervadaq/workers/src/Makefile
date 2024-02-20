GIT_VERSION = $(shell sh -c 'git describe --abbrev=4 --dirty --always')

# Use one of these two lines, but not both
CPPFLAGS  = -g -fno-inline -O0  # debugging & no optimization
# CPPFLAGS  = -O1                 # all warning-free optimizations, combine with GOFAST
#--DEBUG FLAGS--
COMPILE_OPTIONS += -DGOFAST  # comment this OUT to get full logging back

#CPPFLAGS += -Werror -Wall -DLINUX -fPIC -DGIT_VERSION=\"$(GIT_VERSION)\"
CPPFLAGS += -Wall -DLINUX -fPIC -DGIT_VERSION=\"$(GIT_VERSION)\"

LDFLAGS += -shared -Wl,-soname

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=libminerva_workers.so

LDLIBS += -L$(DAQROOT)/lib -lhardware -levent_structure -L$(ET_LIBROOT)/lib -let
include $(DAQROOT)/Make.include
include $(DAQROOT)/Make.options

$(TARGET): $(OBJS)
	@echo $(OBJS)
	@echo $(LDLIBS)
	$(CXX) $(LDFLAGS),$(TARGET) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../../lib;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm -f *.o; 
	rm -f ../../lib/libminerva_workers.so;

