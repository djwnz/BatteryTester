# code to run the MS5607 pressure sensor

import time
import platform

WINDOWS_EXECUTION = False
if (platform.system() == 'Windows'):
    WINDOWS_EXECUTION = True
    import aardvark_py
    import array
    
    # I2C config
    I2C = True
    SPI = True
    GPIO = False
    Pullups = True
    radix = 16
    Bitrate = 100    
else:
    print("no valid OS detected")
    raise
# endif

## Command set
MS5607_ADDRESS = 0x76 # base address
MS5607_RESET = 0x1E
MS5607_CONVERT_P_256 = 0x40
MS5607_CONVERT_P_512 = 0x42
MS5607_CONVERT_P_1024 = 0x44
MS5607_CONVERT_P_2048 = 0x46
MS5607_CONVERT_P_4096 = 0x48
MS5607_CONVERT_P = 0x40 # for ORing with an OSR
MS5607_CONVERT_T_256 = 0x50
MS5607_CONVERT_T_512 = 0x52
MS5607_CONVERT_T_1024 = 0x54
MS5607_CONVERT_T_2048 = 0x56
MS5607_CONVERT_T_4096 = 0x58
MS5607_CONVERT_T = 0x50  # for ORing with an OSR
MS5607_OSR_256 = 0x00
MS5607_OSR_512 = 0x02
MS5607_OSR_1024 = 0x04
MS5607_OSR_2048 = 0x06
MS5607_OSR_4096 = 0x08
MS5607_ADC_READ = 0x00
MS5607_PROM_READ = 0xA0 # required Or-ing with (3 bit PROM address << 1)

# conversion time delays
MS5607_OSR_256_S_DELAY = 0.002
MS5607_OSR_512_S_DELAY = 0.002
MS5607_OSR_1024_S_DELAY = 0.004
MS5607_OSR_2048_S_DELAY = 0.006
MS5607_OSR_4096_S_DELAY = 0.100

DO_2ND_ORDER_COMP = True
PRINT_DEBUG = False

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
        print('*** No Aardvark is present ***')
        Aardvark_free = False
        
    else:
        # there is an aardvark connected to select the first one if there
        # are many
        Aardvark_port = AA_Devices[1][0]
    # end if
    
    
    # If there is an Aardvark there is it free?
    if Aardvark_port >= 8<<7 and Aardvark_free:
        # the aardvark is not free
        print('*** Aardvark is being used, '\
              'disconnect other application or Aardvark device ***')
        # close the aardvark
        aardvark_py.aa_close(Aardvark_port)
        Aardvark_free = False
        
    elif Aardvark_free:
        # Aardvark is available so configure it
        
        # open the connection with the aardvark
        Aardvark_in_use = aardvark_py.aa_open(Aardvark_port)
        
        # set it up in teh mode we need for pumpkin modules
        aardvark_py.aa_configure(Aardvark_in_use, 
                                 aardvark_py.AA_CONFIG_GPIO_I2C)
        
        # default to both pullups on
        aardvark_py.aa_i2c_pullup(Aardvark_in_use, 
                                  aardvark_py.AA_I2C_PULLUP_BOTH)
        
        # set the bit rate to be the default
        aardvark_py.aa_i2c_bitrate(Aardvark_in_use, Bitrate)
        
        # free the bus
        aardvark_py.aa_i2c_free_bus(Aardvark_in_use)
        
        # delay to allow the config to be registered
        aardvark_py.aa_sleep_ms(200)    
        
    # end if    
    
    return Aardvark_in_use
# end def

