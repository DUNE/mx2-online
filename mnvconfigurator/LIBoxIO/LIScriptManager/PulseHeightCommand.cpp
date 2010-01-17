#include "PulseHeightCommand.h"

#include <string>

namespace Minerva
{
	std::string PulseHeightCommand::ToString()
	{
		// note that the two following integer type casts TRUNCATE.
		int highBit = int( (pulseHeight - 4.0429) / 2.01 );	// calculating the necessary high bit.
		int lowBit = int( (pulseHeight - highBit * 2.01 - 4.0429) / .00783 );	// calculating the necessary low bit

          // Converting the low bit into a pair of HEX values
		int lowBit1 = lowBit / 16;		// INTEGER division.
		int lowBit2 = lowBit % 16;

          Lh = Convert.ToString(Lhrough, 16);


           byte Llrough = (byte)Decimal.Floor(L - Lhrough * 16);

           Ll = Convert.ToString(Llrough, 16);
	}

};
