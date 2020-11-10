" ============================================================================
" File:        Self.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "import vim, sys, os.path"
exec g:Lf_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:Lf_py "sys.path.insert(0, os.path.join(cwd, 'python'))"
exec g:Lf_py "from ColorPanelExpl import *"

function! leaderf#ColorPanel#managerId()
    if g:Lf_PythonVersion == 2
        return pyeval("id(colorpanelExplManager)")
    else
        return py3eval("id(colorpanelExplManager)")
    endif
endfunction

" from leaderf/colorscheme.vim
let s:modeMap = {
            \   'Background': 'Lf_hl_stlFuzzyMode',
            \   'Forground': 'Lf_hl_stlRegexMode'
            \ }

function! leaderf#ColorPanel#highlightMode(category, mode)
    let sid = synIDtrans(hlID(s:modeMap[a:mode]))
    let guibg = synIDattr(sid, "bg", "gui")
    let ctermbg = synIDattr(sid, "bg", "cterm")
    exec printf("hi link Lf_hl_%s_stlMode %s", a:category, s:modeMap[a:mode])
    exec printf("hi Lf_hl_%s_stlSeparator1 guibg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_%s_stlSeparator1 ctermbg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    exec printf("hi Lf_hl_%s_stlSeparator2 guifg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_%s_stlSeparator2 ctermfg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    redrawstatus
endfunction

" from leaderf/colorscheme/popup.vim
let s:matchModeMap = {
            \   'Background': 'Lf_hl_popup_fuzzyMode',
            \   'Forground': 'Lf_hl_popup_regexMode'
            \ }

function! leaderf#ColorPanel#hiMatchMode(category, mode) abort
    let sid = synIDtrans(hlID(s:matchModeMap[a:mode]))
    let guibg = synIDattr(sid, "bg", "gui")
    let ctermbg = synIDattr(sid, "bg", "cterm")
    exec printf("hi link Lf_hl_popup_%s_matchMode %s", a:category, s:matchModeMap[a:mode])
    exec printf("hi Lf_hl_popup_%s_sep1 guibg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_popup_%s_sep1 ctermbg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    exec printf("hi Lf_hl_popup_%s_sep2 guifg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_popup_%s_sep2 ctermfg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
endfunction
