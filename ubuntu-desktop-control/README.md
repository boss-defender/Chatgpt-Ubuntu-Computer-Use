# Ubuntu Desktop Control skill

This folder is a portable Codex/ChatGPT skill for Ubuntu GNOME desktop control. It documents the working local path for:

- capturing the compositor view of the whole desktop;
- moving the real pointer and sending clicks or key events through GNOME/Mutter;
- verifying visible results after each short action batch; and
- stopping safely when the target window or state is not what was expected.

It is intentionally a skill package, not a replacement for the ChatGPT application or a promise that every Linux desktop exposes native app bindings. If the computer-use surface exposes only Chrome, the local D-Bus helpers can still operate the same user's GNOME session when the required services and permissions are available.

## Install the skill

Copy this whole folder to the skill directory used by the friend's ChatGPT/Codex installation:

```text
~/.codex/skills/ubuntu-desktop-control/
```

Or use the folder directly in an explicit skill reference:

```text
/home/boss/Documents/Ubuntu_computer-use_Chatgpt/ubuntu-desktop-control/SKILL.md
```

The skill can then be invoked explicitly as `$ubuntu-desktop-control` or by referring to the `SKILL.md` path.

## Ubuntu setup

The verified helpers use the system Python and the user's existing graphical session. On Ubuntu GNOME, install the D-Bus and portal packages once from a visible terminal if they are missing:

```bash
sudo apt install python3-dbus python3-gi gir1.2-glib-2.0 xdg-desktop-portal xdg-desktop-portal-gnome
```

The user should enter the sudo password themselves. Log out and back in if the desktop portal service was newly installed. A Wayland session is preferred; check it with:

```bash
printf 'session=%s desktop=%s wayland=%s\\n' "$XDG_SESSION_TYPE" "$XDG_CURRENT_DESKTOP" "$WAYLAND_DISPLAY"
```

Run the read-only diagnostic before attempting input:

```bash
python3 scripts/check_environment.py
```

PyAutoGUI is optional for X11-only fallbacks and is not required by the GNOME/Mutter path in this skill. If it is needed for a separate X11 application, install it in a virtual environment rather than into the system Python:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pyautogui pillow mss
```

On Wayland, PyAutoGUI/mss alone are not reliable evidence of whole-desktop capture or input; use the portal and Mutter helpers first.

## Basic use

Capture the complete current desktop. By default, the image is saved at `~/.codex/Screenshot_for_chatgpt-work/ubuntu-desktop.png`, keeping the user's `Pictures` folder clean:

```bash
python3 scripts/portal_screenshot.py
```

An explicit path is still supported when needed:

```bash
python3 scripts/portal_screenshot.py /tmp/ubuntu-desktop.png
```

The helper moves the portal-created file into the requested destination instead of leaving a duplicate in `~/Pictures`.

Start the pointer session:

```bash
python3 scripts/mutter_remote_desktop.py
```

Then send commands to that running process. `move` is relative motion; `button 272 1` and `button 272 0` press and release the left mouse button. For a drag, press once, send several small `move` commands, and release. Always capture a new screenshot after the action and inspect it.

Stop the session when finished:

```text
stop
```

## Important limitations

- The screenshot helper captures the compositor's current desktop, not an arbitrary hidden window.
- The pointer helper is tested for GNOME/Mutter and may not work on KDE, Sway, Xfce, a locked screen, a different user session, or a remote desktop without adaptation.
- Native app exposure in the ChatGPT/Codex computer-use bridge is separate from these local helpers. Installing this folder cannot add native-app entries to that bridge.
- Input is real and can change files or accounts. Use it only for a specific user request, preserve confirmation boundaries, and stop on unexpected UI.

## Files

- `SKILL.md` — instructions loaded by Codex/ChatGPT.
- `agents/openai.yaml` — display metadata for skill discovery.
- `scripts/check_environment.py` — read-only session and dependency check.
- `scripts/portal_screenshot.py` — portal-based whole-desktop screenshot.
- `scripts/mutter_remote_desktop.py` — GNOME/Mutter relative pointer and keysym input.
