#!/usr/bin/env python
###########################################################################
#(C) Copyright Pumpkin, Inc. All Rights Reserved.
#
#This file may be distributed under the terms of the License
#Agreement provided with this software.
#
#THIS FILE IS PROVIDED AS IS WITH NO WARRANTY OF ANY KIND,
#INCLUDING THE WARRANTY OF DESIGN, MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE.
###########################################################################
"""
@package M9711.py
Module to provide functions for a M9711 DC load.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

import minimalmodbus
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True

import serial

def get_crc(data):
    crc = [int('0xFF',16), int('0xFF',16)]
    
    for byte in data:
        # binary xor the data
        crc[0] = crc[0]^byte
        
        # right shift the register
        crc[1] = crc[0]
        
        # if the lowest bit is 1
        if crc[1]|int('0x01',16):
            #xor with 0xA001
            crc[1] = crc[1]^int('0x01',16)
            crc[0] = crc[0]^int('0xA0',16)
        # end if
    # end for
    
    print [hex(crc[0]), hex(crc[1])]
    return crc
#end def

data = [int('0x01',16), int('0x03',16), int('0x0B',16), int('0x00',16), int('0x00',16), int('0x02',16)]
get_crc(data)
        
        

with serial.Serial('COM16', 115200, timeout = 0) as ser:
    print ser
    if not ser.is_open:
        ser.open()
        #end if
    ser.write(b'\x10')
    ser.close()
# end with


# ---------
# Classes


load = minimalmodbus.Instrument('COM16', 1)
load.serial.baudrate = 115200


#print load.write_register(2561,2,0)
print load.read_register(2820)

