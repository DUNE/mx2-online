CPPFLAGS  = -g -fno-inline -O0 -Wall -DLINUX -fPIC
CPPFLAGS += -Werror

#--DEBUG FLAGS--
COMPILE_OPTIONS += -DGOFAST  # comment this out to get full logging back

#--CRIM ACCESS FLAGS--
COMPILE_OPTIONS += -DPOLL_INTERRUPT
#COMPILE_OPTIONS += -DASSERT_INTERRUPT

LDFLAGS += -shared -Wl,-soname
CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=libminerva_acquire.so

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
	rm *.o; 
	rm ../../lib/libminerva_acquire.so;

