CPPFLAGS = -g -Wall
CXX = g++
OBJS = hvCheck.o
SRC = hvCheck.cpp
TARGET = hvCheck

CPPFLAGS += -I/usr/include -I$(CAEN_DIR)/include -I$(DAQROOT)/fermihardware/include -I$(DAQROOT)/caeninterface/include 

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

