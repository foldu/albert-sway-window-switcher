"""
Here should be documentation
"""

from subprocess import run, PIPE
import json


from albertv0 import *

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Sway window switcher"
__version__ = "0.1"
__trigger__ = "win "
__author__ = "foldu"
__dependencies__ = ["swaymsg"]

iconPath = iconLookup("window-new")


class Window:
    __slots__ = "id", "workspace", "name"

    def __init__(self, id, workspace, name):
        self.id = id
        self.workspace = workspace
        self.name = name

    def focus(self):
        run(["swaymsg", "[con_id={}] focus".format(self.id)], check=True)

    def get_all():
        first_node = json.loads(
            run(["swaymsg", "-t", "get_tree"], check=True, stdout=PIPE).stdout
        )
        stack = [first_node]
        ret = []
        current_workspace = ""

        while len(stack) != 0:
            node = stack.pop()
            t = node["type"]
            if t in {"floating_con", "con"}:
                # it's a window
                if not node["focused"] and node.get("name", None):
                    ret.append(
                        Window(
                            id=node["id"],
                            workspace=current_workspace,
                            name=node["name"],
                        )
                    )
            elif t == "workspace":
                current_workspace = node["name"]

            try:
                stack += node["nodes"]
            except KeyError:
                pass

        return ret


def window_to_item(win):
    return Item(
        id=win.name,
        icon=iconPath,
        text=win.name,
        subtext="id: {}, workspace: {}".format(win.id, win.workspace),
        completion=win.name,
        actions=[FuncAction("Focus", lambda: win.focus())],
    )


def handleQuery(query):
    if query.isTriggered:
        try:
            all_windows = [
                win
                for win in Window.get_all()
                if query.string.casefold() in win.name.casefold()
            ]
        except Exception as e:
            critical(str(e))
            all_windows = []
        return [window_to_item(win) for win in all_windows]
