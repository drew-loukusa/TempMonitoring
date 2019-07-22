import time
import serial
import datetime 
import argparse 

#TODO:
#==============================================================================#
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
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
    except serial.serialutil.SerialException as e:
        print(e)
        quit()

    # Emit Title, Parameters and Column Labels: 
    print("AM2302 Humidity - Temperature Sensor")
    print("Port: {}\tBaudrate: {}\t\tUpdate Freq (Sec): {}\tTimeout (Sec):{}"
                                .format(port, baudrate,update_freq, timeout))
    print("-"*81)
    print("Time\t\t\tRH\t \tTemp (F)\tHeat Index (F)")   
    
    # Get the data update frequency from the Arduino: 
    interval = None
    while 1:
        data = get_data(ser)
        data = data.split('\t')

        if len(data) > 1:
            #print("data",data)
            interval = int(data[1])/1000
            break

        time.sleep(1)


    # Wait for data on the serial port, then print it out:
    loop = True
    while loop:
        try:
            # The Arduino is set to send data every INTERVAL seconds, 
            # so wait that long between reading data:
            time.sleep(interval)            

            cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")        
            cur_line = get_data(ser)

            print(cur_time + "\t" + cur_line)          
        except:
            print('Data could not be read or Keyboard Interrupt') 
            loop = False

def get_data(ser):
    return ser.readline().decode("utf-8").rstrip('\n')

if __name__ == "__main__":
    main(args.port, args.baudrate, args.timeout)