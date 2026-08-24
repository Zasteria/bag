# Opening a new session

Claude Code loads [`../CLAUDE.md`](../CLAUDE.md) automatically, so a session
already has the briefing before you type anything. What it does *not* have is a
reason to read the rest before starting work — which is what this prompt is for.

Paste this as the first message:

---

Это рабочий репозиторий для модов EU5. Здесь уже накоплены знания и лежат файлы
игры — ничего загружать не нужно.

Прежде чем что-то делать:

1. Прочитай `CLAUDE.md`, `docs/RESEARCH.md` и `docs/PITFALLS.md` целиком.
2. Просмотри `docs/HANDOFF.md` — состояние модов.
3. Запусти `python3 tools/refresh.py`. Он покажет, что сейчас лежит в
   `reference/` и с какими версиями, пересоберёт генерируемые файлы и назовёт
   изменившиеся. Версии в тексте могли устареть — этот вывод не может.

Потом коротко ответь своими словами:

- что за проект и что в нём уже сделано;
- три-четыре правила или грабли, которые ты считаешь самыми важными;
- что лежит в `reference/` и когда ты туда полезешь;
- чего ты **не** можешь (что проверяю в игре я, а не ты) и что тебе от меня
  понадобится;
- готов ли начинать.

Не пересказывай файлы подряд — мне нужно понять, что ты действительно уловил.
Дальше скажу, над чем работаем.

---

## Why it is worded that way

**"Прочитай целиком", not "ознакомься".** A session that skims picks the same
wrong turns again; `PITFALLS.md` exists precisely because none of them announce
themselves.

**Asking for a summary in its own words** is the cheap check that reading
happened. If the answer is generic, say so and have it read again before any
work starts — that costs a minute and saves a round trip through the game.

**Asking what it cannot do** surfaces the constraint that shapes everything
here: only you can run the game. A session that has not registered that will
report guesses as if they were verified.

**Asking what it needs from you** gets the request for `error.log` and
screenshots out of the way at the start, instead of three exchanges in.

**`tools/refresh.py` instead of a paragraph about versions.** `reference/` is
refreshed by hand and without notice, so a session that reads versions out of a
document starts by mistrusting the tree, or worse, reports a routine mod update
as a problem. One command makes the tree its own answer.

## Если сессия про перевод крупного мода

`nd_ru` — самый большой проект в репозитории, и его нельзя вести «на память».
Такой сессии, помимо общего брифинга, нужно прочитать:

1. [`../mods/nd_ru/README.md`](../mods/nd_ru/README.md) — три команды, которыми
   ведётся работа, и что именно проверяет генератор.
2. [`../mods/nd_ru/GLOSSARY.md`](../mods/nd_ru/GLOSSARY.md) — принятые термины.
   Сверяться до перевода, а не после.

И сразу спросить владельца, **какой объём брать в этот раз**: весь мод — около
двадцати семи сессий, поэтому объём режется по приоритету, а не берётся целиком.
Цифры для такого разговора — в [`HANDOFF.md`](HANDOFF.md).

## If the session goes on long

Context runs out well before a mod is finished. Before that happens, have it
write down what it learnt — `RESEARCH.md` for a rule, `PITFALLS.md` for a
mistake and its symptom, `HANDOFF.md` for the state of the work. Then start a
fresh session with the prompt above; nothing is lost that was written down.
