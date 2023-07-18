# dumb-nfuzz
The Dumb Network Fuzzer

dumb-nfuzz is a personal script which i use to fuzz network application. This is a very simple and flexible network based fuzzer that can be used on any TCP/IP based proctocol.  

Core idea is that it takes a samples of network data in binary form, mutates it and sends it to the server or client using socket connection depending upon what you want to fuzz. It supports both random mutator and radamsa mutator. You can also log your data as json, so you can either use it for later or use it for identifying the crash when a network connection has no feedback. 

Disclaimer
------------

This should never be used on any live server or should not be tested without their permission. Try this on your own locally hosted implementation to find bugs. I shall hold no responsibility for misuse of any of these code for any illegal activity that will put you in the jail. 

Requirements
------------

pyradamsa is the only special deps. rest should be inbuilt with python. 

pip install pyradamsa


Usage
------------

   python3 nfuzz.py .py  -i "0.0.0.0" -p "1883" -P 0.2 -f "./in/*"  -l 1000  -v -t 0 -r -j -c "connect"

-i -> IP address of the host

-p -> port number

-P -> percent of the random mutator, ie number of mutated packet/number of packet

-f -> The file containing sample file. Use * to select all files in a folder 

-l -> number of fuzzing iteration 

-v -> verbose - print all the output in the screen

-t -> timeout in seconds - timeout between each fuzz

-r -> radamsa mode - use radamsa mutator instead of the inbuilt one

-j -> log to json file 

-c -> first connection packet if the protocol needs one like mqtt

Generating the sample data
--------------------------

Use wireshark to capture all the data in pcap and select one sample packet you want to save(you need to do your identifying which packet belongs to your target and have some understanding about the data), Select block below Transmission Control layer and right click -> copy as escape string. In terminal use "echo -ne 'paste the value here' > sample_1"  This is the method i use. You can alternatively use export specified bytes or use scapy to automate it. 

You can also use XML or HTML files too to fuzz any custom server implementation like nodejs or python or java based server.


Bugs identified
------------
- aedes MQTT broker - CVE-2020-13410
- GenieACS CWMP server - TBA
- Bevywise MQTT broker - TBA
- Few vendor specific miniupnp - NA
- Some vendor specific webserver - NA
- You can add yours


Future ideas
------------

- Add Timestamp 
- Feedback with a Process ID
- Code coverage?
- Some sort of automated instrumentation


Inspiration
------------

- FSecure/mqtt-fuzz - https://github.com/F-Secure/mqtt_fuzz
- Gamozo Twtich stream on Fuzzing. Super awesome content - https://twitter.com/gamozolabs?lang=en
- AFL network fuzzer which never worked for me. - https://github.com/jdbirdwell/afl



Feel free to patch any issues or add new feature in the code. I am not a daily coder, so dont mind my dumb way of coding. 
