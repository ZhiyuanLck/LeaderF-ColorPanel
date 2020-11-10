LeaderF-ColorPanel
=======

This Plugin use [LeaderF](https://github.com/Yggdroot/LeaderF) to display all cterm colors.

This plugin is **only tested on vim**. There is some code to make the plugin compatible with nvim, but I do not test it and don't know if it works.

Installation
-----------

```vim
Plug 'Yggdroot/LeaderF'
Plug 'ZhiyuanLck/LeaderF-ColorPanel'
```

Usage
-----------
```
usage: Leaderf[!] ColorPanel [-h] [--cols <COLS>] [--rows <ROWS>] [--str <STR>]
                             [--top | --bottom | --left | --right | --fullScreen | --popup]

optional arguments:
  -h, --help            show this help message and exit
  --top                 the LeaderF window is at the top of the screen
  --bottom              the LeaderF window is at the bottom of the screen
  --left                the LeaderF window is at the left of the screen
  --right               the LeaderF window is at the right of the screen
  --fullScreen          the LeaderF window takes up the full screen
  --popup               the LeaderF window is a popup window or floating window

specific arguments:
  --cols <COLS>         number of colors to be show in one row
  --rows <ROWS>         number of colors to be show in one column
  --str <STR>           string to be shown in panel
```

Global setting
-------------

You can set the `cols`, `rows` and `str` globally.

```vim
let g:Lf_ColorPanel_cols = 12
let g:Lf_ColorPanel_rows = 16
let g:Lf_ColorPanel_str = 'xxx'
```

Screenshots
-----------

`:LeaderfColorPanel`

![buffer][1]

`:LeaderfColorPanel --popup`

![popup][2]

Mappings


| Command                    | Description
| -------                    | -----------
| `<C-C>`<br>`<ESC>`         | quit from LeaderF
| `<C-X>`                    | switch between background show mode and forground show mode
| `<C-U>`                    | clear the prompt
| `<C-W>`                    | delete the word before the cursor in the prompt
| `<BS>`                     | delete the preceding character in the prompt
| `<Del>`                    | delete the current character in the prompt
| `<C-k>`                    | scroll up in the result window
| `<C-j>`                    | scroll down in the result window


  [1]: https://github.com/ZhiyuanLck/images/blob/master/leaderf/ColorPanel_buffer.gif
  [2]: https://github.com/ZhiyuanLck/images/blob/master/leaderf/ColorPanel_popup.gif
