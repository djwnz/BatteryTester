# Runs a learning cycle on a BM2 pach with a BQ34z651 controller.


# imports
import BM2_aardvark
import aardvark_py
import Power_Supply
import DC_Load
import sys
import time
import csv
import datetime

# profile specific settings
DISCHARGE_CURRENT = 2.4    # A
CHARGE_CURRENT    = 3.5      # A
CHARGE_VOLTAGE    = 8.4    # V
TERM_VOLTAGE      = 4100   # mV

# other settings
STATE_PAUSE       = 60     # s
SAMPLE_RATE_MS    = 1000  # ms
SLEEP_ONE_SEC     = 1000   # ms
MESSAGE_PERIOD    = 600    # s
IMBALANCE_LIMIT   = 100     # mV

# tracker for state changes
PASS_CRITERIA = 3
pass_count = 0

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

def cell_voltages_good(BM):
    
    cell_voltages = [BM.Data.CellVoltage1, BM.Data.CellVoltage2, BM.Data.CellVoltage3, BM.Data.CellVoltage4]
    if (CHARGE_VOLTAGE > 8 and CHARGE_VOLTAGE < 9):
        # 2 cell
        min_voltage = min(cell_voltages[0:1])
        max_voltage = max(cell_voltages[0:1])
        
    elif (CHARGE_VOLTAGE > 12 and CHARGE_VOLTAGE < 13):
        # 3 cell
        min_voltage = min(cell_voltages[0:2])
        max_voltage = max(cell_voltages[0:2])   
        
    elif (CHARGE_VOLTAGE > 16 and CHARGE_VOLTAGE < 17):
        # 3 cell
        min_voltage = min(cell_voltages)
        max_voltage = max(cell_voltages)      
    
    else:
        print "aborting due to unexpected charging voltage"
        sys.exit()
    # end if
    
    if ((max_voltage - min_voltage) < IMBALANCE_LIMIT):
        return True
    
    else:
        return False
    # end if
# end def

# start csv file to log to
log_filename = "log file " + datetime.datetime.now().strftime("%Y-%m-%d %H-%M") + ".csv"
csv_file = open(log_filename, 'a+')
csv_writer = csv.writer(csv_file, delimiter = ',')

def log_data(BM):
    try:
        csv_file = open(log_filename, 'a+')
        csv_writer = csv.writer(csv_file, delimiter = ',')
        csv_writer.writerow(BM.Data.to_list(current_time - start_time))
        csv_file.close()
        
    except:
        print "failed to access the log file"
    # end try  
# end def
    
   
    
######################### INITIALISATION #######################################    
# initialise Devices
BM = BM2_aardvark.BM2()
Load = DC_Load.DCLoad('M9711')
PS = Power_Supply.PowerSupply('KA3005P')


# initialise hardware
print "Initialising Hardware"

csv_writer.writerow(BM.Data.headers)
csv_file.close()

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


############################## STATE MACHINE ###################################
# states
INITIAL_DISCHARGE       = 0
LOW_REST                = 1
IT_SETUP                = 2
CHARGE                  = 3
VOK_WAIT                = 4
FINAL_DISCHARGE         = 5
MAX_ERROR_WAIT          = 6
COMPLETE                = 7

# state variable
current_state           = INITIAL_DISCHARGE
previous_state          = COMPLETE

last_message_time = start_time
rest_start_time = start_time

break_count = 0

