#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2020, Kovid Goyal <kovid at kovidgoyal.net>

from typing import TYPE_CHECKING

from kitty.config import parse_marker_spec

from .base import (
    MATCH_WINDOW_OPTION, ArgsType, Boss, MatchError, PayloadGetType,
    PayloadType, RCOptions, RemoteCommand, ResponseType, Window
)

if TYPE_CHECKING:
    from kitty.cli_stub import CreateMarkerRCOptions as CLIOptions


class CreateMarker(RemoteCommand):

    '''
    match: Which window to detach
    self: Boolean indicating whether to detach the window the command is run in
    marker_spec: A list or arguments that define the marker specification, for example: ['text', '1', 'ERROR']
    '''

    short_desc = 'Create a marker that highlights specified text'
    desc = (
        'Create a marker which can highlight text in the specified window. For example: '
        'create_marker text 1 ERROR. For full details see: https://sw.kovidgoyal.net/kitty/marks.html'
    )
    options_spec = MATCH_WINDOW_OPTION + '''\n
--self
type=bool-set
If specified apply marker to the window this command is run in, rather than the active window.
'''
    argspec = 'MARKER SPECIFICATION'

    def message_to_kitty(self, global_opts: RCOptions, opts: 'CLIOptions', args: ArgsType) -> PayloadType:
        if len(args) < 2:
            self.fatal('Invalid marker specification: {}'.format(' '.join(args)))
        parse_marker_spec(args[0], args[1:])
        return {'match': opts.match, 'self': opts.self, 'marker_spec': args}

    def response_from_kitty(self, boss: 'Boss', window: 'Window', payload_get: PayloadGetType) -> ResponseType:
        match = payload_get('match')
        if match:
            windows = tuple(boss.match_windows(match))
            if not windows:
                raise MatchError(match)
        else:
            windows = [window if window and payload_get('self') else boss.active_window]
        args = payload_get('marker_spec')

        for window in windows:
            window.set_marker(args)


create_marker = CreateMarker()