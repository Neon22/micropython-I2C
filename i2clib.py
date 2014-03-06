#/usr/bin/python

### add useful methods for i2c commuinications
# Specifically:
# Register commands:
#  - read_register_byte(reg_addr)           # read single byte from register
#  - read_register_word(reg_addr)           # read single word from register
#  - read_register_bytes(reg_addr, length)  # read sequence of bytes from register
#  - read_register_words(reg_addr, length)  # read sequence of words from register
#  - extract_bits(value, bitnum, length)    # extract bit field starting at bitnum for length
#
#  - write_register_byte(reg_addr, byte)    # write single byte to register
#  - write_register_word(reg_addr, word)    # write single word to register
#  - write_register_bytes(reg_addr, bytes)  # write several bytes to register
#  - write_register_words(reg_addr, words)  # write several words to register
#
#  - set_register_byte_bit(reg_addr, bitnum, value)          # write back the modified register with bitnum set to value (0,1)
#  - set_register_word_bit(reg_addr, bitnum, value)          # "
#  - set_register_byte_mask(reg_addr, bitnum, length, value) # write back the modified register with value replacing bits.
#  - set_register_word_mask(reg_addr, bitnum, length, value) #  bits to replace with value start at bitnum for length

# ALT form - less functions but functions more complex and longer, so decided not to use this form
# read_register(reg_addr, size=WORD)


#import pyb_I2C

### Test class if no pyb_I2C to import
### remove this once I2C working in micropython
class pyb_I2C(object):
        def __init__(self, port, addr):
                pass
        def start(self):
                print (" starting")
        def read(self):
                print(" 2 read")
                return 2
        def write(self, byte):
                print (' {} written'.format(byte))
        def readAndStop(self):
                print(" 22 read")
                return(22)
        def stop(self):
                print(" stopped")

###      
class I2C_lib(pyb_I2C):
    """ Extend i2c interface
        Existing methods are:
        - start()
        - write(byte)   # send byte
        - read()        # read byte
        - readAndStop()
        - stop()
    """

    def __init__(self, port, dev_addr):
        " nothing more to add "
        #super().__init__(port, dev_addr) # python 3 form
        super(I2C_lib, self).__init__(port, dev_addr) # python 2.7 - not needed

# Read registers
    def read_register_byte(self, reg_addr):
        " from 8 bit register - read single byte "
        self.start()
        self.write(reg_addr) # prompt for register address
        self.stop()
        # read reply
        self.start()
        return self.readAndStop()

    def read_register_bytes(self, reg_addr, length):
        " from 8 bit register - read list of bytes "
        bytess = []
        self.start()
        self.write(reg_addr) # prompt for register address
        self.stop()
        # read reply
        self.start()
        count = 0
        while count < length:
            byte = self.read()
            count += 1
            if byte:
                bytess.append(byte)
        #
        return bytess

    def read_register_word(self, reg_addr):
        " from 8 bit register - read single word (2 bytes) "
        self.start()
        self.write(reg_addr) # prompt for register address
        self.stop()
        # read reply MSB, LSB
        self.start()
        return (self.read() << 8 + self.readAndStop())

    def read_register_words(self, reg_addr, length):
        " from 8 bit register - read list of words "
        words = []
        self.start()
        self.write(reg_addr) # prompt for register address
        self.stop()
        # read reply
        self.start()
        count = 0
        while count < length:
            word = self.read() << 8 + self.read()
            count += 1
            if word:
                words.append(word)
        #
        self.stop()
        return words

# Bit read operations
    def extract_bits(self, data, bitnum, length):
        """ return right shifted bits in range bitnum, length
            E.g.
            01101001 read byte
            76543210 bit numbers
               xxx   args: bitStart=4, length=3
               010   masked
              -> 010 shifted
            E.g. for words
            1101011001101001 read word
            fedcba9876543210 bit numbers
              xxx            args: bitStart=13, length=3
              010            masked
                      -> 010 shifted
        """
        shift = bitnum - length + 1
        mask = ((1 << length) - 1) << shift
        new = data & mask
        return new >> shift

# Writing registers
    def write_register_byte(self, reg_addr, byte):
        " write byte to register "
        self.start()
        self.write(reg_addr) # prompt for register address
        self.write(byte)
        self.stop()

    def write_register_word(self, reg_addr, word):
        " write word to register"
        self.start()
        self.write(reg_addr) # prompt for register address
        self.write(word >> 8)   # MSB
        self.write(word & 0xFF) # LSB
        self.stop()

    def write_register_bytes(self, reg_addr, bytes):
        " write sequence of bytes to register "
        self.start()
        self.write(reg_addr) # prompt for register address
        for b in bytes:
            self.write(b)
        self.stop()

    def write_register_words(self, reg_addr, words):
        " write sequence of words to register "
        self.start()
        self.write(reg_addr) # prompt for register address
        for w in words: # write pairs of bytes
            self.write(w >> 8)   # MSB
            self.write(w & 0xFF) # LSB
        self.stop()

