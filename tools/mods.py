#!/usr/bin/env python3
"""The mod manager: the workshop, the game's own copies, and this repository.

Everything the owner has to do by hand for a mod update, in one place and with
no session of mine in the loop:

    python3 tools/mods.py           the menu
    python3 tools/mods.py check     just the answer, for a script or a shortcut

What it can do, in the order the work actually happens:

1. **Look at every mod he is subscribed to** — not the five this repository
   tracks — and say which ones the workshop has moved on since Steam last
   downloaded them. That comparison is between Steam's own record of what is
   installed (`appworkshop_3450310.acf`) and Steam's public
   `GetPublishedFileDetails`, so it is the real answer rather than a guess from
   folder dates.

2. **Download the ones he picks, into the game's own workshop folder**, so the
   next launch loads them. Steam itself will not be told to do this on demand —
   hence the unsubscribe-and-resubscribe dance this replaces — so it is done
   with `steamcmd` under his own account and the result is copied over
   `steamapps/workshop/content/3450310/<id>/`, which is where the game reads
   mods from. Anonymous does not work for this app; that was measured.

3. **Update the copies in this repository**, either kind: `reference/mods/` for
   the mods something here is built against (whole, unedited) and
   `reference/playset/` for the rest (text only). Then rebuild everything
   generated from them and say what moved.

4. **Move a mod between those two**, which is the only decision in here that
   changes what this repository watches: promoting one adds it to
   `tools/workshop_mods.txt` and it starts arriving whole and getting checked
   daily on GitHub; demoting one puts it back in the text-only tree.

5. **Commit and push**, to whatever branch he says, `main` included.

Nothing here needs the repository to be checked out anywhere in particular and
nothing needs a session: steps 1 and 2 do not touch git at all, so it is
usable as a mod updater on a day when modding is the last thing on his mind.

Settings that are his rather than the repository's — where steamcmd lives, which
Steam account, which branch — go in `tools/mods.local.json`, which is ignored by
git.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refs  # noqa: E402
import workshop  # noqa: E402

APP_ID = workshop.APP_ID
SETTINGS = Path(__file__).resolve().parent / "mods.local.json"
STEAMCMD_ZIP = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"


# ------------------------------------------------------------------- settings


def settings_read() -> dict:
    if not SETTINGS.is_file():
        return {}
    try:
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def settings_write(values: dict) -> None:
    SETTINGS.write_text(json.dumps(values, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")


# ------------------------------------------------------------ where Steam is

STEAM_ROOTS = {
    "win32": [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam", r"C:\Steam"],
    "darwin": ["~/Library/Application Support/Steam"],
    "linux": ["~/.steam/steam", "~/.local/share/Steam",
              "~/snap/steam/common/.local/share/Steam"],
}


def steam_roots(configured: str | None = None) -> list[Path]:
    """Every Steam library on this machine, the registry's answer first."""
    roots: list[Path] = []
    if configured:
        roots.append(Path(configured).expanduser())

    if sys.platform == "win32":
        try:
            import winreg
            for hive, key in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                              (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")):
                try:
                    with winreg.OpenKey(hive, key) as handle:
                        for name in ("SteamPath", "InstallPath"):
                            try:
                                roots.append(Path(winreg.QueryValueEx(handle, name)[0]))
                            except OSError:
                                pass
                except OSError:
                    pass
        except ImportError:
            pass

    roots += [Path(p).expanduser() for p in STEAM_ROOTS.get(sys.platform, STEAM_ROOTS["linux"])]

    # Every library folder Steam knows about, not just the one it installed into.
    found: list[Path] = []
    for root in roots:
        if root not in found and root.is_dir():
            found.append(root)
        vdf = root / "steamapps/libraryfolders.vdf"
        if vdf.is_file():
            for match in re.finditer(r'"path"\s+"([^"]+)"', vdf.read_text(encoding="utf-8", errors="replace")):
                library = Path(match.group(1).replace("\\\\", "\\"))
                if library.is_dir() and library not in found:
                    found.append(library)
    return found


def workshop_content(configured: str | None = None) -> Path | None:
    """`steamapps/workshop/content/<app>/`, wherever this machine keeps it."""
    if configured:
        given = Path(configured).expanduser()
        for candidate in (given / APP_ID, given):
            if candidate.is_dir():
                return candidate
        return None
    for root in steam_roots():
        candidate = root / "steamapps/workshop/content" / APP_ID
        if candidate.is_dir():
            return candidate
    return None


# --------------------------------------------------------- what Steam installed


def parse_vdf(text: str) -> dict:
    """Steam's text key-value format, enough of it to read an `.acf`."""
    tokens = re.finditer(r'"((?:[^"\\]|\\.)*)"|([{}])', text)
    stack: list[dict] = [{}]
    pending: str | None = None
    for token in tokens:
        quoted, brace = token.group(1), token.group(2)
        if brace == "{":
            child: dict = {}
            stack[-1][pending or ""] = child
            stack.append(child)
            pending = None
        elif brace == "}":
            if len(stack) > 1:
                stack.pop()
        elif pending is None:
            pending = quoted
        else:
            stack[-1][pending] = quoted
            pending = None
    return stack[0]


def installed_times(content: Path) -> dict[str, int]:
    """Workshop id -> when Steam says the copy on disk was updated.

    Steam keeps this in `appworkshop_<app>.acf` beside the content folder, and
    it is the only honest local answer: file dates say when the download landed
    here, which is not the same as which version it is.
    """
    acf = content.parent.parent / ("appworkshop_%s.acf" % APP_ID)
    times: dict[str, int] = {}
    if acf.is_file():
        data = parse_vdf(acf.read_text(encoding="utf-8", errors="replace"))
        for section in ("WorkshopItemsInstalled", "WorkshopItemDetails"):
            block = data.get("AppWorkshop", {}).get(section, {})
            for item, fields in block.items():
                if isinstance(fields, dict) and fields.get("timeupdated"):
                    times.setdefault(item, int(fields["timeupdated"]))
    # Anything downloaded but not in the record falls back to the folder's date.
    for folder in content.iterdir():
        if folder.is_dir() and folder.name.isdigit() and folder.name not in times:
            newest = max((p.stat().st_mtime for p in folder.rglob("*") if p.is_file()),
                         default=folder.stat().st_mtime)
            times[folder.name] = int(newest)
    return times


# ------------------------------------------------------------------- the model

REFERENCE = "reference"
PLAYSET = "playset"
UNTRACKED = "—"


@dataclass
class Mod:
    """One subscribed mod, and everything known about it from all three places."""

    id: str
    title: str = ""
    installed: int = 0          # what Steam has on disk
    published: int = 0          # what the workshop has now
    where: str = UNTRACKED      # reference / playset / not copied here
    folder: Path | None = None  # the copy in this repository
    version: str | None = None
    key: str = ""               # the name tools/workshop_mods.txt gives it

    @property
    def outdated(self) -> bool:
        return bool(self.published and self.installed and self.published > self.installed)

    @property
    def name(self) -> str:
        return self.title or self.key or self.id


@dataclass
class World:
    """Everything the menu needs to know, gathered once."""

    content: Path | None
    mods: list[Mod] = field(default_factory=list)
    asked_steam: bool = False

    @property
    def outdated(self) -> list[Mod]:
        return [m for m in self.mods if m.outdated]

    def by_id(self, item: str) -> Mod | None:
        return next((m for m in self.mods if m.id == item), None)


def gather(configured: dict, ask_steam: bool = True) -> World:
    content = workshop_content(configured.get("workshop"))
    world = World(content=content)
    if content is None:
        return world

    times = installed_times(content)
    # What this tool put there itself. Steam's own record still names the
    # version *it* downloaded, so without this a mod updated from here reads as
    # outdated for ever — right up until Steam happens to fetch it again.
    for item, stamp in (configured.get("installed") or {}).items():
        try:
            times[item] = max(times.get(item, 0), int(stamp))
        except (TypeError, ValueError):
            continue
    tracked = {item.id: item for item in workshop.tracked()}
    in_reference = workshop.local_copies()
    in_playset = {}
    for mod in refs.playset():
        found = re.search(r"(\d{6,})", mod.folder)
        if found:
            in_playset[found.group(1)] = mod

    for folder in sorted(content.iterdir()):
        if not folder.is_dir() or not folder.name.isdigit():
            continue
        mod = Mod(id=folder.name, installed=times.get(folder.name, 0))
        if folder.name in tracked:
            mod.where, mod.key = REFERENCE, tracked[folder.name].key
            copy = in_reference.get(folder.name)
            if copy:
                mod.folder, mod.version = copy.path, copy.version
        elif folder.name in in_playset:
            mod.where = PLAYSET
            mod.folder = in_playset[folder.name].path
            mod.version = in_playset[folder.name].version
        world.mods.append(mod)

    # A tracked mod whose copy is here but which Steam has not downloaded still
    # belongs in the list — it is exactly the case worth seeing.
    for item in workshop.tracked():
        if world.by_id(item.id) is None:
            copy = in_reference.get(item.id)
            world.mods.append(Mod(id=item.id, where=REFERENCE, key=item.key,
                                  folder=copy.path if copy else None,
                                  version=copy.version if copy else None))

    if ask_steam:
        try:
            details = workshop.steam_details([m.id for m in world.mods])
            world.asked_steam = True
        except SystemExit:
            details = {}
        for mod in world.mods:
            detail = details.get(mod.id, {})
            mod.title = detail.get("title", "")
            mod.published = int(detail.get("time_updated") or 0)

    world.mods.sort(key=lambda m: (m.where != REFERENCE, m.where != PLAYSET, m.name.lower()))
    return world


# --------------------------------------------------------------------- talking


def say(text: str = "") -> None:
    print(text, flush=True)


def ask(prompt: str, default: str = "") -> str:
    try:
        answer = input(prompt).strip()
    except EOFError:
        return default
    return answer or default


def yes(prompt: str, default: bool = True) -> bool:
    suffix = " [Д/н] " if default else " [д/Н] "
    answer = ask(prompt + suffix).lower()
    if not answer:
        return default
    return answer[0] in "yдd"


def when(stamp: int) -> str:
    return workshop.when(stamp) if stamp else "—"


def pick(mods: list[Mod], prompt: str) -> list[Mod]:
    """Numbers, ranges, or Enter for all of them."""
    answer = ask(prompt)
    if answer in {"0", "н", "n"}:
        return []
    if not answer:
        return list(mods)
    chosen: list[Mod] = []
    for part in re.split(r"[,\s]+", answer):
        if not part:
            continue
        if "-" in part:
            start, _, end = part.partition("-")
            if start.isdigit() and end.isdigit():
                for number in range(int(start), int(end) + 1):
                    if 1 <= number <= len(mods):
                        chosen.append(mods[number - 1])
            continue
        if part.isdigit() and 1 <= int(part) <= len(mods):
            chosen.append(mods[int(part) - 1])
    seen: set[str] = set()
    return [m for m in chosen if not (m.id in seen or seen.add(m.id))]


# ------------------------------------------------------------------- steamcmd


def steamcmd_path(configured: dict) -> str | None:
    """Where steamcmd is, offering to fetch it if it is nowhere."""
    given = configured.get("steamcmd")
    if given and Path(given).expanduser().is_file():
        return str(Path(given).expanduser())

    names = ["steamcmd.exe"] if sys.platform == "win32" else ["steamcmd.sh", "steamcmd"]
    for candidate in [Path(p) / name for p in ("C:/steamcmd", "~/steamcmd", ".")
                      for name in names]:
        if candidate.expanduser().is_file():
            return str(candidate.expanduser())
    found = shutil.which("steamcmd")
    if found:
        return found

    say()
    say("steamcmd не найден. Он нужен, чтобы скачивать моды по требованию —")
    say("именно это заменяет отписку и подписку.")
    if not yes("Скачать его сейчас?"):
        return None
    where = ask("Куда положить [C:\\steamcmd]: ", "C:\\steamcmd" if sys.platform == "win32"
                else str(Path.home() / "steamcmd"))
    target = Path(where).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    say("качаю %s ..." % STEAMCMD_ZIP)
    try:
        with urllib.request.urlopen(STEAMCMD_ZIP, timeout=120) as answer:
            payload = answer.read()
    except Exception as exc:                      # noqa: BLE001 - report and go on
        say("не вышло: %s" % exc)
        return None
    if sys.platform == "win32":
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            archive.extractall(target)
        binary = target / "steamcmd.exe"
    else:
        say("на этой системе steamcmd ставится из архива для Linux — пропускаю.")
        return None
    if not binary.is_file():
        say("в архиве нет steamcmd — что-то поменялось на стороне Valve.")
        return None
    configured["steamcmd"] = str(binary)
    settings_write(configured)
    say("готово: %s" % binary)
    return str(binary)


def steam_login(configured: dict) -> str | None:
    login = configured.get("login")
    if login:
        return login
    say()
    say("Нужен твой аккаунт Steam — тот, на котором куплена игра.")
    say("Пароль этот скрипт не видит и не хранит: его спросит сам steamcmd,")
    say("и после первого раза он логинится сам.")
    login = ask("Логин Steam: ")
    if not login:
        return None
    configured["login"] = login
    settings_write(configured)
    return login


def download(configured: dict, chosen: list[Mod], content: Path | None) -> list[Mod]:
    """Fetch these mods with steamcmd and put them where the game looks."""
    binary = steamcmd_path(configured)
    if not binary:
        return []
    login = steam_login(configured)
    if not login:
        say("без логина скачать нечего — Steam не отдаёт моды этой игры анонимно.")
        return []

    command = [binary, "+login", login]
    for mod in chosen:
        command += ["+workshop_download_item", APP_ID, mod.id]
    command += ["+quit"]

    say()
    say("steamcmd: качаю %d мод(ов) под аккаунтом %s" % (len(chosen), login))
    say("(если он спросит код Steam Guard — введи его прямо здесь)")
    say()
    subprocess.run(command)

    downloaded = Path(binary).resolve().parent / "steamapps/workshop/content" / APP_ID
    got = [mod for mod in chosen if (downloaded / mod.id).is_dir()]
    if not got:
        say()
        say("steamcmd ничего не положил в %s" % downloaded)
        say("Смотри его вывод выше: чаще всего это незавершённый вход.")
        return []

    if content is None:
        say("папка мастерской Steam не найдена, копировать некуда.")
        return got
    say()
    if not yes("Скопировать %d в папку мастерской Steam, чтобы игра увидела новые версии?"
               % len(got)):
        return got

    for mod in got:
        target = content / mod.id
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(downloaded / mod.id, target)
        size = sum(p.stat().st_size for p in target.rglob("*") if p.is_file())
        mod.installed = mod.published or int(time.time())
        installed = configured.setdefault("installed", {})
        installed[mod.id] = mod.installed
        say("  %-44s %s" % (mod.name[:44], workshop.human(size)))
    settings_write(configured)
    say()
    say("Готово. Игра берёт моды из этой папки, так что следующий запуск —")
    say("уже с новыми версиями. Лаунчер иногда показывает старый номер версии,")
    say("пока Steam не сверится сам; на то, что грузится, это не влияет.")
    return got


# ------------------------------------------------------- the repository's side


def run_python(script: str, *args: str) -> int:
    done = subprocess.run([sys.executable, str(refs.REPO / script), *args], cwd=refs.REPO)
    return done.returncode


def update_reference(world: World, chosen: list[Mod] | None = None) -> list[str]:
    """Replace the whole copies under `reference/mods/` from the workshop."""
    if world.content is None:
        say("папка мастерской не найдена.")
        return []
    tracked = {item.id: item for item in workshop.tracked()}
    wanted = [m for m in (chosen or world.mods) if m.id in tracked]
    if not wanted:
        say("нечего обновлять: ни один из выбранных модов не в reference.")
        return []

    here = workshop.local_copies()
    done: list[str] = []
    for mod in wanted:
        source = world.content / mod.id
        if not source.is_dir():
            say("  %-44s Steam его не скачал" % mod.name[:44])
            continue
        item = tracked[mod.id]
        existing = here.get(mod.id)
        folder = workshop.folder_for(item, source, existing)
        files, size = workshop.copy_in(source, refs.MODS / folder)
        note = ""
        if existing is not None and existing.folder != folder:
            shutil.rmtree(existing.path, ignore_errors=True)
            note = "  (заменил %s)" % existing.folder
        done.append(item.key)
        say("  %-24s %-40s %4d файлов %9s%s"
            % (item.key, folder, files, workshop.human(size), note))
    return done


def update_playset(world: World) -> None:
    """The text-only copies. Told where the workshop is, because this machine's
    Steam may be on a drive the default search does not know about."""
    if world.content is None:
        say("папка мастерской не найдена.")
        return
    run_python("tools/workshop.py", "playset", "--from", str(world.content))


def rebuild() -> None:
    say()
    say("--- пересборка всего, что генерируется из этих файлов ---")
    run_python("tools/refresh.py")
    run_python("tools/workshop.py", "record")


# ---------------------------------------------------------- moving mods around


def slug(text: str) -> str:
    made = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return made or "mod"


def promote(mod: Mod, world: World) -> None:
    """Track this mod: whole copy in `reference/mods/`, watched for updates."""
    default = slug(mod.title or mod.id)
    key = ask("Короткое имя для него [%s]: " % default, default)
    reason = ask("Зачем он здесь (одна строка): ", "")

    text = workshop.MANIFEST.read_text(encoding="utf-8").rstrip("\n")
    line = "%-11s %s" % (mod.id, key)
    if reason:
        line = "%-34s # %s" % (line, reason)
    text += "\n" + line + "\n"
    workshop.MANIFEST.write_text(text, encoding="utf-8")

    if mod.where == PLAYSET and mod.folder is not None:
        shutil.rmtree(mod.folder, ignore_errors=True)
    if world.content is not None and (world.content / mod.id).is_dir():
        item = workshop.Tracked(id=mod.id, key=key, reason=reason)
        source = world.content / mod.id
        folder = workshop.folder_for(item, source, None)
        files, size = workshop.copy_in(source, refs.MODS / folder)
        say("  %s: %d файлов, %s" % (folder, files, workshop.human(size)))
    say()
    say("%s теперь в reference — целиком, и за его обновлениями следит" % key)
    say("ежедневная проверка на GitHub.")


def demote(mod: Mod, world: World) -> None:
    """Stop tracking: text-only copy in the playset, no daily check."""
    lines = workshop.MANIFEST.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if not line.strip().startswith(mod.id)]
    workshop.MANIFEST.write_text("\n".join(kept) + "\n", encoding="utf-8")

    if mod.folder is not None and mod.folder.exists():
        shutil.rmtree(mod.folder, ignore_errors=True)
    if world.content is not None and (world.content / mod.id).is_dir():
        item = workshop.Tracked(id=mod.id, key=slug(mod.title or mod.id), reason="")
        source = world.content / mod.id
        folder = workshop.folder_for(item, source, None)
        refs.PLAYSET.mkdir(parents=True, exist_ok=True)
        files, size = workshop.copy_slim(source, refs.PLAYSET / folder)
        say("  %s: %d файлов текста, %s" % (folder, files, workshop.human(size)))
    say()
    say("Готово. Помни: если на него что-то здесь опиралось — оно сломается,")
    say("потому что в playset лежит только текст.")


