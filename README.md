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

* Copy `commands-xmppnotify.conf` to `/etc/icinga2/conf.d/`.


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

