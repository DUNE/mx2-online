CPPFLAGS = -g -Wall
CXX = g++
OBJS = runCrocStatus.o
SRC = runCrocStatus.cpp
TARGET = runCrocStatus

# General Environment
CPPFLAGS += -I/usr/include
# log4cpp Classes 
CPPFLAGS += -I/usr/local/include
# MINERvA DAQ Classes
CPPFLAGS += -I$(CAEN_DIR)/include -I$(DAQROOT)/fermihardware/include -I$(DAQROOT)/caeninterface/include

# log4cpp Libraries
LDLIBS += -L/usr/local/lib -llog4cpp -L/usr/lib64 -lpthread
# MINERvA DAQ Libraries
LDLIBS += -L/usr/lib64 -lCAENVME -L$(DAQROOT)/lib -lhardware -lminerva_acquire

$(TARGET): $(OBJS)
	@echo $(OBJS)
	$(CXX) -o $(TARGET) $(OBJS) $(LDLIBS)

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) -g -fno-inline -O0 -DLINUX -c $< -o $@

clean:
	rm $(OBJS)
	rm $(TARGET)

