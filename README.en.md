# Yet Another Alfred Translator

English | [中文](README.md)

An Alfred 5 workflow for Chinese ⇆ English translation, powered by the Youdao AI Cloud (有道智云) translation API.

Highlights:

- **Zero dependencies**: uses only the macOS built-in `/usr/bin/python3` standard library, ships no binaries, works on both Intel and Apple Silicon
- **Keys stay local**: appKey/secret are configured via Alfred's Configure Workflow panel, stored only on your machine and never distributed with the workflow
- **Automatic direction detection**: a query containing any Chinese character translates zh→en, otherwise auto→zh (Chinese sentences with punctuation or digits are detected correctly)
- **Dictionary info**: word/phrase queries show US/UK phonetics and per-part-of-speech definitions (v. / n. / adj. each on its own row), fetched from the Youdao dictionary API in parallel with the translation request, so it adds no latency
- **Pronunciation**: ⌘↵ speaks locally (macOS `say`), ⌥↵ plays Youdao online audio (cached, falls back to local on failure)
- **Quota friendly**: input debouncing plus a 24-hour result cache (can be disabled)
- **Code-friendly**: camelCase/snake_case identifiers are split into words automatically (`getHTTPServer` → `get HTTP Server`, acronyms kept intact)

## Installation

1. Download `YetAnotherTranslator-*.alfredworkflow` from [Releases](https://github.com/AlainOUYANG/YetAnotherAlfredTranslator/releases) and double-click to install (or clone this repo and run `scripts/install.sh` to build it yourself)
2. Register at Youdao AI Cloud and create an app (free, new users get trial credit):
   1. Sign up at https://ai.youdao.com/
   2. In the console, create a "Text Translation" (文本翻译) service
   3. Create an application (choose API as the integration type), bind the text translation service, and get the App ID and App Secret
3. Open this workflow's **Configure Workflow** panel in Alfred and fill in the App ID and Secret
4. (Optional) Double-click the Hotkey nodes on the left of the canvas to set hotkeys (double-tap ⌥ is recommended) for translating the currently selected text. Exported workflows do not carry hotkey bindings, so set them after installing

## Usage

| Action | Effect |
|---|---|
| `yd hello` / `yd 你好` | Translate (the trigger keyword is configurable) |
| ↵ | Copy the result to the clipboard and hide Alfred |
| ⌘↵ | Speak locally (voice configurable) |
| ⌥↵ | Play Youdao online pronunciation |
| ⇧ | Quick Look the Youdao dictionary page |
| ⌘L | Show the full translation in Large Type (for long text) |
| Hotkey | Translate the currently selected text |

When no key is configured, triggering the workflow shows guide items linking to the registration page and the configuration panel.

## Development

```bash
# Unit tests (pure stdlib, no network)
/usr/bin/python3 -m unittest discover tests

# Command-line debugging (without installing into Alfred)
cd src && youdao_app_key=xxx youdao_app_secret=yyy alfred_workflow_cache=/tmp/yat \
  /usr/bin/python3 translate.py "hello world" | /usr/bin/python3 -m json.tool

# Build / build and install
scripts/build.sh
scripts/install.sh
```

Layout: `src/` is what gets packaged (`translate.py` Script Filter entry, `youdao.py` translation API client with the v3 sha256 signature, `dictapi.py` dictionary definitions, `util.py` detection and caching, `speak.sh` pronunciation, `info.plist` node graph and configuration panel); `tests/` unit tests; `scripts/` build scripts.

## License

[MIT](LICENSE)
