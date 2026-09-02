#!/usr/bin/env python3
"""Забрать диагностику `where_to_produce` из логов игры.

Мод пишет отчёт в `debug.log` одним куском между `WTP ==== BEGIN` и
`WTP ==== END`. Этот скрипт находит последний такой кусок, чистит его от
префиксов лога, складывает строки по локациям в одну и кладёт результат
файлом рядом с репозиторием — и в буфер обмена, если это Windows.

Дальше остаётся вставить его в чат: там всё, что мод знает о последнем
расчёте, и читать это можно без игры.

    python3 tools/diag.py                 # найти логи игры и забрать последний отчёт
    python3 tools/diag.py <файл|папка>    # взять из этого лога или этой папки логов
    python3 tools/diag.py --raw           # без укладки строк, как в логе
    python3 tools/diag.py --all           # все отчёты в файле, а не последний

Почему это вообще нужно: только игрок может запустить игру, и один прогон —
самое дорогое, что здесь тратится (`docs/pitfalls/diagnosis.md`). Отчёт
существует, чтобы один прогон отвечал на весь вопрос сразу, а не на его
четверть.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAME_FOLDER = "Paradox Interactive/Europa Universalis V"
OUT = REPO / "diagnostics.txt"

BEGIN = "WTP ==== BEGIN"
END = "WTP ==== END"
TAG = "WTP "


def strip_prefix(line: str) -> str:
    """Убрать всё, что игра приписала перед нашей строкой.

    **Форма префикса не угадывается, а обходится.** Первая версия резала его
    регуляркой по предполагаемому виду `[16:04:22][effect.cpp:1234]: ` -- и на
    настоящем логе 2026-09-02 не совпала ни на одной строке, после чего `fold`
    выбросил их все и файл вышел в ноль байт. Резать надо по тому, что мы сами
    написали: `WTP` есть в каждой нашей строке и больше нигде.

    Строка без `WTP` -- это `debug_log_scopes`, называющая локацию. Она нужна
    целиком и не трогается.
    """
    at = line.find(TAG)
    return line[at:].rstrip() if at >= 0 else line.rstrip()


def documents() -> list[Path]:
    """Все правдоподобные папки «Документы», ответ реестра первым.

    То же, что делает `mods.py`: Windows разрешает переносить «Документы», а
    OneDrive переносит их не спрашивая, поэтому `%USERPROFILE%\\Documents` --
    догадка, а не ответ.
    """
    found: list[Path] = []
    if sys.platform == "win32":
        try:
            import winreg
            key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as handle:
                found.append(Path(winreg.QueryValueEx(handle, "Personal")[0]))
        except (ImportError, OSError):
            pass
    home = Path.home()
    found += [home / "Documents", home / "OneDrive/Documents",
              home / "OneDrive - Personal/Documents"]
    return [p for p in found if p.is_dir()]


def logs_folder() -> Path | None:
    """`Documents/Paradox Interactive/Europa Universalis V/logs`, если она есть."""
    for folder in documents():
        target = folder / GAME_FOLDER / "logs"
        if target.is_dir():
            return target
    return None


def sources(given: str | None) -> list[Path]:
    """Файлы, в которых искать отчёт: `debug.log` первым, `error.log` следом.

    В `error.log` мод пишет только заголовок -- этого хватает, чтобы понять,
    что расчёт был и с какими числами, если `debug.log` почему-то не дошёл.
    """
    if given:
        where = Path(given).expanduser()
        if where.is_file():
            return [where]
        if where.is_dir():
            return [where / name for name in ("debug.log", "error.log")
                    if (where / name).is_file()]
        return []
    folder = logs_folder()
    if not folder:
        return []
    return [folder / name for name in ("debug.log", "error.log")
            if (folder / name).is_file()]


def blocks(text: str) -> list[list[str]]:
    """Каждый отчёт из файла, по порядку. Незакрытый последний тоже отдаётся.

    Игра могла закрыться посреди записи, и половина отчёта лучше, чем ничего:
    неполный кусок помечается там, где его печатают.
    """
    found: list[list[str]] = []
    current: list[str] | None = None
    for line in text.splitlines():
        if BEGIN in line:
            current = []
        if current is None:
            continue
        current.append(strip_prefix(line))
        if END in line:
            found.append(current)
            current = None
    if current:
        current.append("WTP ==== ОТЧЁТ ОБОРВАН: в логе нет строки END ====")
        found.append(current)
    return found


def fold(lines: list[str]) -> list[str]:
    """Свести `LG`-строки к одной строке на локацию и подписать её именем.

    В логе локация названа отдельной строкой (это `debug_log_scopes`), потом
    идут её числа, потом по строке на каждый поставленный товар. Читать это
    подряд невозможно, а сложенное -- можно: одна строка на локацию, и в ней
    сразу видно, что город получил, а что досталось селу.
    """
    out: list[str] = []
    pending: list[str] = []          # строки без метки WTP: имя локации от игры
    goods: list[str] = []
    row: str | None = None

    def flush() -> None:
        nonlocal row, goods
        if row is None:
            return
        out.append(row + (" | " + ", ".join(goods) if goods else " | -- пусто"))
        row, goods = None, []

    for line in lines:
        if not line:
            continue
        if line.startswith("WTP LG "):
            goods.append(line[len("WTP LG "):])
            continue
        if line.startswith("WTP L "):
            flush()
            name = " ".join(pending).strip()
            pending = []
            row = ("WTP L " + (name + " " if name else "") + line[len("WTP L "):])
            continue
        if not line.startswith("WTP"):
            # Строка самой игры: имя локации перед её блоком, либо шум.
            pending.append(line)
            continue
        flush()
        # **Ничего не выбрасывается.** Не перед локацией такая строка -- это
        # `debug_log_scopes` над самопроверкой, то есть имя страны; либо чужая
        # запись, попавшая между нашими. И то и другое помечается `~` и остаётся
        # видимым: молча съеденная строка -- ровно то, из-за чего первый отчёт
        # пришёл пустым.
        out.extend("~ " + stray for stray in pending)
        pending = []
        out.append(line)
    flush()
    out.extend("~ " + stray for stray in pending)
    return out


def headline(lines: list[str]) -> list[str]:
    """Несколько строк, по которым сразу видно, что отчёт настоящий."""
    wanted = ("WTP BUILD methods", "WTP SELFTEST 1", "WTP PICK", "WTP PASS", "WTP ROOM")
    return [line for line in lines if line.startswith(wanted)]


def clipboard(text: str) -> bool:
    """Положить в буфер обмена. Windows -- `clip`, иначе честно сказать «нет».

    `clip.exe` читает stdin в кодовой странице консоли, если не увидит метку
    UTF-16LE в начале, -- поэтому `utf-16`, который её и ставит, а не
    `utf-16-le`, который нет. Иначе русские комментарии в отчёте приезжают
    кракозябрами.
    """
    for command in (["clip"], ["pbcopy"], ["xclip", "-selection", "clipboard"]):
        encoding = "utf-16" if command[0] == "clip" else "utf-8"
        try:
            subprocess.run(command, input=text.encode(encoding), check=True)
            return True
        except (OSError, subprocess.CalledProcessError):
            continue
    return False


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="diag.py",
        description="Забрать отчёт «Диагностика» мода where_to_produce из логов игры.")
    parser.add_argument("source", nargs="?",
                        help="файл лога или папка logs; по умолчанию -- логи игры")
    parser.add_argument("--raw", action="store_true",
                        help="не складывать строки локаций, оставить как в логе")
    parser.add_argument("--all", action="store_true",
                        help="все отчёты из файла, а не только последний")
    parser.add_argument("--out", metavar="FILE", default=str(OUT),
                        help=f"куда записать (по умолчанию {OUT.name} в корне репозитория)")
    parsed = parser.parse_args(argv[1:])

    files = sources(parsed.source)
    if not files:
        print("Логи игры не найдены.")
        print("Ожидались в: Documents/%s/logs" % GAME_FOLDER)
        print("Можно указать папку или файл прямо: python3 tools/diag.py <путь>")
        return 1

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        found = blocks(text)
        if not found:
            print("%s: отчёта нет" % path.name)
            continue
        chosen = found if parsed.all else found[-1:]
        body: list[str] = []
        for number, block in enumerate(chosen, start=1):
            if len(chosen) > 1:
                body.append("### отчёт %d из %d" % (number, len(chosen)))
            body.extend(block if parsed.raw else fold(block))
            body.append("")
        # **Пустой файл не пишется никогда.** 2026-09-02: укладка выбросила все
        # строки разом, потому что не узнала их, и `diagnostics.txt` вышел в ноль
        # байт -- инструмент, который молча отдаёт пустоту, хуже отсутствующего.
        # Если после укладки осталось меньше, чем было в логе, отдаётся сырое.
        raw = [line for block in chosen for line in block]
        if len([line for line in body if line.strip()]) < len(raw) // 2:
            print("Укладка не узнала строки этого лога -- отдаю как есть.")
            print("Покажите этот файл сессии: по нему видно, что за формат.")
            body = raw
        out = Path(parsed.out).expanduser()
        out.write_text("\n".join(body) + "\n", encoding="utf-8")

        print("%s: отчётов в файле %d, взят %s; строк в отчёте %d"
              % (path.name, len(found), "все" if parsed.all else "последний", len(raw)))
        print("Записано: %s  (%d строк)" % (out, len(body)))
        if clipboard("\n".join(body)):
            print("И скопировано в буфер обмена -- можно вставлять в чат.")
        else:
            print("Буфер обмена недоступен: откройте файл и скопируйте оттуда.")
        print()
        for line in headline(chosen[-1]):
            print("  " + line)
        return 0

    print("Ни в одном из логов отчёта нет. Нажмите «Диагностика» в меню мода и")
    print("повторите; кнопка на вкладке «Расчёт», рядом с «Показать план».")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
