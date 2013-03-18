#ifndef FrameHeader_h
#define FrameHeader_h
/*! \file FrameHeader.h
*/

/*! 
  \class FrameHeader
  \brief Class for the Minerva Frame Header.
  \author Gabriel Perdue

  See DocDB 8405. For most frames the CROC-E channel will write 
  this information directly into the data stream. However, for 
  DAQHeaders, we will use this class to fill the Minerva Frame
  Header part of the buffer.
  */

//! Encode the bank types used in the offline software framework.
namespace HeaderData {

  /*! 
    \enum BankType
    \brief The offline software bank type used for unpacking raw data. 
    */
  typedef enum {
    ADCBank,   
    DiscrBank,
    FPGABank,
    DAQBank,    
    TRIPBank,     
    SentinelBank 
  } BankType;

}

class FrameHeader {

  friend std::ostream& operator<<(std::ostream&, const FrameHeader&);

  private:
  unsigned short bank_header[4]; 

  public:
  FrameHeader(int crateID, int crocID, int chanID, 
      int bank, int feb_number, int firmware, int hit, int length);
  ~FrameHeader() { };
  const unsigned short inline *GetBankHeader() const { return bank_header; };
};


#endif
