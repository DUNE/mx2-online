#ifndef FrontEndBoard_h
#define FrontEndBoard_h

#include "TRIPFrame.h"
#include "ADCFrame.h"
#include "DiscrFrame.h"
#include "FPGAFrame.h"


/*! \class FrontEndBoard
 *
 * \brief The class which holds all of the information associated with an FrontEndBoard.
 *
 */

class FrontEndBoard {

	private:
		febAddresses boardNumber; 
		TRIPFrame  * tripFrame;    
		ADCFrame   * adcFrame;      
		DiscrFrame * discrFrame;   
    FPGAFrame  * fgpaFrame;

		
	public:
		FrontEndBoard( febAddresses theAddress ); 
		~FrontEndBoard() { };    

		/*! Get functions */
		febAddresses inline GetBoardNumber() {return boardNumber;};

    std::auto_ptr<FPGAFrame> GetFPGAFrame();

};

#endif