# ------------------------------------------------------------------ git at the end


def repository_dirty() -> list[str]:
    done = workshop.git("status", "--porcelain", check=False)
    return [line for line in done.stdout.splitlines() if line.strip()]


def commit_and_push() -> None:
    changed = repository_dirty()
    if not changed:
        say("в репозитории нечего коммитить — всё уже отправлено.")
        return
    say()
    say("Изменения (%d):" % len(changed))
    for line in changed[:20]:
        say("  " + line)
    if len(changed) > 20:
        say("  ... и ещё %d" % (len(changed) - 20))

    say()
    default = "reference: обновление модов из мастерской"
    message = ask("Сообщение коммита [%s]: " % default, default)
    branch = workshop.git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    target = ask("В какую ветку пушить [%s]: " % branch, branch)

    if target != branch:
        if yes("Переключиться на %s?" % target):
            switch = workshop.git("checkout", target, check=False)
            if switch.returncode != 0:
                say((switch.stdout + switch.stderr).strip())
                return
        else:
            return

    workshop.git("add", "-A")
    workshop.git("commit", "-m", message)
    say("коммит сделан.")
    for wait in (2, 4, 8, 16, 0):
        done = workshop.git("push", "-u", "origin", target, check=False)
        if done.returncode == 0:
            say("запушено в %s." % target)
            return
        say((done.stdout + done.stderr).strip())
        if wait:
            say("не вышло, пробую снова через %d с" % wait)
            time.sleep(wait)
    say("пуш не удался — попробуй `git push` руками.")


