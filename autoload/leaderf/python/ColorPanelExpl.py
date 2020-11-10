#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
import re
from ColorPanelInstance import ColorPanelInstance
from ColorPanelUtils import *
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


#*****************************************************
# ColorPanelExplorer
#*****************************************************
class ColorPanelExplorer(Explorer):
    def __init__(self):
        self._self_type = "ColorPanel"

    def getContent(self, *args, **kwargs):
        arguments = kwargs.get("arguments", {})
        rows, cols = get_size(arguments)
        string = lfEval("get(g:, 'Lf_ColorPanel_str', 'xxx')")
        string = arguments.get("--str", [string])[0]
        content = []
        n = 0
        for i in range(rows):
            line = []
            for j in range(cols):
                line.append('{:>3} {}'.format(n, string))
                n += 1
                if n == 256:
                    break
            content.append(' '.join(line))
            if n == 256:
                break
        return content

    def getStlCategory(self):
        return "ColorPanel"

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))


#*****************************************************
# ColorPanelExplManager
#*****************************************************
class ColorPanelExplManager(Manager):
    def __init__(self):
        super(ColorPanelExplManager, self).__init__()

    def _getExplClass(self):
        return ColorPanelExplorer

    def _getInstance(self):
        if self._instance is None:
            self._instance = ColorPanelInstance(
                    self,
                    self._getExplorer().getStlCategory(),
                    self._cli,
                    self._beforeEnter,
                    self._afterEnter,
                    self._beforeExit,
                    self._afterExit)
        return self._instance

    def _search(self, content, is_continue=False, step=0):
        self._result_content = self._content

    def _is_popup(self):
        return ("--popup" in self._arguments or lfEval("g:Lf_WindowPosition") == 'popup') \
                and "--bottom" not in self._arguments

    def _set_attributes(self):
        if self._is_popup():
            winid = self._getInstance().getPopupWinId()
            bufnr = lfEval("winbufnr(%d)" % winid)
            if lfEval("has('nvim')") == '1':
                lfCmd("call nvim_win_set_option(%d, 'number', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'cursorline', v:false)" % winid)
            else:
                lfCmd("call win_execute(%d, 'setlocal nonu')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nocursorline')" % winid)
        else:
            if lfEval("has('nvim')") == '1':
                lfCmd("call nvim_buf_set_option(%s, 'number', v:false)" % bufnr)
                lfCmd("call nvim_buf_set_option(%s, 'cursorline', v:false)" % bufnr)
            else:
                lfCmd("setlocal nonu")
                lfCmd("setlocal nocursorline")

    def startExplorer(self, win_pos, *args, **kwargs):
        self._current_mode = 'INPUT'
        self.show_bg = False
        self._cli._is_full_path = False
        arguments = kwargs.get("arguments", {})
        if ("--bottom" in arguments
                or "--top" in arguments
                or lfEval("g:Lf_WindowPosition") == 'bottom'
                or lfEval("g:Lf_WindowPosition") == 'top'):
            rows, cols = get_size(arguments)
            self._getInstance()._win_height = rows - 2 # 2 is input window height in popup
        super(ColorPanelExplManager, self).startExplorer(win_pos, *args, **kwargs)

    def _set_text_prop(self, color=None):
        rows, cols = get_size(self._arguments)
        winid = self._getInstance().getPopupWinId()
        lfCmd("highlight clear Lf_hl_cursorline")
        lfCmd("call prop_clear(1, 16, {'bufnr': winbufnr(%d)})" % (winid))
        for i in range(256):
            if self.show_bg:
                c = i if color is None else color
                lfCmd("highlight! CtermColor%d ctermfg=%d ctermbg=%d" % (i, c, i))
            else:
                bg = 'bg'
                if color is None and self._is_popup() and int(lfEval("hlexists('Lf_hl_popup_window')")):
                    popup_hl = lfEval("execute('highlight Lf_hl_popup_window')")
                    match = re.search(r'(?<=ctermbg\=)\w+', popup_hl)
                    if match is not None:
                        bg = match.group(0)
                c = bg if color is None else str(color)
                lfCmd("highlight! CtermColor%d ctermbg=%s ctermfg=%d" % (i, c, i))
            lfCmd("call prop_type_delete('CtermColor%d', {'bufnr': winbufnr(%d)})" % (i, winid))
            lfCmd("call prop_type_add('CtermColor%d', {'bufnr': winbufnr(%d), 'highlight': 'CtermColor%d'})"
                    % (i, winid, i))
        n = 0
        string = lfEval("get(g:, 'Lf_ColorPanel_str', 'xxx')")
        string = self._arguments.get("--str", [string])[0]
        col_len = 4 + len(string) + 1
        for i in range(rows):
            for j in range(cols):
                lfCmd("call prop_add(%d, %d, {'length': %d, 'bufnr': winbufnr(%d), 'type': 'CtermColor%d'})"
                        % (i + 1, j * col_len + 5, len(string), winid, n))
                n += 1
                if n == 256:
                    break
            if n == 256:
                break

    def _setStlMode(self, **kwargs):
        mode = 'Background' if self.show_bg else 'Forground'
        self._getInstance().setStlMode(mode)
        self._getInstance().setPopupStl(self._current_mode)

    def input(self):
        self._preview_open = False
        self._getInstance().hideMimicCursor()
        if self._getInstance().getWinPos() in ('popup', 'floatwin'):
            self._cli.buildPopupPrompt()
            lfCmd("call leaderf#colorscheme#popup#hiMode('%s', '%s')" % (self._getExplorer().getStlCategory(), self._current_mode))
            self._getInstance().setPopupStl(self._current_mode)

        if self._getInstance().getWinPos() == 'popup':
            lfCmd("call leaderf#ResetPopupOptions(%d, 'filter', '%s')"
                    % (self._getInstance().getPopupWinId(), 'leaderf#PopupFilter'))

        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None

        self._hideHelp()
        self._set_text_prop()
        self._set_attributes()

        for cmd in self._cli.input(self._callback):
            if equal(cmd, '<Update>') or equal(cmd, '<Shorten>'):
                cmd = self._cli._cmdline
                if cmd and re.match(r'\d', cmd[-1]) is None:
                    self._cli._backspace()
                if len(self._cli._cmdline) > 3:
                    cmd[:3] = []
                    self._cli._cursor_pos -= 3
                self._set_text_prop(self._parse_line())
            elif equal(cmd, '<C-x>'):
                self.show_bg = not self.show_bg
                self._setStlMode()
                self._set_text_prop(self._parse_line())
            elif equal(cmd, '<Quit>'):
                self.quit()
                break
            elif equal(cmd, '<C-j>'):
                if self._is_popup():
                    lfCmd("""call win_execute(%d, 'exec "norm! \<C-F>"')""" % (self._getInstance().getPopupWinId()))
                else:
                    lfCmd('exec "norm! \<C-F>"')
            elif equal(cmd, '<C-k>'):
                if self._is_popup():
                    lfCmd("""call win_execute(%d, 'exec "norm! \<C-B>"')""" % (self._getInstance().getPopupWinId()))
                else:
                    lfCmd('exec "norm! \<C-B>"')

    def _parse_line(self):
        line = ''.join(self._cli._cmdline)
        match = re.match(r'\d{1,3}', line)
        if match is None:
            return None
        color = int(match.group(0))
        if color > 256:
            color = None
        return color


#*****************************************************
# selfExplManager is a singleton
#*****************************************************
colorpanelExplManager = ColorPanelExplManager()

__all__ = ['colorpanelExplManager']
