#!/bin/python3
import argparse
import logging
import pymsteams

HOST = 'host'
SERVICE = 'service'

OK = 'OK'
WARNING = 'WARNING'
CRITICAL = 'CRITICAL'
UNKNOWN = 'UNKNOWN'
SERVICE_STATES = [OK, WARNING, CRITICAL, UNKNOWN]

OK_ID = 1
WARNING_ID = 2
CRITICAL_ID = 3
UNKNOWN_ID = 4
SERVICE_STATE_IDS = [OK_ID, WARNING_ID, CRITICAL_ID, UNKNOWN_ID]

SOFT = 'SOFT'
HARD = 'HARD'
STATE_TYPES = [SOFT, HARD]

UP = 'UP'
DOWN = 'DOWN'
UNREACHABLE = 'UNREACHABLE'
HOST_STATES = [UP, DOWN, UNREACHABLE]

UP_ID = 0
DOWN_ID = 1
UNREACHABLE_ID = 2
HOST_STATE_IDS = [UP_ID, DOWN_ID, UNREACHABLE_ID]


class ParamHandler(object):

    def __init__(self):
        self._argp = argparse.ArgumentParser(description='M$ Teams Chat Bot')
        host_parameters = self._argp.add_argument_group('Icinga2 Host '
                                                        'Parameters')
        service_parameters = self._argp.add_argument_group('Icinga2 Service '
                                                           'Parameters')

        self._argp.add_argument('-v', '--verbosity', action='count', default=0)
        self._argp.add_argument('--webhook_url', help='Incoming webhook URL',
                                required=True)
        self._argp.add_argument('--notification_target',
                                choices=[HOST, SERVICE],
                                required=True)

        # unicode directly copied from link below:
        # https://www.unicode.org/emoji/charts-beta/full-emoji-list.html#1f525
        self._argp.add_argument('--emoji_problem', help='Markup String for '
                                                        'Icinga2 Transition '
                                                        'type Problem',
                                default='🔥')

        # unicode directly copied from link below:
        # https://www.unicode.org/emoji/charts-beta/full-emoji-list.html#2705
        self._argp.add_argument('--emoji_recovery', help='Markup String for '
                                                         'Icinga2 transition '
                                                         'type Recovery',
                                default='✅')
        self._argp.add_argument('--emoji_custom', help='Markup String for '
                                                       'Icinga2 transition '
                                                       'type Custom',
                                default='❕')

        self._argp.add_argument('--notification_type',
                                help='Icinga2 notification.type')
        self._argp.add_argument('--notification_author',
                                help='Icinga2 notification.author')
        self._argp.add_argument('--notification_comment',
                                help='Icinga2 notification.comment')

        # Available service runtime macros. Will be autofilled by Icinga2.
        # see https://icinga.com/docs/icinga2/latest/doc/03-monitoring-basics/#service-runtime-macros
        service_parameters.add_argument('--service_name',
                                        help='Icinga2 service.name')
        service_parameters.add_argument('--service_display_name',
                                        help='Icinga2 service.display_name')
        service_parameters.add_argument('--service_state',
                                        choices=SERVICE_STATES,
                                        help='Icinga2 service.state.')
        service_parameters.add_argument('--service_state_id',
                                        choices=SERVICE_STATE_IDS,
                                        help='Icinga2 service.state_id')
        service_parameters.add_argument('--service_state_type',
                                        choices=STATE_TYPES,
                                        help='Icinga2 service.state_type')
        service_parameters.add_argument('--service_check_attempt',
                                        help='Icinga2 service.check_attempt')
        service_parameters.add_argument('--service_max_check_attempts',
                                        help='Icinga2 service.max_check_attempts')
        service_parameters.add_argument('--service_last_state',
                                        choices=SERVICE_STATES,
                                        help='Icinga2 service.last_state')
        service_parameters.add_argument('--service_last_state_id',
                                        choices=SERVICE_STATE_IDS,
                                        help='Icinga2 service.last_state_id')
        service_parameters.add_argument('--service_last_state_type',
                                        choices=STATE_TYPES,
                                        help='Icinga2 service.last_state_type')
        service_parameters.add_argument('--service_last_state_change',
                                        help='Icinga2 service.last_state_change')
        service_parameters.add_argument('--service_downtime_depth',
                                        help='Icinga2 service.downtime_depth')
        service_parameters.add_argument('--service_duration_sec',
                                        help='Icinga2 service.duration_sec')
        service_parameters.add_argument('--service_latency',
                                        help='Icinga2 service.latency')
        service_parameters.add_argument('--service_execution_time',
                                        help='Icinga2 service.execution_time')
        service_parameters.add_argument('--service_output',
                                        help='Icinga2 service.output')
        service_parameters.add_argument('--service_perfdata',
                                        help='Icinga2 service.perfdata')
        service_parameters.add_argument('--service_last_check',
                                        help='Icinga2 service.last_check')
        service_parameters.add_argument('--service_check_source',
                                        help='Icinga2 service.check_source')

        # Available host runtime macros. Will be autofilled by Icinga2.
        # see https://icinga.com/docs/icinga2/latest/doc/03-monitoring-basics/#host-runtime-macros
        host_parameters.add_argument('--host_name',
                                     help='Icinga2 host.name')
        host_parameters.add_argument('--host_display_name',
                                     help='Icinga2 host.display_name')
        host_parameters.add_argument('--host_state',
                                     choices=HOST_STATES,
                                     help='Icinga2 host.state.')
        host_parameters.add_argument('--host_state_id',
                                     choices=SERVICE_STATE_IDS,
                                     help='Icinga2 host.state_id')
        host_parameters.add_argument('--host_state_type',
                                     choices=STATE_TYPES,
                                     help='Icinga2 host.state_type')
        host_parameters.add_argument('--host_check_attempt',
                                     help='Icinga2 host.check_attempt')
        host_parameters.add_argument('--host_max_check_attempts',
                                     help='Icinga2 host.max_check_attempts')
        host_parameters.add_argument('--host_last_state',
                                     choices=HOST_STATES,
                                     help='Icinga2 host.last_state')
        host_parameters.add_argument('--host_last_state_id',
                                     choices=SERVICE_STATE_IDS,
                                     help='Icinga2 host.last_state_id')
        host_parameters.add_argument('--host_last_state_type',
                                     choices=STATE_TYPES,
                                     help='Icinga2 host.last_state_type')
        host_parameters.add_argument('--host_last_state_change',
                                     help='Icinga2 host.last_state_change')
        host_parameters.add_argument('--host_downtime_depth',
                                     help='Icinga2 host.downtime_depth')
        host_parameters.add_argument('--host_duration_sec',
                                     help='Icinga2 host.duration_sec')
        host_parameters.add_argument('--host_latency',
                                     help='Icinga2 host.latency')
        host_parameters.add_argument('--host_execution_time',
                                     help='Icinga2 host.execution_time')
        host_parameters.add_argument('--host_output',
                                     help='Icinga2 host.output')
        host_parameters.add_argument('--host_perfdata',
                                     help='Icinga2 host.perfdata')
        host_parameters.add_argument('--host_last_check',
                                     help='Icinga2 host.last_check')
        host_parameters.add_argument('--host_check_source',
                                     help='Icinga2 host.check_source')

        host_parameters.add_argument('--host_num_services',
                                     help='Icinga2 service.num_services')
        host_parameters.add_argument('--host_num_services_ok',
                                     help='Icinga2 service.num_services_ok')
        host_parameters.add_argument('--host_num_services_warning',
                                     help='Icinga2 service.num_services_warning')
        host_parameters.add_argument('--host_num_services_unknown',
                                     help='Icinga2 service.num_services_unknown')
        host_parameters.add_argument('--host_num_services_critical',
                                     help='Icinga2 service.num_services_critical')

        self.args = self._argp.parse_args()

        if self.args.verbosity == 3:
            logging.basicConfig(level=logging.DEBUG)
        if self.args.verbosity == 2:
            logging.basicConfig(level=logging.INFO)
        if self.args.verbosity == 1:
            logging.basicConfig(level=logging.WARNING)
        if self.args.verbosity == 0:
            logging.basicConfig(level=logging.CRITICAL)


class Message(object):
    '''
    <EMOJI> <NOTIFICATION TYPE>: <HOSTNAME> [<SERVICENAME>] is [<SERVICE-STATE> | <HOST-STATE>]
    [BUTTON-ICINGA], [BUTTON-GRAFANA]
        [OPTIONAL]
        > Various Metrics
    '''

    def __init__(self, params):
        emoji = vars(params)['emoji_{}'.format(params.notification_type)]
        service_name = f"{params.service_name} " if \
            params.notification_target == SERVICE else ''
        state = f"{params.service_state} " if \
            params.notification_target == SERVICE \
            else f"{params.host_state} "

        message = pymsteams.connectorcard(params.webhook_url)
        message.title(f"{emoji} {params.notification_type}: "
                      f"{params.host_display_name} {service_name} is {state}")

        message.text("🔥TODO")
        message.send()


def main():
    params = ParamHandler().args
    Message(params)


if __name__ == "__main__":
    main()