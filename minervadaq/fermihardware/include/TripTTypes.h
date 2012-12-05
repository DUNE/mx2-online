#ifndef TripTTypes_h
#define TripTTypes_h

/* tripT types */

/*! \enum TriPFunctions
 *
 * \brief "Address" of the TRiP-T which is to be read from or written to 
 *
 */
typedef enum TRiPFunctions { //typecast to unsigned char
	tNone = 0x00,
	tAll  = 0x01,
	tTR0  = 0x02,
	tTR1  = 0x03,
	tTR2  = 0x04,
	tTR3  = 0x05,
	tTR4  = 0x06,
	tTR5  = 0x07
};

typedef struct TripRegisterValues {
	int tripRegIBP;
	int tripRegIBBNFOLL;
	int tripRegIFF;
	int tripRegIBPIFF1REF;
	int tripRegIBOPAMP;
	int tripRegIB_T; 
	int tripRegIFFP2;
	int tripRegIBCOMP;
	int tripRegVREF;
	int tripRegVTH; 
	int tripRegPIPEDEL;
	int tripRegGAIN;
	int tripRegIRSEL;
	int tripRegIWSEL;
};


#endif
