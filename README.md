# Ubuntu Desktop Control for ChatGPT

A reusable Codex/ChatGPT skill for verified Ubuntu GNOME desktop screenshots, real pointer movement, keyboard input, and safe visible UI automation when the normal computer-use surface exposes only a browser.

## What it provides

The skill connects three pieces:

- ChatGPT/Codex skill instructions for safe, screenshot-first desktop work.
- xdg-desktop-portal for capturing the complete visible desktop on Wayland.
- GNOME/Mutter RemoteDesktop D-Bus for real pointer, click, drag, and keysym events.

It does not bypass Linux security, provide root access, or make every Linux application behave like a native Windows or macOS connector.

# Install in ChatGPT or Codex

Follow the steps below to load the skills contained in this repository into your ChatGPT Work session.

**1. Download or Clone the Repository**

Download this repository as a ZIP file, or clone it using Git.

After downloading, open the repository folder.

**2. Unzip the Required File**

Inside the repository, find the file named:

```text
UnZip-it-first
```

Unzip/extract this file.

After extraction, you should have:

* `README.md`
* Two additional folders containing the skill files

Keep the entire structure intact.

**3. Copy the Folder Path**

Copy the **full path of the repository folder** containing:

```text
README.md
+ Folder 1
+ Folder 2
```

For example:

on Linux:

```text
/home/yourname/Downloads/repository-name
```

**4. Open ChatGPT Work**

Open your ChatGPT **Work** session where you want to use these skills.

Paste the repository/folder path into the conversation and use the following prompt.

**5. Paste This Prompt**

```text
Please scan and analyze the entire folder at this path:

[PASTE THE FULL FOLDER PATH HERE]

I want you to fully inspect the repository, including:

- README.md
- Both folders extracted from "UnZip-it-first"
- All files and subfolders inside those folders
- Any skill definitions, instructions, documentation, examples, configuration files, scripts, or supporting resources

Do not analyze only the README.md. Recursively inspect the complete folder structure.

Your tasks:

1. Identify every skill contained in the repository.
2. Read and understand each skill's instructions, purpose, workflow, requirements, constraints, and usage patterns.
3. Understand how the skills relate to each other.
4. Identify important dependencies, tools, commands, file structures, conventions, and prerequisites.
5. Determine how each skill should be used in future tasks.
6. Pay attention to any priority rules, safety restrictions, required workflows, or instructions that must be followed.
7. Do not skip files just because they appear secondary or technical.
8. Check for duplicate, conflicting, outdated, or overlapping instructions and explain how they should be resolved.
9. Build a clear internal understanding of the complete skill system.

After analyzing everything, treat these skills as reusable knowledge for ChatGPT Work.

When appropriate in future tasks, use the relevant skill instructions automatically instead of asking me to explain them again. So save it or keep it as your additional skills.

Important:
- Do not modify, delete, rename, or move any files.
- Do not execute anything unless it is necessary for understanding the repository.
- Do not assume a file's purpose without reading it.
- Do not stop after finding the first skill.
- Recursively inspect the entire repository.
- Base your understanding on the actual contents of the files.

At the end, provide me with:

A. A complete list of all discovered skills
B. A short explanation of what each skill does
C. The important rules/workflows you learned
D. Any dependencies or prerequisites
E. Any conflicts, missing files, or problems you found
F. A concise summary confirming that you analyzed the entire folder

Most importantly, preserve the useful instructions from these files as reusable skill knowledge for Work.
```

**6. Important Note**

ChatGPT's official documentation explains how Skills work and how they can be used in ChatGPT.

Official guide:

https://help.openai.com/en/articles/20001066-skills-in-chatgpt/

### Folder Structure

Your final folder should look approximately like this:

```text
repository-name/
│
├── README.md
│
├── folder-1/
│   ├── ...
│   └── ...
│
└── folder-2/
    ├── ...
    └── ...
```

**Important**

Use the **parent repository folder path**, not the path of only one individual skill folder.

The goal is for ChatGPT to inspect the **entire repository**, understand the complete skill collection, and use the relevant instructions during future work.



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
