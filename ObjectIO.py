#   ___    _         _                 _     ___    ___  
#  / _ \  | |__     (_)   ___    ___  | |_  |_ _|  / _ \ 
# | | | | | '_ \    | |  / _ \  / __| | __|  | |  | | | |
# | |_| | | |_) |   | | |  __/ | (__  | |_   | |  | |_| |
#  \___/  |_.__/   _/ |  \___|  \___|  \__| |___|  \___/  1.0.0
#                 |__/                                   
# by Ryan Jones (https://github.com/rcj0003)

# ================================================================================== #
# The MIT License (MIT)
#
# Copyright (c) 2019 Ryan Jones
#
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ================================================================================== #

import json
import sys

class Compatibility():
    """Provides simple methods to aid with compatibility."""
    def getVersion():
        """Returns a tuple providing the major, minor, patch, and pre-release identifier like so: (Major, Minor, Patch, Identifier)"""
        return (1, 0, 1, "")

    def getVersionString():
        """Returns the version in the following format: Major.Minor.Patch(-Pre-release Indetifier)\nThe identifier may be absent if the release is a full release."""
        versionData = Compatibility.getVersion()
        return ("%s.%s.%s" % versionData[:-1]) + ("" if len(versionData[3]) == 0 else "-%s" % versionData[3])

    def getSimpleVersion():
        """Returns a tuple providing the major, minor, and patch information for easier handing of compatibility."""
        return Compatibility.getVersion()[:-1]

    def getMajorVersion():
        """Returns the major version number."""
        return Compatibility.getVersion()[0]

class Utils():
   """Provides a set of general purpose utilities."""
   def getClass(moduleName, className):
      """Returns the object for the class from the provided module."""
      try:
         return getattr(sys.modules[moduleName], className)
      except KeyError:
         raise TypeError("'%s' class definition doesn't exist in the '%s' module." % (className, moduleName))

class DataUtils():
   """Provides a set of utilities for byte arrays."""
   def addRawUtf16CharacterToUtf8ByteArray(array, character):
      """Writes a UTF16 character into a UTF8 byte array by splitting it up into 2 characters. When combined, these characters will read as the original character."""
      string = chr(character >> 8) + chr(character & 0xFF)
      for char in string:
         array.append(ord(char))
   
   def addEscapedUtf16CharacterToUtf8ByteArray(array, character):
      """Writes a UTF16 character into a UTF8 byte array via the Unicode control character."""
      string = f"\\u{character:04x}"
      for char in string:
         array.append(ord(char))

   def convertStringToUtf16Bytes(string):
      """Converts the string into a UTF16 byte array."""
      data = []
      for value in Stream().map(lambda x: ord(x), string):
         data.append(value >> 8)
         data.append(value & 0xFF)
      return data
   
   def convertStringToUtf8Bytes(string):
      """Converts the string into a UTF8 byte array."""
      data = []
      for value in Stream().map(lambda x: ord(x), string):
         if value > 255:
            Utilities.addRawUtf16CharacterToUtf8ByteArray(data, value)
         else:
            data.append(value)
      return data

   def convertListToString(byteData):
      """Converts a list of integers into a string via its character codes."""
      return "".join(Stream().map(lambda x: chr(x), byteData))

   def convertUtf16BytesToString(byteData):
      """Converts a UTf16 byte array into a string by first converting it to a list of character codes."""
      data = []
      offset = 0

      while len(byteData) - (offset * 2) > 0:
         byte1 = byteData[offset * 2]
         byte2 = byteData[(offset * 2) + 1]

         offset += 1

         data.append((byte1 << 8) + byte2)
      
      return DataUtils.convertListToString(data)

