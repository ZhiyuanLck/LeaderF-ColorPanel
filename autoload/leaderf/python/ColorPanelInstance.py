#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import time
import itertools
from ColorPanelUtils import *
from leaderf.utils import *
from leaderf.instance import *

class ColorPanelInstance(LfInstance):
    def __init__(self, manager, category, cli,
                 before_enter_cb,
                 after_enter_cb,
                 before_exit_cb,
                 after_exit_cb):
        super(ColorPanelInstance, self).__init__(
                 manager,
                 category, cli,
                 before_enter_cb,
                 after_enter_cb,
                 before_exit_cb,
                 after_exit_cb)

    def setStlMode(self, mode):
        lfCmd("let g:Lf_{}_StlMode = '{}'".format(self._category, mode))
        if self._win_pos in ('popup', 'floatwin'):
            lfCmd("call leaderf#ColorPanel#hiMatchMode('{0}', g:Lf_{0}_StlMode)".format(self._category))
        else:
            lfCmd("call leaderf#ColorPanel#highlightMode('{0}', g:Lf_{0}_StlMode)".format(self._category))

    def _createPopupWindow(self, clear):
        # `type(self._window_object) != type(vim.current.window)` is necessary, error occurs if
        # `Leaderf file --popup` after `Leaderf file` without it.
        if self._window_object is not None and type(self._window_object) != type(vim.current.window)\
                and isinstance(self._window_object, PopupWindow): # type is PopupWindow
            if self._window_object.tabpage == vim.current.tabpage and lfEval("get(g:, 'Lf_Popup_VimResized', 0)") == '0' \
                    and "--popup-width" not in self._arguments and "--popup-height" not in self._arguments:
                if self._popup_winid > 0 and self._window_object.valid: # invalid if cleared by popup_clear()
                    # clear the buffer first to avoid a flash
                    if clear and lfEval("g:Lf_RememberLastSearch") == '0' \
                            and "--append" not in self._arguments \
                            and "--recall" not in self._arguments:
                        self.buffer.options['modifiable'] = True
                        del self._buffer_object[:]
                        self.refreshPopupStatusline()

                    self._popup_instance.show()
                    return
            else:
                lfCmd("let g:Lf_Popup_VimResized = 0")
                self._popup_instance.close()

        buf_number = int(lfEval("bufadd('{}')".format(escQuote(self._buffer_name))))

# >>>>>>>>>>Refactor>>>>>>>>>>>
        rows, cols = get_size(self._arguments)
        maxwidth = 8 * cols
        maxheight = rows
