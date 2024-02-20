#CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC -Werror
CPPFLAGS = -g -fno-inline -O0 -Wall -DLINUX -fPIC

CXX = g++
OBJS = $(patsubst %.cpp,%.o,$(wildcard *.cpp))
SRC = $(wildcard *.cpp)
TARGET=tests

LDLIBS += -L$(DAQROOT)/lib -lhardware -lminerva_workers -levent_structure
include $(DAQROOT)/Make.include
include $(DAQROOT)/Make.options

# LDFLAGS = -Wl,--rpath -Wl,$(DAQROOT)/sqlite/lib

$(TARGET): $(OBJS)
	@echo $(OBJS)
	@echo $(LDLIBS)
	$(CXX) $(LDFLAGS) -o $(TARGET) $(OBJS) $(LDLIBS)
	mv $(TARGET) ../bin;

$(OBJS): %.o: %.cpp
	@echo $(SRC) 
	$(CXX) $(CPPFLAGS) $(INCLUDE) $(COMPILE_OPTIONS) -c $< -o $@

clean:
	rm -f *.o; 
	cd $(DAQROOT)/bin; rm -f $(TARGET)
