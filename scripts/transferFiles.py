#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import traceback
from ftplib import FTP_TLS, error_perm

def download(src,dst):
    try:
        with open(dst, 'wb') as local_file:
            ftp.retrbinary('RETR ' + src, local_file.write)
        print("SUCCESS")
        sys.exit(0)
    except error_perm:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

def upload(src,dst):
    try:
        with open(src, 'rb') as local_file:
            ftp.storbinary('STOR ' + dst, local_file)
        print("SUCCESS")
        sys.exit(0)
    except error_perm:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("launch",choices=["get_input","get_after_cut","send_proteasome","send_HLA","send_TAP"])
    parser.add_argument("uuid")
    parser.add_argument("server_ip", type=str)
    parser.add_argument("server_user",type=str)
    parser.add_argument("server_passwd",type=str)
    args = parser.parse_args()
    try:
        with FTP_TLS(host=args.server_ip, user=args.server_user, passwd=args.server_passwd) as ftp:
            ftp.prot_p()
            ftp.cwd("angel_userdata")
            if args.launch == "get_input":
                download(args.uuid + ".csv", fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}.csv")
            elif args.launch == "get_after_cut":
                download(args.uuid + "_cutted.csv", fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}_cutted.csv")
            elif args.launch == "send_proteasome":
                upload(fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}_Proteasome_result.csv",f"{args.uuid}_Proteasome.csv")
            elif args.launch == "send_TAP":
                upload(fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}_TAP.csv",f"{args.uuid}_TAP.csv")
            elif args.launch == "send_HLA":
                upload(fr"C:\Users\SmirnygaTotoshka\Desktop\diplom\angel_userdata\{args.uuid}\{args.uuid}_HLA.csv",f"{args.uuid}_HLA.csv")
            else:
                raise Exception("Wrong transfer mode")
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(2)
