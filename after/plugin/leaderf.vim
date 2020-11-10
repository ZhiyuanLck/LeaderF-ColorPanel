let s:extension = {
            \   "name": "ColorPanel",
            \   "help": "navigate the files in directory",
            \   "manager_id": "leaderf#ColorPanel#managerId",
            \   "arguments": [
            \       {"name": ["--cols"], "nargs": "1", "help": "number of colors to be show in one row"},
            \       {"name": ["--rows"], "nargs": "1", "help": "number of colors to be show in one column"},
            \       {"name": ["--str"], "nargs": "1", "help": "string to be shown in panel"},
            \   ]
            \ }

" In order that `Leaderf ghq` is available
call g:LfRegisterPythonExtension(s:extension.name, s:extension)

command! -bar -nargs=? -complete=dir LeaderfColorPanel Leaderf ColorPanel <args>

" In order to be listed by :LeaderfSelf
call g:LfRegisterSelf("LeaderfColorPanel", "show cterm colors")