with BM:
    BM2_power_switch_init()  
    
    # state machine
    while (current_state != COMPLETE):
        
        if not BM.update_data():
            print "After " + get_runtime() + " Data collection from BM2 was bad"
            
            log_data(BM)
            next
        # end if
        
        # new time interval
        current_time = time.time()
        
        # log the data
        log_data(BM)
        
        # potentially print a message
        if ((current_state != MAX_ERROR_WAIT) and ((time.time() - last_message_time) > MESSAGE_PERIOD)):
            # print a periodic message 
            print "After " + get_runtime() + " Voltage is " + str(BM.Data.Voltage/1000.0) + "V, Current is " + str(BM.Data.Current) + "mA"
            last_message_time = time.time()            
        #end if        

        if ((current_state == INITIAL_DISCHARGE) or (current_state == FINAL_DISCHARGE)):
            # discharge the pack
            
            if ((current_state == INITIAL_DISCHARGE) and (current_state != previous_state)):
                # just entered this state
                print "Starting Learning Cycle by discharging the pack"
                previous_state = current_state
            
            elif ((current_state == FINAL_DISCHARGE) and (current_state != previous_state)):
                # just entered this state
                print "OCV Measurement taken successfully (Voltage = " + str(BM.Data.Voltage/1000.0) + "V) after " + get_runtime() + ", transitioning to discharge again"
                previous_state = current_state
            
            elif (current_state == FINAL_DISCHARGE):
                if BM.get_VOK() == False:
                    print " VOK has not be reset!"
                # end if    
            # end if
            
            # discharge
            try:
                with Load:
                    # configure the load for a discharge
                    Load.set_mode('constant_current', DISCHARGE_CURRENT)
                    Load.load_on()      
                    
                    # connect the load to the BM
                    BM2_power_switch_set(1)  
                # end with
            
            except:
                print "Communications with the Load failed"
                old_load = Load
                try: 
                    Load = DC_Load.DCLoad('M9711')
                    
                except: 
                    "Failed to re-initialise the Load"
                    Load = old_load
                # end try                
                next
            # end try
            
            # check exit criteria
            if BM.get_CUV() == True:
                break_count += 1
            
            else:
                break_count = 0
            # end if
            
            if break_count >=2:
                if (current_state == INITIAL_DISCHARGE):
                    current_state = LOW_REST
                    
                else:
                    current_state = MAX_ERROR_WAIT
                # end if  
                
                break_count = 0
            # end if
                
            
        elif (current_state == LOW_REST):
            if (previous_state != current_state):
                # just entered this state
                print "Pack is discharged to " + str(BM.Data.Voltage/1000.0) + "V after " + get_runtime() + ", relaxing"
                previous_state = current_state
                
                #check cell voltage validity
                if BM.Data.Voltage > TERM_VOLTAGE:
                    print "Warning, may not be discharging the pack far enough"
                    
                    print "Cell volatages = " + str([BM.Data.CellVoltage1, BM.Data.CellVoltage2, BM.Data.CellVoltage3, BM.Data.CellVoltage4]) + "mV"
                # end if      
                
                #check faults
                if (BM.Data.SafetyStatus > 0):
                    print "Warning, Fault occurred at bottom of discharge"
                    
                    print "SafetyStatus = " + str(BM.Data.SafetyStatus)
                # end if                 
                
                rest_start_time = time.time()
            # end if
        
            #disconnect the pack from the load
            BM2_power_switch_set(0)
            
            # turn the load off
            Load.load_off()
            
            # check exit criteria
            if ((time.time() - rest_start_time) > STATE_PAUSE*10):
                break_count += 1
            
            else:
                break_count = 0
            # end if
            
            if break_count >=2:                
                current_state = IT_SETUP
                break_count = 0
            # end if
        
        elif (current_state == IT_SETUP):
            if (previous_state != current_state):
                #check cell voltage validity
                if cell_voltages_good(BM) == False:
                    print "Aborting due to cell imbalance"
                    sys.exit()
                # end if
                    
                print "Relaxing Complete (Voltage = " + str(BM.Data.Voltage/1000.0) + "V) sending IT_ENABLE"
                
                # send the command to start the learning cycles
                BM2_aardvark.send_SMB_data(['0x00', '0x21', '0x00'], BM.port)    
                
                previous_state = current_state
            # end if              
            
            # check exit criteria
            if ((BM.get_QEN() == 1) and (BM.get_RDIS() == 0)):
                break_count += 1
            
            else:
                break_count = 0
            # end if
            
            if break_count >=2:                 
                current_state = CHARGE
                break_count = 0
            # end if
            
        elif (current_state == CHARGE):
            if (previous_state != current_state):
                print "IT_ENABLE acccepted after " + get_runtime() + ", starting to charge"
                previous_state = current_state
            # end if
        
            try:
                # start charging the pack to full
                with PS:
                    # configure the power supply and turn it on
                    PS.set_voltage(CHARGE_VOLTAGE)
                    PS.set_current(CHARGE_CURRENT)
                    PS.output_on()
                # end with
                
            except:
                print "Failed to communicate with the Power Supply"
                next
            # end try
            
            # connect the PS to the BM
            BM2_power_switch_set(1)    
                     
            # check exit criteria
            if (BM.get_FC() == True):
                break_count += 1
            
            else:
                break_count = 0
            # end if
            
            if break_count >=2:                 
                current_state = VOK_WAIT
                break_count = 0
            # end if
            
        elif (current_state == VOK_WAIT):
            if (previous_state != current_state):
                print "Pack is charged to " + str(BM.Data.Voltage/1000.0) + "V after " + get_runtime() + ", relaxing"
                previous_state = current_state
            # end if        
                
            #disconnect the pack from the power supply
            BM2_power_switch_set(0)
            
            try:
                with PS:
                    # turn the power supply off
                    PS.output_off()
                # end with
            
            except:
                print "Failed to communicate with the Power Supply"
                next
            # end try
      
            # check exit criteria
            if (BM.get_VOK() == False) and (BM.Data.MaxError == 3) and (BM.Data.UpdateStatus == '0x0D'):
                break_count += 1
            
            else:
                break_count = 0
            # end if
            
            if break_count >=2:                 
                current_state = FINAL_DISCHARGE
                break_count = 0
            # end if
            
        elif (current_state == MAX_ERROR_WAIT):
            if (previous_state != current_state):
                print "Pack is discharged to " + str(BM.Data.Voltage/1000.0) + "V after " + get_runtime() + ", relaxing"
                previous_state = current_state
            # end if         
            
            #disconnect the pack from the load
            BM2_power_switch_set(0)
            
            #check faults
            if (BM.Data.SafetyStatus > 0):
                print "Warning, Fault occurred at bottom of discharge"
                
                print "SafetyStatus = " + str(BM.Data.SafetyStatus)
            # end if            
            
            try:
                with Load:
                    # turn the load off
                    Load.load_off()
                # end with
                
            except:
                print "Communications with the Load failed"
                old_load = Load
                try: 
                    Load = DC_Load.DCLoad('M9711')
                    
                except: 
                    "Failed to re-initialise the Load"
                    Load = old_load
                # end try
                next
            # end try            
            
            # check exit criteria
            if (BM.Data.MaxError == 1) and (BM.get_VOK() == False) and (BM.Data.UpdateStatus == '0x0E'):
                break_count += 1
            
            else:
                break_count = 0
            # end if
            
            if break_count >=2:                 
                current_state = COMPLETE
                break_count = 0
            # end if
            
            if ((time.time() - last_message_time) > MESSAGE_PERIOD):
                # print a periodic message 
                print "After " + get_runtime() + "MaxError is " + str(BM.Data.MaxError) + "%"
                last_message_time = time.time()
            #end if
        # end if
    
        # wait for next loop
        aardvark_py.aa_sleep_ms(SAMPLE_RATE_MS)  
    #end while 
    
    print "Learning Cycle has been completed successfully" 
# end with
    
      