#ifndef RunHeader_cxx
#define RunHeader_cxx
/*! \file RunHeader.cpp
*/

#include "log4cppHeaders.h"
#include "RunHeader.h"

log4cpp::Category& runevt = log4cpp::Category::getInstance(std::string("runevt"));

//----------------------------------------------------------------
RunHeader::RunHeader(FrameHeader *header, 
		     std::vector <unsigned short> configurations)
{
#ifndef GOFAST
  runevt.setPriority(log4cpp::Priority::DEBUG);
  runevt.debugStream() << "->Entering RunHeader::RunHeader... Building a Run Header.";
#else
  runevt.setPriority(log4cpp::Priority::INFO);
#endif

  dataLength = runHeaderSize;
  runevt.debugStream() << " dataLength. = " << dataLength ;
  printf("\n  dataLength = %d ", dataLength ) ;
  data = new unsigned char[dataLength];
  bzero(data,dataLength);

  int nChannels = configurations.size();
  printf("\n  nChannels = %d", nChannels);

#ifndef GOFAST
  runevt.debugStream() << " nChannels = " << nChannels ;
  for ( int i=0; i<nChannels; i++)
  {
    runevt.debug ( "\n configurations[%d]= 0x%4.4X\n ",  i ,configurations.at(i)) ;
    printf("\n  configurations[%d] = 0x%4.4X\n", i, configurations.at(i));
  }
#endif

  int ptr = 0;
  // Fill in frame header 
  printf("\n  before headerData ");
  const unsigned short * headerData = header->GetBankHeader();
  for ( int i=0; i<FrameHeader::FRAME_HEADER_SIZE; i++)
  {
    *(unsigned short *)(&data[ptr]) = headerData[i];
    ptr += sizeof(unsigned short);
  }    
#ifndef GOFAST  
   for ( int i=0; i<FrameHeader::FRAME_HEADER_SIZE; i++) {
   runevt.debug ( " headerData[%d]= 0x%4.4X\n ",  i , (int)(headerData[i]) ) ;
   }
#endif    
   printf("\n  before (&data[ptr]) = nChannels");

  *(int *)(&data[ptr]) = nChannels;
  ptr += sizeof(nChannels);

 printf("\n  before filling data with configurations");
//for ( int i=0; i<nChannels*2; i++)
 for ( int i=0; i<nChannels; i++)
  {   
    *(unsigned short *)(&data[ptr]) = configurations.at(i);
    printf ("\n data[%d] = 0x%4.4X", i, data[i]);
    ptr += sizeof(unsigned short);
  }
    
  
 #ifndef GOFAST  
   for ( int i=0; i<dataLength; i++) {
   runevt.debug ( " data[%d]= 0x%4.4X\n ",  i , (int)(data[i]) ) ;
   }
#endif    
 
  
}

//----------------------------------------------------------------
RunHeader::~RunHeader() 
{ 
  this->ClearData();
}

//----------------------------------------------------------------
unsigned char* RunHeader::GetData() const 
{ 
  return data; 
}

//----------------------------------------------------------------
unsigned short RunHeader::GetDataLength() const 
{ 
  return dataLength;
}

//----------------------------------------------------------------
void RunHeader::ClearData() 
{ 
  if ( (dataLength > 0) && (data != NULL) ) 
  {
    delete [] data;
    data = NULL;
    dataLength = 0;
  }
}

//----------------------------------------------------------------
unsigned char RunHeader::GetData(int i) const 
{
  if (i < dataLength) 
  { 
    return data[i]; 
  }
  return 0;
}

#endif
