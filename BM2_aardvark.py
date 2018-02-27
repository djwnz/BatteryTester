#!/usr/bin/env python
################################################################################
#(C) Copyright Pumpkin, Inc. All Rights Reserved.
#
#This file may be distributed under the terms of the License
#Agreement provided with this software.
#
#THIS FILE IS PROVIDED AS IS WITH NO WARRANTY OF ANY KIND,
#INCLUDING THE WARRANTY OF DESIGN, MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE.
################################################################################
"""
@package BM2_aardvark.py
Module to handle talking to a BM2 with the aardvark
"""

__author__ = 'David Wright (david@pumpkininc.com)'
__version__ = '0.3.1' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

import aardvark_py
from array import array
from struct import unpack


# ---------
# Constants

# I2C config
I2C = True
SPI = True
GPIO = False
Pullups = True
radix = 16
Bitrate = 100

#
# ----------------
# Classes

class BM2:
    """
    Class that operates the Aardvark device

    @attribute message      (string) Place to store error messages
    @attribute port         (Aardvark_py.Aardvark handle) 
                                     The aardvark port in use
    """ 

    def __init__(self):
        """
        Initialise the BM2 object to its default values
        """
        self.message = ''
        
        self.port = configure_aardvark()
        
        if (self.port == None):
            self.message = "No Aardvark found"
        #end if
    #end def

    def __enter__(self):
        """
        For use with the 'with' operator
        """   
        return self
    # end def
    
    def __exit__(self, type, value, traceback):
        """
        Ensures that the aardvark port is closed correctly
        
        For use with the 'with' operator
        """      
        if self.port != None:
            aardvark_py.aa_close(self.port)
        #end if
    #end def
    
    def get_Voltage(self):
        return send_SMB_command('0x09', self.port, 'uint')
    #end def
    
    def get_Current(self):
        return send_SMB_command('0x0A', self.port, 'int')
    #end def    
    
    def get_ChargingVoltage(self):
        return send_SMB_command('0x14', self.port, 'uint')
    #end def
    
    def get_ChargingCurrent(self):
        return send_SMB_command('0x15', self.port, 'uint')
    #end def
    
    def get_OperationStatus(self):
        return send_SMB_command('0x54', self.port, 'uint')
    #end def       
    
    def get_RDIS(self):
        return (self.get_OperationStatus() & int('0004',16)) != 0
    # end def
    
    def get_VOK(self):
        return (self.get_OperationStatus() & int('0002',16)) != 0
    # end def    
    
    def get_QEN(self):
        return (self.get_OperationStatus() & int('0001',16)) != 0
    # end def    
    
    def get_TaperCurrent(self):
        send_SMB_data(['0x77', '0x24', '0x00'], self.port)
        aardvark_py.aa_sleep_ms(50) 
        flash_page = send_SMB_command('0x78', self.port, 'page')
        flash_page = flash_page[1:] # remove length byte
        return flash_page[3] + flash_page[2]*256
    #end def    
    
    def get_UpdateStatus(self):
        send_SMB_data(['0x77', '0x52', '0x00'], self.port)
        aardvark_py.aa_sleep_ms(50) 
        flash_page = send_SMB_command('0x78', self.port, 'page')
        flash_page = flash_page[1:] # remove length byte
        return "0x%0.2X" % flash_page[12]
    #end def     
    
# end class
    

#
# ----------------
# Public Functions



#
# ----------------
# Private Functions

def configure_aardvark():
    """ 
    Function to configure the aardvark for pySCPI operation if there is one
    available.
    
    @return  (aardvark_py.aardvark)   The handle of the aardvark to be used
                                      'None' if there is not one available
    """
    # define the handle to return
    Aardvark_in_use = None
    
    # find all connected aardvarks
    AA_Devices = aardvark_py.aa_find_devices(1)
    
    # define a port mask
    Aardvark_port = 8<<7
    
    # assume that an aardvark can be found until proved otherwise
    Aardvark_free = True
    
    # Check if there is an Aardvark present
    if (AA_Devices[0] < 1):
        # there is no aardvark to be found
        print '*** No Aardvark is present ***'
        Aardvark_free = False
        
    else:
        # there is an aardvark connected to select the first one if there
        # are many
        Aardvark_port = AA_Devices[1][0]
    # end if
    
    
    # If there is an Aardvark there is it free?
    if Aardvark_port >= 8<<7 and Aardvark_free:
        # the aardvark is not free
        print '*** Aardvark is being used, '\
              'disconnect other application or Aardvark device ***'
        # close the aardvark
        aardvark_py.aa_close(Aardvark_port)
        Aardvark_free = False
        
    elif Aardvark_free:
        # Aardvark is available so configure it
        
        # open the connection with the aardvark
        Aardvark_in_use = aardvark_py.aa_open(Aardvark_port)
        
        # set it up in teh mode we need for pumpkin modules
        aardvark_py.aa_configure(Aardvark_in_use, 
                                 aardvark_py.AA_CONFIG_SPI_I2C)
        
        # default to both pullups on
        aardvark_py.aa_i2c_pullup(Aardvark_in_use, 
                                  aardvark_py.AA_I2C_PULLUP_BOTH)
        
        # set the bit rate to be the default
        aardvark_py.aa_i2c_bitrate(Aardvark_in_use, Bitrate)
        
        # free the bus
        aardvark_py.aa_i2c_free_bus(Aardvark_in_use)
        
        # delay to allow the config to be registered
        aardvark_py.aa_sleep_ms(200)    
        
        print "Starting Aardvark communications\n"
    # end if    
    
    return Aardvark_in_use
