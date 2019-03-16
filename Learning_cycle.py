# Runs a learning cycle on a BM2 pach with a BQ34z651 controller.


# imports
import BM2_aardvark
import aardvark_py
import Power_Supply
import DC_Load
import sys
import time

# settings
DISCHARGE_CURRENT = 0.5
CHARGE_CURRENT    = 2
CHARGE_VOLTAGE    = 8.4
STATE_PAUSE       = 60
SAMPLE_RATE_MS    = 10000
SLEEP_ONE_SEC     = 1000
MESSAGE_PERIOD    = 600

# definitions
def BM2_power_switch_init():
    # output state low
    aardvark_py.aa_gpio_set(BM.port, 0)
    
    # direction as output
    aardvark_py.aa_gpio_direction(BM.port, aardvark_py.AA_GPIO_SS)
# end def

def BM2_power_switch_set(state):
    
    if (state == 1):
        aardvark_py.aa_gpio_set(BM.port, aardvark_py.AA_GPIO_SS) 
        
    else:
        aardvark_py.aa_gpio_set(BM.port, 0) 
    # end if
# end def

start_time = time.time()

def get_runtime():
    return '%.0f mins' % ((time.time() - start_time)/60)
# end def



# initialise Devices
BM = BM2_aardvark.BM2()
Load = DC_Load.DCLoad('M9711')
PS = Power_Supply.PowerSupply('KA3005P')


# initialise hardware
print "Initialising Hardware"

with PS:
    PS.output_off()
    PS.set_current(CHARGE_CURRENT)
    PS.set_voltage(CHARGE_VOLTAGE)
# end with

with Load:
    Load.load_off()
    Load.set_mode('constant_current', DISCHARGE_CURRENT)
# end with

with BM:
    # initialise power switch
    # this is a PCB just for learning cycles
    BM2_power_switch_init() 
    
    # verify SMB comms
    if ((BM.get_ChargingVoltage()/1000.0) != CHARGE_VOLTAGE):
        print "Warning BM2 communications may be in error"
        print "Charging Voltage = " + str(BM.get_ChargingVoltage()/1000.0) + "V"
    # end if
# end with
    

print "Starting Learning Cycle by discharging the pack"
with BM:
    
    # initialise power switch
    # this is a PCB just for learning cycles
    BM2_power_switch_init()    
    
    # prep pack by discharging to low voltage 
    with Load:
        # configure the load for a discharge
        Load.set_mode('constant_current', DISCHARGE_CURRENT)
        Load.load_on()
        
        # connect the load to the BM
        BM2_power_switch_set(1)
        
        current_time = time.time()
        # discharge until the CUV warning is given
        while BM.get_CUV() == False:
            # wait 1 second
            aardvark_py.aa_sleep_ms(SAMPLE_RATE_MS)

            if ((time.time() - current_time) > MESSAGE_PERIOD):
                # print a periodic message 
                print "After " + get_runtime() + " Voltage is " + str(BM.get_Voltage()/1000.0) + "V, Current is " + str(BM.get_Current()) + "mA"
                current_time = time.time()
            #end if
        #end while
        
        #disconnect the pack from the load
        BM2_power_switch_set(0)
        
        # turn the load off
        Load.load_off()
        
        print "Pack is discharged after " + get_runtime() + ", relaxing"
    # end with
    
    # wait to allow the pack to relax
    aardvark_py.aa_sleep_ms(SLEEP_ONE_SEC*STATE_PAUSE*10)
    print "Relaxing Complete sending IT_ENABLE"
    
    # send the command to start the learning cycles
    BM2_aardvark.send_SMB_data(['0x00', '0x21', '0x00'], BM.port)
    
    # wait for the command to be processed
    aardvark_py.aa_sleep_ms(SAMPLE_RATE_MS)
    
    if ((BM.get_QEN() != 1) or (BM.get_RDIS() != 0)):
        print "starting of learning cycle has failed"
        sys.exit()
    # end if
    
    print "IT_ENABLE acccepted after " + get_runtime() + ", starting to charge"
    
    # start charging the pack to full
    with PS:
        # configure the power supply and turn it on
        PS.set_voltage(CHARGE_VOLTAGE)
        PS.set_current(CHARGE_CURRENT)
        PS.output_on()
        
        # connect the PS to the BM
        BM2_power_switch_set(1)    
        
        current_time = time.time()
        # discharge until the FC signal is given
        while BM.get_FC() == False:
            # wait 1 second
            aardvark_py.aa_sleep_ms(SAMPLE_RATE_MS)

            if ((time.time() - current_time) > MESSAGE_PERIOD):
                # print a periodic message 
                print "After " + get_runtime() + " Voltage is " + str(BM.get_Voltage()/1000.0) + "V, Current is " + str(BM.get_Current()) + "mA"
                current_time = time.time()
            #end if
        #end while
        
        #disconnect the pack from the power supply
        BM2_power_switch_set(0)
        
        # turn the power supply off
        PS.output_off()
        
        print "Pack is charged after " + get_runtime() + ", relaxing"
    # end with        
        
    current_time = time.time()
    # wait for the pack to detect OCV measurement success
    while BM.get_VOK() == True:
        # wait 1 second
        aardvark_py.aa_sleep_ms(SAMPLE_RATE_MS)

        if ((time.time() - current_time) > MESSAGE_PERIOD):
            # print a periodic message 
            print "After " + get_runtime() + " OCV Measurement is yet to be taken"
            current_time = time.time()
        #end if
    #end while   
    
    print "OCV Measurement taken successfully after " + get_runtime() + ", transitioning to discharge again"
    
    with Load:
        # configure the load for a discharge
        Load.set_mode('constant_current', DISCHARGE_CURRENT)
        Load.load_on()
        
        # connect the load to the BM
        BM2_power_switch_set(1)
        
        current_time = time.time()
        # discharge until the CUV warning is given
        while BM.get_CUV() == False:
            # wait 1 second
            aardvark_py.aa_sleep_ms(SAMPLE_RATE_MS)
            
            if BM.get_VOK() == False:
                print " VOK has not be reset!"
            # end if
            
            if ((time.time() - current_time) > MESSAGE_PERIOD):
                # print a periodic message 
                print "After " + get_runtime() + "Voltage is " + str(BM.get_Voltage()/1000.0) + "V, Current is " + str(BM.get_Current()) + "mA"
                current_time = time.time()
            #end if
        #end while
        
        #disconnect the pack from the load
        BM2_power_switch_set(0)
        
        # turn the load off
        Load.load_off()
        
        print "Pack is discharged after " + get_runtime() + ", relaxing"
    # end with   
    
    current_time = time.time()
    while BM.get_MaxError() > 1:
        aardvark_py.aa_sleep_ms(SAMPLE_RATE_MS)
        
        if ((time.time() - current_time) > MESSAGE_PERIOD):
            # print a periodic message 
            print "After " + get_runtime() + "MaxError is " + str(BM.get_MaxError()) + "%"
            current_time = time.time()
        #end if
    #end while 
    
    print "Learning Cycle has been completed successfully"
# end with
    
        