# ---------------------------------------------------------------------- screens


def show_updates(world: World) -> list[Mod]:
    if world.content is None:
        say("Папка мастерской Steam не найдена.")
        say("Укажи её:  python3 tools/mods.py --workshop \"D:\\SteamLibrary\\steamapps\\workshop\\content\"")
        return []
    if not world.asked_steam:
        say("Steam не ответил — без сети сказать, что обновилось, нельзя.")
        return []

    outdated = world.outdated
    say()
    say("Подписка: %d мод(ов). В reference: %d, в playset: %d."
        % (len(world.mods),
           sum(1 for m in world.mods if m.where == REFERENCE),
           sum(1 for m in world.mods if m.where == PLAYSET)))
    if not outdated:
        say("Обновлять нечего: у тебя стоят те же версии, что и в мастерской.")
        return []

    say()
    say("Отстают от мастерской:")
    say("  %-3s %-46s %-17s %s" % ("#", "мод", "у тебя", "в мастерской"))
    for number, mod in enumerate(outdated, 1):
        say("  %-3d %-46s %-17s %s"
            % (number, mod.name[:46], when(mod.installed), when(mod.published)))
    return outdated


def screen_updates(world: World, configured: dict) -> None:
    outdated = show_updates(world)
    if not outdated:
        return
    say()
    chosen = pick(outdated, "Что скачать? [Enter — все, номера через запятую, 0 — назад]: ")
    if not chosen:
        return
    got = download(configured, chosen, world.content)
    if not got:
        return
    say()
    if yes("Обновить и копии в репозитории для тех из них, что там есть?"):
        say()
        update_reference(world, got)
        if any(m.where == PLAYSET for m in got):
            update_playset(world)
        rebuild()


