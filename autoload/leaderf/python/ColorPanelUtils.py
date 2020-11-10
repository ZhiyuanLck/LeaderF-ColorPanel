#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import math
from leaderf.utils import lfEval

def get_size(arguments):
    is_popup = ("--popup" in arguments or lfEval("g:Lf_WindowPosition") == 'popup') \
            and "--bottom" not in arguments
    string = lfEval("get(g:, 'Lf_ColorPanel_str', 'xxx')")
    string = arguments.get("--str", [string])[0]
    col_len = 4 + len(string) + 1
    default_col = 12 if is_popup else 999
    cols = lfEval("get(g:, 'Lf_ColorPanel_cols', %d)" % default_col)
    cols = arguments.get("--cols", [cols])[0]
    cols = int(cols)
    cols = default_col if cols < 1 else cols
    vim_cols = int(lfEval("&columns"))
    if ("--left" in arguments
            or "--right" in arguments
            or lfEval("g:Lf_WindowPosition") == 'left'
            or lfEval("g:Lf_WindowPosition") == 'right'):
        vim_cols = math.floor(vim_cols / 2)
    max_cols = math.floor((vim_cols - 2) / col_len)
    cols = min(cols, max_cols)
    fit_rows = math.ceil(256 / cols)
    rows = lfEval("get(g:, 'Lf_ColorPanel_rows', %d)" % fit_rows)
    rows = arguments.get("--rows", [rows])[0]
    rows = int(rows)
    rows = fit_rows if rows < 1 else rows
    max_rows = int(lfEval("&lines"))
    if is_popup:
        max_rows -= 2
    rows = min(rows, max_rows, fit_rows) + 2 # input window
    return rows, cols
