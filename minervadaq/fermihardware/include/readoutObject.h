#ifndef readoutObject_h
#define readoutObject_h

#include "croc.h"

class readoutObject {
	private:
		int febID; // Board Number for the generic FEB
		std::vector<channels*> channelsVector; // All the CROC FE Channels that have an FEB with number febID
		std::vector<int> hitsPerChannelVector; // Number of ADC hits remaining on each channel.  
		std::vector<int> origHitsPerChannelVector; // "Original" number of ADC hits on each channel. 
	public:
		readoutObject(int id) {
			febID = id;
		};
		~readoutObject() { };

		std::vector<channels*> inline *getChannelsVector() { return &channelsVector; };
		std::vector<int> inline *getHitsPerChannelVector() { return &hitsPerChannelVector; };
		std::vector<int> inline *getOrigHitsPerChannelVector() { return &origHitsPerChannelVector; };
		int inline getFebID() { return febID; };
		void inline addData(channels* ch, int h) {  // add to the end of the vector
			channelsVector.push_back(ch); 
			hitsPerChannelVector.push_back(h);
			origHitsPerChannelVector.push_back(h);
		};
		channels inline *getChannel(int indx) { return channelsVector[indx]; };
		void inline setHitsPerChannel(int indx, int h) { hitsPerChannelVector[indx] = h; };
		void inline setOrigHitsPerChannel(int indx, int h) { origHitsPerChannelVector[indx] = h; };
		int inline getHitsPerChannel(int indx) { return hitsPerChannelVector[indx]; };
		int inline getOrigHitsPerChannel(int indx) { return origHitsPerChannelVector[indx]; };
		void inline zeroOrigHitsPerChannel() { 
			for (unsigned int i=0; i<origHitsPerChannelVector.size(); i++) {
				origHitsPerChannelVector[i] = 0;
			}
		};
		int inline getDataLength() {
			if (hitsPerChannelVector.size() == channelsVector.size()) {
				return hitsPerChannelVector.size();
			} else {
				std::cout << "Data length mismatch in readoutObject!" << std::endl;
				return 0;
			}
		}
};
#endif

