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
@package PowerSupply.py
Module to handle the control of a generic power supply, providing an \
abstraction layer for the user.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

from koradserial import KoradSerial
import sys
import serial

# ---------
# Classes

class PowerSupply(object):
    
    def __init__(self, Model):
        self.model = Model
        
        if self.model == 'KA3005P':
            port = findKoradPort()
            if port != 'NULL':
                self.PS = KoradSerial(port)
                self.output = self.PS.channels[0]

            else:
                raise IOError('No Korad Power Supply was detected')
            # end if
            
        else:
            raise ValueError('The Power Supply model selected is not supported'+
                             'by this Module')
        # end if
    # end def
        
    def close(self):
        if self.model == 'KA3005P':
            self.PS.close()
        # end if        
    #end def
    
    def output_on(self):
        if self.model == 'KA3005P':
            self.PS.output.on()
        # end if 
    # end def
    
    def output_off(self):
        if self.model == 'KA3005P':
            self.PS.output.off()
        # end if 
    # end def    
    
    def get_output(self):
        if self.model == 'KA3005P':
            return self.PS.status.output
    
    def get_output_voltage(self):
        if self.model == 'KA3005P':
            return self.output.output_voltage
        # end if 
    # end def 
    
    def get_voltage(self):
        if self.model == 'KA3005P':
            return self.output.voltage
        # end if 
    # end def    
    
    def set_voltage(self, volts):
        if self.model == 'KA3005P':
            self.output.voltage = volts
        # end if 
    # end def      
        
    def get_output_current(self):
        if self.model == 'KA3005P':
            return self.output.output_current
        # end if 
    # end def 
    
    def get_current(self):
        if self.model == 'KA3005P':
            return self.output.current
        # end if 
    # end def    
    
    def set_current(self, amps):
        if self.model == 'KA3005P':
            self.output.current = amps
        # end if 
    # end def         
            
#
# ----------------
# Private Functions
            
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
# end def

def findKoradPort():
    power_supply_port = 'NULL'
    available_ports = serial_ports()
    
    for port in available_ports:
        try:
            with KoradSerial(port) as com_test:
                model_name = com_test.model.encode('ascii','ignore')
                if model_name.startswith('KORAD'):
                    power_supply_port = port
                    break;
                # end if
        except:
            pass
        # end try
    # end for    
    
    return power_supply_port
# end def