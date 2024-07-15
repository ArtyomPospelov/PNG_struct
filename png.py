import byteWalker as bw

#PNG CHUNKS:
class PNGChunk:
    def __init__(self, name, data, crc):
        self.name = name
        self.data = data
        self.crc = crc

class PNGIHDRChunk(PNGChunk):
    def __init__(self, name, data, crc):
        super().__init__(name, data, crc)
        walker = bw.ByteWalker(self.data, isLE=False)
        self.width = walker.get_Int(4) #image width in pixels
        self.height = walker.get_Int(4) #image height in pixels
        self.bitDepth = walker.get_Int() #image sample bit depth
        self.colorType = walker.get_Int() #color type
        self.colorTypeStr = "Gray-scale" if self.colorType == 0 else "Truecolor" if self.colorType == 2 else "Indexed color" \
        if self.colorType == 3 else "Gray-scale with alpha data" if self.colorType == 4 else "Truecolor with alpha data" if self.colorType == 6 else ""
        self.compression = walker.get_Int() #compression method
        self.compressionStr = "Deflate" if self.compression == 0 else ""
        self.filtering = walker.get_Int() #filtering method
        self.interlace = walker.get_Int() #interlace method
        self.interlaceStr = "No interlace" if self.interlace == 0 else "Adam7 interlace" if self.interlace == 1 else ""

class PNGTEXTChunk(PNGChunk):
    def __init__(self, name, data, crc):
        super().__init__(name, data, crc)
        isKeySet, isNullSep, isTextSet = False, False, False
        key, text = "", ""
        for i in range(len(self.data)):
            chCode = self.data[i]
            if  chCode == 0:
                if not isKeySet:
                    isKeySet = True
                elif not isNullSep:
                    isNullSep = True
                elif not isTextSet:
                    isTextSet = True
                continue

            ch = chr(self.data[i])
            
            if not isKeySet:
                key += ch
            elif not isTextSet:
                text += ch
        self.key = key
        self.text = text

class PNGBKGDChunk(PNGChunk):
    TYPE_INDEX = 0
    TYPE_GRAYSCALE = 1
    TYPE_TRUECOLOR = 2

    def __init__(self, name, data, crc):
        super().__init__(name, data, crc)
    
    def parse(self, colorType):
        walker = bw.ByteWalker(self.data)

        if colorType == 3:
            self.type = self.TYPE_INDEX
            self.index = walker.get_Int()
        elif colorType == 0 or colorType == 4:
            self.type = self.TYPE_GRAYSCALE
            self.value = walker.get_Int(2)
        elif colorType == 2 or colorType == 6:
            self.type = self.TYPE_TRUECOLOR
            self.red = walker.get_Int(2)
            self.green = walker.get_Int(2)
            self.blue = walker.get_Int(2)
        else:
            return False
        
        return True

class PNGPHYSChunk(PNGChunk):
    def __init__(self, name, data, crc):
        super().__init__(name, data, crc)
        walker = bw.ByteWalker(self.data)
        self.ppx = walker.get_Int(4)
        self.ppy = walker.get_Int(4)
        self.unit = walker.get_Int()
        self.unitStr = "Unknown" if self.unit == 0 else "Meter" if self.unit == 1 else ""

class PNGGAMAChunk(PNGChunk):
    def __init__(self, name, data, crc):
        super().__init__(name, data, crc)
        walker = bw.ByteWalker(self.data)
        self.gamma = walker.get_Int(4)

#PNG file overall structure:
class PNGStruct:
    STAT_OK = 0
    STAT_NOPNG = 1
    STAT_INVALID_DATA = 2

    def __init__(self, rawBytes : bytes):
        self.bw = bw.ByteWalker(rawBytes, isLE=False)
        self.status = self.STAT_OK
        self.totalSize = len(rawBytes)
        self.chunks = []

    def parse(self):
        if self.bw.is_Out():
            self.status = self.STAT_INVALID_DATA
            return False
        if self.bw.get_HexView(8) != "89504E470D0A1A0A":
            self.status = self.STAT_NOPNG
            return False
        
        #parse chunks:
        ihdrChunk = None

        while not self.bw.is_Out():
            dataLen = self.bw.get_Int(4)
            chunkName = self.bw.get_String(count=4)
            data = self.bw.get_RawBytes(dataLen)
            crc = self.bw.get_Int(4)

            if dataLen == None or chunkName == None or data == None or crc == None:
                break

            chunkNameUpp = chunkName.upper()

            if chunkNameUpp == "IHDR":
                ihdrChunk = PNGIHDRChunk(chunkName, data, crc)
                self.chunks.append(ihdrChunk)
            elif chunkNameUpp == "TEXT":
                self.chunks.append(PNGTEXTChunk(chunkName, data, crc))
            elif chunkNameUpp == "BKGD":
                self.chunks.append(PNGBKGDChunk(chunkName, data, crc))
            elif chunkNameUpp == "PHYS":
                self.chunks.append(PNGPHYSChunk(chunkName, data, crc))
            elif chunkNameUpp == "GAMA":
                self.chunks.append(PNGGAMAChunk(chunkName, data, crc))
            else:
                self.chunks.append(PNGChunk(chunkName, data, crc))

        #activate co-independent chunks:
        if not ihdrChunk:
            self.status = self.STAT_INVALID_DATA
            return False #ihdr chunk required

        bkgdChunks = list(filter(lambda chunk: type(chunk) == PNGBKGDChunk, self.chunks))
        for chunk in bkgdChunks:
            if not chunk.parse(ihdrChunk.colorType):
                self.status = self.STAT_INVALID_DATA
                return False

        self.status = self.STAT_OK
        return True
