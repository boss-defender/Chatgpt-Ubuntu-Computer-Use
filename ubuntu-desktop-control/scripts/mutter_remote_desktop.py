from __future__ import annotations

import sys

import dbus
from dbus.mainloop.glib import DBusGMainLoop


REMOTE = "org.gnome.Mutter.RemoteDesktop"
OBJECT = "/org/gnome/Mutter/RemoteDesktop"
INTERFACE = "org.gnome.Mutter.RemoteDesktop.Session"


def main() -> int:
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    remote = bus.get_object(REMOTE, OBJECT)
    session_path = remote.CreateSession(dbus_interface=REMOTE)
    session = bus.get_object(REMOTE, session_path)
    session.Start(dbus_interface=INTERFACE)
    print(f"READY {session_path}", flush=True)

    for raw_line in sys.stdin:
        parts = raw_line.strip().split()
        if not parts:
            continue
        command = parts[0]
        try:
            if command == "move" and len(parts) == 3:
                session.NotifyPointerMotionRelative(
                    float(parts[1]),
                    float(parts[2]),
                    dbus_interface=INTERFACE,
                )
            elif command == "moveabs" and len(parts) == 4:
                session.NotifyPointerMotionAbsolute(
                    parts[1],
                    float(parts[2]),
                    float(parts[3]),
                    dbus_interface=INTERFACE,
                )
            elif command == "button" and len(parts) == 3:
                session.NotifyPointerButton(
                    int(parts[1]),
                    dbus.Boolean(int(parts[2])),
                    dbus_interface=INTERFACE,
                )
            elif command == "key" and len(parts) == 3:
                session.NotifyKeyboardKeysym(
                    dbus.UInt32(int(parts[1])),
                    dbus.Boolean(int(parts[2])),
                    dbus_interface=INTERFACE,
                )
            elif command == "stop":
                session.Stop(dbus_interface=INTERFACE)
                print("STOPPED", flush=True)
                return 0
            else:
                print(f"ERR unsupported command: {raw_line.strip()}", flush=True)
                continue
            print("OK", flush=True)
        except Exception as exc:
            print(f"ERR {type(exc).__name__}: {exc}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
