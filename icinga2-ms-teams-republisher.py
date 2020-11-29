#!/usr/bin/python3
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

OK_ID = 0
WARNING_ID = 1
CRITICAL_ID = 2
UNKNOWN_ID = 3
SERVICE_STATE_IDS = [OK_ID, WARNING_ID, CRITICAL_ID, UNKNOWN_ID]

OK_COLOR = '#00FF00'
WARNING_COLOR = '#FFA500'
CRITICAL_COLOR = '#FF0000'
UNKNOWN_COLOR = '#800080'
SERVICE_STATE_COLORS = [OK_COLOR, WARNING_COLOR, CRITICAL_COLOR, UNKNOWN_COLOR]

SOFT = 'SOFT'
HARD = 'HARD'
STATE_TYPES = [SOFT, HARD]

UP = 'UP'
DOWN = 'DOWN'
UNREACHABLE = 'UNREACHABLE'
HOST_STATES = [UP, DOWN, UNREACHABLE]

UP_COLOR = '#39FF14'
DOWN_COLOR = '#Bb0000'
UNREACHABLE_COLOR = '#BC13FE'
HOST_STATE_COLORS = [UP_COLOR, DOWN_COLOR, UNREACHABLE_COLOR]

UP_ID = 0
DOWN_ID = 1
UNREACHABLE_ID = 2
HOST_STATE_IDS = [UP_ID, DOWN_ID, UNREACHABLE_ID]

