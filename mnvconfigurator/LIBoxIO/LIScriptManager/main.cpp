void other();

int main()
{
	return 0;
}

void other()
{
		// note that the two following integer type casts TRUNCATE.
		int highBit = int( (pulseHeight - 4.0429) / 2.01 );
		int lowBit = int( (pulseHeight - highBit * 2.01 - 4.0429) / .00783 );

          // Converting the low bit into a pair of HEX values
		int lowBit1 = lowBit / 16;		// INTEGER division.
		int lowBit2 = lowBit % 16;
}
