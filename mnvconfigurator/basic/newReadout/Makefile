CPPFLAGS = -g -Wall -O0 -DLINUX
CXX = g++
OBJS = newReadout.o
SRC = newReadout.cpp
TARGET = newReadout

#COMPILE_OPTIONS += -DSHOWFPGA
#COMPILE_OPTIONS += -DSHOWDISC
#COMPILE_OPTIONS += -DSHOWADC
#COMPILE_OPTIONS += -DDEBUG_VERBOSE

CPPFLAGS += -I/usr/include -I$(CAEN_DIR)/include -I$(DAQROOT)/fermihardware/include -I$(DAQROOT)/caeninterface/include 

LDLIBS += -L/usr/lib64 -lCAENVME -L$(DAQROOT)/lib -lhardware -lminerva_acquire

$(TARGET): $(OBJS)
	@echo $(OBJS)
	$(CXX) -o $(TARGET) $(OBJS) $(LDLIBS)

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm $(OBJS)
	rm $(TARGET)

