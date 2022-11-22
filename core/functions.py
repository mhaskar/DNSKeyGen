#!/usr/bin/python3

import os
import random
import string
from .dnsserver import *
from termcolor import cprint
from validators import domain

def print_error(message):
    cprint("[-] %s" % message, "red")


def print_success(message):
    cprint("[+] %s" % message, "green")


def print_info(message):
    cprint("[!] %s" % message, "yellow")


def check_root():
    uid = os.getuid()
    if uid != 0:
        root_message = "\033[1mPlease run it as root\033[0m"
        print_error(root_message)
        exit()


def check_domain(domain_name):
    return domain(domain_name)


def key_to_hex(key):
    new_key = []
    for opcode in key:
        new_hex_opcode = hex(ord(opcode)).replace("0x", "")
        # This will fix a bug happen when we return any opcode begin with 0x0
        # For example, 0x0f will be translated to 0xf which will break the opcode sequence
        # We will check if the length of the opcode is equal to 3 and then append extra 0
        # So the final result will be 0x0f insted of 0xf
        # The 0x0 will automatically be replaced later on with 0x00
        # Taken from https://github.com/mhaskar/DNSStager/blob/main/core/functions.py#L98
        if len(new_hex_opcode) == 3:
            new_hex_opcode = new_hex_opcode.replace("0x", "0x0")

        if new_hex_opcode == "0x0":
            new_hex_opcode = "0x00"

        new_key.append(new_hex_opcode)
    return "".join(new_key)  

def key_ipv4_value(key):
    if len(key) != 4:
        ipv4_key_length_error_message = "Key length for IPv4 keys should be 4 bytes only"
        print_error(ipv4_key_length_error_message)
        exit()
    nkey = [str(ord(i)) for i in key]
    ipv4 = ".".join(nkey)
    return ipv4

def key_ipv6_value(key):
    octets_splitter = 4
    opcodes = [key[i:i+octets_splitter] for i in range(0, len(key), octets_splitter)]
    ipv6 = ":".join(opcodes)
    return ipv6

def generate_record_ipv6(domain, key):
    ipv6_record = key_ipv6_value(key)
    zones = {domain: [Record(AAAA, ipv6_record)]}
    return zones


def generate_record_txt(domain, key):
    zones = {domain: [Record(TXT, key)]}
    return zones


def generate_record_ipv4(domain, key):
    ipv4_record = key_ipv4_value(key)
    zones = {domain: [Record(A, ipv4_record)]}
    return zones


def start_dns_server(zones, tcp):
    resolver = Resolver(zones)
    if tcp:
        tcp_flag_to_use = True
    else:
        tcp_flag_to_use = False
    try:
        print_success("Starting the DNS server ..")
        server = DNSServer(resolver, port=53, address="0.0.0.0", tcp=tcp_flag_to_use)
        server.start()
    except Exception as e:
        print_error("Can't start the DNS server")
        print_error(e)



def generate_ipv6_key():
    key = "".join([random.choice(string.ascii_uppercase) for i in range(16)])
    return key


def generate_txt_key():
    key = "".join([random.choice(string.ascii_uppercase) for i in range(int(random.choice(range(10, 25))))])
    return key


def generate_ipv4_key():
    key = "".join([random.choice(string.ascii_uppercase) for i in range(4)])
    return key


def show_banner():
    yellow = '\33[33m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'
    cyan = "\033[36m"
    banner = r'''

{0}    
██████╗ ███╗   ██╗███████╗██╗  ██╗███████╗██╗   ██╗ ██████╗ ███████╗███╗   ██╗
██╔══██╗████╗  ██║██╔════╝██║ ██╔╝██╔════╝╚██╗ ██╔╝██╔════╝ ██╔════╝████╗  ██║
██║  ██║██╔██╗ ██║███████╗█████╔╝ █████╗   ╚████╔╝ ██║  ███╗█████╗  ██╔██╗ ██║
██║  ██║██║╚██╗██║╚════██║██╔═██╗ ██╔══╝    ╚██╔╝  ██║   ██║██╔══╝  ██║╚██╗██║
██████╔╝██║ ╚████║███████║██║  ██╗███████╗   ██║   ╚██████╔╝███████╗██║ ╚████║
╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝
{1}
                                        {2}Exchange keyzzz via DNS{1} | {3}V1.0 beta{1}
                                                                              '''.format(red, end, green, cyan)
    print(banner)