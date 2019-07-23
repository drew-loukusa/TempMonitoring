# TempMonitoring
My room was too hot and I wanted to know how warm it was getting. I had some spare parts lying around so I cobbeled together a temp sensor and an Arduino with some Python to make a live temp monitoring thingy which sends the data to my computer.

For hardware I'm using and Arduino Uno with an AM2302 Temperature/Humidity Sensor.
For software I'm using a Python script to control everything and of course an Arduino sketch on the Arduino itself.

The picture below shows the wiring setup I'm using. It doesn't matter which 5V or GND you use, just as long as you don't mix them up.
The picture does not actually show a AM2302 sensor because Fritizing (the software I used to make the diagram) did not have that part.

If you have a AM2302, just make sure that you hookup the '+' to the 5V and the '-' to ground (GND). 

More info to come on how the script works...

![Image description](https://github.com/drew-loukusa/TempMonitoring/blob/master/WiringDiagram.JPG)

Credit to cactus.io for the Arduino sketch that I modified/used as a starting place:
For details on how to hookup the DHT22 sensor to the Arduino then checkout this page
http://cactus.io/hookups/sensors/temperature-humidity/am2302/hookup-arduino-to-am2302-temp-humidity-sensor