def screen_repository(world: World) -> None:
    say()
    say("Что обновить в репозитории из того, что уже скачано Steam:")
    say("  1  reference — пять модов целиком, те, на которых всё здесь держится")
    say("  2  playset — все остальные, только текст")
    say("  3  и то, и другое")
    say("  0  назад")
    choice = ask("> ")
    if choice not in {"1", "2", "3"}:
        return
    say()
    if choice in {"1", "3"}:
        update_reference(world)
    if choice in {"2", "3"}:
        update_playset(world)
    rebuild()


def screen_list(world: World, configured: dict) -> None:
    while True:
        say()
        say("  %-3s %-46s %-10s %-10s %s" % ("#", "мод", "где", "версия", "обновление"))
        for number, mod in enumerate(world.mods, 1):
            say("  %-3d %-46s %-10s %-10s %s"
                % (number, mod.name[:46], mod.where, (mod.version or "—")[:10],
                   "есть" if mod.outdated else ""))
        say()
        answer = ask("Номер мода (0 — назад): ")
        if not answer or answer == "0":
            return
        if not answer.isdigit() or not 1 <= int(answer) <= len(world.mods):
            continue
        mod = world.mods[int(answer) - 1]

        say()
        say("%s  (id %s)" % (mod.name, mod.id))
        say("  сейчас: %s" % mod.where)
        if mod.where == REFERENCE:
            say("  1  вернуть в playset (только текст, без ежедневной проверки)")
        else:
            say("  1  отправить в reference (целиком, с проверкой обновлений)")
        say("  2  скачать свежую версию в Steam")
        say("  0  назад")
        choice = ask("> ")
        if choice == "1":
            if mod.where == REFERENCE:
                if yes("Убрать %s из reference?" % mod.name, default=False):
                    demote(mod, world)
            else:
                promote(mod, world)
            world.mods = gather(configured).mods
        elif choice == "2":
            download(configured, [mod], world.content)


