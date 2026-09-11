# Ubuntu Desktop Control for ChatGPT

This repository packages a reusable `ubuntu-desktop-control` skill plus a small local companion prototype. Together they help ChatGPT/Codex work with a visible Ubuntu GNOME desktop when the normal computer-use surface exposes only a browser.

The skill can capture the compositor view of the whole desktop, move the real pointer, click, send keyboard events, and verify the visible result after each short action batch. It is designed for Ubuntu GNOME on Wayland, with clear safety boundaries and an explicit stop path.

## What problem this solves

Linux desktop computer use can be more limited than Windows or macOS when the assistant is connected only to a browser surface. A local Ubuntu session may have native applications open, but the browser connector does not automatically expose those windows as controllable app objects.

This project adds a local bridge:

```text
ChatGPT/Codex skill
        |
        +-- xdg-desktop-portal -> whole-desktop screenshots
        |
        +-- GNOME/Mutter D-Bus -> real pointer and keyboard events
        |
        +-- visible Ubuntu applications -> verified UI result
```

It does not bypass the desktop security model, turn ChatGPT into unrestricted root access, or guarantee that every Linux application will behave like a native Windows or macOS computer-use connector.

## Project contents

- `ubuntu-desktop-control/SKILL.md` — the reusable skill instructions.
- `ubuntu-desktop-control/README.md` — skill-specific setup and helper reference.
- `ubuntu-desktop-control/scripts/portal_screenshot.py` — compositor screenshot helper.
- `ubuntu-desktop-control/scripts/mutter_remote_desktop.py` — GNOME/Mutter pointer and keysym input helper.
- `ubuntu-desktop-control/scripts/check_environment.py` — read-only prerequisite check.
- `ubuntu_companion/` — an older local-first Responses API prototype with dry-run and audit behavior.

## Install the skill in ChatGPT or Codex

The easiest portable option is to download or clone this repository and install the `ubuntu-desktop-control` folder as a skill. In ChatGPT, open **Plugins → Skills → Create → Upload from your computer**, then select the skill folder or its packaged archive if the upload dialog requests an archive. Review the skill before installing it.