# Bit operations
    def set_register_byte_bit(self, reg_addr, bitnum, value):
        " read register byte, set/reset a bit, and write back to register "
        byte = self.read_register_byte(reg_addr)
        new = byte | (1<< bitnum) if value else byte & ~(1 << bitnum)
        self.write_register_byte(reg_addr, new)

    def set_register_word_bit(self, reg_addr, bitnum, value):
        " read register word, set/reset a bit, and write back to register "
        word = self.read_register_word(reg_addr)
        new = word | (1<< bitnum) if value else word & ~(1 << bitnum)
        self.write_register_word(reg_addr, new)

    def set_register_byte_mask(self, reg_addr, bitnum, length, value):
        """ read byte from register and store back replacing a bit sequence.
            - bits start at bitnum for length, and are replaced by value
            - if value is too large to be expressed in length bits, then mask to fit.
            E.g. 01101001 read byte
                 76543210 bit numbers
                    xxx   bitnum=4, len = 3
                    101   replacement value
                 01110101 end result saved to register
                 - to set all the (bitnum, len) bits   - make value = -1
                 - to clear all the (bitnum, len) bits - make value = 0
        """
        byte = self.read_register_byte(reg_addr)
        shift = bitnum - length + 1
        #mask = (pow(2, length) - 1) # invert gets us original bits only
        mask = (1 << length) - 1 # invert gets us original bits only
        value = value & mask # trim value if too big for len bits
        self.write_register_byte(reg_addr, (byte & ~(mask << shift)) + (value << shift))
        
    def set_register_word_mask(self, reg_addr, bitnum, length, value):
        """ read word from register and store back replacing some bits.
            - bits start at bitnum for length and are replaced by value
            - if value is too large to be expressed in length bits, then mask to fit.
            E.g. 1101011001101001 read word
                 fedcba9876543210 bit numbers
                    xxx           bitnum=12, len = 3
                    010           replacement value
                 1100101001101001 end result saved to register
                 - to set all the (bitnum, len) bits   - make value = -1
                 - to clear all the (bitnum, len) bits - make value = 0
        """
        word = self.read_register_word(reg_addr)
        shift = bitnum - length + 1
        #mask = (pow(2, length) - 1) # invert gets us original bits only
        mask = (1 << length) - 1 # invert gets us original bits only
        value = value & mask # trim value if too big for len bits
        self.write_register_word(reg_addr, (word & ~(mask << shift)) + (value << shift))
    
    def scan(self):
        " Scan all 0xFF byte address and return list of responders "
        visible_regs = []
        for i in range(256):
            p = self.read_register_byte(i)
            if p:
                print("Register {} responded".format(i))
                visible_regs.append(i)
        return visible_regs

        
            
# Tests
if __name__ == '__main__':
    b = 0b01101001
    w = 0b1101011001101001
    i2c = I2C_lib(1,0xf)
    print i2c
    print ("i2c.extract_bits(b, 5, 3)")
    print (" {}, {}".format(bin(b), i2c.extract_bits(b, 5, 3)))
    print
    print ("read_register_byte(self, reg_addr)")
    print ("i2c.read_register_byte(1)")
    print (i2c.read_register_byte(1))
    print ("i2c.read_register_bytes(1, 3)")
    print (i2c.read_register_bytes(1, 3))
    print ("i2c.read_register_word(1)")
    print (i2c.read_register_word(1))
    print ("i2c.read_register_words(1, 3)")
    print (i2c.read_register_words(1, 3))
    #
    print
    print ("i2c.write_register_byte(reg_addr, byte)")
    print ("i2c.write_register_byte(1, 12)")
    print (i2c.write_register_byte(1, 12))
    print ("i2c.write_register_word(1, 12)")
    print (i2c.write_register_word(1, 12))
    print ("i2c.write_register_bytes(1, [1, 2, 3])")
    print (i2c.write_register_bytes(1, [1, 2, 3]))
    print ("i2c.write_register_words(1, [1, 2, 257])")
    print (i2c.write_register_words(1, [1, 2, 257]))
    #
    print
    print ("i2c.set_register_byte_bit(reg_addr, bitnum, value)")
    print ("i2c.set_register_byte_bit(1, 4, 0)")
    print (i2c.set_register_byte_bit(1, 4, 0))
    print ("i2c.set_register_byte_bit(1, 3, 1)")
    print (i2c.set_register_byte_bit(1, 3, 1))
    print ("i2c.set_register_word_bit(1, 3, 1)")
    print (i2c.set_register_word_bit(1, 3, 1))
    #
    print ("i2c.set_register_byte_mask(reg_addr, bitnum, length, value)")
    print ("i2c.set_register_byte_mask(1, 3, 3, 5)")
    print (i2c.set_register_byte_mask(1, 3, 3, 5))
    print ("i2c.set_register_word_mask(1, 3, 3, 5))")
    print (i2c.set_register_word_mask(1, 3, 3, 5))