class Stream():
   """Offers functionality similar to Java's Stream class."""
   def __init__(self, *results):
      self.results = []
      for x in results:
         if hasattr(x, "__iter__"):
            self.results += list(x)
         else:
            self.results.append(x)

   def __iter__(self):
      for x in self.results:
         yield x

   def __getitem__(self, key):
      return self.results[key]

   def __bool__(self):
      return len(self.results) > 0

   def __len__(self):
      return len(self.results)

   def __add__(self, other):
      if hasattr(other, "__iter__"):
         self.results = self.results + list(other)
      else:
         self.results.append(other)
      return self

   def __iadd__(self, other):
      if hasattr(other, "__iter__"):
         self.results = self.results + list(other)
      else:
         self.results.append(other)
      return self

   def __repr__(self):
      return "Stream[%s]" % self.results
        
   def map(self, function, data = None):
      """Maps the provides data using the provided function and stores it as the results.\n'function' - The function to be used to map the results.\n'data' - The data to be mapped. If no argument is provided, the already stored results will be used."""
      if data == None:
         data = self.results
      self.results = list(map(function, list(data)))
      return self

   def selectiveMap(self, filterFunction, mapFunction):
      """Maps only the stored data that passes the filter function provided.\n'filterFunction' - The function to filter the results.\n'mapFunction' - The function to be used for mapping."""
      plist = Utilities.createEmbeddedList(range(0, len(self)), self)
      Stream(plist).filterResults(lambda x: filterFunction(x[1])).forEach(lambda x: Stream.__setElementAt(self.results, x[0], mapFunction(x[1])))
      return self

   def __setElementAt(plist, index, newElement):
      # Internal function so we can do an assignment operator in a lambda, normally not allowed.
      plist[index] = newElement
   
   def addMapToResults(self, function, data):
      """Maps the provides data using the provided function and adds it the current results.\n'function' - The function to be used to map the results.\n'data' - The data to be mapped."""
      self.results += list(map(function, list(data)))
      return self
    
   def filter(self, function):
      """Filters stored results using the function provided, and thus alters the final result.\n'function' - The function used to filter the stored results."""
      self.results = list(filter(function, self.results))
      return self

   def forEach(self, function):
      """Executes the given function and passes each stored result as a parameter."""
      for x in self:
         function(x)
      return self

   def toArray(self):
      """Returns the results of all maps and filters."""
      return self.results

   def clear(self):
      """Clears stored results."""
      self.results.clear()
      return self

