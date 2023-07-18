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
        with open(filename, "rb") as file:
            corpus.add(file.read())
    corpus = list(map(bytearray, corpus))

    if not corpus:
        print(f"No files found in the corpus folder: {folder}")
        sys.exit(1)

def mutate(mutate_corpus: bytearray, percent: float):
    mutate_data = bytearray(random.choice(mutate_corpus))
    for _ in range(random.randint(0, int((len(mutate_data) - 1) * percent))):
        mutate_data[random.randint(0, len(mutate_data) - 1)] = random.randint(0, 255)
    return mutate_data


def mutate_radamsa(mutate_corpus):
    rada = pyradamsa.Radamsa()
    mutate_data = bytearray(random.choice(mutate_corpus))
    return rada.fuzz(mutate_data)


def main(argv):
    arguments = argparse.ArgumentParser(description='Dumb-NFuzz Network')
    arguments.add_argument('-i', '--ip', type=str, required=True, help='IP address')
    arguments.add_argument('-p', '--port', type=int, required=True, help='Port number')
    arguments.add_argument('-P', '--percent_fuzz', type=float, default=0.0, help='Mutation percentage')
    arguments.add_argument('-f', '--folder', type=str, required=True, default='./in/*', help='Corpus folder')
    arguments.add_argument('-l', '--loop', type=int, default=1, help='Number of iterations')
    arguments.add_argument('-c', '--connect', type=str, help='Connect file')
    arguments.add_argument('-t', '--timeout', type=int, default=0, help='Timeout in seconds')
    arguments.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
    arguments.add_argument('-r', '--radamsa', action='store_true', help='Use Radamsa for mutation')
    arguments.add_argument('-j', '--logger', action='store_true', help='Enable logging')

    args = arguments.parse_args(argv)

    print('IP is', args.ip)
    print('Port is', args.port)
    print('Mutation Percentage is', args.percent_fuzz * 100)
    print('Corpus folder is', args.folder)
    print('Iteration is', args.loop)
    print('Connect file is', args.connect)
    print('Timeout is', args.timeout)
    print('Verbose is', args.verbose)
    print("Radamsa is", args.radamsa)

    set_corpus(args.folder)
    start = time.time()

    if args.connect:
        with open(args.connect, "rb") as file:
            connect_pk = file.read()
    else:
        connect_pk = b''

    for i in range(args.loop):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((args.ip, args.port))
            s.settimeout(0.1)

            if args.radamsa:
                x = mutate_radamsa(mutate_corpus=corpus)
            else:
                x = mutate(mutate_corpus=corpus, percent=args.percent_fuzz)

            elapsed = time.time() - start

            s.sendall(connect_pk + x)

            try:
                data = s.recv(1024)

                if args.logger:
                    with open("data_file.json", "a") as json_file:
                        json_temp = {"S": binascii.hexlify(connect_pk + x).decode("utf-8"),
                                     "R": binascii.hexlify(data).decode("utf-8")}
                        json.dump(json_temp, json_file)
                        json_file.write('\n')

                if args.verbose:
                    print(f"Sent [{connect_pk + x}]")
                    print(f"Recv [{repr(data)}]")
                    print(f"[{elapsed:10.4f}] corpus {i + 1:10} | cps {float(i + 1) / elapsed:10.4f}")

            except socket.timeout:
                print(f"Recv [NULL]")
                print(f"Sent [{connect_pk + x}]")

            except SocketError as e:
                if e.errno != errno.ECONNRESET:
                    print(f"Sent [{connect_pk + x}]")
                    raise
                pass

            finally:
                pass

            time.sleep(args.timeout)


if __name__ == "__main__":
    main(sys.argv[1:])
