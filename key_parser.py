# -*- coding: utf-8 -*-

import re

from datetime import date
from io import StringIO

from models import Key, Signature

key_start_regex = re.compile(r'^pub +([a-y0-9]+) (\d{4})-(\d{2})-(\d{2}) \[([A-Z]+)\] (\[expires: (\d{4})-(\d{2})-(\d{2})\])?$')
key_fingerprint_regex = re.compile(r'^ +([A-Z0-9]{40}) *$')
uid_regex = re.compile(r'^uid +\[ +[a-z]+ +\] ([\w| ]+) (\([\w| ]+\))? ?<([a-z0-9\.@-_]+)>$')
sig_regex = re.compile(r'^sig .*([A-Z0-9]{16}) (\d{4})-(\d{2})-(\d{2})  (.*)$')
sig_userid_regex = re.compile(r'^([\w| ]+) (\([\w| ]+\))? ?<([a-z0-9\.@-_]+)>$')

class KeyParser:
    def __init__(self, session):
        self.session = session

    def __parse_key_sigs(self, buf, key):
        sigs = []

        sig_match = sig_regex.match(buf.readline())

        while sig_match:
            signer_key = sig_match.group(1)
            sign_date = date(
                int(sig_match.group(2)), 
                int(sig_match.group(3)),
                int(sig_match.group(4))
            )

            # Skip self signatures
            if signer_key != key.fingerprint[-16:]:
                sig_userid_match = sig_userid_regex.match(sig_match.group(5))

                if not sig_userid_match:
                    signer_name = None
                    signer_email = None
                else:
                    signer_name = sig_userid_match.group(1)
                    signer_email = sig_userid_match.group(3)

                sigs.append(Signature(
                    signer_key=signer_key,
                    sign_date=sign_date,
                    signer_name=signer_name,
                    signer_email=signer_email
                ))

            sig_match = sig_regex.match(buf.readline())

        return sigs

    def __parse_key(self, buf, algo, created, usage, expiry):
        fingerprint_match = key_fingerprint_regex.match(buf.readline())

        if not fingerprint_match:
            return None

        fingerprint = fingerprint_match.group(1)

        uid_match = uid_regex.match(buf.readline())

        if not uid_match:
            return None

        name = uid_match.group(1)
        desc = uid_match.group(2)
        email = uid_match.group(3)

        key = Key(
            fingerprint=fingerprint,
            algo=algo,
            created=created,
            usage=usage,
            expiry=expiry,
            email=email,
            name=name,
            description=desc
        )

        return key

    def parse_and_store(self, raw_string):
        buf = StringIO(raw_string)

        line = buf.readline()
        while line:
            key_match = key_start_regex.match(line)

            if key_match:
                algo = key_match.group(1)
                created = date(
                    int(key_match.group(2)), 
                    int(key_match.group(3)),
                    int(key_match.group(4))
                )
                usage = key_match.group(5)
                if key_match.group(6):
                    expiry = date(
                        int(key_match.group(7)), 
                        int(key_match.group(8)),
                        int(key_match.group(9))
                    )
                else:
                    expiry = None

                key = self.__parse_key(buf, algo, created, usage, expiry)

                if key is not None:
                    self.session.add(key)
                    self.session.flush()

                    key.sigs = self.__parse_key_sigs(buf, key)

            line = buf.readline()

        self.session.commit()
