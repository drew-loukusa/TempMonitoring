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

    # Quit if timeout is less than the update freq 
    if timeout <= update_freq: 
        print("ERROR: Timeout was set to a value less than the update frequency")
        quit()

    # Open the port:
    try:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout, write_timeout=5)
    except serial.serialutil.SerialException as e:
        print(e)
        quit()


    # Transmit the update frequency to the Arduino:    
    # Wait 2 seconds for the Arduino to setup:
    time.sleep(2)      
    for i in range(3):
        try:             
            data = str(update_freq)+"$"
            ser.write(data.encode('utf-8'))
            break
        except Exception as e:
            print(e)
            print("Failed to send update frequency to Arduino. ")
            print("Retrying again in 5 seconds...")
            time.sleep(5)
    else:
        print("Could not write to the Arduino after multiple attempts. Exiting program.")
        quit()

    # Emit Title, Parameters and Column Labels: 
    print("AM2302 Humidity - Temperature Sensor")
    print("Port: {}\tBaudrate: {}\t\tUpdate Freq (Sec): {}\tTimeout (Sec):{}"
                                .format(port, baudrate,update_freq, timeout))
    print("-"*81)
    print("Time\t\t\tRH\t \tTemp (F)\tHeat Index (F)")      

    # Wait for data on the serial port, then print it out:
    loop = True
    while loop:
        try:
            time.sleep(0.05)
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
        except:
            print('Data could not be read or Keyboard Interrupt') 
            loop = False

def get_data(ser):
    return ser.readline().decode("utf-8").rstrip('\n')

if __name__ == "__main__":
    main(args.port, args.baudrate, args.timeout, args.update_freq)