OpenAI describes skills as reusable workflows that can contain instructions, examples, and code. Availability and installation can differ by plan, workspace settings, and product surface; see the [official Skills in ChatGPT guide](https://help.openai.com/en/articles/20001066-skills-in-chatgpt/).

For a local Codex installation, copy the skill folder to:

```text
~/.codex/skills/ubuntu-desktop-control/
```

Then invoke it explicitly with `$ubuntu-desktop-control` when asking for Ubuntu desktop work.

## Ubuntu prerequisites

The tested path uses the system Python, the current user's graphical session, D-Bus, and the desktop portal. On Ubuntu GNOME, install missing packages from a visible terminal:

```bash
sudo apt install python3-dbus python3-gi gir1.2-glib-2.0 xdg-desktop-portal xdg-desktop-portal-gnome
```

The user should enter the sudo password themselves. Check the session without changing anything:

```bash
cd ubuntu-desktop-control
python3 scripts/check_environment.py
```

A healthy GNOME/Wayland session normally reports `XDG_SESSION_TYPE=wayland`, `dbus=OK`, `gi=OK`, and both the desktop portal and Mutter remote-desktop D-Bus names as available.

## Prompts to give ChatGPT

Start a task with an explicit request to use the skill, the target application, the desired result, and the verification requirement. These are useful copy-and-paste examples.

### Inspect first; do not change anything

```text
Use $ubuntu-desktop-control. Inspect the connected Ubuntu desktop and take a fresh compositor screenshot. Tell me which visible applications are open and whether native app control is exposed. Do not click, type, launch, save, upload, or change anything.
```

### Open and use an application

```text
Use $ubuntu-desktop-control to open the visible Ubuntu application named Blender. Use real pointer and keyboard input only after checking the latest screenshot. Perform this exact task: [describe the task]. After every short action batch, capture the desktop again and verify the visible result. Stop if the UI differs from expectations.
```

### Draw or edit with the real pointer

```text
Use $ubuntu-desktop-control. In the already-open Blender window, use the real Ubuntu pointer to draw [object]. Do not generate a scripted substitute. Work in small verified strokes, capture a screenshot after each stage, and stop the pointer session when finished.
```

### File operation

```text
Use $ubuntu-desktop-control to create `/home/my-user/Documents/example.txt` through the visible Ubuntu desktop. Before making the change, show me what application and path you will use. After saving, take a fresh screenshot and verify the file is visibly present. Do not use sudo and do not touch any other files.
```

### Troubleshoot a blocked native application

```text
Use $ubuntu-desktop-control to diagnose why the Ubuntu desktop application is not controllable. Run only the read-only environment check, inspect a compositor screenshot, and report whether the problem is the browser connector, the desktop portal, GNOME/Mutter input, permissions, or the application itself. Do not install packages or change settings without asking.
```

### Safe general-purpose template

```text
Use $ubuntu-desktop-control for this Ubuntu desktop task:

Target application/window: [name]
Exact desired result: [one concrete outcome]
Allowed actions: [click/type/drag/open/save]
Do not do: [passwords, uploads, messages, deletion, sudo, etc.]
Verification: take a fresh screenshot after each short action batch and confirm the result visually.
Stop condition: stop immediately if the target window, prompt, or coordinates do not match.
```

## Advantages

- Gives ChatGPT a practical path to inspect the whole visible Ubuntu desktop even when only a browser is exposed.
- Uses the Wayland-friendly compositor portal instead of treating a black X11 capture as a valid screenshot.
- Uses GNOME/Mutter's remote input path for real pointer motion, clicks, drags, and keyboard events.
- Makes verification part of the workflow, reducing false claims that an application changed when it did not.
- Includes safety boundaries: explicit task scope, no password handling, confirmation before consequential actions, audit-aware fallbacks, and a stop command.
- The skill is portable and can be reviewed, copied, shared, or uploaded as a reusable workflow.

## Disadvantages and limits

This improves Ubuntu desktop use; it does not make Ubuntu equivalent to Windows or macOS computer use.

- The path is tested for Ubuntu GNOME/Mutter. KDE, Sway, Xfce, locked sessions, multiple users, remote desktops, and other compositors may need different adapters.
- Native app objects may still be absent from the ChatGPT/Codex bridge. The local helper is a separate bridge, not a magic connector added to the browser surface.
- Pointer motion is relative and coordinate mapping can drift with scaling, multiple monitors, pointer acceleration, window movement, or lag. Every action needs visual verification.
- Some applications do not expose useful accessibility information, so screenshot interpretation and raw pointer work are slower and less reliable than an app-specific API.
- Portal or Mutter permissions can expire, be denied, or require the user to take over. A locked screen or missing D-Bus service blocks the helper.
- Real pointer and keyboard input can change files, accounts, or external services. The skill must not be used for passwords, secrets, financial transactions, or unattended destructive work.
- Uploaded skills are subject to ChatGPT plan, workspace, and product availability. Review the files before installation and do not assume that a skill installed on one surface automatically syncs to another.

## Manual helper use

Capture the current complete desktop:

```bash
python3 ubuntu-desktop-control/scripts/portal_screenshot.py /tmp/ubuntu-desktop.png
```

Start the pointer session:

```bash
python3 ubuntu-desktop-control/scripts/mutter_remote_desktop.py
```

The helper accepts:

```text
move DX DY       # relative pointer motion
button 272 1     # left-button press
button 272 0     # left-button release
key KEYSYM 1     # key press
key KEYSYM 0     # key release
stop             # end the remote session
```

For a drag or drawing stroke, press the button, send several small `move` commands, and release it. Stop the helper as soon as the requested task is complete.

## Verification and tests

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q ubuntu_companion tests ubuntu-desktop-control
python3 ubuntu-desktop-control/scripts/check_environment.py
```

The last check is read-only. Do not report a live desktop action as complete unless a fresh screenshot visibly confirms it.
