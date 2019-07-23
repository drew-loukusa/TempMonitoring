import time
import serial
import datetime 
import argparse 

#TODO:
#==============================================================================#

# The next thing to add:

# ---> Sending the data update frequency to the Arduino from the script itself.



# I should change it so that I have the python script send the data update frequency it 
# expects to the Arduino.

# The Arduino would have to wait for an initial message, then start sending data.

# That would actually be the way to do it. 

# You could have a number of options that you could set here in the script,
# or even better, with command line flags, that then get sent to the Arduino.

# You could have it change: what data gets recorded, format, etc etc. 

# DEFAULTS:
#==============================================================================#
#The following line is for serial over GPIO:
PORT = "COM5"
BAUDRATE = 9600 
TIMEOUT = 300 # Seconds
UPDATE_FREQUENCY = 30 # Seconds

# ARGS:
#==============================================================================#
p = argparse.ArgumentParser()
add = p.add_argument

add('-p',   dest    = 'port', 
            default = PORT, 
            help    = "Which port the program shoud listen on")

add('-b',   dest    = 'baudrate',
            default = BAUDRATE, 
            help    = "Baud rate such as 9600 or 115200 etc")

add('-t',   dest    = 'timeout', 
            default = TIMEOUT,
            help    = "Set a read timeout value. Must be set to a value greater\
                        than the update frequency")

add('-uf',  dest    = 'update_freq', 
            default = UPDATE_FREQUENCY,
            help    = "Set how often the data is updated. Interval should not be\
                        less than 3 seconds since values from the sensor can be\
                        up to 2 seconds old.")

args = p.parse_args()

# Main:
#==============================================================================#
def main(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT, update_freq=UPDATE_FREQUENCY):
    
    timeout     = float(timeout)
    update_freq = float(update_freq)

    # Quit if timeout is less than the update freq:
    #----------------------------------------------------------------------------#
    if timeout <= update_freq: 
        print("ERROR: Timeout was set to a value less than the update frequency")
        quit()

    # Open the port:
    #----------------------------------------------------------------------------#
    try:
        ser = serial.Serial(port=port, 
                            baudrate=baudrate, 
                            timeout=timeout, 
                            write_timeout=5)

    except serial.serialutil.SerialException as e:
        print(e)
        quit()


    # Transmit the update frequency to the Arduino:       
    #----------------------------------------------------------------------------#    
   
    time.sleep(2) # Wait 2 seconds for the Arduino to setup.

    # I haven't figured out why yet, but the program freezes if you don't wait 
    # for the Arduino to get started. I think the write() call gets stuck because 
    # the port hasn't been opened yet by the Arduino? I tried setting write_timeout
    # for the Serial object but that didn't seem to help.

    # In any case, this works. I'll have to look into this more.

    data = str(update_freq)+"$"
    ser.write(data.encode('utf-8'))       

    # Emit Title, Parameters and Column Labels: 
    #----------------------------------------------------------------------------#
    print("AM2302 Humidity - Temperature Sensor")
    print("Port: {}\tBaudrate: {}\t\tUpdate Freq (Sec): {}\tTimeout (Sec):{}"
                                .format(port, baudrate,update_freq, timeout))
    print("-"*81)
    print("Time\t\t\tRH\t \tTemp (F)\tHeat Index (F)")      

    # Wait for data on the serial port, then print it out as it's recieved:
    #----------------------------------------------------------------------------#
    loop = True
    while loop:
        try:          
            cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")        
            cur_line = get_data(ser)            

            # Occasionally, the script will read before the data is sent
            # by the Arduino. If this happens then we just wait a tiny bit,
            # then read again:
            if cur_line == "":
                time.sleep(0.05)
                cur_line = get_data(ser)

            print(cur_time + "\t" + cur_line)  

            # The Arduino is set to send data every update_freq seconds, 
            # so wait that long between reading data:
            time.sleep(update_freq)                        
        except KeyboardInterrupt:            
            loop = False
        except:
            print('Data could not be read') 

def emit_output(*strings, mode):
    # Build string to be emitted:
    outtext = ""
    for string in in strings:
        outtext += string 

    if mode = 1:
        print(outtext)

    if mode = 0;
        pass

    # okay so either I need to add a conditional to the main() that either DOES or does not 
    # create and opens a file object, which can then be passed into this function...

    # OR

    # I reopen the file  inside this function each time I want to write data out.

    # The first option  is better from a memory and efficieny stand point, the second
    # will make for a cleaner main(). For this purpose it doesn't really matter, but it's 
    # always good to keep these things in mind.


def get_data(ser):
    return ser.readline().decode("utf-8").rstrip('\n')

if __name__ == "__main__":
    main(args.port, args.baudrate, args.timeout, args.update_freq)