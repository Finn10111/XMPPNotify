#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pip3 install dnspython

import argparse
import configparser
from slixmpp import ClientXMPP
from socket import gethostname

class XMPPNotify(ClientXMPP):
    def __init__(self, jid, password, nick, recipient, msg):
        ClientXMPP.__init__(self, jid, password)
        self.recipient = recipient
        self.msg = msg
        self.nick = nick
        self.add_event_handler("session_start", self.session_start)
        # self.add_event_handler("message", self.message)

    async def session_start(self, event):
        self.send_presence()
        await self.get_roster()

        recipient_type = "account"
        try:
            info = await self['xep_0030'].get_info(jid=self.recipient)
            disco_info=info['disco_info']
            if disco_info:
                for category, typ, _, name in disco_info['identities']:
                    if category == "conference":
                        recipient_type = "muc"
                        break
        except:
            # Some servers do not support Service Discovery (XEP-0030)
            # Assume they don't support MUCs (XEP-0045) as well
            pass

        if recipient_type == "muc":
            await self.plugin['xep_0045'].join_muc_wait(self.recipient, self.nick)
            self.send_message(mto=self.recipient, mbody=self.msg, mtype='groupchat')
        else:
            self.send_message(mto=self.recipient, mbody=self.msg, mtype='chat')

        self.disconnect()

    def message(self, msg):
        pass


def build_message(args):
    # Prefix all output lines by "> "
    if args.output:
        output = "> " + args.output.replace("\n", "\n> ")
    else:
        output = ""

    if args.servicename:
        # service
        message = """[{notificationtype}] {servicedisplayname} on {hostdisplayname} is {servicestate}!
{output}
When: {longdatetime}
Ref: {hostname}!{servicename}
Monitoring host: {monitoringhostname}\
""".format(
            notificationtype=args.notificationtype,
            monitoringhostname=gethostname(),
            servicedisplayname=args.servicedisplayname,
            hostdisplayname=args.hostdisplayname,
            servicestate=args.state,
            output=output,
            longdatetime=args.longdatetime,
            servicename=args.servicename,
            hostname=args.hostname
        )
    else:
        message = """[{notificationtype}] {hostdisplayname} is {hoststate}!
{output}
When: {longdatetime}
Ref: {hostname}
Monitoring host: {monitoringhostname}\
""".format(
            notificationtype=args.notificationtype,
            monitoringhostname=gethostname(),
            hostdisplayname=args.hostdisplayname,
            hoststate=args.state,
            output=output,
            longdatetime=args.longdatetime,
            hostname=args.hostname
        )

    if args.hostaddress:
        message += "\nIPv4: {}".format(args.hostaddress)

    if args.hostaddress6:
        message += "\nIPv6: {}".format(args.hostaddress6)

    if args.notificationcomment:
        # Prefix comment lines by "> "
        comment = "> " + args.notificationcomment.replace("\n", "\n> ")
        message += """\n
Comment by {notificationauthorname}
{comment}
""".format(
            notificationauthorname=args.notificationauthorname,
            comment=comment
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


def build_argparser():
    parser = argparse.ArgumentParser(description='XMPP Notifications')

    # General config
    parser.add_argument('-C', '--config', dest='configfile',
                        default='/etc/xmppnotify.cfg',
                        help='Account configuration file (%(default)s)')

    # required
    parser.add_argument('-d', '--longdatetime')
    parser.add_argument('-e', '--servicename')  # service only
    parser.add_argument('-l', '--hostname')
    parser.add_argument('-n', '--hostdisplayname')
    parser.add_argument('-o', '--output')  # host or service output
    parser.add_argument('-s', '--state')  # host or service state
    parser.add_argument('-u', '--servicedisplayname')  # service only
    parser.add_argument('-t', '--notificationtype')

    # optional
    parser.add_argument('-4', '--hostaddress')
    parser.add_argument('-6', '--hostaddress6')
    parser.add_argument('-b', '--notificationauthorname')
    parser.add_argument('-c', '--notificationcomment')
    parser.add_argument('-i', '--icingaweb2url')

    parser.add_argument('-r', '--jid', required=True,
                        help="Target JID")

    return parser


if __name__ == '__main__':
    parser = build_argparser()
    args = parser.parse_args()

    config = configparser.RawConfigParser()
    config.read(args.configfile)
    jid = config.get('Account', 'jid')
    password = config.get('Account', 'password')
    nick = config.get('Account', 'nick', fallback = jid.split("@")[0])

    message = build_message(args)

    xmpp = XMPPNotify(jid, password, nick, args.jid, message)
    xmpp.register_plugin('xep_0030')  # Service Discovery
    xmpp.register_plugin('xep_0004')  # Data Forms
    xmpp.register_plugin('xep_0045')  # MUC
    xmpp.register_plugin('xep_0060')  # PubSub
    xmpp.register_plugin('xep_0199')  # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    xmpp.process(forever=False)
