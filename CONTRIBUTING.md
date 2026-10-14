# Contributing to ai-screenshot

Thanks for helping. Humans and AI agents are both welcome. The detailed rules for agents are in [AGENTS.md](AGENTS.md).

## Ground rules

- Keep stdout to a single path line, and send errors to stderr with an `[error]` prefix.
- No network access and no new dependencies.
- Keep changes small, and add a test for every behaviour change.

## Running the tests

```bash
python3 -m venv ~/.venvs/ai-screenshot-dev
~/.venvs/ai-screenshot-dev/bin/pip install -e . pytest
~/.venvs/ai-screenshot-dev/bin/python -m pytest -q -m "not real"
```

Continuous integration runs the unit tests on Python 3.9 and 3.13. The `real` test is excluded there because it needs an X11 display.

## Opening a pull request

1. Fork the repository and create a branch with a descriptive name.
2. Make the change with tests.
3. Describe what changed, why, and which tests you ran. If you ran the `real` test, say so and give the environment.
4. If an AI agent wrote or helped write the change, say so and name the tool and model.

## Reporting bugs

Open an issue with the command, the output you got, your desktop environment, and the output you expected. Use a private security advisory for anything that could expose screen contents.

## Licence

By contributing, you agree that your contribution is released under the MIT licence in [LICENSE](LICENSE).
