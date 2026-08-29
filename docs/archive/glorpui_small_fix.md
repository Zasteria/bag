# `Glorp UI small fix` — the other addon, measured against ours

Workshop 3784988919, in `reference/` for comparison. It looks like
`glorpui_hints` and is not. This is the full comparison, made 2026-08-27; what
came out of it is in [`../../mods/glorpui_hints/CLAUDE.md`](../../mods/glorpui_hints/CLAUDE.md).


`Glorp UI small fix` (workshop 3784988919, in `reference/` for comparison,
version 0.1) appeared in late August 2026 and looks at first glance like our
mod. It is not. Measured, not skimmed:

| | `glorpui_hints` (ours) | `Glorp UI small fix` |
| --- | --- | --- |
| keys per language | 1128 | 768 |
| of them Glorp UI's own hint keys | 759 | 763 |
| **new hint content** | **364 keys** | 5 |
| languages | **11** (2026-08-27; was Russian) | 10 (no English) |
| gating | 253 lines by country trigger, plus 5 by `has_advance` | 3 privileges by `has_advance` |
| CMM setting | yes | no |

**The overlap is the translation half only.** Both give Glorp UI's ~760
`GLORP_UI_SVH_*` keys a Russian text, and on those keys whichever mod mounts
later wins. The styles differ: he keeps Glorp UI's `[government_reform|e]`
concept link and puts it in brackets after the name; ours replaces it with the
Russian phrase and drops the link.

**What our mod does that his does not exist to do at all:** the 364 keys of hint
content from the twenty source kinds Glorp UI's generator never reads. His mod
translates Glorp UI's list; ours also *extends* it. That half is untouched by
him.

**What he had that we did not — both taken on 2026-08-27, neither by copying
his text:**

- **Ten languages.** ~~The one place his mod was ahead.~~ Ours ships eleven
  now, English included. What was actually worth taking from his files is a
  *shape*: he puts the verb after the object in German, Turkish, Japanese and
  Korean, which is why our openers are written with a `{ref}` placeholder rather
  than as a prefix. A prefix-substitution design cannot express those four
  languages at all. The words are ours, and fourteen of the category nouns are
  neither his nor ours — they are game concepts, which is a route he did not
  take and which is both free and more accurate. See
  [`research/translation.md`](../research/translation.md#shipping-in-all-eleven-languages).
- **A gate for privileges locked behind an advance.** Glorp UI's
  `glorpui_svh_privilege_takeable` filter reads a privilege's `potential`/`allow`
  and nothing else, so a privilege whose only lock is an advance's
  `unlock_estate_privilege` is recommended to a country that cannot take it. His
  census is exact and reproduces here: **10 vanilla privileges are locked that
  way**, four of them appear in Glorp UI's hints, and `ayans_privilege` is
  already filtered by `has_or_had_tag = TUR` in its own potential — so **three
  leak**: `peasants_yeomanry`, `jaysh_armies`, `ghazi_privilege`. **Done, from
  the data**: `generate.py` scans `common/advances` for `unlock_estate_privilege`
  rather than listing the three, so a patch that locks an eleventh is picked up
  by a rebuild, and it gates `ayans_privilege` too — the tag check in its
  potential is not the advance, and both have to hold. Five hint keys in all.
  **The mechanism is his and it is the real prize**: a `customizable_localization`
  *cannot be overridden*, first definition wins, later duplicates dropped with
  `gamedatabase.h: Duplicated key ... will not be created from file` — his file
  carries that log line. So the base mod's rule is untouchable and the way round
  is to take over the localization key it prints. Now in
  [`PITFALLS.md`](../pitfalls/localization.md).
- **Four Glorp UI keys whose Russian is broken grammar** — `GLORP_UI_AVG_CONTROL`
  ("Средняя значение"), `GLORP_UI_AVG_PROXIMITY`, `SWAP_TO_AVG_CONTROL`,
  `REFRESH_AVG_PROX` ("Обновить Средняя расстояние"). Note his file's header
  claims they are *absent* from Glorp UI's Russian; they are not, they are
  present and wrong. Same practical effect, different reason. **Done**, in
  Russian only — the other nine translations of those four keys were checked and
  are grammatical, so Glorp UI keeps ownership of its own text there.

**`TO_MOVE_FURTHER_TO_LEFT/RIGHT` we already fix**, in `ru_loc_fix`: vanilla's
Russian references `$SOCIEALVALUE_..._GEN$` — a typo for `SOCIETALVALUE` — and
we repair the reference. He repoints the key at
`[SocietalValue.GetLeftLabelWithNoTooltip]` instead, for ten languages. Two
routes to the same repair; ours does not need Glorp UI installed.

**If both mods are loaded**, the later one wins every shared key, which means
his three gated privileges silently ungate if ours mounts after him. Running
both is not useful: pick one for the translation half, and ours for the content.
