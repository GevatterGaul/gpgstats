#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
from subprocess import Popen, PIPE

from models import init_db, Key, Signature
from output import HTMLOutput


from key_parser import KeyParser


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate statistics over your gnupg keyring')
    parser.add_argument('-R', '--no-refresh', help='Do not regenerate the key db', action='store_true', default=False)
    parser.add_argument('-p', '--print-keys', help='Print available keys', action='store_true', default=False)
    parser.add_argument('-c', '--ca-key', help='Infos for a CA key', action='store', default=None)
    parser.add_argument('-d', '--domain', help='Domain to get statistics for', action='store', default=None)

    args = parser.parse_args()

    session = init_db()

    if not args.no_refresh:
        list_sig_command = [
            'gpg',
            '--list-sigs'
        ]

        list_sig_out = Popen(list_sig_command, stdout=PIPE)

        kp = KeyParser(session)
        kp.parse_and_store(list_sig_out.stdout.read().decode('utf-8'))

    if args.print_keys:
        keys = session.query(Key).all()
        num_sigs = session.query(Signature).count()

        for key in keys:
            print(key)
            for sig in key.sigs:
                print(sig)
            print()

        print('{} keys and {} sigs parsed'.format(len(keys), num_sigs))

    output = HTMLOutput(session, ca_key=args.ca_key, domain=args.domain)
    output.gen_html()


'B273EB75CADE64DC'