class MS5607:
    def __init__(self, pin_5 = 0):
        self.port = 0
        self.address = MS5607_ADDRESS
        if (pin_5 == 0):
            self.address += 1
        elif (pin_5 != 1):
            print("Invalid pin 5 state, reverting to default")
        # end if
    # end if

    def __enter__(self):
        if (WINDOWS_EXECUTION):
            # configure the aardvark adapter
            self.port = configure_aardvark()
                
            if (self.port == None):
                raise IOError("No Aardvark was found")
            # end if
            
            # power the device
            aardvark_py.aa_gpio_set(self.port, aardvark_py.AA_GPIO_MISO) 
            aardvark_py.aa_gpio_direction(self.port, aardvark_py.AA_GPIO_MISO)    
        # end if
        
        time.sleep(0.1)
        
        self.reset()
        
        return self
    #end def
    
    def __exit__(self, type, value, traceback):
        if self.port != None:
            aardvark_py.aa_close(self.port)
        #end if
        
        self.port = None
    # end def
    
    def reset(self):
        self.write([MS5607_RESET])
    # end def
        

    def write(self, byte_list):
        if (WINDOWS_EXECUTION):
            out_data = array.array('B', byte_list)  
            aardvark_py.aa_i2c_write(self.port, self.address, aardvark_py.AA_I2C_NO_FLAGS, out_data) 
        # end if
    # end def

    def read(self, read_length):
        
        return_list = []
        if (WINDOWS_EXECUTION):  
            in_data = array.array('B', [1]*read_length) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_read(self.port, self.address, aardvark_py.AA_I2C_NO_FLAGS, in_data)   
            
            return_list = [i for i in in_data]
        # end if
        
        return return_list
    # end def

    def sample(self, OSR):
        
        # configure for selected OSR
        SELECTED_OSR = MS5607_OSR_256
        OSR_DELAY = MS5607_OSR_4096_S_DELAY
        if (OSR == 256):
            SELECTED_OSR = MS5607_OSR_256
            OSR_DELAY = MS5607_OSR_256_S_DELAY
        elif (OSR == 512):
            SELECTED_OSR = MS5607_OSR_512
            OSR_DELAY = MS5607_OSR_512_S_DELAY
        elif (OSR == 1024):
            SELECTED_OSR = MS5607_OSR_1024
            OSR_DELAY = MS5607_OSR_1024_S_DELAY
        elif (OSR == 2048):
            SELECTED_OSR = MS5607_OSR_2048
            OSR_DELAY = MS5607_OSR_2048_S_DELAY
        elif (OSR == 4096):
            SELECTED_OSR = MS5607_OSR_4096
            OSR_DELAY = MS5607_OSR_4096_S_DELAY
        else:
            print("Invalid OSR provided, reverting to defaults")
        # end if
        
        # ensure the readings are valid
        prom_valid = False
        trial_counter = 0
        
        while ((not prom_valid) and (trial_counter < 3)):
        
            # read prom data
            prom_data = []
            for address in range(8):
                
                self.write([MS5607_PROM_READ+(address<<1)])    
                time.sleep(0.1)
                in_data = self.read(2)
                
                prom_data.append((in_data[0]<<8) + in_data[1])
            # end for
            
            # extract the desired values from the PROM
            RES = prom_data[0]
            SENS_T1 = prom_data[1]*(2**16.0)
            OFF_T1 = prom_data[2]*(2**17.0)
            TCS = prom_data[3]/(2**7.0)
            TCO = prom_data[4]/(2**6.0)
            T_REF = prom_data[5]*(2**8.0)
            TEMPSENS = prom_data[6]/(2**23.0)
            
            # check the crc
            prom_valid = self.check_crc(prom_data)
            
            if (not prom_valid):
                self.reset()
                time.sleep(0.1)
                print("Resetting to correct invalid data")
            # end if
            
            if (PRINT_DEBUG):
                print("CRC check success = " + str(prom_valid))
                print(prom_data)
            # end if  
        # end while
        
        ## read temp and pressure
        # start the pressure conversion
        self.write([MS5607_CONVERT_P + SELECTED_OSR])    
    
        # wait for the conversion to happen
        time.sleep(OSR_DELAY)        
    
        # request ADC data
        self.write([MS5607_ADC_READ])  
        
        # read data
        in_data = self.read(3) 
        uncomp_P = ((in_data[0]<<16) + (in_data[1]<<8) +(in_data[2]))    
    
        # start temperature conversion
        self.write([MS5607_CONVERT_T+ SELECTED_OSR])    
    
        # wait for the conversion to happen
        time.sleep(OSR_DELAY)        
    
        # request ADC data
        self.write([MS5607_ADC_READ])  
        
        # read data
        in_data = self.read(3) 
        uncomp_T = ((in_data[0]<<16) + (in_data[1]<<8) + in_data[2])   
        
        if (PRINT_DEBUG):
            print("uncomp_P = " + str(uncomp_P) + ", uncomp_T = " + str(uncomp_T))
        # end if
            
        ## compensation as per the MS5607 datasheet
        # temperature compensation
        dT = uncomp_T - T_REF
        TEMP = 2000 + dT*TEMPSENS
        
        # second order compensation
        T2 = 0
        OFF2 = 0
        SENS2 = 0        
        if (DO_2ND_ORDER_COMP):
            if (TEMP < 2000):
                T2 = (dT**2.0)/(2**31.0)
                OFF2 = 61*((TEMP-2000)**2.0)/(2**4.0)
                SENS2 = 2*((TEMP-2000)**2.0)
                
                if (TEMP < -1500):
                    OFF2 = OFF2 + 15*((TEMP+1500)**2.0)
                    SENS2 = SENS2 + 8*((TEMP+1500)**2.0)
                # end if
            # end if
        # end if    
        
        comp_T = TEMP - T2 # 0.01C
        comp_T_C = comp_T/100.0
    
        # pressure compensation
        OFF = OFF_T1 + TCO*dT - OFF2
        SENS = SENS_T1 + TCS*dT - SENS2
        comp_P = (uncomp_P*(SENS/(2**21.0))-OFF)/(2**15.0) # Pa
        
        return comp_T_C, comp_P, prom_valid
    # end def
    
    def check_crc(self, data_16_bit):
        
        # working variable
        n_rem = 0
        
        # convert 16 bit data into 8 bit data
        data_8_bit = []
        for i in data_16_bit:
            data_8_bit.append(i>>8)
            data_8_bit.append(i&0x00FF)
        # end for
        
        # extract the CRC code
        crc_code = data_8_bit[-1]&0x0F
        
        # set the CRC byte to zero
        data_8_bit[-1] = 0
        
        for i in data_8_bit:
            n_rem = n_rem ^ i
        
            for i in range(8):
                if (n_rem & 0x8000):
                    n_rem = (n_rem<<1) ^ 0x3000
                else:
                    n_rem = (n_rem<<1)
                # end if
            # end for
        # end for
        
        # return the appropriate 4 bits
        crc_calc = ((n_rem>>12) & 0x000F) 
        return crc_calc == crc_code
    # end def
# end class

def test():
    
    global PRINT_DEBUG
    PRINT_DEBUG = True
    
    with MS5607(pin_5 = 0) as sensor:
        
        if  not sensor.check_crc([0x3132,0x3334,0x3536,0x3738,0x3940,0x4142,0x4344,0x450B]):
            print("CRC test failed")
        # end if
        
        
        while (1):
            
            [T, P, valid] = sensor.sample(4096)
            
            if (not valid):
                print("Data is corrupted, power cycle the sensor")
                break
            # end if
            
            # print
            print("Pressure = " + str(P/1000) + "kPa, Temperature = " + str(T) + "C")
            
            # wait
            time.sleep(2)
        # end while
    # end with
        
# end def
    

if __name__ == '__main__':
    # if this code is not running as an imported module run test code
    test()
# end if
