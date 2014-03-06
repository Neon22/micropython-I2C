micropython-I2C
===============

Extra functions in python to extend the base I2C functions in micropython.
Specifically:
Register commands:
 - read_register_byte(reg_addr)           # read single byte from register
 - read_register_word(reg_addr)           # read single word from register
 - read_register_bytes(reg_addr, length)  # read sequence of bytes from register
 - read_register_words(reg_addr, length)  # read sequence of words from register
 - extract_bits(value, bitnum, length)    # extract bit field starting at bitnum for length
 - write_register_byte(reg_addr, byte)    # write single byte to register
 - write_register_word(reg_addr, word)    # write single word to register
 - write_register_bytes(reg_addr, bytes)  # write several bytes to register
 - write_register_words(reg_addr, words)  # write several words to register
 - set_register_byte_bit(reg_addr, bitnum, value)          # write back the modified register with bitnum set to value (0,1)
 - set_register_word_bit(reg_addr, bitnum, value)          #  "
 - set_register_byte_mask(reg_addr, bitnum, length, value) # write back the modified register with value replacing bits.
 - set_register_word_mask(reg_addr, bitnum, length, value) #  bits to replace with value start at bitnum for length