---
name: ubuntu-desktop-control
description: Control and verify visible Ubuntu desktop applications with compositor screenshots and GNOME/Mutter pointer and keyboard input when native app bindings are unavailable.
---

# Ubuntu Desktop Control

Use this skill when the user explicitly asks to operate a visible Ubuntu/Linux desktop application, move the real pointer, click, type, or inspect the whole desktop. It is a local helper bridge for the user's graphical session; it does not turn a browser-only computer-use surface into a native-app connector.

## Control-path decision

1. Inspect the connected computer-use state first. If native apps are exposed, use that surface and refresh state after each UI action.
2. If only a browser is exposed, use the local helpers in `scripts/` only when the user requested desktop control and the helper can reach the same graphical session.
3. On GNOME/Wayland, use `portal_screenshot.py` for a fresh full-desktop screenshot and `mutter_remote_desktop.py` for real pointer/keyboard input. Do not use an X11 screenshot as evidence when the desktop is Wayland; it may be black or incomplete.
4. Re-capture the desktop after every short batch of actions and verify the visible result before reporting success.

## Prerequisites

The helper path is tested for an Ubuntu GNOME session with D-Bus, `xdg-desktop-portal`, and Mutter's remote-desktop interface. Check rather than assume:

```text
python3 scripts/check_environment.py
```

The screenshot helper needs the system Python modules `dbus` and `gi`. The pointer helper needs the D-Bus name `org.gnome.Mutter.RemoteDesktop`. If either is absent, report the exact missing prerequisite; do not silently claim that a desktop action happened.

## Screenshot workflow

Capture the entire current desktop before acting and after each meaningful action. The default path is a hidden Codex working folder, not the user's Pictures directory:

```text
python3 scripts/portal_screenshot.py
# default output: ~/.codex/Screenshot_for_chatgpt-work/ubuntu-desktop.png
```

Pass an explicit output path only when the user asks for a different location. The helper moves the portal-created image into the requested path so it does not leave an extra screenshot in `~/Pictures`.

Inspect the image, identify the target window and its current coordinates, and map pointer locations from the actual image dimensions. The script captures the compositor view of the current desktop; it is not a claim that the target application is natively exposed to the ChatGPT/Codex connector.

## Pointer and keyboard workflow

Start the helper as a persistent process and send it commands through standard input:

```text
python3 scripts/mutter_remote_desktop.py
```

It prints `READY` after the GNOME/Mutter session starts. Supported commands are:

```text
move DX DY                 # relative pointer motion
button 272 1               # left-button press; 272 is Linux BTN_LEFT
button 272 0               # left-button release
key KEYSYM 1               # key press, using an X11 keysym number
key KEYSYM 0               # key release
stop                       # stop the remote session
```

Use small, deliberate motion batches. For an approximate absolute location, first move to the top-left using a large negative relative movement, then move by the coordinates measured in the latest screenshot. This is only a convenience technique: verify the resulting pointer action visually because compositor scaling, pointer acceleration, multiple monitors, or a changed window layout can alter the mapping.

For a drag or freehand drawing, press the button, send a sequence of relative `move` commands, then release. Keep the sequence bounded and stop immediately if the screenshot does not match the expected application state.

## Safety and approval boundaries

- Keep inspection and dry-run behavior as the default.
- Treat clicking, typing, launching applications, changing files, uploads, messages, purchases, account actions, and system settings as consequential. Obtain the product-required confirmation immediately before the mutation when required.
- Never type passwords, API keys, tokens, payment data, or other sensitive information.
- Do not install packages, bypass security prompts, or delete data merely to make the task appear complete. If setup needs sudo, leave the command visible for the user to approve and enter credentials.
- Maintain a clear stop path: send `stop`, close the helper process, or ask the user to take over. Do not leave a remote-input session running after the task.
- A screenshot proves only what is visibly present. A helper command, a running application, or a browser connection is not proof that a native UI action succeeded.

## Reporting

Report the actual control path used, whether the result was visually verified, and any limitation. Distinguish a compositor screenshot from a native app binding, and distinguish a dry-run or environment check from a live pointer action.

For the setup and copy instructions, read [README.md](README.md).
