# ai-screenshot

A minimal command-line tool that captures the full physical screen as a PNG and prints the file path. It is built for AI agents that need to look at what is on a desktop, but it is also useful on its own.

```bash
$ ai-screenshot
/home/you/Pictures/screenshots/screenshot-2026-10-14T11-25-03-971961-70b2b4.png
```

Nothing else is written to stdout. Errors go to stderr, prefixed with `[error]`, and the exit code is 1.

## Requirements

- Linux with an active **X11** session. Wayland is not supported.
- ImageMagick's `import` command:

  ```bash
  sudo apt install imagemagick
  ```

- Python 3.9 or newer.

## Install

```bash
pip install -e .
```

## Usage

```bash
ai-screenshot            # capture the whole screen, print the path
```

Files are saved to `~/Pictures/screenshots/` with a timestamp and a random suffix, so repeated captures never overwrite each other.

## Privacy

`ai-screenshot` captures **everything** visible on the screen, including notifications, open chats, and password managers. It does not redact anything, and it does not delete old captures. Review the folder regularly, and do not point an AI agent at a screen that is showing secrets.

## What it does not do

- It does not capture a single window or a browser page. Use a browser tool for that.
- It does not extract text (no OCR).
- It does not work under Wayland.

## Development

```bash
python3 -m venv ~/.venvs/ai-screenshot-dev
~/.venvs/ai-screenshot-dev/bin/pip install -e . pytest
~/.venvs/ai-screenshot-dev/bin/python -m pytest -q -m "not real"
```

The `real` tests take a real screenshot and need an X11 session with ImageMagick installed. They save a file into `~/Pictures/screenshots/`, so run them only when you are happy for that to happen:

```bash
~/.venvs/ai-screenshot-dev/bin/python -m pytest -q -m real
```

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).

## Licence

MIT. See [LICENSE](LICENSE).
