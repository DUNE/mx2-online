#ifndef LIBOXEXCEPTIONS_H
#define LIBOXEXCEPTIONS_H 1

#include <stdexcept>
#include <string>

namespace Minerva
{
	class LIBoxNoSerialException : public std::exception
	{
		virtual const char * what() const throw()
		{
			return "Serial port must be initialized before use!";
		}
	};
	
	class LIBoxSerialConnectionException : public std::exception
	{
		virtual const char * what() const throw()
		{
			return "Error: could not connect to serial device...";
		}
	};
	
	class LIBoxSerialParameterException : public std::exception
	{
		virtual const char * what() const throw()
		{
			return "Error: could not set serial device parameter...";
		}
	};
	
	class LIBoxFileException : public std::exception
	{
		public:
			virtual ~LIBoxFileException() throw() {}
			LIBoxFileException(std::string filename);
			virtual const char * what() const throw();
			
			inline std::string getFile() { return file; };
			
		private:
			// don't allow the default constructor to be used.  we ALWAYS want the filename!
			LIBoxFileException() {}
			
			std::string file;
	};

};

#endif
