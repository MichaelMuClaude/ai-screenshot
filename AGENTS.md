# AGENTS.md — guide for AI agents contributing to ai-screenshot

This file is for AI coding agents that read, test, or change this project. The human-facing version of the same rules is in [CONTRIBUTING.md](CONTRIBUTING.md).

## What this project is

`ai-screenshot` is a command-line tool. It captures the full X11 screen with ImageMagick's `import` command, saves a PNG under `~/Pictures/screenshots/`, and prints the path. Other tools and agents depend on its output format, so keep it stable.

## Promises to keep

1. **Stable stdout.** On success, stdout contains exactly one line: the absolute path of the saved PNG. Nothing else.
2. **Errors on stderr.** Every failure prints a message starting with `[error]` to stderr and returns exit code 1.
3. **No silent data loss.** Captures get a unique name (timestamp plus random suffix). Never overwrite an existing file.
4. **No network access.** The tool captures the screen and writes a local file. Do not add uploads, telemetry, or remote calls.
5. **No shell interpolation.** Call `import` through a list of arguments, never through `shell=True` or string concatenation.

If a change breaks one of these, do not merge it.

## Layout

```
src/ai_screenshot/
  cli.py        capture logic, filename generation, error handling, main()
  __init__.py   version
tests/
  test_cli.py   unit tests (mocked) and one `real` end-to-end test
SKILL.md        usage guide for agents that call the tool
```

## Setup and checks

Keep the virtualenv outside any folder synced by a file-sync tool. Those tools break venv shebangs.

```bash
python3 -m venv ~/.venvs/ai-screenshot-dev
~/.venvs/ai-screenshot-dev/bin/pip install -e . pytest
~/.venvs/ai-screenshot-dev/bin/python -m pytest -q -m "not real"
```

The unit tests mock the `import` call and must run without a display. Do not add a test that needs a real display unless it is marked `real`.

The `real` test takes a real screenshot and writes a file into `~/Pictures/screenshots/`. Run it only on a machine with an X11 session and ImageMagick, and say in the pull request that you ran it. Do not run it in CI.

## Rules for changes

- **Keep changes small.** One fix or feature per pull request.
- **Add a test for each behaviour change**, including the failure path.
- **Do not hardcode user paths or machine names.** Use `os.path.expanduser` and environment variables.
- **Do not add dependencies.** The project has no runtime dependencies, and we want to keep it that way.
- **Keep the Python floor at 3.9.**
- **Do not add redaction or automatic deletion without discussion.** These change what users get, so open an issue first.

## Pull request description

Include:

- What changed and why, in two or three sentences.
- The test command you ran and its result.
- Whether you ran the `real` test, and on what environment.
- A line stating that the change was produced with AI assistance, and which tool and model you used. Disclosure is expected.

## Security

Do not report vulnerabilities in a public issue. Use a private security advisory on GitHub instead.

## Good first tasks for agents

- Add a unit test for a failure path that is not yet covered, for example an unwritable output folder.
- Improve an error message so it names the missing dependency and how to install it.
- Check that `README.md` and `SKILL.md` agree with the actual behaviour.
