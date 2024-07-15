
class ByteWalker:
    def __init__(self, bytes : bytes, isLE = True):
        self.bytes = bytes
        self.bytesLen = len(self.bytes)
        self.pos = 0
        self.byteOrder = "little" if isLE else "big"

    def is_Out(self):
        return not self.bytesLen or (self.bytesLen <= self.pos)

    def get_Int(self, count=1):
        if self.is_Out():
            return None
        num = int.from_bytes(self.bytes[self.pos:self.pos+count], self.byteOrder)
        self.pos += count
        return num
    
    def get_HexView(self, count=1):
        if self.is_Out():
            return None
        hexView = self.bytes[self.pos:self.pos+count].hex().upper()
        if self.byteOrder == "little":
            hexView = hexView[::-1]
        self.pos += count
        return hexView
    
    def get_String(self, encoding="utf-8", count=1):
        if self.is_Out():
            return None
        string = self.bytes[self.pos:self.pos+count].decode(encoding, "replace")
        self.pos += count
        return string
    
    def get_RawBytes(self, count):
        if self.is_Out():
            return None
        bb = self.bytes[self.pos:self.pos+count]
        self.pos += count
        return bb