def menu(configured: dict) -> int:
    world = gather(configured)
    while True:
        outdated = len(world.outdated)
        say()
        say("=" * 62)
        say("  МОДЫ EU5")
        say("  подписка: %-3d   reference: %-3d   playset: %-3d   обновлений: %d"
            % (len(world.mods),
               sum(1 for m in world.mods if m.where == REFERENCE),
               sum(1 for m in world.mods if m.where == PLAYSET),
               outdated))
        say("=" * 62)
        say("  1  Проверить обновления в мастерской и скачать")
        say("  2  Обновить копии в репозитории (reference / playset)")
        say("  3  Мои моды: список, что где лежит, перенос между ними")
        say("  4  Коммит и пуш")
        say("  5  Перечитать всё заново")
        say("  0  Выход")
        choice = ask("> ")

        if choice == "1":
            screen_updates(world, configured)
            world = gather(configured)
        elif choice == "2":
            screen_repository(world)
            world = gather(configured)
        elif choice == "3":
            screen_list(world, configured)
        elif choice == "4":
            commit_and_push()
        elif choice == "5":
            world = gather(configured)
        elif choice in {"0", "q", "в", "выход"}:
            return 0


# ------------------------------------------------------------------- the shell


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="mods.py",
        description="Обновление модов EU5: мастерская, папка игры и этот репозиторий.")
    parser.add_argument("command", nargs="?", default="menu",
                        choices=["menu", "check"],
                        help="menu — меню (по умолчанию); check — только отчёт")
    parser.add_argument("--workshop", metavar="DIR",
                        help="папка steamapps/workshop/content, если она не там, где обычно")
    parser.add_argument("--steamcmd", metavar="PATH", help="путь к steamcmd")
    parser.add_argument("--login", metavar="USER", help="аккаунт Steam")
    parsed = parser.parse_args(argv[1:])

    configured = settings_read()
    for name in ("workshop", "steamcmd", "login"):
        given = getattr(parsed, name)
        if given:
            configured[name] = given
    if any(getattr(parsed, n) for n in ("workshop", "steamcmd", "login")):
        settings_write(configured)

    if parsed.command == "check":
        world = gather(configured)
        return 1 if show_updates(world) else 0

    try:
        return menu(configured)
    except KeyboardInterrupt:
        say()
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