# end def

def send_SMB_data(data, Aardvark_in_use):
    """
    Function to send a SCPI command to the slave device
    
    @param[in]    data:            the hex data to send (list of strings)
    @param[in]    Aardvark_in_use: The Aaardvark to use to read the data
                                   (aardvark_py.aardvark)
    """  
    BM2_Address = int('0x0B', 16)
    write_data = []
    
    for byte in data:
        if is_hex(byte):
            write_data = write_data + [int(byte,16)]
        else:
            return None
        # end if
    # end for
    
    out_data = array('B', write_data)  

    # Write the data to the slave device
    aardvark_py.aa_i2c_write(Aardvark_in_use, BM2_Address, 
                    aardvark_py.AA_I2C_NO_FLAGS, out_data)    
    
    aardvark_py.aa_sleep_ms(1)
# end def

def send_SMB_command(command, Aardvark_in_use, return_format):
    """
    Function to send a SCPI command to the slave device
    
    @param[in]    command:         the hex command to send (string)
    @param[in]    Aardvark_in_use: The Aaardvark to use to read the data
                                   (aardvark_py.aardvark)
    @param[in]    return_format    format to return the data in
    """  
    BM2_Address = int('0x0B', 16)
    
    # convert the data into a list of bytes and append the terminator
    if is_hex(command):
        write_data = [int(command,16)]
    
        # convert to an array to be compiant with the aardvark
        out_data = array('B', write_data)  
        
        # Write the data to the slave device
        #aardvark_py.aa_i2c_write(Aardvark_in_use, BM2_Address, 
                                 #aardvark_py.AA_I2C_NO_FLAGS, out_data)
        
        aardvark_py.aa_sleep_ms(1)
        
        if return_format == 'none':
            return None
        
        elif return_format == 'int':
            # define array to read data into
            in_data = array('B', [1]*2) 
            
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)    
            
            return unpack('<h', ''.join([chr(x) for x in in_data]))[0]
            
        elif return_format == 'uint':
            # define array to read data into
            in_data = array('B', [1]*2) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)  
            
            return unpack('<H', ''.join([chr(x) for x in in_data]))[0]               
            
        elif return_format == 'char':
            
            # define array to read data into
            in_data = array('B', [1]*1) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)  
            
            return unpack('<B', ''.join([chr(x) for x in in_data]))[0] 
            
        elif return_format == 'schar':
            
            # define array to read data into
            in_data = array('B', [1]*1) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)   
            
            return unpack('<b', ''.join([chr(x) for x in in_data]))[0]                 
        
        elif return_format == 'hex':
            
            # define array to read data into
            in_data = array('B', [1]*2) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)  
            
            return ' '.join(['%02X' % x for x in reversed(in_data)])
        # end if   
        
        elif return_format == 'page':
            
            # define array to read data into
            in_data = array('B', [1]*32) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)  
            
            return list(in_data)
        # end if           
            
    else:
        return None
    # end if
# end def

def is_hex(s):
    """
    Determine if a string is a hexnumber
    
    @param[in]  s:       The string to be tested (string).
    @return     (bool)   True:    The string is a hex number.
                         False:   The command is not a hex number.
    """    
    # if it can be converted to a base 16 int then it is hex
    try:
        int(s, 16)
        return True
    
    except ValueError:
        # it could not be converted therefore is not hex
        return False
    # end try
# end def

def _test():
    """
    Test code for this module.
    """
    try:
        aardvark = configure_aardvark()
        
        print send_SMB_command('0x54', aardvark, 'hex')
        print send_SMB_command('0x54', aardvark, 'uint')
        print (send_SMB_command('0x54', aardvark, 'uint') & int('F000',16)) != 0
        print (send_SMB_command('0x54', aardvark, 'uint') & int('7000',16)) != 0
        
        aardvark_py.aa_close(aardvark)
        
    except:
        pass
    # end try
    
    with BM2() as battery_pack:
        print battery_pack.get_Voltage()
        print battery_pack.get_Current()
        print battery_pack.get_ChargingVoltage()
        print battery_pack.get_ChargingCurrent()
        print battery_pack.get_RDIS()
        print battery_pack.get_VOK()     
        print battery_pack.get_TaperCurrent()
        print battery_pack.get_UpdateStatus()
    #end with
    
# end def

if __name__ == '__main__':
    # if this code is not running as an imported module run test code
    _test()
# end if