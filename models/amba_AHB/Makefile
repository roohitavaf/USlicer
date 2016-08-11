# Super Generic Makefile
#
# This Makefile compiles every *.cpp and every *.h file into their *.o files.
# Then, an executable is linked and named after the current directory. Make
# sure to have set the environment variable $SYSTEMC_HOME set correctly.
#
# If you need specific changes, write them to ./Makefile.local. This file gets
# include (see below) after variable declarations. Check out
# http://stackoverflow.com/questions/8346118/check-if-a-makefile-exists-before-including-it/8346208#8346208
# for more info on how to (not) override variables.
#
# To (compile and) run the current system c design:
# $> make run
#
# To create the uppaal model:
# $> make uppaal
#


# use current directory name as target name
TARGET = $(shell basename $(CURDIR))
# the name of the ast output file
AST_NAME = $(TARGET)
AST_FILE = $(AST_NAME).ast.xml # this name is given by sc2ast
SC2AST_CMD = java -jar ../../sc2ast.jar
SC2UPPAAL_CMD = java -jar ../../sc2uppaal.jar

# the name of the uppaal model
UPPAAL_FILE = $(TARGET).uppaal.xml

HEADER_FILES = $(wildcard *.h)
CPP_FILES = $(wildcard *.cpp)
ALL_SRC_FILES= $(HEADER_FILES) $(CPP_FILES)
OBJS = $(CPP_FILES:.cpp=.o)

CXX = g++
# -g debug informations, -E output preprocessing result and stop
CFLAGS = -g -Wall -Wno-unused-variable -Wno-unused-but-set-variable #-Wextra
SYSCFLAGS = -DSYSC -DSC_INCLUDE_DYNAMIC_PROCESSES
ARCH ?= $(shell uname -m)
ifeq ($(ARCH),x86_64)
LIBDIR = $(SYSTEMC_HOME)/lib-linux64
else
LIBDIR = $(SYSTEMC_HOME)/lib-linux
endif
# use '-isystem' instead of '-I' to block warnings from included systemc headers *workaround*
INCDIRS = -isystem $(SYSTEMC_HOME)/src 
LIBS = -lsystemc -lm

-include Makefile.local

all: $(OBJS)
	$(CXX) $(CFLAGS) $(INCDIRS) -L $(LIBDIR) -Wl,-rpath=$(LIBDIR) -o $(TARGET) $(OBJS) $(LIBS)

USERDEFINES=
%.o: %.cpp $(HEADER_FILES)
	$(CXX) $(CFLAGS) $(SYSCFLAGS) $(INCDIRS) $(USERDEFINES) -c $*.cpp

run: all
	./$(TARGET)

# make only preprocessing, 'make all' will comlain, screw that!
# use: $> make pp > myoutput
pp: CFLAGS += -E
pp: all

ast: 
	$(SC2AST_CMD) -f $(ALL_SRC_FILES) -o $(AST_NAME)

# ex:
# $> make ARGS="-a '-h'" uppaal
UPPAALDEP=ast
ARGS=
uppaal: $(UPPAALDEP)
	$(SC2UPPAAL_CMD) -i $(AST_FILE) -o $(UPPAAL_FILE) $(ARGS)


clean:
	rm -rf *.o $(TARGET) $(AST_NAME) *syscir $(TARGET).tar.gz $(TARGET).zip AnalysisResult.txt ./logs ./log log.* $(MEMCHK_QRY_FILE) 2> /dev/null