STATE_COLORS = {
    OK: OK_COLOR,
    WARNING: WARNING_COLOR,
    CRITICAL: CRITICAL_COLOR,
    UNKNOWN: UNKNOWN_COLOR,
    UP: UP_COLOR,
    DOWN: DOWN_COLOR,
    UNREACHABLE: UNKNOWN_COLOR
}


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

        # https://www.unicode.org/emoji/charts-beta/full-emoji-list.html#1f525
        self._argp.add_argument('--emoji_problem', help='Markup String for '
                                                        'Icinga2 Transition '
                                                        'type Problem',
                                default='🔥')

        # https://www.unicode.org/emoji/charts-beta/full-emoji-list.html#2705
        self._argp.add_argument('--emoji_recovery', help='Markup String for '
                                                         'Icinga2 transition '
                                                         'type Recovery',
                                default='✅')

        # https://www.unicode.org/emoji/charts-beta/full-emoji-list.html#2755
        self._argp.add_argument('--emoji_custom', help='Markup String for '
                                                       'Icinga2 transition '
                                                       'type Custom',
                                default='❕')
        # https://www.unicode.org/emoji/charts-beta/full-emoji-list.html#26a0
        self._argp.add_argument('--emoji_warning', help='Markup String for '
                                                        'Icinga2 transition '
                                                        'type Warning',
                                default='⚠')

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
        service_parameters.add_argument('--service_state_id', type=int,
                                        choices=SERVICE_STATE_IDS,
                                        help='Icinga2 service.state_id')
        service_parameters.add_argument('--service_state_type',
                                        choices=STATE_TYPES,
                                        help='Icinga2 service.state_type')
        service_parameters.add_argument('--service_check_attempt', type=int,
                                        help='Icinga2 service.check_attempt')
        service_parameters.add_argument('--service_max_check_attempts', type=int,
                                        help='Icinga2 service.max_check_attempts')
        service_parameters.add_argument('--service_last_state',
                                        choices=SERVICE_STATES,
                                        help='Icinga2 service.last_state')
        service_parameters.add_argument('--service_last_state_id', type=int,
                                        choices=SERVICE_STATE_IDS,
                                        help='Icinga2 service.last_state_id')
        service_parameters.add_argument('--service_last_state_type',
                                        choices=STATE_TYPES,
                                        help='Icinga2 service.last_state_type')
        service_parameters.add_argument('--service_last_state_change',
                                        help='Icinga2 service.last_state_change')
        service_parameters.add_argument('--service_downtime_depth', type=int,
                                        help='Icinga2 service.downtime_depth')
        service_parameters.add_argument('--service_duration_sec', type=float,
                                        help='Icinga2 service.duration_sec')
        service_parameters.add_argument('--service_latency', type=float,
                                        help='Icinga2 service.latency')
        service_parameters.add_argument('--service_execution_time', type=float,
                                        help='Icinga2 service.execution_time')
        service_parameters.add_argument('--service_output',
                                        help='Icinga2 service.output')
        service_parameters.add_argument('--service_perfdata',
                                        help='Icinga2 service.perfdata')
        service_parameters.add_argument('--service_last_check', type=int,
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
        host_parameters.add_argument('--host_state_id', type=int,
                                     choices=SERVICE_STATE_IDS,
                                     help='Icinga2 host.state_id')
        host_parameters.add_argument('--host_state_type',
                                     choices=STATE_TYPES,
                                     help='Icinga2 host.state_type')
        host_parameters.add_argument('--host_check_attempt', type=int,
                                     help='Icinga2 host.check_attempt')
        host_parameters.add_argument('--host_max_check_attempts', type=int,
                                     help='Icinga2 host.max_check_attempts')
        host_parameters.add_argument('--host_last_state',
                                     choices=HOST_STATES,
                                     help='Icinga2 host.last_state')
        host_parameters.add_argument('--host_last_state_id', type=int,
                                     choices=SERVICE_STATE_IDS,
                                     help='Icinga2 host.last_state_id')
        host_parameters.add_argument('--host_last_state_type',
                                     choices=STATE_TYPES,
                                     help='Icinga2 host.last_state_type')
        host_parameters.add_argument('--host_last_state_change',
                                     help='Icinga2 host.last_state_change')
        host_parameters.add_argument('--host_downtime_depth', type=int,
                                     help='Icinga2 host.downtime_depth')
        host_parameters.add_argument('--host_duration_sec', type=float,
                                     help='Icinga2 host.duration_sec')
        host_parameters.add_argument('--host_latency', type=float,
                                     help='Icinga2 host.latency')
        host_parameters.add_argument('--host_execution_time', type=float,
                                     help='Icinga2 host.execution_time')
        host_parameters.add_argument('--host_output',
                                     help='Icinga2 host.output')
        host_parameters.add_argument('--host_perfdata',
                                     help='Icinga2 host.perfdata')
        host_parameters.add_argument('--host_last_check', type=int,
                                     help='Icinga2 host.last_check')
        host_parameters.add_argument('--host_check_source',
                                     help='Icinga2 host.check_source')

        host_parameters.add_argument('--host_num_services', type=int,
                                     help='Icinga2 service.num_services')
        host_parameters.add_argument('--host_num_services_ok', type=int,
                                     help='Icinga2 service.num_services_ok')
        host_parameters.add_argument('--host_num_services_warning', type=int,
                                     help='Icinga2 service.num_services_warning')
        host_parameters.add_argument('--host_num_services_unknown', type=int,
                                     help='Icinga2 service.num_services_unknown')
        host_parameters.add_argument('--host_num_services_critical', type=int,
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
        self.message = pymsteams.connectorcard(params.webhook_url)

        _emoji = vars(params)['emoji_{}'.format(params.notification_type.
                                                lower())]
        _notification_type = params.notification_type

        _target_name = f"{params.service_name}" if \
            params.notification_target == SERVICE else params.host_display_name

        # First replace for readablility, second to prevent auto-markdown
        _target_name = _target_name.replace('service_apply_', '').\
            replace('_', '-')

        _state = f"{params.service_state}" if \
            params.notification_target == SERVICE \
            else f"{params.host_state}"

        self.message.text(f"<strong>{params.notification_type}</strong> on Host"
                          f"<strong>{params.host_display_name}</strong>")

        message_sections = [f"{_emoji} {params.notification_target.upper()} "
                            f"<strong>{_target_name}</strong> is "
                            f"{_state.upper()} {_emoji}"]

        self.message.color(STATE_COLORS[_state.upper()])

        for section in message_sections:
            s = pymsteams.cardsection()
            s.text(section)
            self.message.addSection(s)

    def send(self):
        self.message.send()


def main():
    Message(ParamHandler().args).send()


if __name__ == "__main__":
    main()
