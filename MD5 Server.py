"""
Author : Ariel Shiffer
Program name : md5
Description : This program is working
with a lot of clients and opens threads
for each one of them to find the encryptions
of the knows md5 string.
Date : 16.11.2022
"""

#imports:
import hashlib
import threading
from threading import Thread
import socket
from _thread import *
import select

#constans:
START_NUMBER_CHECK = 0
CHECK_RANGE = 10000
IP = '0.0.0.0'
PORT = 30113
QUEUE_SIZE = 1
LENGTH_NUM = 7
MD5_STRING = 'a113637de6d9ebca9e69b80f5e567ff6'#Only to check if it works = 6969420
W = 'ec9c0f7edcc18a98b1f31853b1813301'#The original md5 string from the ex

#globals:
is_found = False
found_number = ''


def client_handling(client_socket,current_number):
    """
    This function makes sure the client is ready to get the start
    of the range, if he is it sends him the start of the checking range,
    the md5 string, the length of the original number and the length of the range
    of the checking. It waits for the client to do the checking and waits to find
    out if he found the number or not.
    :param client_socket: The socket of the client.
    :param current_number: The start of the range we want the client to check.
    """
    global is_found
    global found_number
    ch = ''
    client_msg = ''
    while ch != '#':
        ch = client_socket.recv(1).decode()
        if ch != '':
            client_msg += ch
    if client_msg[:-1] == 'ready':
        msg = current_number + '#' + str(MD5_STRING) + '#' + str(LENGTH_NUM) +\
              '#' + str(CHECK_RANGE) + '##'
        client_socket.send(msg.encode())
        ch = ''
        client_msg = ''
        while client_msg[-2:] != '##':
            ch = client_socket.recv(1).decode()
            if ch != '':
                client_msg += ch
        if client_msg.split('#')[0] == 'Found':
            print('*******************************************************')
            is_found = True
            found_number = client_msg.split('#')[1]


def main():
    """
    This function waits to clients to connect and opening a thread
    and sending to them the start of the range we want them to check
    and increasing the start of the range. Then checks if we found the
    number or not. If we found the number we print it.
    """
    global is_found
    global found_number
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)

        clients_connected = []
        threads = []
        start_number = START_NUMBER_CHECK
        current_number = start_number
        while not is_found:

            rlist, wlist, xlist = select.select([server_socket] +
                                                clients_connected,
                                                clients_connected,
                                                clients_connected)

            for current_socket in xlist:
                clients_connected.remove(current_socket)

                current_socket.close()
            for current_socket in rlist:

                if current_socket is server_socket:
                    client_socket, client_address = server_socket.accept()
                    clients_connected.append(client_socket)

                elif current_socket is not server_socket:
                    if not is_found:
                        client_thread = Thread(target=client_handling,
                                               args=(current_socket,
                                                     str(current_number).zfill(LENGTH_NUM)))
                        client_thread.start()
                        threads.append(client_thread)
                        current_number += CHECK_RANGE

            for t in threads:
                t.join()
            threads = []
            print(is_found)
            if is_found:
                print('The base number is ' + found_number)
                for c_socket in clients_connected:
                    clients_connected.remove(c_socket)
                    c_socket.close()
            else:
                print('didnt find yet')

    except socket.error as err:
        print('received socket exception - ' + str(err))

    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