class ObjectStream():
   """Offers functionality similar to Java's ObjectInput and ObjectOutput classes."""
   def __init__(self, *data, readOnly = False):
      self.data = []
      self.offset = 0
      for x in data:
         if hasattr(x, "__iter__"):
            self.data += list(x)
         else:
            self.data.append(x)

   def __reserveBytes(self, amount, function):
      offset = len(self.data)

      while amount > 0:
         self.data.append(0)
         amount -= 1

      return lambda value: function(value, offset)

   def getBytes(self):
      """Returns a list of all bytes that the stream is storing. The returned list is mutable, but not linked to the stream's internal list."""
      return list(self.data)
   
   def getRemainingBytes(self):
      """Returns a list of all bytes that have not already been read by the stream."""
      return self.data[self.offset:]
   
   def getRemainingByteCount(self):
      """Returns the amount of free readable bytes."""
      return len(self.data) - self.offset

   def getObjectStreamFromRemaining(self):
      """Returns a new instance of an ObjectStream with the remaining unread bytes."""
      return ObjectStream(self.getRemainingBytes())

   def writeByte(self, data, offset = -1):
      """Writes the byte to the end of the stream unless an argument is provided to specify the location."""
      if data < 0 or data > 255:
         raise ValueError("Expected byte, got %s" % data.__class__.__name__)
      
      if offset == -1:
         self.data.append(data)
      else:
         self.data[offset] = data
   
   def readByte(self, offset = -1):
      """Reads the byte at the current offset and advances it by one unless an argument specifying the offset is provided."""
      data = 0
      if offset == -1:
         data = self.data[self.offset]
         self.offset += 1
      else:
         data = self.data[offset]
      return data

   def writeBytes(self, byteData):
      """Writes all bytes in the list to the stream."""
      for byte in byteData:
         self.writeByte(byte)

   def readBytes(self, amount):
      """Reads the amount of bytes provided and advances the stream by that amount."""
      data = self.data[self.offset:self.offset + amount]
      self.offset += len(data)
      return data
   
   def writeUtf8(self, string):
      """Writes the string as a UTF8 string to the stream. UTF16 characters will be converted to 2 UTF8 characters. Data is terminated by a 0."""
      self.data += DataUtils.convertStringToUtf8Bytes(string)
      self.data.append(0)

   def readUtf8(self):
      """Reads the stream for a string until the reading is terminated by a '0' or until no bytes are available bytes are available."""
      string = ""
      
      previousByte = self.readByte()
      
      if previousByte == 0:
         return ""
         
      currentByte = self.readByte()

      string = chr(previousByte)
         
      while self.getRemainingByteCount() > 0 and previousByte != 0 and currentByte != 0:
         string += chr(currentByte)
            
         previousByte = currentByte
         currentByte = self.readByte()

      return string

   def writeUtf16(self, string):
      """Writes a string to the stream in UTF16 format. The data is terminated by two 0's."""
      self.data += DataUtils.convertStringToUtf16Bytes(string)
      self.data.append(0)
      self.data.append(0)

   def readUtf16(self, size = -1):
      """Reads the stream for a string until the reading is terminated by 2 zeroes or until no bytes are available bytes are available. An error will be thrown if the data read is not a multiple of 2."""
      if size == -1:
         byte = self.readByte()
         zeroes = 0

         data = []
         
         while self.getRemainingBytes() > 0 and zeroes < 2:
            if byte == 0:
               zeroes += 1
            else:
               zeroes = 0
            
            data.append(byte)
            
            byte = self.readByte()

         # Remove trailing whitespace and fixing cursor.
         data.pop()
         data.pop()
         self.offset -= 1

         return DataUtils.convertUtf16BytesToString(data)
      else:
         return DataUtils.convertListToString(self.readBytes(size))

   def writeInt(self, integer, byteOffset = -1):
      """Writes an integer to the stream."""
      for offset in range(0, 4):
         if byteOffset == -1:
            self.data.append((integer & 0xFF000000) >> 24)
         else:
            self.data[byteOffset + offset] = (integer & 0xFF000000) >> 24
         integer = integer << 8

   def readInt(self, byteOffset = -1):
      """Reads the next 4-bytes in the stream to return an integer."""
      integer = 0
      for offset in range(0, 4):
         integer = integer << 8
         if byteOffset == -1:
            integer += self.readByte()
         else:
            integer += self.readByte(byteOffset + offset)
      return integer
   
   def writeObject(self, obj):
      """Writes an entire object to the stream and additional meta-data required to reconstruct the object later on."""

      if self == obj:
         raise RecursionError("The stream cannot write itself to its stream.")
      
      self.writeUtf8(obj.__class__.__module__)
      self.writeUtf8(obj.__class__.__name__)
      self.writeByte(0) # Version Byte
      writeSizeFunction = self.__reserveBytes(4, self.writeInt)
      currentSize = len(self.data)

      if hasattr(obj, "writeToObjectStream") and hasattr(obj, "readFromObjectStream"):
         obj.writeToObjectStream(self)
      else:
         if hasattr(obj, "__dict__"):
            self.writeByte(1) # Byte flag of 1 indicates that the object relies on a dictionary attribute.
            metadata = vars(obj)
            self.writeInt(len(metadata))
            
            for variable, value in metadata.items():
               self.writeUtf8(variable)
               self.writeObject(value)
         else:
            self.writeByte(0) # Byte flag of 0 indicates that the object doesn't have a dictionary attribute. Generally indicates generic variables like integers.
            self.writeUtf8(json.dumps(obj))

      writeSizeFunction(len(self.data) - currentSize)

   def readObject(self):
      """Reconstructs an object from the stream based on meta data and object data in the stream."""
      moduleName = self.readUtf8()
      className = self.readUtf8()
      version = self.readByte()
      dataSize = self.readInt()
      
      objectClass = None
      newObject = None

      objectClass = Utils.getClass(moduleName, className)

      if hasattr(objectClass, "writeToObjectStream") and hasattr(objectClass, "readFromObjectStream"):
         newObject = objectClass()
         newObject.readFromObjectStream(self)
      else:
         if self.readByte() == 0:
            newObject = json.loads(self.readUtf8())
         else:
            newObject = objectClass()
            metadata = {}
            metadataSize = self.readInt()

            while metadataSize > 0:
               metadata.update({self.readUtf8(): self.readObject()})
               metadataSize -= 1
            
            newObject.__dict__.update(metadata)

      return newObject

   def writeToObjectStream(self, stream):
      """Writes this object to the provided stream."""
      stream.writeByte(0) # Version byte
      stream.writeInt(self.offset)
      stream.writeInt(len(self.data))
      stream.writeBytes(self.data)

   def readFromObjectStream(self, stream):
      """Instantiates this object from the provided stream."""
      version = self.readByte()
      self.offset = stream.readInt()
      self.data = stream.readBytes(stream.readInt())

if __name__ == "__main__":
   print("[ObjectIO %s] by Ryan Jones @ 2019" % Compatibility.getVersionString())
