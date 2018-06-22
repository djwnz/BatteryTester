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
@package Multimeter.py
Module to handle the control of a generic multimeter, providing an \
abstraction layer for the user.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

import Tkinter as TK
import sys


# ---------
# Classes

class Multimeter(object):
    """
    Class to serve as an abstraction layer between the program and the multimeter 
    in use. Links a generic set of multimeter functionality to the 
    specific functions required to operate the selected multimeter.
    
    @attribute model    (string)     The model of the multimeter in use
    @attribute port     (string)     The port used by the multimeter
    @attribute MM       (object)     The multimeter object
    """    
    
    def __init__(self, Model):
        """
        Initialise the PowerSupply Object
    
        @param[in] Model     The model of the power supply selected (string)
        """       
        
        # Initialise attributes
        self.model = Model
        self.port = NULL
        
        # check to see if the model requested is selected
        if self.model == '34410A':
            # find the port associated with the 34410A multimeter
            pass
            # TODO
            
        else:
            # The requested multimeter is not supported
            raise ValueError('The Multimeter model selected is not supported'+
                             'by this Module')
        # end if        
    #end def
    
    
    def __enter__(self):
        """
        Enter a specific usage of the Multimeter Object. this is called by the
        with statement.
    
        """        
        
        # check to see if a multimeter has been detected previously
        if self.port == 'NULL':
            # it has not so attempt to detect one based on the model requested
            if self.model == '34410A':
                # connect to the 34410A
    
                pass
            # end if
            
        else:
            # A port has previously been found so communicate through that port
            pass
            # TODO
            
        #end if
        
        # return the object for use in with statement
        return self
    # end def
    
    
    def get_DC_voltage(self):
        """ 
        Retrieve a voltage measurement from the Multimeter
        
        @return   (float)     The voltage in volts
        """
        if self.model == '34410A':
            return 8.4#TODO
        # end if 
    # end def
    
    
    def get_DC_current(self):
        """ 
        Retrieve a current measurement from the Multimeter
        
        @return   (float)     The current in amps
        """        
        if self.model == '34410A':
            return 1.0#TODO
        # end if 
    # end def    
    
    
    def get_resistance(self):
        """ 
        Retrieve a resistance measurement from the Multimeter
        
        @return   (float)     The resistance measurement in ohms
        """        
        if self.model == '34410A':
            return 10000.0#TODO
        # end if
    # end def     
    
    
    def __exit__(self, type, value, traceback):
        """
        Exit the with statement and close all ports associuated with the 
        power supply
        """
        # only close a port if one was found.
        if self.port != 'NULL':
            if self.model == '34410A':
                # close comms #TODO
            #end if
        # end if        
    #end def    
# end class            
            
#
# ----------------
# Private Functions
            
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
            
    @return    (list of strings)   list of usable com ports
    """
    
    # determine the system that this code is running on and build a list of 
    # all possible ports
    if sys.platform.startswith('win'):
        # windows
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    # end if

    # initialise result list
    result = []
    
    # iterate through all the ports checking for serial comms
    for port in ports:
        # attempt to establist communications
        try:
            s = serial.Serial(port)
            s.close()
            
            # add to the list of useable ports
            result.append(port)
            
        except (OSError, serial.SerialException):
            # was not a useable port
            pass
        # end try
    # end for
    
    return result
# end def

def findKoradPort():
    """ 
    Find the port that the Korad power supply is operating on
    
    @return   (string)    the name of the port that the power supply is using
                          'NULL' if it cannot be found
    """
    
    # initialise return value
    power_supply_port = 'NULL'
    
    # find all available ports
    available_ports = [default_port] + serial_ports()
    
    # iterate through the available ports to see if any is the power supply
    for port in available_ports:
        # try to communicate with each port as if it was the power supply
        try:
            # open the power supply port
            with KoradSerial(port) as com_test:
                # request the model name
                model_name = com_test.model.encode('ascii','ignore')
                
                # if the power supply name is acceptible then store that port 
                # name and exit
                if model_name.startswith('KORAD'):
                    power_supply_port = port
                    break;
                # end if
            # end with
        except:
            # this port is not a Korad power supply
            pass
        # end try
    # end for    
    
    return power_supply_port
# end def

def _test():
    """
    Test code for this module.
    """
    # construct the root frame
    root = TK.Tk()
    root.geometry('800x600')
    
    # construct a frame for the power supply gui
    test_frame = TK.Frame(root)
    test_frame.grid(row = 0, column = 0)
    
    # initialise the power supply gui
    PS_GUI = Power_Supply_GUI(test_frame, root, 'KA3005P')
    
    # start the GUI
    root.mainloop()
# end def

if __name__ == '__main__':
    # if this code is not running as an imported module run test code
    _test()
# end if