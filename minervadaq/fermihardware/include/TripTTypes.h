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

static const TripRegisterValues DefaultTripRegisterValues = {
60  , /* tripRegIBP */
120 , /* tripRegIBBNFOLL */
0   , /* tripRegIFF */
160 , /* tripRegIBPIFF1REF */
40  , /* tripRegIBOPAMP */
0   , /* tripRegIB_T */
0   , /* tripRegIFFP2 */
20  , /* tripRegIBCOMP */
165 , /* tripRegVREF */
238 , /* tripRegVTH */  
15  , /* tripRegPIPEDEL */
11  , /* tripRegGAIN */
3   , /* tripRegIRSEL */
3   , /* tripRegIWSEL */
};

#endif
