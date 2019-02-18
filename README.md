XMPP Notify Plugin for Icinga 2 (should work with nagios etc.)

# Installation

* Copy xmppnotify.py to /etc/icinga2/scripts/xmppnotify.py
* Copy xmppnotify.sample.cfg to /etc/xmppnotify.cfg and enter xmpp credentials

# Icinga2 configuration

## Templates
    template Notification "xmpp-host-notification" {
      command = "xmpp-host-notification"

      states = [ Up, Down ]
      types = [ Problem, Acknowledgement, Recovery, Custom ]

      period = "24x7"
      interval = 8h

      vars += {
        notification_icingaweb2url = "https://monitoring.finnchristiansen.de/icingaweb2"
      }
    }

    template Notification "xmpp-service-notification" {
      command = "xmpp-service-notification"

      states = [ OK, Warning, Critical, Unknown ]
      types = [ Problem, Acknowledgement, Recovery, Custom ]

      period = "24x7"
      interval = 8h

      vars += {
        notification_icingaweb2url = "https://monitoring.finnchristiansen.de/icingaweb2"
      }
    }

## Commands
    object NotificationCommand "xmpp-host-notification" {
      command = [ SysconfDir + "/icinga2/scripts/xmppnotify.py" ]

      arguments += {
        "-4" = {
          required = true
          value = "$notification_address$"
        }
        "-6" = "$notification_address6$"
        "-b" = "$notification_author$"
        "-c" = "$notification_comment$"
        "-d" = {
          required = true
          value = "$notification_date$"
        }
        "-i" = "$notification_icingaweb2url$"
        "-l" = {
          required = true
          value = "$notification_hostname$"
        }
        "-n" = {
          required = true
          value = "$notification_hostdisplayname$"
        }
        "-o" = {
          required = true
          value = "$notification_hostoutput$"
        }
        "-r" = {
          required = true
          value = "$notification_useremail$"
        }
        "-s" = {
          required = true
          value = "$notification_hoststate$"
        }
        "-t" = {
          required = true
          value = "$notification_type$"
        }
      }

      vars += {
        notification_address = "$address$"
        notification_address6 = "$address6$"
        notification_author = "$notification.author$"
        notification_comment = "$notification.comment$"
        notification_type = "$notification.type$"
        notification_date = "$icinga.long_date_time$"
        notification_hostname = "$host.name$"
        notification_hostdisplayname = "$host.display_name$"
        notification_hostoutput = "$host.output$"
        notification_hoststate = "$host.state$"
        notification_useremail = "$user.vars.xmpp$"
      }
    }

    object NotificationCommand "xmpp-service-notification" {
      command = [ SysconfDir + "/icinga2/scripts/xmppnotify.py" ]

      arguments += {
        "-4" = "$notification_address$"
        "-6" = "$notification_address6$"
        "-b" = "$notification_author$"
        "-c" = "$notification_comment$"
        "-d" = {
          required = true
          value = "$notification_date$"
        }
        "-e" = {
          required = true
          value = "$notification_servicename$"
        }
        "-i" = "$notification_icingaweb2url$"
        "-l" = {
          required = true
          value = "$notification_hostname$"
        }
        "-n" = {
          required = true
          value = "$notification_hostdisplayname$"
        }
        "-o" = {
          required = true
          value = "$notification_serviceoutput$"
        }
        "-r" = {
          required = true
          value = "$notification_useremail$"
        }
        "-s" = {
          required = true
          value = "$notification_servicestate$"
        }
        "-t" = {
          required = true
          value = "$notification_type$"
        }
        "-u" = {
          required = true
          value = "$notification_servicedisplayname$"
        }
      }

      vars += {
        notification_address = "$address$"
        notification_address6 = "$address6$"
        notification_author = "$notification.author$"
        notification_comment = "$notification.comment$"
        notification_type = "$notification.type$"
        notification_date = "$icinga.long_date_time$"
        notification_hostname = "$host.name$"
        notification_hostdisplayname = "$host.display_name$"
        notification_servicename = "$service.name$"
        notification_serviceoutput = "$service.output$"
        notification_servicestate = "$service.state$"
        notification_useremail = "$user.vars.xmpp$"
        notification_servicedisplayname = "$service.display_name$"
      }
    }

## Notifications
    apply Notification "xmpp-icingaadmin" to Host {
      import "xmpp-host-notification"

      user_groups = host.vars.notification.xmpp.groups
      users = host.vars.notification.xmpp.users

      assign where host.vars.notification.xmpp
    }

    apply Notification "xmpp-icingaadmin" to Service {
      import "xmpp-service-notification"

      user_groups = host.vars.notification.xmpp.groups
      users = host.vars.notification.xmpp.users

      assign where host.vars.notification.xmpp
    }

## Users
    object User "icingaadmin" {
      import "generic-user"

      display_name = "Icinga Admin"
      groups = [ "icingaadmins" ]

      email = "foo@example.org"
      vars.xmpp = "bar@example.org"
    }

