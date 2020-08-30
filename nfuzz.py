
import sys
import socket
import time
import binascii 
import random
import glob
import argparse
from socket import error as SocketError
import errno
import pyradamsa
import json

def set_corpus(folder):
   global corpus
   corpus_filenames = glob.glob(folder)
   corpus = set()
   for filename in corpus_filenames:
      corpus.add(open(filename,"rb").read())
   corpus = list(map(bytearray, corpus))
   #print(corpus)

def mutate(mutate_corpus: bytearray, percent: float):
   assert isinstance(percent, float)
   mutate_data=bytearray(random.choice(mutate_corpus))
   for _ in range(random.randint(0,int((len(mutate_data)-1)*percent))):
      mutate_data[random.randint(0,len(mutate_data)-1)] = random.randint(0,255)
   return mutate_data
def mutate_radamsa(mutate_corpus):
   rada = pyradamsa.Radamsa()
   mutate_data=bytearray(random.choice(mutate_corpus))
   return rada.fuzz(mutate_data)

def main(argv):
   number=0 
   connect_pk=b''
   arguments = argparse.ArgumentParser(description='DFuzz Network')
   arguments.add_argument('-i','--ip', action='store', type=str, required=True, default='127.0.0.1')
   arguments.add_argument('-p','--port', action='store', type=int, required=True)
   arguments.add_argument('-P','--percent_fuzz', action='store', type=float, required=False)
   arguments.add_argument('-f','--folder', action='store', type=str, required=True, default='./in/*')
   arguments.add_argument('-l','--loop', action='store', type=int, required=False)
   arguments.add_argument('-c','--connect', action='store', type=str, required=False)
   arguments.add_argument('-t','--timeout', action='store', type=int, required=False, default=0)
   arguments.add_argument('-v','--verbose', action='store', type=bool, required=False, default=False)
   arguments.add_argument('-r','--radamsa', action='store', type=bool, required=False, default=False)
   arguments.add_argument('-j','--logger', action='store', type=bool, required=False, default=False)
   args = arguments.parse_args()
   print ('IP is ', args.ip)
   print ('Port is ', args.port)
   print ('Mutatation Percentage is ', args.percent_fuzz*100)
   print ('Corpus folder is ', args.folder)
   print ('Iteration is ', args.loop)
   print ('Connect file is ', args.connect)
   print ('Timeout is ',args.timeout)
   print ('Verbose is ',args.verbose)
   print ("Radamsa is", args.radamsa)
   set_corpus(args.folder)
   start = time.time()
   if args.connect:
      connect_pk=open(args.connect,"rb").read()
   for i in range(args.loop):
   	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         s.connect((args.ip, int(args.port)))
         s.settimeout(0.1)
         if args.radamsa:
            x = mutate_radamsa(mutate_corpus=corpus)
            #print("radamsa mode")
         else:
            x = mutate(mutate_corpus=corpus,percent=args.percent_fuzz)
            #print("normal mode")         
         elapsed = time.time() - start
         number += 1
         cps = float(number) / elapsed
         s.sendall(connect_pk+x)
         try:
            data = s.recv(1024)
            with open("data_file.json", "a") as json_file:
               json_temp = {"S":binascii.hexlify(connect_pk+x).decode("utf-8"),"R":binascii.hexlify(data).decode("utf-8")}
               json.dump(json_temp, json_file)
               json_file.close()
            #print(json_temp)
            if args.verbose:
               print(f"Sent [{connect_pk+x}]" )
               print(f"Recv [{repr(data)}]" )
               print(f"[{elapsed:10.4f}] corpus {number:10} | cps {cps:10.4f}")
         	#print('Recv data: ', repr(data))
         except socket.timeout:
            print(f"Recv [NULL]" )
            print(f"Sent [{connect_pk+x}]")
         except SocketError as e:
            if e.errno != errno.ECONNRESET:
               print(f"Sent [{connect_pk+x}]")
               raise
            pass
         finally:
         	pass
         s.close()
         time.sleep(args.timeout)
         
if __name__ == "__main__":
   main(sys.argv[1:])

