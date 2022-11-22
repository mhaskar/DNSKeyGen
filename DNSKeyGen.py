#!/usr/bin/python3


import argparse
from core.functions import *


check_root()


parser = argparse.ArgumentParser(description='DNSKeyGen arguments parser')

parser.add_argument(
    '--domain',
    required=False,
    help='The domain you want to use to host the key'
)


parser.add_argument(
    '--record',
    required=False,
    help='The record you want to use (A, AAAA or TXT)'
)


parser.add_argument(
    '--key',
    required=False,
    help='The key you want to use as DNS response'
)


parser.add_argument(
    '--generatekey',
    required=False,
    help='Generate random key to use',
    action='store_true'
)

parser.add_argument(
    '--tcp',
    required=False,
    help='Use DNS over tcp',
    action='store_true'
)


args = parser.parse_args()

domain = args.domain
record = args.record
key = args.key
generate_key = args.generatekey
tcp = args.tcp

if domain is None:
    no_domain_error_message = "Please enter a domain using --domain option"
    print_error(no_domain_error_message)
    exit()

if record is None:
    no_record_error_message = "Please enter a record using --record option"
    print_error(no_record_error_message)
    exit()

if key is None and generate_key is None:
    no_key_error_message = "Please enter a key using --key or use --generatekey to auto generate key for you"
    print_error(no_key_error_message)
    exit()

if key is not None and generate_key is None:
    key = key

if key is None and generate_key is not None:
    if record == "A":
        key = generate_ipv4_key()
    elif record == "AAAA":
        key = generate_ipv6_key()
    elif record == "TXT":
        key = generate_txt_key()
    else:
        no_valid_error_message = "Please choose a valid DNS record (A, AAAA or TXT)"
        print_error(no_valid_error_message)
        exit()


show_banner()
if not check_domain(domain):
    domain_name_error_message = "Please enter a valid domain name"
    print_error(domain_name_error_message)
    exit()



if record == "A":
    generating_ipv4_zone_message = "Generating IPv4 (A) DNS record for the domain %s" % domain
    print_info(generating_ipv4_zone_message)
    zones = generate_record_ipv4(domain, key)
    key_ipv4 = key_ipv4_value(key)
    sucessful_ipv4_message = "Using key %s as A record (%s) for the domain %s" % (key, key_ipv4, domain)
    print_info(sucessful_ipv4_message)


elif record == "AAAA":
    if len(key) != 16:
        ipv6_key_length_error_message = "Please use 16 bytes key for the IPv6 (AAAA) record"
        print_error(ipv6_key_length_error_message)
        exit()
    
    generating_ipv6_zone_message = "Generating IPv6 (AAAA) DNS record for the domain %s" % domain
    print_info(generating_ipv6_zone_message)
    key_to_use = key_to_hex(key)
    zones = generate_record_ipv6(domain, key_to_use)
    key_ipv6 = key_ipv6_value(key_to_use)
    sucessful_ipv6_message = "Using key %s as AAAA (%s) record for the domain %s" % (key, key_ipv6, domain)
    print_info(sucessful_ipv6_message)


elif record == "TXT":
    
    generating_txt_zone_message = "Generating TXT DNS record for the domain %s" % domain
    print_info(generating_txt_zone_message)
    zones = generate_record_txt(domain, key)
    sucessful_ipv6_message = "Using key %s as TXT (%s) record for the domain %s" % (key, key, domain)
    print_info(sucessful_ipv6_message)

start_dns_server(zones, tcp)