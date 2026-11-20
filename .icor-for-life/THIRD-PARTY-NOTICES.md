# Third-party notices

Since ICOR for Life 2.3.0 this folder bundles no Obsidian plugin and no
theme. You install the ICOR for Life plugins, our own work, from Obsidian's
community directory, and each brings its own notices from its repository.
This file keeps their notices for reference. Before 2.3.0 every bundled
plugin was an ICOR for Life plugin; none was a third-party community
install. From 1.7.0 the shell inside the app has been **ICOR
for Life - Terminal**, our own plugin, replacing the third-party
Terminal plugin by polyipseity (AGPL-3.0); from 1.10.0 the outliner
inside the app is **ICOR for Life - Outliner**, our own plugin,
replacing the third-party Outliner community plugin (MIT).

What follows is not a notice about a bundled tool. It is the licenses of
the open-source libraries some of our own plugins use inside their code
- MIT and Apache notices that travel with that code under its own
license, whichever plugin folder it ships in.

## Components inside the ICOR plugins

The ICOR plugins are our own work. Several of them bundle no
third-party code at all: ICOR Focus, ICOR Interface and myICOR Connect are
hand-written JavaScript against the Obsidian plugin API, ICOR for
Life - Outliner is hand-written TypeScript against the CodeMirror and
Obsidian editor APIs, ICOR for Life - Canvases is hand-written TypeScript
against the Obsidian plugin API alone, and ICOR for Life - PDF Annotation
is hand-written
TypeScript against the Obsidian plugin API and the built-in PDF viewer's
own objects (the pdf.js inside Obsidian, not a bundled copy). The `rect=`
and `color=` parameters in the links it copies use the names the PDF++
plugin (Ryota Ushio, MIT) uses, so a link reads the same in both; that is
two parameter names, no code.

**ICOR Planner** embeds the source-tool glyphs (Todoist, ClickUp) as SVG
path data from the Simple Icons project (https://simpleicons.org),
released under CC0 1.0 Universal. The brand marks themselves remain
subject to their owners' trademark policies.

**ICOR Chat** bundles the Claude Agent SDK for TypeScript
(`@anthropic-ai/claude-agent-sdk`), published by Anthropic, version
0.3.226, from https://github.com/anthropics/claude-agent-sdk-typescript.
The SDK is not open source. Its package declares its license as "SEE
LICENSE IN README.md", and that README places use of the SDK under
Anthropic's Commercial Terms of Service, at
https://www.anthropic.com/legal/commercial-terms.

The Claude Code binary is NOT bundled or redistributed. ICOR Chat runs the
copy of Claude Code already installed on your own machine, unmodified, and
you sign in to it with your own Anthropic account through Anthropic's own
sign-in flow. The plugin never collects, stores, or relays your
credentials, and your Claude usage is billed to you under your own
agreement with Anthropic. myICOR is not affiliated with, endorsed by, or
partnered with Anthropic.

Two open-source libraries are bundled alongside the SDK. Their notices
follow in full:

  Zod - MIT License - https://github.com/colinhacks/zod

    Copyright (c) 2020 Colin McDonnell

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
    BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
    ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

  OpenTelemetry API for JavaScript - Apache License 2.0 -
  https://github.com/open-telemetry/opentelemetry-js

    Copyright The OpenTelemetry Authors

    Licensed under the Apache License, Version 2.0 (the "License"); you
    may not use this file except in compliance with the License. You may
    obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
    implied. See the License for the specific language governing
    permissions and limitations under the License.

    This library is redistributed unmodified.

**ICOR SQLite Viewer** bundles sql.js (a WebAssembly build of SQLite,
MIT License, https://github.com/sql-js/sql.js) as its mobile and
fallback engine; SQLite itself is public domain. The full notice ships
in the plugin's own `THIRD-PARTY-NOTICES.md`. The desktop engine is the
`sqlite3` command line tool already on the member's machine, which is
not bundled or redistributed.

**ICOR Terminal** bundles the xterm.js terminal emulator and five of its
addons, all by The xterm.js authors and all under the MIT License, from
https://github.com/xtermjs/xterm.js:

| Component | Version | Used for |
| --- | --- | --- |
| `@xterm/xterm` | 6.0.0 | the terminal emulator, rendering and input; its `css/xterm.css` is included in `styles.css` with its license header |
| `@xterm/addon-fit` | 0.11.0 | sizing the grid to the pane |
| `@xterm/addon-search` | 0.16.0 | the find bar |
| `@xterm/addon-web-links` | 0.12.0 | clickable URLs in output |
| `@xterm/addon-unicode11` | 0.9.0 | correct width of Unicode 11 characters, including emoji |
| `@xterm/addon-webgl` | 0.19.0 | the WebGL renderer where the graphics stack allows it |

Copyright (c) 2017-2019, The xterm.js authors (MIT). Copyright (c)
2014-2016, SourceLair Private Company (MIT). Copyright (c) 2012-2013,
Christopher Jeffrey (MIT). The MIT License text is the same one
reproduced above under Zod. The full notice, with each component listed,
ships in the plugin's own `THIRD-PARTY-NOTICES.md`.

The plugin's pseudo-terminal helper (shipped inside `main.js` as readable
Python source) uses only the Python 3 standard library. Python itself is
NOT bundled or redistributed; the plugin runs the `python3` already
installed on the member's machine, which is a prerequisite on macOS and
Linux (see `README.md`). Lucide icon names are resolved through
Obsidian's own API at runtime; no icon assets are bundled.

No copyleft-licensed code (GPL, LGPL, AGPL or MPL) is bundled inside any
ICOR plugin, and from Scaffold 1.7.0 no copyleft component ships in this
vault at all.

Obsidian itself is NOT bundled or redistributed; users install it from
obsidian.md under Obsidian's own terms.
