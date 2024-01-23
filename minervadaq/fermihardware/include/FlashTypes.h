#ifndef FlashTypes_h
#define FlashTypes_h

//typecast to unsigned char
typedef enum OpCodes { 
    opcMainMemoryProgramPageThroughBuffer1 = 0x82,
    opcMainMemoryProgramPageThroughBuffer2 = 0x85,
    opcMainMemoryPageRead = 0xD2,
    opcStatusRegisterRead = 0xD7
};


//typecast to unsigned char
typedef enum OpCodeByteCounts { 
    opcbMainMemoryPageRead = 8,
    opcbMainMemoryProgramPageThroughBuffer1 = 4,
    opcbMainMemoryProgramPageThroughBuffer2 = 4,
    opcbStatusRegisterRead = 1
};

#endif
