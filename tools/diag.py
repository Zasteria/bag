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
PRESS = "WTP PRESS "
PRESSAT = "WTP PRESSAT"


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
    if at >= 0:
        return line[at:].rstrip()
    # Строка движка: `[14:27:01][jomini_effect_impl.cpp:2531]: Район Тырговиште
    # (3574)`. Нужна её вторая половина -- имя локации; всё до последней `]: `
    # это отметка времени и файл движка, и читать их незачем.
    mark = line.rfind("]: ")
    return (line[mark + 3:] if mark >= 0 else line).rstrip()


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

    **Нажатия редактора идут в отчёт вперёд него самого.** Мод пишет строку
    `WTP PRESS` в момент нажатия, то есть до того, как нажата «Диагностика», --
    и это единственная хронология, которая вообще есть: окно изменений
    сравнивает план с сохранённым и по устройству своему сливает два нажатия по
    одной локации в одну строку. Владелец, 2026-09-05: «В окне изменений -- всё
    смешивается. Там нет хронологии изменений… Так что сам проверяй всё в
    диагностике.» Отчёту достаются нажатия, сделанные после прошлого отчёта, --
    ровно то, что он и описывает.

    **Имя локации -- строка над меткой `WTP PRESSAT`, и только она.** Его пишет
    `debug_log_scopes` изнутри скоупа локации; метка идёт сразу следом и не
    читает ничего, поэтому между ними встать нечему. Первая версия брала строку
    над самим нажатием, и в прогоне 2026-09-06 подписала первое нажатие строкой
    `Important assertion failed: … (Getting player in synchronous state)` --
    движок ругается на `GetPlayer` внутри `debug_log` один раз за сессию, и это
    попало ровно между именем и строкой. Метки нет -- нажатие идёт без имени,
    как и то, у которого обход никуда не встал.

    **Список нажатий отдаёт «Диагностика», а «Показать изменения» -- нет.** Обе
    кнопки пишут свой кусок между `BEGIN` и `END`, и первая версия отдавала
    нажатия тому куску, который случился раньше: нажал «Показать изменения»,
    потом «Диагностика» -- и хронология оставалась в окне изменений, а в отчёте
    её не было. Кусок узнаётся по строке `EDIT asked`, которую пишет только
    диагностика.
    """
    found: list[list[str]] = []
    current: list[str] | None = None
    waiting: list[str] = []          # нажатия, у которых отчёта ещё не было
    previous = ""
    named = ""                       # имя локации, снятое с метки PRESSAT
    for line in text.splitlines():
        if BEGIN in line:
            current = list(waiting)
        if current is None:
            if PRESSAT in line:
                if TAG not in previous:
                    named = strip_prefix(previous)
            elif PRESS in line:
                if named:
                    waiting.append(named)
                waiting.append(strip_prefix(line))
                named = ""
            previous = line
            continue
        current.append(strip_prefix(line))
        if END in line:
            found.append(current)
            if any(l.startswith("WTP EDIT asked") for l in current):
                waiting = []
            current = None
        previous = line
    if current:
        current.append("WTP ==== ОТЧЁТ ОБОРВАН: в логе нет строки END ====")
        found.append(current)
    return found


RIGHT_NAMES = {
    "constantinopolitan_silk_monopoly_rights": "шёлковая монополия",
    "flemish_cloth_industries_right": "фламандское сукно",
    "royal_artisan_rights": "ремесленные",
    "royal_book_rights": "книгопечатные",
    "royal_brewing_rights": "винокуренные",
    "royal_jewelry_rights": "ювелирные",
    "royal_masonry_rights": "каменные и стекольные",
    "royal_naval_rights": "корабельные",
    "royal_textile_rights": "текстильные",
    "royal_tooling_rights": "инструментальные",
    "royal_weaponry_rights": "оружейные",
    "scandinavian_bergslag_privileges": "бергслаген",
    "scandinavian_tar_privileges": "смоляные",
}


def right_legend(lines: list[str]) -> dict[int, str]:
    """Номер права -> его имя, прочитанное из строки `RQ legend` самого отчёта.

    **Из отчёта, а не из таблицы здесь.** Число прав меняется вместе с модом, и
    список, зашитый в читалку, разъехался бы молча -- а имя не то, это подпись
    под чужим числом. `RIGHT_NAMES` только переводит ключ на русский, и ключ, для
    которого перевода нет, печатается как есть.
    """
    legend = next((l for l in lines if l.startswith("WTP RQ legend")), "")
    out: dict[int, str] = {}
    for pair in re.findall(r"(\d+)=([a-z_]+)", legend):
        out[int(pair[0])] = RIGHT_NAMES.get(pair[1], pair[1])
    return out


def grantable_rights(lines: list[str]) -> set[int] | None:
    """Номера прав, которые эта держава вообще может выдать, или `None`.

    **Оценка есть у всякого права, а выдать можно не всякое.** `RQ` печатает то,
    что земля заплатила бы за связку, и печатает это для всех тринадцати -- в том
    числе для шёлковой монополии Константинополя и для скандинавских привилегий,
    которых у Мюнстера не будет никогда. Строка `RIGHT` знает разницу
    (`grantable=`), и без неё «текстильные 620» в списке читается как право,
    которое почему-то не досталось городу, а не как чужое.

    `None` -- отчёт старее этого поля. **Читалка, которая на старом отчёте
    объявляет чужими все права разом, хуже, чем читалка без этой пометки**: это
    ровно тот предохранитель, который срабатывает всегда
    (`docs/pitfalls/diagnosis.md`).
    """
    out = set()
    seen = False
    for line in lines:
        if not line.startswith("WTP RIGHT "):
            continue
        number = re.match(r"WTP RIGHT (\d+)", line)
        state = field(line, "grantable")
        if number is None or state is None:
            continue
        seen = True
        if state:
            out.add(int(number.group(1)))
    return out if seen else None


def render_rq(line: str, names: dict[int, str], granted: int | None,
              grantable: set[int] | None) -> str:
    """Строка `RQ` по-человечески: права по убыванию оценки, выданное помечено.

    Владелец, 2026-09-03: «Понятия не имею где конкретно искать строку Гослара».
    Числа в отчёте были, но `1=0 2=0 3=0` -- это не ответ на вопрос «почему этот
    город получил именно это право», а сырьё для ответа. Ответ -- вот эта строка.

    Права, которых держава выдать не может, идут в конце и помечены: их оценка
    объясняет не выбор города, а только то, чего он лишён по происхождению.
    """
    scores = [(int(k), int(float(v))) for k, v in re.findall(r"(\d+)=(-?[\d.]+)", line)]
    scores = [(k, v) for k, v in scores if v > 0]
    if not scores:
        return "    права: ни одно право здесь ничего не набрало"
    ours = (lambda number: True) if grantable is None else grantable.__contains__
    scores.sort(key=lambda kv: (not ours(kv[0]), -kv[1]))
    parts = []
    for number, value in scores:
        name = names.get(number, str(number))
        if not ours(number):
            parts.append(f"{name} {value} (не для этой державы)")
        else:
            parts.append(f"{name} {value}" + (" ← выдано" if number == granted else ""))
    return "    права: " + " | ".join(parts)


def fold(lines: list[str]) -> list[str]:
    """Свести `LG`-строки к одной строке на локацию и подписать её именем.

    В логе локация названа отдельной строкой (это `debug_log_scopes`), потом
    идут её числа, потом по строке на каждый поставленный товар. Читать это
    подряд невозможно, а сложенное -- можно: одна строка на локацию, и в ней
    сразу видно, что город получил, а что досталось селу.

    **Имя берётся одно, даже если движок назвал локацию дважды.** Отчёты до
    2026-09-03 звали `debug_log_scopes` и перед `L`, и перед `RQ`, и каждая
    строка начиная со второй уносила имя предыдущей: «WTP L Район Липпштадт
    (980) Район Зост (981) rank=2». Лишний вызов убран в самом моде, но читалка
    не должна снова разъехаться молча, если он вернётся, — а свести две подписи
    к одной она может и без него.
    """
    names = right_legend(lines)
    grantable = grantable_rights(lines)
    out: list[str] = []
    pending: list[str] = []          # строки без метки WTP: имя локации от игры
    goods: list[str] = []
    moved: list[str] = []            # что этот план изменил против прошлого
    row: str | None = None
    rq: str | None = None            # оценки прав города, идут внутри его блока

    def flush() -> None:
        nonlocal row, goods, rq, moved
        if row is None:
            # Оценки прав без своей локации: такого быть не должно, и если стало
            # -- это видно, а не съедено.
            if rq:
                out.append("~ " + rq)
                rq = None
            return
        out.append(row + (" | " + ", ".join(goods) if goods else " | -- пусто"))
        # **Что этот план изменил здесь против прошлого.** Ровно то, о чём
        # владелец просил 2026-09-03: «"локация" -- убрано X добавлено Y».
        if moved:
            gone = [g[1:] for g in moved if g.startswith("-")]
            came = [g[1:] for g in moved if g.startswith("+")]
            parts = []
            if gone:
                parts.append("убрано " + ", ".join(gone))
            if came:
                parts.append("добавлено " + ", ".join(came))
            out.append("    изменено: " + "; ".join(parts))
        if rq:
            match = re.search(r"\bright=(\d+)", row)
            granted = int(match.group(1)) if match and match.group(1) != "0" else None
            out.append(render_rq(rq, names, granted, grantable))
        row, goods, rq, moved = None, [], None, []

    for line in lines:
        if not line:
            continue
        if line.startswith("WTP LG "):
            goods.append(line[len("WTP LG "):])
            continue
        if line.startswith("WTP LD "):
            moved.append(line[len("WTP LD "):])
            continue
        # **`RQ` принадлежит своей локации и не должна её закрывать.** Она
        # приходит внутри блока города, между `L` и `LG`, и без этой ветки
        # `flush` сработал бы раньше товаров: строка локации ушла бы «пустой», а
        # товары повисли бы ни на чём.
        #
        # **`RQ legend` -- не она.** Это подпись под номерами, одна на отчёт, и
        # `startswith("WTP RQ ")` ловил её тоже: в отчётах до 2026-09-03 она
        # приходила после `LOCS`, когда никакой локации уже не открыто, и
        # `flush` выбрасывал её молча -- в отчёте владельца легенды нет ни в
        # одном из трёх нажатий. Приди она на строку раньше, она бы затёрла
        # оценки последнего города.
        if re.match(r"WTP RQ \d", line):
            rq = line
            continue
        # **Нажатие редактора несёт своё имя так же, как локация.** Строка
        # `debug_log_scopes` стоит над ним ровно затем, и без этой ветки она
        # уехала бы в «~ …» отдельной строкой, а нажатие осталось бы без места.
        if line.startswith(PRESS):
            flush()
            named = [part for part in (p.strip() for p in pending) if part]
            name = named[-1] if named else ""
            out.extend("~ " + stray for stray in named[:-1])
            pending = []
            out.append(PRESS + (name + " " if name else "") + line[len(PRESS):])
            continue
        if line.startswith("WTP L "):
            flush()
            # **Имя -- последняя подпись перед строкой, а не все они склеенные.**
            # Движок называет текущую область на каждый `debug_log_scopes`, и
            # подпись, пришедшая раньше внутри предыдущего блока, называет
            # предыдущую локацию. Ближайшая к строке -- её собственная.
            named = [part for part in (p.strip() for p in pending) if part]
            name = named[-1] if named else ""
            out.extend("~ " + stray for stray in named[:-1])
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


def plural(count: int, one: str, few: str, many: str) -> str:
    """«1 домик», «2 домика», «5 домиков» -- строка для человека, а не для лога.

    Отчёт для сессии может быть каким угодно; сводка «коротко» существует ровно
    затем, чтобы её читал владелец, и «1 домик(ов)» в ней -- это тот же
    неготовый инструмент, что и сырой лог вместо укладки.
    """
    tail, hundred = count % 10, count % 100
    if tail == 1 and hundred != 11:
        word = one
    elif 2 <= tail <= 4 and not 12 <= hundred <= 14:
        word = few
    else:
        word = many
    return f"{count} {word}"


def field(line: str, name: str) -> int | None:
    """Число из `name=<число>` в строке отчёта."""
    found = re.search(r"\b%s=(-?\d+)" % re.escape(name), line)
    return int(found.group(1)) if found else None


def good_names(lines: list[str]) -> dict[int, str]:
    """Номер товара -> его имя, из строк `G<n>` самого отчёта.

    **Из отчёта, а не из таблицы здесь** -- по той же причине, что и права:
    порядок товаров задаёт мод и меняется вместе с ним, а подпись под чужим
    номером хуже голого номера. Строка нажатия печатает номер, потому что
    47 веток на каждое нажатие -- это диспетчер на горячем пути ради того, что
    читалка делает даром.
    """
    out: dict[int, str] = {}
    for line in lines:
        found = re.match(r"WTP G(\d+) (\S+) ", line)
        if found:
            out[int(found.group(1))] = found.group(2)
    return out


def journal(lines: list[str]) -> list[str]:
    """Нажатия редактора по порядку, по-русски.

    Владелец, 2026-09-05: «В окне изменений -- всё смешивается. Там нет
    хронологии изменений… Так что сам проверяй всё в диагностике.» Окно
    изменений -- разница с сохранённым планом, а не журнал: два нажатия по одной
    локации в нём одна строка, и какое было первым, из неё не достать. Лог --
    хронология по устройству, и вот она.
    """
    names = good_names(lines)
    name = lambda number: names.get(number or 0, "№%s" % number)
    charters = right_legend(lines)
    charter = lambda number: charters.get(number or 0, "грамота №%s" % number)
    out: list[str] = []
    for line in lines:
        if not line.startswith(PRESS):
            continue
        tail = re.search(r"\bn=\d", line)
        where = line[len(PRESS):tail.start()].strip() if tail else ""
        n, op = field(line, "n"), field(line, "op")
        done, fail = field(line, "done"), field(line, "fail")
        esg, evicted = field(line, "esg"), field(line, "evicted")
        if op == 1:
            what = "«+1» " + name(field(line, "good"))
            if done and evicted:
                got = "поставлено, вытеснен " + name(esg)
            elif done:
                got = "поставлено на свободное место"
            elif fail:
                got = "отказано, всё возвращено"
            else:
                got = "ничего не сделано: не нашлось где"
        elif op == 2:
            what = "«−1» " + name(field(line, "good"))
            if done and field(line, "norefill"):
                got = "убрано, место осталось пустым"
            elif done:
                got = "убрано, место занял " + name(esg)
            else:
                got = "ничего не сделано: убирать нечего"
        elif op in (3, 4):
            # **Грамоты: нажатие переставляет её, а не добавляет.** `rfrom` --
            # чья была локация, `rto` -- чьей стала; на «+1» вторая та, что
            # нажали, на «−1» первая.
            src, dst = field(line, "rfrom"), field(line, "rto")
            what = ("«+1» " + charter(dst)) if op == 3 else ("«−1» " + charter(src))
            if done and op == 3:
                got = "город передан, взят у «%s»" % charter(src)
            elif done:
                got = "снята, город достался «%s»" % charter(dst)
            elif fail:
                got = "отказано: город передать некому"
            else:
                got = "ничего не сделано: не нашлось города"
        else:
            continue
        out.append("  %s. %s%s: %s"
                   % (n, what, " → " + where if where else "", got))
    if not out:
        return []
    return ["Журнал нажатий (по порядку, из лога -- в окне изменений хронологии "
            "нет):"] + out


def digest(lines: list[str]) -> list[str]:
    """Разбор отчёта в несколько строк по-русски.

    **Он существует, потому что отчёт не для человека.** Владелец, 2026-09-02:
    «проверить насколько всё идеально и выгодно распределено я не могу из-за
    того что это сложно для меня как человека». Числа в отчёте есть, а вывод из
    них -- арифметика, и её делает эта функция, а не он.
    """
    out: list[str] = ["=== коротко ==="]
    first = lambda prefix: next((l for l in lines if l.startswith(prefix)), "")

    selftest = first("WTP SELFTEST 1")
    if selftest and "=12345 " not in selftest:
        out.append("!! самопроверка не вернула 12345 -- числа ниже верить нельзя")

    pas, room, gain = first("WTP PASS"), first("WTP ROOM"), first("WTP GAIN")
    placed, rooms = field(pas, "placed"), field(pas, "rooms")
    if placed is not None and rooms:
        out.append("Земля: %d зданий на %d мест (%d%% заполнено), локаций %s, "
                   "провинций %s" % (placed, rooms, round(100 * placed / rooms),
                                     field(pas, "used_locs"), field(pas, "provs")))
    fed, total = field(gain, "fed"), field(gain, "gain_total")
    if fed is not None and placed:
        out.append("Выгода от места: %d зданий из %d (%d%%) что-то получают от "
                   "местного сырья; в среднем %.1f%% от потолка своего рецепта"
                   % (fed, placed, round(100 * fed / placed),
                      (total or 0) / placed / 10))
    if room:
        out.append("Тумблеры сейчас: город %s, село %s (из %s городской стороны, "
                   "настоящего городского ранга %s)"
                   % (field(room, "town"), field(room, "village"),
                      field(room, "towns"), field(room, "rank or above")))

    # **Ручные веса, если они выставлены.** Вес переживает план, сохранение и
    # смену области, поэтому забытый вес неотличим от формулы, которая сошла с
    # ума. Печатается только то, что не ноль.
    weights = [(l.split()[2], field(l, "weight"), field(l, "band")) for l in lines
               if l.startswith("WTP WEIGHT ")]
    weights = [(g, w, b) for g, w, b in weights if w]
    if weights:
        out.append("Ручные веса (одна полоса = %d): " % (weights[0][2] or 200)
                   + ", ".join("%s %+d" % (g, w) for g, w, _ in weights))
    moved = field(room, "moved")
    if moved is not None:
        out.append("Против прошлого плана изменилось локаций: %d%s"
                   % (moved, "" if moved else " — ни одной"))

    counts = {}
    for line in lines:
        if line.startswith("WTP G") and " | ng=" in line:
            name = line.split()[2]
            n = field(line.split("| ng=")[1], "n")
            if n is not None:
                counts[name] = n
    if counts:
        placed_goods = {g: n for g, n in counts.items() if n}
        order = sorted(placed_goods.items(), key=lambda kv: -kv[1])
        share = sorted(placed_goods.values())
        half = share[len(share) // 2]
        out.append("Товары: поставлено %d из %d, что земля вообще может делать; "
                   "на товар от %d до %d зданий, посередине %d"
                   % (len(placed_goods), len(counts), share[0], share[-1], half))
        out.append("  больше всех: " + ", ".join("%s %d" % kv for kv in order[:6]))
        out.append("  меньше всех: " + ", ".join("%s %d" % kv for kv in order[-6:]))

    rights = [(line.split()[3], field(line, "given")) for line in lines
              if line.startswith("WTP RIGHT")]
    taken = [(k, v) for k, v in rights if v]
    if taken:
        can = sum(1 for line in lines
                  if line.startswith("WTP RIGHT") and field(line, "grantable"))
        out.append("Права: выдано %d, разных %d из %d возможных этой державе, "
                   "больше всего у «%s» (%d)"
                   % (sum(v for _, v in taken), len(taken), can or len(taken),
                      RIGHT_NAMES.get(max(taken, key=lambda kv: kv[1])[0],
                                      max(taken, key=lambda kv: kv[1])[0]),
                      max(taken, key=lambda kv: kv[1])[1]))
        # **Ровно ли легли грамоты** -- вопрос, который владелец задавал трижды:
        # «я не буду удовлетворён пока не увижу в вестфалии относительно
        # одинаковое количество каждого городского права». Лестница уровней
        # поднимает потолок по одному городу, так что разброс между самой частой
        # и самой редкой грамотой должен быть 1, самое большее 2. Больше --
        # значит, какую-то грамоту земля не пускает вовсе, и это видно в «RQ».
        grantable = [line.split()[3] for line in lines
                     if line.startswith("WTP RIGHT") and field(line, "grantable")]
        spread = sorted((dict(rights).get(k, 0), k) for k in grantable)
        if len(spread) > 1:
            low, high = spread[0], spread[-1]
            out.append("  разброс: от %d («%s») до %d («%s»)%s"
                       % (low[0], RIGHT_NAMES.get(low[1], low[1]),
                          high[0], RIGHT_NAMES.get(high[1], high[1]),
                          "" if high[0] - low[0] <= 2 else
                          " -- перекос, смотри «RQ» у редкой"))
    # **Какие грамоты план предполагает, а выдать сегодня нельзя.** План
    # намеренно считает по `potential`, а не по открытию: это цель, к которой
    # строят, и девять общих грамот приходят в третью эпоху всем сразу
    # (`generate.plan_right_gates`). Вопрос «а могу ли я её выдать прямо сейчас»
    # от этого не исчезает, и отвечает на него только эта строка.
    locked = [line.split()[3] for line in lines
              if line.startswith("WTP RIGHT") and field(line, "given")
              and field(line, "unlocked") == 0]
    if locked:
        out.append("Из них ещё не открыты (план на них рассчитывает, выдать "
                   "сегодня нельзя): " + ", ".join(RIGHT_NAMES.get(k, k) for k in locked))

    # **Почему у товара ровно столько домиков.** Это вопрос, который владелец
    # задаёт чаще всех остальных вместе взятых -- «где хоть одна печка болотного
    # железа» -- и до 2026-09-03 отчёт на него не отвечал: `q` печатается после
    # плана и несёт всё, что добавила открытая лестница, так что «квота 2» на
    # экране могла означать квоту 1. `open_sweeps` -- то, что надо вычесть.
    #
    # **Печатается один случай, и он однозначен**: товар поставил *ровно* свою
    # квоту, и квота мала потому, что область уже добывает это сырьё сама. Это
    # правило владельца, 2026-09-01 («там уже есть 2 рго глины — тебе нужно
    # всего 3 домика»), и единственное место, где его видно в работе. Общее
    # «упёрлись в квоту» сюда не идёт: на заполненной земле в квоту упирается
    # всё подряд, и строка из двадцати товаров ничего не отвечает.
    opensw = field(pas, "open_sweeps")
    if opensw is not None:
        capped = []
        for line in lines:
            # `WTP GOODS legend` тоже начинается с «WTP G» и тоже несёт « | ng=»;
            # строка самого товара -- та, где после G стоит номер.
            if not re.match(r"WTP G\d+ ", line) or " | ng=" not in line:
                continue
            tail = line.split("| ng=")[1]
            ng = field("ng=" + tail, "ng")
            q, n, rgo = (field(tail, k) for k in ("q", "n", "rgo"))
            if not ng or not n or q is None or not rgo:
                continue
            if n == q - opensw and n < ng:
                capped.append("%s: %s при %d РГО и своей доле %d, мест на земле %d"
                              % (line.split()[2], plural(n, "домик", "домика",
                                                         "домиков"), rgo,
                                 q - opensw, ng))
        if capped:
            # **Строка называет всю арифметику, а не одно РГО.** Она говорила
            # «1 РГО = 1 домик, квота на столько же меньше» — и владелец поймал её
            # на этом 2026-09-03: у железа 1 домик при 2 РГО, что по этому правилу
            # должно давать 3, а не 1. Правило было верным, а доля, из которой
            # вычитали, — нет: она считалась от мест, оставшихся после грамот, и
            # выходила 2, так что два РГО забирали её целиком. Теперь на экране
            # обе цифры, и такой вопрос больше не стоит прогона.
            base = field(pas, "quota")
            out.append("Упёрлись в свою долю (доля земли %s на товар, минус одно "
                       "за каждое своё РГО, но не ниже 1): %s"
                       % (base if base is not None else "?", "; ".join(capped)))

    # **Правка плана — своей строкой.** Она была невидима для отчёта до
    # 2026-09-04, и это стоило прогона, в котором 27 домиков встали сверх лимита,
    # а сказать почему было нечем. Владелец: «Добавляй скан информации для себя в
    # диагностике на функцию редактора, чтобы ты видел чё там происходит.»
    asked, scan, walk = (first("WTP EDIT asked"), first("WTP EDIT scan"),
                         first("WTP EDIT walk"))
    presses = field(asked, "presses")
    if presses:
        op = {1: "«+1»", 2: "«−1»", 3: "«+1» грамота",
              4: "«−1» грамота"}.get(field(asked, "op"), "ничего")
        done, fail = field(asked, "done"), field(asked, "fail")
        got = ("поставлено" if done else
               "отказано, всё возвращено" if fail else "ничего не сделано")
        which = (field(asked, "right") if (field(asked, "op") or 0) > 2
                 else field(asked, "good"))
        idle = field(asked, "idle")
        out.append("Правка: нажатий %d%s, последнее — %s №%s: %s"
                   % (presses,
                      "" if idle is None else ", из них впустую %d" % idle,
                      op, which, got))
        if field(scan, "hit"):
            out.append("  обход встал на локацию: %s, домиков %s из %s, жертва "
                       "№%s (выгода %s) — выселено: %s, место было: %s, "
                       "домиков стало %s"
                       % ("город" if field(scan, "town") else "село",
                          field(scan, "load"),
                          field(walk, "cap_urban") if field(scan, "town")
                          else field(walk, "cap_rural"),
                          field(scan, "esg"), field(scan, "esw"),
                          "да" if field(walk, "evicted") else "нет",
                          "да" if field(walk, "room") else "нет",
                          field(walk, "load_after")))
        else:
            out.append("  обход не нашёл ни одной локации: подходящих %s, из них "
                       "с местом или жертвой %s"
                       % (field(scan, "fitn"), field(scan, "cands")))

    out.extend(journal(lines))

    cut = [line.split()[1] for line in lines
           if line.startswith("WTP P") and re.search(r"sweeps=(\d+)/\1\b", line)]
    out.append("Проходы, упёршиеся в лимит кругов: " + (", ".join(cut) if cut else "нет"))
    out.append("=== дальше подробности, они для сессии ===")
    return out


def headline(lines: list[str]) -> list[str]:
    """Несколько строк, по которым сразу видно, что отчёт настоящий."""
    wanted = ("WTP BUILD methods", "WTP SELFTEST 1", "WTP PICK", "WTP PASS",
              "WTP GAIN", "WTP ROOM", "WTP EDIT asked", "WTP EDIT scan",
              "WTP EDIT walk")
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
            folded = block if parsed.raw else fold(block)
            if len(chosen) > 1:
                body.append("### отчёт %d из %d" % (number, len(chosen)))
            # Разбор идёт первым: файл открывают сверху, и первое, что должно
            # быть видно -- это вывод, а не 47 строк счётчиков.
            body.extend(digest(folded))
            body.extend(folded)
            body.append("")
        # **Пустой файл не пишется никогда.** 2026-09-02: укладка выбросила все
        # строки разом, потому что не узнала их, и `diagnostics.txt` вышел в ноль
        # байт -- инструмент, который молча отдаёт пустоту, хуже отсутствующего.
        #
        # **Но и «стало меньше строк» -- не признак потери**: укладка затем и
        # нужна, чтобы товары локации ушли в её собственную строку, и на живом
        # логе она честно убирает четыре строки из пяти. Первая версия этой
        # проверки считала именно строки и на первом же настоящем отчёте
        # отдала сырое. Считается то, что теряться не должно: каждая строка
        # `WTP`, кроме `WTP LG`, обязана дойти до файла.
        raw = [line for block in chosen for line in block]
        # `WTP RQ` is folded into the location's own «права:» line, which does
        # not carry the tag -- so it is not lost, and counting it here as a line
        # that must survive fires the safety net on every report that has one.
        # It did, from 2026-09-03: the fold was never used, the file came out raw,
        # and `digest(raw)` then summed **all five presses into one** «коротко» --
        # 263 charters granted over 48 towns. A safety net that always fires is a
        # broken tool, not a careful one.
        # **Every line the fold consumes on purpose has to be listed here, and
        # forgetting one fires the net on every report.** It has happened twice:
        # `WTP RQ` in the morning of 2026-09-03 and `WTP LD` the same evening.
        # The rule to carry: a line folded into another line is not a lost line,
        # and the safeguard is about lines that vanish without a trace.
        folded = ("WTP LG ", "WTP RQ ", "WTP LD ")
        must = sum(1 for line in raw
                   if line.startswith(TAG)
                   and not line.startswith(folded))
        kept = sum(1 for line in body if line.startswith(TAG))
        if kept < must:
            print("Укладка потеряла %d строк из %d -- отдаю как есть."
                  % (must - kept, must))
            print("Покажите этот файл сессии: по нему видно, что за формат.")
            body = digest(raw) + raw
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
        for line in digest(fold(chosen[-1])):
            print(line)
        return 0

    print("Ни в одном из логов отчёта нет. Нажмите «Диагностика» в меню мода и")
    print("повторите; кнопка на вкладке «Расчёт», рядом с «Показать план».")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