# <<<<<<<<<<Refactor<<<<<<<<<<<

        line, col = [int(i) for i in lfEval("get(g:, 'Lf_PopupPosition', [0, 0])")]
        if line == 0:
            line = (int(lfEval("&lines")) - maxheight) // 2
        else:
            line = min(line, int(lfEval("&lines")) - maxheight)

        if col == 0:
            col = (int(lfEval("&columns")) - maxwidth) // 2
        else:
            col = min(col, int(lfEval("&columns")) - maxwidth)

        if line <= 0:
            line = 1

        if col <= 0:
            col = 1

        self._popup_maxheight = max(maxheight - 2, 1) # there is an input window above

        if lfEval("has('nvim')") == '1':
            self._win_pos = "floatwin"
            floatwin_height = 1

            config = {
                    "relative": "editor",
                    "anchor"  : "NW",
                    "height"  : floatwin_height,
                    "width"   : maxwidth,
                    "row"     : line + 1,
                    "col"     : col
                    }
            lfCmd("silent noswapfile let winid = nvim_open_win(%d, 1, %s)" % (buf_number, str(config)))
            self._popup_winid = int(lfEval("winid"))
            self._setAttributes()
            try:
                lfCmd("call nvim_win_set_option(%d, 'foldcolumn', 1)" % self._popup_winid)
            except vim.error:
                lfCmd("call nvim_win_set_option(%d, 'foldcolumn', '1')" % self._popup_winid)
            lfCmd("call nvim_win_set_option(%d, 'winhighlight', 'Normal:Lf_hl_popup_window')" % self._popup_winid)

            self._tabpage_object = vim.current.tabpage
            self._buffer_object = vim.buffers[buf_number]
            self._window_object = FloatWindow(self._popup_winid, vim.current.window, self._buffer_object, self._tabpage_object, line + 1)
            self._popup_instance.content_win = self._window_object

            input_win_config = {
                    "relative": "editor",
                    "anchor"  : "NW",
                    "height"  : 1,
                    "width"   : maxwidth,
                    "row"     : line,
                    "col"     : col
                    }

            if self._input_buffer_number == -1:
                self._input_buffer_number = int(lfEval("bufadd('')"))

            buf_number = self._input_buffer_number
            lfCmd("silent let winid = nvim_open_win(%d, 0, %s)" % (buf_number, str(input_win_config)))
            winid = int(lfEval("winid"))
            lfCmd("call nvim_buf_set_option(%d, 'buflisted', v:false)" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'buftype', 'nofile')" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'bufhidden', 'hide')" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'undolevels', -1)" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'swapfile', v:false)" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'filetype', 'leaderf')" % buf_number)

            lfCmd("call nvim_win_set_option(%d, 'list', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'number', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'relativenumber', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'spell', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'foldenable', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'foldmethod', 'manual')" % winid)
            try:
                lfCmd("call nvim_win_set_option(%d, 'foldcolumn', 0)" % winid)
            except vim.error:
                lfCmd("call nvim_win_set_option(%d, 'foldcolumn', '0')" % winid)
            # lfCmd("call nvim_win_set_option(%d, 'signcolumn', 'no')" % winid)
            lfCmd("call nvim_win_set_option(%d, 'cursorline', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'colorcolumn', '')" % winid)
            lfCmd("call nvim_win_set_option(%d, 'winhighlight', 'Normal:Lf_hl_popup_inputText')" % winid)
            def getWindow(number):
                for w in vim.windows:
                    if number == w.number:
                        return w
                return vim.current.window

            self._popup_instance.input_win = FloatWindow(winid, getWindow(int(lfEval("win_id2win(%d)" % winid))), vim.buffers[buf_number], vim.current.tabpage, line)

            show_stl = 0
            if lfEval("get(g:, 'Lf_PopupShowStatusline', 1)") == '1':
                show_stl = 1
                stl_win_config = {
                        "relative": "editor",
                        "anchor"  : "NW",
                        "height"  : 1,
                        "width"   : maxwidth,
                        "row"     : line + 1 + floatwin_height,
                        "col"     : col
                        }

                if self._stl_buffer_number == -1:
                    self._stl_buffer_number = int(lfEval("bufadd('')"))

                buf_number = self._stl_buffer_number
                lfCmd("silent let winid = nvim_open_win(%d, 0, %s)" % (buf_number, str(stl_win_config)))
                winid = int(lfEval("winid"))
                lfCmd("call nvim_buf_set_option(%d, 'buflisted', v:false)" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'buftype', 'nofile')" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'bufhidden', 'hide')" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'undolevels', -1)" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'swapfile', v:false)" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'filetype', 'leaderf')" % buf_number)

                lfCmd("call nvim_win_set_option(%d, 'list', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'number', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'relativenumber', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'spell', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'foldenable', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'foldmethod', 'manual')" % winid)
                try:
                    lfCmd("call nvim_win_set_option(%d, 'foldcolumn', 0)" % winid)
                except vim.error:
                    lfCmd("call nvim_win_set_option(%d, 'foldcolumn', '0')" % winid)
                # lfCmd("call nvim_win_set_option(%d, 'signcolumn', 'no')" % winid)
                lfCmd("call nvim_win_set_option(%d, 'cursorline', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'colorcolumn', '')" % winid)
                lfCmd("call nvim_win_set_option(%d, 'winhighlight', 'Normal:Lf_hl_popup_blank')" % winid)
                self._popup_instance.statusline_win = FloatWindow(winid, getWindow(int(lfEval("win_id2win(%d)" % winid))), vim.buffers[buf_number], vim.current.tabpage, line + 1 + floatwin_height)

            if "--recall" in self._arguments:
                self.refreshPopupStatusline()

            lfCmd("augroup Lf_Floatwin_Close")
            lfCmd("autocmd! WinEnter * call leaderf#closeAllFloatwin(%d, %d, %d, %d)" % (self._popup_instance.input_win.id,
                                                                                         self._popup_instance.content_win.id,
                                                                                         self._popup_instance.statusline_win.id if show_stl else -1,
                                                                                         show_stl))
            lfCmd("augroup END")
        else:
            self._win_pos = "popup"

            options = {
                    "maxwidth":        maxwidth,
                    "minwidth":        maxwidth,
                    "maxheight":       self._popup_maxheight,
                    "zindex":          20480,
                    "pos":             "topleft",
                    "line":            line + 1,      # there is an input window above
                    "col":             col,
                    "padding":         [0, 0, 0, 1],
                    "scrollbar":       0,
                    "mapping":         0,
                    "filter":          "leaderf#PopupFilter",
                    }

            lfCmd("silent noswapfile let winid = popup_create(%d, %s)" % (buf_number, str(options)))
            self._popup_winid = int(lfEval("winid"))
            lfCmd("call win_execute(%d, 'setlocal nobuflisted')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal buftype=nofile')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal bufhidden=hide')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal undolevels=-1')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal noswapfile')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal nolist')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal number norelativenumber')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal nospell')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal nofoldenable')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal foldmethod=manual')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal shiftwidth=4')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal cursorline')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal foldcolumn=0')" % self._popup_winid)
            # lfCmd("call win_execute(%d, 'silent! setlocal signcolumn=no')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal colorcolumn=')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'silent! setlocal filetype=leaderf')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal wincolor=Lf_hl_popup_window')" % self._popup_winid)

            self._tabpage_object = vim.current.tabpage
            self._buffer_object = vim.buffers[buf_number]
            self._window_object = PopupWindow(self._popup_winid, self._buffer_object, self._tabpage_object, line+1)
            self._popup_instance.content_win = self._window_object

            input_win_options = {
                    "maxwidth":        maxwidth + 1,
                    "minwidth":        maxwidth + 1,
                    "maxheight":       1,
                    "zindex":          20480,
                    "pos":             "topleft",
                    "line":            line,
                    "col":             col,
                    "scrollbar":       0,
                    "mapping":         0,
                    }

            if self._input_buffer_number == -1:
                self._input_buffer_number = int(lfEval("bufadd('')"))

            buf_number = self._input_buffer_number
            lfCmd("silent let winid = popup_create(%d, %s)" % (buf_number, str(input_win_options)))
            winid = int(lfEval("winid"))
            lfCmd("call win_execute(%d, 'setlocal nobuflisted')" % winid)
            lfCmd("call win_execute(%d, 'setlocal buftype=nofile')" % winid)
            lfCmd("call win_execute(%d, 'setlocal bufhidden=hide')" % winid)
            lfCmd("call win_execute(%d, 'setlocal undolevels=-1')" % winid)
            lfCmd("call win_execute(%d, 'setlocal noswapfile')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nolist')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nonumber norelativenumber')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nospell')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nofoldenable')" % winid)
            lfCmd("call win_execute(%d, 'setlocal foldmethod=manual')" % winid)
            lfCmd("call win_execute(%d, 'setlocal shiftwidth=4')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nocursorline')" % winid)
            lfCmd("call win_execute(%d, 'setlocal foldcolumn=0')" % winid)
            # lfCmd("call win_execute(%d, 'silent! setlocal signcolumn=no')" % winid)
            lfCmd("call win_execute(%d, 'setlocal colorcolumn=')" % winid)
            lfCmd("call win_execute(%d, 'setlocal wincolor=Lf_hl_popup_inputText')" % winid)
            lfCmd("call win_execute(%d, 'silent! setlocal filetype=leaderf')" % winid)

            self._popup_instance.input_win = PopupWindow(winid, vim.buffers[buf_number], vim.current.tabpage, line)

            if lfEval("get(g:, 'Lf_PopupShowStatusline', 1)") == '1':
                statusline_win_options = {
                        "maxwidth":        maxwidth + 1,
                        "minwidth":        maxwidth + 1,
                        "maxheight":       1,
                        "zindex":          20480,
                        "pos":             "topleft",
                        "line":            line + 1 + self._window_object.height,
                        "col":             col,
                        "scrollbar":       0,
                        "mapping":         0,
                        }

                if self._stl_buffer_number == -1:
                    self._stl_buffer_number = int(lfEval("bufadd('')"))

                buf_number = self._stl_buffer_number
                lfCmd("silent let winid = popup_create(%d, %s)" % (buf_number, str(statusline_win_options)))
                winid = int(lfEval("winid"))
                lfCmd("call win_execute(%d, 'setlocal nobuflisted')" % winid)
                lfCmd("call win_execute(%d, 'setlocal buftype=nofile')" % winid)
                lfCmd("call win_execute(%d, 'setlocal bufhidden=hide')" % winid)
                lfCmd("call win_execute(%d, 'setlocal undolevels=-1')" % winid)
                lfCmd("call win_execute(%d, 'setlocal noswapfile')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nolist')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nonumber norelativenumber')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nospell')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nofoldenable')" % winid)
                lfCmd("call win_execute(%d, 'setlocal foldmethod=manual')" % winid)
                lfCmd("call win_execute(%d, 'setlocal shiftwidth=4')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nocursorline')" % winid)
                lfCmd("call win_execute(%d, 'setlocal foldcolumn=0')" % winid)
                # lfCmd("call win_execute(%d, 'silent! setlocal signcolumn=no')" % winid)
                lfCmd("call win_execute(%d, 'setlocal colorcolumn=')" % winid)
                lfCmd("call win_execute(%d, 'setlocal wincolor=Lf_hl_popup_blank')" % winid)
                lfCmd("call win_execute(%d, 'silent! setlocal filetype=leaderf')" % winid)

                self._popup_instance.statusline_win = PopupWindow(winid, vim.buffers[buf_number], vim.current.tabpage, line + 1 + self._window_object.height)

            lfCmd("call leaderf#ResetPopupOptions(%d, 'callback', function('leaderf#PopupClosed', [%s, %d]))"
                    % (self._popup_winid, str(self._popup_instance.getWinIdList()), id(self._manager)))

        if not self._is_popup_colorscheme_autocmd_set:
            self._is_popup_colorscheme_autocmd_set = True
            lfCmd("call leaderf#colorscheme#popup#load('{}', '{}')".format(self._category, lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))
            lfCmd("augroup Lf_Popup_{}_Colorscheme".format(self._category))
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#popup#load('{}', '{}')".format(self._category,
                    lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))
            lfCmd("autocmd VimResized * let g:Lf_Popup_VimResized = 1")
            lfCmd("augroup END")

    def _createBufWindow(self, win_pos):
        self._win_pos = win_pos
        lfCmd("let g:Lf_VimResized = 0")

        saved_eventignore = vim.options['eventignore']
        vim.options['eventignore'] = 'all'
        try:
            orig_win = vim.current.window
            for w in vim.windows:
                vim.current.window = w
                if lfEval("exists('w:lf_win_view')") == '0':
                    lfCmd("let w:lf_win_view = {}")
                lfCmd("let w:lf_win_view['%s'] = winsaveview()" % self._category)
        finally:
            vim.current.window = orig_win
            vim.options['eventignore'] = saved_eventignore

        if win_pos != 'fullScreen':
            self._restore_sizes = lfEval("winrestcmd()")
            self._orig_win_count = len(vim.windows)

        """
        https://github.com/vim/vim/issues/1737
        https://github.com/vim/vim/issues/1738
        """
        # clear the buffer first to avoid a flash
        if self._buffer_object is not None and self._buffer_object.valid \
                and lfEval("g:Lf_RememberLastSearch") == '0' \
                and "--append" not in self._arguments \
                and "--recall" not in self._arguments:
            self.buffer.options['modifiable'] = True
            del self._buffer_object[:]

        if win_pos == 'bottom':
            lfCmd("silent! noa keepa keepj bo sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'belowright':
            lfCmd("silent! noa keepa keepj bel sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'aboveleft':
            lfCmd("silent! noa keepa keepj abo sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'top':
            lfCmd("silent! noa keepa keepj to sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'fullScreen':
            lfCmd("silent! noa keepa keepj $tabedit %s" % self._buffer_name)
        elif win_pos == 'left':
            lfCmd("silent! noa keepa keepj to vsp %s" % self._buffer_name)
        elif win_pos == 'right':
            lfCmd("silent! noa keepa keepj bo vsp %s" % self._buffer_name)
        else:
            lfCmd("echoe 'Wrong value of g:Lf_WindowPosition'")

        lfCmd("doautocmd WinEnter")

        self._tabpage_object = vim.current.tabpage
        self._window_object = vim.current.window
        self._initial_win_height = self._window_object.height
        if (self._reverse_order or lfEval("get(g:, 'Lf_AutoResize', 0)") == '1') and "--recall" not in self._arguments:
            self._window_object.height = 1

        if self._buffer_object is None or not self._buffer_object.valid:
            self._buffer_object = vim.current.buffer

        self._setAttributes()

        if not self._is_colorscheme_autocmd_set:
            self._is_colorscheme_autocmd_set = True
            lfCmd("call leaderf#colorscheme#popup#load('{}', '{}')".format(self._category, lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))
            lfCmd("call leaderf#colorscheme#highlight('{}')".format(self._category))
            lfCmd("augroup Lf_{}_Colorscheme".format(self._category))
            lfCmd("autocmd!")
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#highlight('{}')".format(self._category))
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#highlightMode('{0}', g:Lf_{0}_StlMode)".format(self._category))
            lfCmd("autocmd ColorScheme <buffer> doautocmd syntax")
            lfCmd("autocmd CursorMoved <buffer> let g:Lf_{}_StlLineNumber = 1 + line('$') - line('.')".format(self._category))
            lfCmd("autocmd VimResized * let g:Lf_VimResized = 1")
            lfCmd("augroup END")

        saved_eventignore = vim.options['eventignore']
        vim.options['eventignore'] = 'all'
        try:
            orig_win = vim.current.window
            for w in vim.windows:
                vim.current.window = w
                if lfEval("exists('w:lf_win_view')") != '0' and lfEval("has_key(w:lf_win_view, '%s')" % self._category) != '0':
                    lfCmd("call winrestview(w:lf_win_view['%s'])" % self._category)
        finally:
            vim.current.window = orig_win
            vim.options['eventignore'] = saved_eventignore
