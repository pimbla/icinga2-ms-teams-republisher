#!/usr/bin/python3
import argparse
import logging
import pymsteams
from pathlib import Path

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
        self._argp.add_argument('--icinga2_url', help='Icinga2 base URL. E.g.:'
                                                      'https://icinga2.XYZ.TLD')
        self._argp.add_argument('--grafana_url', help='Icinga2 base URL. E.g.:'
                                                      'https://grafana.XYZ.TLD')
        self._argp.add_argument('--icingaweb_graph_ini_path', help='Path to the '
                                                      'file containing the '
                                                      'Icingaweb2 Graph config')
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
                                        help='Icinga2 service.name',
                                        required=True)
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
        service_parameters.add_argument('--service_check_command',
                                        help='Icinga2 service.check_command')

        # Available host runtime macros. Will be autofilled by Icinga2.
        # see https://icinga.com/docs/icinga2/latest/doc/03-monitoring-basics/#host-runtime-macros
        host_parameters.add_argument('--host_name',
                                     help='Icinga2 host.name',
                                     required=True)
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
                                     help='Icinga2 host.num_services')
        host_parameters.add_argument('--host_num_services_ok', type=int,
                                     help='Icinga2 service.num_services_ok')
        host_parameters.add_argument('--host_num_services_warning', type=int,
                                     help='Icinga2 service.num_services_warning')
        host_parameters.add_argument('--host_num_services_unknown', type=int,
                                     help='Icinga2 service.num_services_unknown')
        host_parameters.add_argument('--host_num_services_critical', type=int,
                                     help='Icinga2 service.num_services_critical')
        service_parameters.add_argument('--host_check_command',
                                        help='Icinga2 host.check_command')

        self.args = self._argp.parse_args()

        if self.args.verbosity == 3:
            logging.basicConfig(level=logging.DEBUG)
        if self.args.verbosity == 2:
            logging.basicConfig(level=logging.INFO)
        if self.args.verbosity == 1:
            logging.basicConfig(level=logging.WARNING)
        if self.args.verbosity == 0:
            logging.basicConfig(level=logging.CRITICAL)


class GrafanaHandler(object):
    '''
    [check_command_toru_disk]
    dashboard = "toru-overview"
    panelId = "12"

    '''
    def __init__(self, grafana_base_url, fp_graph_ini, host_name,
                 service_name, target_command, time=1):

        self._host_name = host_name
        self._service_name = service_name
        self._graph_identifier = {}
        self._grafana_base_url = grafana_base_url
        self._target_command = target_command
        self._time = time

        if Path(fp_graph_ini).is_file():
            with open(fp_graph_ini, 'r') as f:
                new_block = False
                for line in f:
                    line = line.strip()
                    if new_block:
                        if line.startswith('[') & line.endswith(']'):
                            command = line[1:-1]
                            dashboard = next(f).split(' = ')[1].strip().\
                                replace("\"", '')
                            panel_id = next(f).split(' = ')[1].strip().\
                                replace("\"", '')
                            self._graph_identifier[command] = \
                                (dashboard, panel_id)
                    if not line:
                        new_block = True
                        continue
                    new_block = False

    def get_url(self):
        try:
            dashboard, panel_id = self._graph_identifier[self._target_command]
        except KeyError:
            raise KeyError
        return f"{self._grafana_base_url}/dashboard/db/{dashboard}" \
               f"?var-hostname={self._host_name}" \
               f"&var-service=self._service_name" \
               f"&from=now-{self._time}h" \
               f"&to=now&panelId={panel_id}" \
               f"&fullscreen"


class Message(object):

    def __init__(self, params):
        self.message = pymsteams.connectorcard(params.webhook_url)

        _emoji = vars(params)['emoji_{}'.format(params.notification_type.
                                                lower())]

        _target_name = f"{params.service_name}" if \
            params.notification_target == SERVICE else params.host_display_name
        # First replace for readablility, second to prevent auto-markdown
        _target_name = _target_name.replace('service_apply_', '').\
            replace('_', '-')

        _command = params.service_check_command if \
            params.notification_target == SERVICE \
            else params.host_check_command

        _state = f"{params.service_state}" if \
            params.notification_target == SERVICE \
            else f"{params.host_state}"
        
        _output = f"{params.service_output}" if \
            params.notification_target == SERVICE \
            else f"{params.host_output}"
        _output = (_output[:95] + ' [...]') if len(_output) > 95 else _output

        self.message.text(f"<strong>{params.notification_type}</strong> "
                          f"on Host "
                          f"<strong>{params.host_display_name}</strong>")

        message_sections = [f"<strong>{params.notification_target.title()} "
                            f"Name</strong>:  "
                            f"{_target_name}\n\n"
                            f"<strong>{params.notification_target.title()} "
                            f"State</strong>:   "
                            f"{_emoji} {_state.upper()} {_emoji}\n\n"
                            f"<strong>{params.notification_target.title()} "
                            f"Output</strong>: "
                            f"{_output}"]

        if params.icinga2_url:
            _icinga2_url = f"{params.icinga2_url}/monitoring/host/"
            _icinga2_url += f"services?host={params.host_name}" \
                            f"&service={params.service_name}" if \
                            params.notification_target == SERVICE \
                            else f"show?host={params.host_name}"
            self.message.addLinkButton("Icinga2", _icinga2_url)

        if params.grafana_url:
            grafana_handler = GrafanaHandler(params.grafana_url,
                                             params.icingaweb_graph_ini_path,
                                             params.host_name,
                                             params.service_name,
                                             _command)
            try:
                self.message.addLinkButton("Grafana", grafana_handler.get_url())
            except KeyError as e:
                logging.critical(str(e))
            
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
