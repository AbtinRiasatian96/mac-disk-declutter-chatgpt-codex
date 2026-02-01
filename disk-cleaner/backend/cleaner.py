import os
import shutil
from datetime import datetime
from typing import Iterable

from send2trash import send2trash

from .config import history_log_path


def delete_items(paths: Iterable[str], mode: str) -> None:
    log_path = history_log_path()
    timestamp = datetime.now().isoformat(timespec="seconds")
    with open(log_path, "a", encoding="utf-8") as handle:
        for path in paths:
            if not os.path.exists(path):
                continue
            if mode == "trash":
                send2trash(path)
                action = "TRASH"
            else:
                _permanent_delete(path)
                action = "DELETE"
            handle.write(f"{timestamp} {action} {path}\n")


def _permanent_delete(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
