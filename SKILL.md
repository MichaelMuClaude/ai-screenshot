---
name: ai-screenshot
description: Capture the full physical screen as a PNG and return its path, so an agent can look at what is on the user's display. Use when the user asks what is on their screen or wants help with a visible error or window. Not for browser page captures.
---

# ai-screenshot

## What it does

Captures the whole screen as a PNG, saves it under `~/Pictures/screenshots/`, and prints the full file path on stdout.

## When to use it

- The user asks what is currently on their screen, or asks for help with a visible error, dialog, or window layout.
- A desktop application's state is hard to describe in words and the image would be clearer.

## When not to use it

- To capture a browser page or a single window. This tool captures the entire screen only.
- To extract text from the screen. This tool does not run OCR.

## Usage

```bash
ai-screenshot
```

No arguments.

- **Success:** stdout contains the absolute path of the PNG. Read that file to see the image.
- **Failure:** stderr contains a message starting with `[error]`, and the exit code is non-zero. Typical causes are no `DISPLAY` variable (no X11 session), ImageMagick's `import` missing, or the output folder not writable.

## Privacy

The capture includes everything on screen, including notifications and any open secrets. Check what is visible before capturing when the screen may contain sensitive content, and tell the user when a capture contains something private.
