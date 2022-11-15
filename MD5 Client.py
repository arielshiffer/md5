"""
Author : Ariel Shiffer
Program name : md5
Description : This program opening a thread
for each core in the computer and checks if one
of the numbers in the range is the encryption of
the known md5 string.
Date : 16.11.2022
"""

#imports:
import hashlib
import os
import socket
import time
from _thread import *
import threading

#constants:
SERVER_PORT = 30113
SERVER_IP = '127.0.0.1'

#globals:
md5_string = ''
check_range = 0
length_of_num = 0
is_found = False
found_string = ''
current = ''

def md5_check(start_number):
    """
    This function gets a variable(int) and check every numbers
    md5 encryption and in a known range.
    if the encryption of the number is equal to the md5 string we got from the
    server. if it is it means we found the original number.
    :param start_number: The start of the checking range. type int.
    """
    global length_of_num
    global check_range
    global md5_string
    global is_found
    global found_string
    global current
    j = start_number

    while j < start_number + (check_range // os.cpu_count()) and not is_found:
        string_check = str(j).zfill(length_of_num)
        print(string_check)
        result = hashlib.md5(string_check.encode())
        if result.hexdigest() == md5_string:
            print('found')
            is_found = True
            found_string = string_check
        j += 1
        current = string_check


def main():
    """
    This function connects to the server and gets the start of the checking range,
    the md5 string, the length of the original number and the length of the range
    of the checking. It sends  'ready' to the server when ready and opens a thread
    for every core in the computer. when finished it sends back to the server if
    we found the number or not.
    """
    global is_found
    global found_string
    global length_of_num
    global check_range
    global md5_string
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((SERVER_IP, SERVER_PORT))
        curren_open_threads = []

        while not is_found:
        # Start a new thread and return its identifier
            my_socket.send('ready#'.encode())
            ch = ''
            server_msg = ''
            while server_msg[-2:] != '##':
                ch = my_socket.recv(1).decode()
                if ch != '':
                    server_msg += ch
            start_number = server_msg.split('#')[0]
            md5_string = server_msg.split('#')[1]
            length_of_num = int(server_msg.split('#')[2])
            check_range = int(server_msg.split('#')[3])

            send_number = int(start_number)

            for i in range(0, os.cpu_count()):
                client_thread = threading.Thread(target=md5_check,
                                                 args=(send_number,))
                client_thread.start()
                send_number = send_number + (check_range //
                                             int(os.cpu_count()))
                curren_open_threads.append(client_thread)
            for t in curren_open_threads:
                t.join()
            curren_open_threads = []

            if is_found:
                protocol = 'Found#' + found_string + '##'
            else:
                protocol = 'NotFound#' + current + '##'
            my_socket.send(protocol.encode())

        protocol = 'Found#' + found_string + '##'
        my_socket.send(protocol.encode())


    except socket.error as err:
        print('received socket error ' + str(err))
    finally:
        my_socket.close()


if __name__ == '__main__':
    main()
