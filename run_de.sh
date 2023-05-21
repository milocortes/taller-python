#!/bin/bash

for (( port=8888; port<=8897; port++ ))
do 
   python test_de_remote.py "127.0.0.1" $port &    
done