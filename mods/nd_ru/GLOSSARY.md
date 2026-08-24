# Словарь

Термины, уже выбранные в этом переводе. **Сверяйтесь с ним прежде, чем
переводить слово заново** — расхождение в терминах на двухстах файлах читается
как небрежность, и заметить его потом дороже, чем свериться сейчас.

## Как проверять термин игры

Слова, которыми игра называет свои собственные понятия, **не выбираются на глаз**.
Их спрашивают у самой игры:

```
python3 mods/nd_ru/tools/term.py Levies
    game_concept_levies
        en: Levies
        ru: Ополчение
```

Инструмент сопоставляет английское значение с локализацией игры в
`reference/game/main_menu/localization/` и печатает русское значение того же
ключа. `--key ADVANCES` ищет по имени ключа.

Так был пойман первый промах этого перевода: advances — это **«Улучшения»**, а
вовсе не «достижения», как казалось до того, как локализация игры попала в
репозиторий.

## Понятия игры

| Английский | По-русски | Откуда |
| --- | --- | --- |
| Advance / Advances | Улучшение / Улучшения | `game_concept_advance(s)` |
| Levies | Ополчение | `game_concept_levies` |
| Bureaucracy | Бюрократический механизм | `game_concept_bureaucracy` |

Внутри `[advances|e]` и прочих ссылок на понятия название подставляет сама игра,
поэтому там ничего переводить не нужно и нельзя. Термин из таблицы нужен только
там, где мод пишет слово обычным текстом.

## Повторяющиеся слова этого мода

| Английский | По-русски | Замечание |
| --- | --- | --- |
| formable country | образуемая страна | так это называет игра |
| destiny tree | древо судьбы | |
| standing | вес | в Дунайском вопросе — влияние кандидатуры |
| cause (Union Cause) | дело (дело унии) | |
| the crown | корона | и как предмет, и как государь |
| realm | держава | не «королевство»: держава бывает и республикой |
| estates | сословия | |
| diet / Landtag | сейм / ландтаг | сейм — общее слово, ландтаг — когда мод пишет Landtag |
| composite monarchy | составная монархия | |
| Crown Confidence | доверие короне | шкала в кризисе наследования |
| Old Liberties | старые вольности | |
| pact tier | ступень договора | |
| menace at the gates | угроза у ворот | |
| upkeep / maintenance | содержание | «Содержание солеварни» |
| Impact (модификатор бюрократии) | Влияние | `Влияние: $bureaucracy$` |
| has already happened | уже произошло | общий файл `nd_event_guards` |

## Что оставлено латиницей нарочно

Имена собственные, которые в русском тексте так и читаются. Их **не переводить**:

`Antemurale Christianitatis`, `Gesamtmonarchie`, `Erbverbruederung`,
`Kameralhoheit`, `Geheime Konferenz`, `Grenz-Generalat`, `Landstaende der
Erblande`, `Directorium in publicis et cameralibus`, `Reformationskommission`,
`Militaergrenze`, `Verneuerte Landesordnung`, `Bella Gerant Alii`,
`Konzivilisation`, `Josephinismus`, `Privilegium Maius`, `Festungsbaukunst`,
`Bollwerk des Glaubens`, `Kreuzzugsgeist`, `Kaiserliche Ordnung`,
`Kongressdiplomatie`, `Cuius Regio, Eius Religio`, `Universalis Monarchia`,
`indivisibiliter ac inseparabiliter`.

Всего таких значений около сорока. Проверить список:

```
python3 - <<'PY'
import re, sys; sys.path.insert(0, "mods/nd_ru/tools"); import scope
srcs = {}
for p in (scope.MOD / "translations").glob("*.yml"): srcs.update(scope.read(p))
for k, v in srcs.items():
    s = scope.MARKUP.sub("", v).strip()
    if re.search(r"[A-Za-z]{2}", s) and not re.search(r"[А-Яа-яЁё]", s):
        print(k, "=", v)
PY
```

## Правила, а не список

- **Историческое русское имя важнее транслитерации.** `Peace of Lodi` →
  «Лодийский мир», не «мир Лоди». `Soest` → Зуст. `Kanem-Bornu` → Канем-Борну.
- **Латинское название страны сохраняется латинской формой**, если мод взял его
  нарочно, чтобы отличить от обычного: `Aegyptus` → Эгиптус, потому что рядом
  существует обычный Египет.
- **Кавычки — «ёлочки».** Прямая кавычка `"` обрывает строку; экранированная
  `\"` в исходнике мода допустима, но в переводе лучше «».
- **Тире — длинное**, дефис только внутри слов.
- **Числа с запятой**: `0,006`, а не `0.006`.

## Спорное, что стоит подтвердить на экране

Решения приняты, но иначе тоже можно:

- `Aegyptus` → **Эгиптус** (латинская форма ради отличия от Египта)
- `Regnum Gothorum` → **Королевство готов** (переведено, хотя мод оставил латынь)
- `Yavana` → прилагательное **яванский** (путается с островом Ява)
- `Khilafah` → **Халифат** (обычным словом, без арабской транслитерации)
