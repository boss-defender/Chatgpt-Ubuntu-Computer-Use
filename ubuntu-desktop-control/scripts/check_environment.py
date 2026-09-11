from __future__ import annotations

import importlib.util
import os
import shutil


def module_status(name: str) -> str:
    return "OK" if importlib.util.find_spec(name) is not None else "MISSING"


def dbus_name_status(name: str) -> str:
    try:
        import dbus

        bus = dbus.SessionBus()
        owner = bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
        present = bool(
            owner.NameHasOwner(
                name,
                dbus_interface="org.freedesktop.DBus",
            )
        )
        return "OK" if present else "MISSING"
    except Exception as exc:  # diagnostic output should identify the blocker
        return f"ERROR: {exc}"


print(f"XDG_SESSION_TYPE={os.environ.get('XDG_SESSION_TYPE', '') or '<unset>'}")
print(f"XDG_CURRENT_DESKTOP={os.environ.get('XDG_CURRENT_DESKTOP', '') or '<unset>'}")
print(f"WAYLAND_DISPLAY={os.environ.get('WAYLAND_DISPLAY', '') or '<unset>'}")
print(f"DISPLAY={os.environ.get('DISPLAY', '') or '<unset>'}")
print(f"python3={shutil.which('python3') or 'MISSING'}")
print(f"module dbus={module_status('dbus')}")
print(f"module gi={module_status('gi')}")
print(
    "D-Bus org.freedesktop.portal.Desktop="
    + dbus_name_status("org.freedesktop.portal.Desktop")
)
print(
    "D-Bus org.gnome.Mutter.RemoteDesktop="
    + dbus_name_status("org.gnome.Mutter.RemoteDesktop")
)
