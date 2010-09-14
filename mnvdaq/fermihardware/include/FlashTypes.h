#ifndef FlashTypes_h
#define FlashTypes_h

//these are as yet unused
typedef enum OpCodes { //typecast to unsigned char
    opcMainMemoryProgramPageThroughBuffer1 = 0x82,
    opcMainMemoryProgramPageThroughBuffer2 = 0x85,
    opcMainMemoryPageRead = 0xD2,
    opcStatusRegisterRead = 0xD7
};

typedef enum OpCodeByteCounts { //typecast to unsigned char
    opcbMainMemoryPageRead = 8,
    opcbMainMemoryProgramPageThroughBuffer1 = 4,
    opcbMainMemoryProgramPageThroughBuffer2 = 4,
    opcbStatusRegisterRead = 1
};

#endif
