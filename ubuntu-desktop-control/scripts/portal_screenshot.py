from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


DEFAULT_SCREENSHOT_PATH = (
    Path.home() / ".codex" / "Screenshot_for_chatgpt-work" / "ubuntu-desktop.png"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture the current compositor desktop through xdg-desktop-portal."
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=DEFAULT_SCREENSHOT_PATH,
        help=(
            "PNG path to create (default: "
            f"{DEFAULT_SCREENSHOT_PATH})"
        ),
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    loop = GLib.MainLoop()
    result: dict[str, object] = {}

    def on_response(code, results, **_kwargs):
        result["code"] = int(code)
        result["results"] = dict(results)
        loop.quit()

    proxy = bus.get_object(
        "org.freedesktop.portal.Desktop",
        "/org/freedesktop/portal/desktop",
    )
    request_path = proxy.Screenshot(
        "",
        dbus.Dictionary({"interactive": dbus.Boolean(False)}, signature="sv"),
        dbus_interface="org.freedesktop.portal.Screenshot",
    )
    bus.add_signal_receiver(
        on_response,
        dbus_interface="org.freedesktop.portal.Request",
        signal_name="Response",
        path=str(request_path),
        bus_name="org.freedesktop.portal.Desktop",
    )
    GLib.timeout_add_seconds(20, loop.quit)
    loop.run()

    if result.get("code") != 0:
        raise SystemExit(f"portal screenshot failed: {result}")
    values = result.get("results", {})
    uri = str(values.get("uri", ""))
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        raise SystemExit(f"unexpected screenshot URI: {uri}")

    source = Path(unquote(parsed.path))
    # The portal may create its temporary file in ~/Pictures. Move it to the
    # dedicated Codex folder so the user's Pictures directory is not polluted.
    shutil.move(source, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
