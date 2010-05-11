#ifndef readoutObject_h
#define readoutObject_h

#include "croc.h"

class readoutObject {
	private:
		int febID;
		std::vector<channels*> channelsVector;
		std::vector<int> hitsPerChannelVector;
	public:
		readoutObject(int id) {
			febID = id;
		};
		~readoutObject() { };

		std::vector<channels*> inline *getChannelsVector() { return &channelsVector; };
		std::vector<int> inline *getHitsPerChannelVector() { return &hitsPerChannelVector; };
		int inline getFebID() { return febID; };
		void inline addData(channels* ch, int h) {  // add to the end of the vector
			channelsVector.push_back(ch); 
			hitsPerChannelVector.push_back(h);
		};
		channels inline *getChannel(int indx) { return channelsVector[indx]; };
		void inline setHitsPerChannel(int indx, int h) { hitsPerChannelVector[indx] = h; };
		int inline getHitsPerChannel(int indx) { return hitsPerChannelVector[indx]; };
		void inline zeroHitsPerChannel() { 
			for (unsigned int i=0; i<hitsPerChannelVector.size(); i++) {
				hitsPerChannelVector[i] = 0;
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

