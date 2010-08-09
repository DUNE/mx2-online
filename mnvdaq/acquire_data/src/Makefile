CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC

#--CRIM ACCESS FLAGS--
COMPILE_OPTIONS += -DPOLL_INTERRUPT
#COMPILE_OPTIONS += -DASSERT_INTERRUPT
#--DEBUG FLAGS--
#COMPILE_OPTIONS += -DSHOWFPGA   # "new" readout flag
#COMPILE_OPTIONS += -DSHOW_REGISTERS
#COMPILE_OPTIONS += -DSHOW_DATABYTES        # Show full data frames during debugging.
#COMPILE_OPTIONS += -DDEBUG_ET_REPORT_EVENT
#COMPILE_OPTIONS += -DDEBUG_INIT          # Initialization messages.
#COMPILE_OPTIONS += -DDEBUG_IRQ           # IRQ Setup.
#COMPILE_OPTIONS += -DDEBUG_VERBOSE
#COMPILE_OPTIONS += -DDEBUG_TRIGGER
#COMPILE_OPTIONS += -DDEBUG_SENDMESSAGE  
#COMPILE_OPTIONS += -DDEBUG_FASTCOMMAND  # CROC FastCommand Register
#COMPILE_OPTIONS += -DDEBUG_COSMICS
#COMPILE_OPTIONS += -DDEBUG_LIMITEDBANKS
#--READOUT FLAGS--
COMPILE_OPTIONS += -DREAD_DISC
COMPILE_OPTIONS += -DREAD_ADC
#COMPILE_OPTIONS += -DZEROSUPPRESSION  # Don't read the end of gate hit.

LDFLAGS += -shared -Wl,-soname
CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=libminerva_acquire.so

LDLIBS += -L$(DAQROOT)/lib -lhardware -lcaeninterface -L$(ET_LIBROOT)/lib -let
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

