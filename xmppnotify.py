#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pip3 install dnspython

import argparse
import configparser
from slixmpp import ClientXMPP
from socket import gethostname


class XMPPNotify(ClientXMPP):
    def __init__(self, jid, password, recipient, msg):
        ClientXMPP.__init__(self, jid, password)
        self.recipient = recipient
        self.msg = msg
        self.add_event_handler("session_start", self.session_start)
        # self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.send_message(mto=self.recipient, mbody=self.msg)
        self.disconnect()

    def message(self, msg):
        pass


def build_message(args):
    if args.servicename:
        # service
        message = """***** Service Monitoring on {monitoringhostname} *****

{servicedisplayname} on {hostdisplayname} is {servicestate}!

Info:    {serviceoutput}

When:    {longdatetime}
Service: {servicename}
Host:    {hostname}
""".format(
            monitoringhostname=gethostname(),
            servicedisplayname=args.servicedisplayname,
            hostdisplayname=args.hostdisplayname,
            servicestate=args.state,
            serviceoutput=args.output,
            longdatetime=args.longdatetime,
            servicename=args.servicename,
            hostname=args.hostname
        )
    else:
        message = """***** Host Monitoring on {monitoringhostname} *****

{hostdisplayname} is {hoststate}!

Info:    {hostoutput}

When:    {longdatetime}
Host:    {hostname}
""".format(
            monitoringhostname=gethostname(),
            hostdisplayname=args.hostdisplayname,
            hoststate=args.state,
            hostoutput=args.output,
            longdatetime=args.longdatetime,
            hostname=args.hostname
        )

    if args.hostaddress:
        message += "\nIPv4:    {}".format(args.hostaddress)

    if args.hostaddress6:
        message += "\nIPv6:    {}".format(args.hostaddress6)

    if args.notificationcomment:
        message += """
        \nComment by {notificationauthorname}
 {notificationcomment}
""".format(
            notificationauthorname=args.notificationauthorname,
            notificationcomment=args.notificationcomment
        )

    if args.icingaweb2url and args.servicename:
        message += "\n" + args.icingaweb2url + \
            "/monitoring/service/show?host={hostname}&service={servicename}" \
            .format(
                hostname=args.hostname,
                servicename=args.servicename
            )
    elif args.icingaweb2url:
        message += "\n" + args.icingaweb2url + \
            "/monitoring/host/show?host={hostname}" \
            .format(
                hostname=args.hostname,
            )

    return message


if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('/etc/xmppnotify.cfg')
    jid = config.get('Account', 'jid')
    password = config.get('Account', 'password')

    parser = argparse.ArgumentParser(description='XMPP Notifications')
    # required
    parser.add_argument('-d', '--longdatetime')
    parser.add_argument('-e', '--servicename')  # service only
    parser.add_argument('-l', '--hostname')
    parser.add_argument('-n', '--hostdisplayname')
    parser.add_argument('-o', '--output')  # host or service output
    parser.add_argument('-r', '--jid')
    parser.add_argument('-s', '--state')  # host or service state
    parser.add_argument('-u', '--servicedisplayname')  # service only
    parser.add_argument('-t', '--notificationtype')

    # optional
    parser.add_argument('-4', '--hostaddress')
    parser.add_argument('-6', '--hostaddress6')
    parser.add_argument('-b', '--notificationauthorname')
    parser.add_argument('-c', '--notificationcomment')
    parser.add_argument('-i', '--icingaweb2url')

    args = parser.parse_args()
    message = build_message(args)

    xmpp = XMPPNotify(jid, password, args.jid, message)
    xmpp.register_plugin('xep_0030')  # Service Discovery
    xmpp.register_plugin('xep_0004')  # Data Forms
    xmpp.register_plugin('xep_0060')  # PubSub
    xmpp.register_plugin('xep_0199')  # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    xmpp.process(forever=False)
