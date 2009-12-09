CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC
#COMPILE_OPTIONS += -DTHREAD_ME
COMPILE_OPTIONS += -DNO_THREAD
#COMPILE_OPTIONS += -DDEBUG_THREAD 
COMPILE_OPTIONS += -DDEBUG_ME
#COMPILE_OPTIONS += -DTIME_ME
COMPILE_OPTIONS += -DPOLL_INTERRUPT
#COMPILE_OPTIONS += -DASSERT_INTERRUPT
COMPILE_OPTIONS += -DSHOW_REGISTERS
COMPILE_OPTIONS += -DREPORT_EVENT
COMPILE_OPTIONS += -DREAD_DISC
COMPILE_OPTIONS += -DREAD_ADC

LDFLAGS += -shared -Wl,-soname
CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=libminerva_acquire.so

LDLIBS += -L$(DAQROOT)/lib -lhardware -lcaeninterface -L$(ET_LIBROOT)/lib -let
include $(DAQROOT)/Make.include

$(TARGET): $(OBJS)
	@echo $(OBJS)
	@echo $(LDLIBS)
	$(CXX) $(LDFLAGS),$(TARGET) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../../lib;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@
#	$(CXX) $(CPPFLAGS) $(INCLUDE) -c $< -o $@

clean:
	rm *.o; 
	rm ../../lib/libminerva_acquire.so;

