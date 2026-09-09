# Ubuntu Desktop Control for ChatGPT

A reusable Codex/ChatGPT skill for verified Ubuntu GNOME desktop screenshots, real pointer movement, keyboard input, and safe visible UI automation when the normal computer-use surface exposes only a browser.

## What it provides

The skill connects three pieces:

- ChatGPT/Codex skill instructions for safe, screenshot-first desktop work.
- xdg-desktop-portal for capturing the complete visible desktop on Wayland.
- GNOME/Mutter RemoteDesktop D-Bus for real pointer, click, drag, and keysym events.

It does not bypass Linux security, provide root access, or make every Linux application behave like a native Windows or macOS connector.

## Repository contents

- ubuntu-desktop-control/SKILL.md — reusable skill instructions.
- ubuntu-desktop-control/README.md — skill-specific setup and helper reference.
- ubuntu-desktop-control/agents/openai.yaml — discovery metadata.
- ubuntu-desktop-control/scripts/portal_screenshot.py — Wayland desktop screenshot helper.
- ubuntu-desktop-control/scripts/mutter_remote_desktop.py — GNOME/Mutter pointer and keyboard helper.
- ubuntu-desktop-control/scripts/check_environment.py — read-only prerequisite check.

## Install in ChatGPT or Codex

Download or clone this repository, then install the ubuntu-desktop-control folder as a skill. In ChatGPT, use **Plugins → Skills → Create → Upload from your computer** and review the files before installing them. OpenAI's official guide is [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt/).

For local Codex, copy the folder to:

~~~text
~/.codex/skills/ubuntu-desktop-control/
~~~

Then invoke it explicitly with $ubuntu-desktop-control.

## Ubuntu prerequisites

The tested path uses Ubuntu GNOME on Wayland, the current user's graphical session, D-Bus, and the desktop portal. Install missing packages from a visible terminal:

~~~bash
sudo apt install python3-dbus python3-gi gir1.2-glib-2.0 xdg-desktop-portal xdg-desktop-portal-gnome
~~~

The user should enter any sudo password themselves. Run the read-only check:

~~~bash
cd ubuntu-desktop-control
python3 scripts/check_environment.py
~~~

## Prompts to give ChatGPT

### Inspect only

> Use $ubuntu-desktop-control. Inspect the connected Ubuntu desktop and take a fresh compositor screenshot. Tell me which visible applications are open and whether native app control is exposed. Do not click, type, launch, save, upload, or change anything.

### Open and use an application

> Use $ubuntu-desktop-control to open the visible Ubuntu application named Blender. Use real pointer and keyboard input only after checking the latest screenshot. Perform this exact task: [describe the task]. After every short action batch, capture the desktop again and verify the visible result. Stop if the UI differs from expectations.

### Draw or edit with the real pointer

> Use $ubuntu-desktop-control. In the already-open Blender window, use the real Ubuntu pointer to draw [object]. Do not generate a scripted substitute. Work in small verified strokes, capture a screenshot after each stage, and stop the pointer session when finished.

### File operation

> Use $ubuntu-desktop-control to create /home/my-user/Documents/example.txt through the visible Ubuntu desktop. Before making the change, show me what application and path you will use. After saving, take a fresh screenshot and verify the file is visibly present. Do not use sudo and do not touch any other files.

### Troubleshoot

> Use $ubuntu-desktop-control to diagnose why the Ubuntu desktop application is not controllable. Run only the read-only environment check, inspect a compositor screenshot, and report whether the problem is the browser connector, desktop portal, GNOME/Mutter input, permissions, or the application itself. Do not install packages or change settings without asking.

### General template

> Use $ubuntu-desktop-control for this Ubuntu desktop task:
>
> Target application/window: [name]
> Exact desired result: [one concrete outcome]
> Allowed actions: [click/type/drag/open/save]
> Do not do: [passwords, uploads, messages, deletion, sudo, etc.]
> Verification: take a fresh screenshot after each short action batch and confirm the result visually.
> Stop condition: stop immediately if the target window, prompt, or coordinates do not match.

## Advantages

- Gives ChatGPT a practical path to inspect the whole visible Ubuntu desktop when only a browser surface is exposed.
- Uses the Wayland-friendly compositor portal instead of treating an invalid or black capture as success.
- Uses GNOME/Mutter's remote-input path for real pointer motion, clicks, drags, and keyboard events.
- Makes visual verification part of the workflow, reducing false claims that an application changed.
- Includes safety boundaries, approval points, and an explicit stop command.
- Can be reviewed, copied, shared, and installed as a reusable workflow.

## Disadvantages and limits

This improves Ubuntu desktop use; it does not make Ubuntu equivalent to Windows or macOS computer use.

- The tested path targets Ubuntu GNOME/Mutter. KDE, Sway, Xfce, locked sessions, multiple users, remote desktops, and other compositors may need different adapters.
- Native app objects may still be absent from the ChatGPT/Codex bridge. This local helper is a separate bridge, not a magic connector added to the browser surface.
- Coordinates can drift with scaling, multiple monitors, pointer acceleration, window movement, or lag. Every action needs fresh visual verification.
- Some applications expose little accessibility information, so screenshot interpretation and raw pointer work are slower and less reliable than an app-specific API.
- Portal or Mutter permissions can expire or be denied. A locked screen or missing D-Bus service blocks the helper.
- Real pointer and keyboard input can change files, accounts, or external services. Do not use it for passwords, secrets, financial transactions, or unattended destructive work.
- Skill availability can differ by ChatGPT plan, workspace, and product surface; do not assume an installation on one surface automatically syncs to another.

## Manual helper use

Capture the complete desktop:

~~~bash
python3 ubuntu-desktop-control/scripts/portal_screenshot.py /tmp/ubuntu-desktop.png
~~~

Start the pointer session:

~~~bash
python3 ubuntu-desktop-control/scripts/mutter_remote_desktop.py
~~~

Commands accepted by the pointer helper:

~~~text
move DX DY       # relative pointer motion
moveabs AREA X Y # absolute motion inside an input area
button 272 1     # left-button press
button 272 0     # left-button release
key KEYSYM 1     # key press
key KEYSYM 0     # key release
stop             # end the remote session
~~~

For drawing, press the button, send several small move commands, release it, and stop the helper immediately when finished.

## Verification

From the repository root:

~~~bash
python3 -m compileall -q ubuntu-desktop-control
python3 ubuntu-desktop-control/scripts/check_environment.py
~~~

The environment check is read-only. Do not report a live desktop action as complete unless a fresh screenshot visibly confirms it.
