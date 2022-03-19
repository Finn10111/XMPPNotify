#!/usr/bin/env python3

from pprint import pprint
from xmppnotify import build_argparser, build_message


commonargs = \
    ["--hostname", "HOSTNAME",
     "--hostdisplayname", "HOSTDISPLAYNAME",
     "-o", "outputline1\noutputline2",
     "--hostaddress", "127.0.0.1",
     "--hostaddress6", "::1",
     "--icingaweb2url", "ICINGAWEB2URL",
     "--state", "STATE", "--longdatetime", "2019-12-31 23:59:59",
     "--jid", "recipient@exmaple.net"]

if __name__ == '__main__':
    parser = build_argparser()

    args = parser.parse_args(commonargs +
                             ["--notificationtype", "PROBLEM",
                              "-e", "servicename",
                              "--servicedisplayname", "servicedisplayname"])
    pprint(build_message(args))

    args = parser.parse_args(commonargs +
                             ["--notificationtype", "RECOVERY",
                              "--notificationauthorname",
                              "NOTIFICATIONAUTHORNAME",
                              "--notificationcomment",
                              "NOTIFICATIONCOMMENT\nMORE COMMENTS"])
    pprint(build_message(args))
