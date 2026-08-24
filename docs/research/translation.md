# Translating somebody else's mod

Two of the mods here are translations. What that job actually is, what it
costs, and the ways a localization breaks in silence.

## Translating a mod that ships without your language

A separate mod carrying one `.yml` is the whole job. It needs no dependency on
the mod it translates — the keys simply add, and nothing collides — and only a
CMF dependency if it redefines one of CMF's own shared keys. `auto_build_ru` is
the worked example; its `mods/auto_build_ru/tools/generate_ru.py` is written
against one mod but
the shape of it is reusable.

**A mod may ship a language that is only the English text.** National Destinies
ships eleven languages whose files are byte identical to the English ones apart
from the `l_<language>:` header, so it reads in English in a Russian game while
`localization/russian/` plainly exists. Diff against `english/` before believing
a language is present.

That changes the job from adding keys to **overriding** them, which is confirmed
working in game: a separate localization mod loaded after the base mod replaces
the base mod's values for the same keys. Load order decides, so the translation
declares a dependency on the mod it translates and has to sit below it in the
playset.

**Read the size before quoting one.** A mod's key count badly overstates the
work. Of Advanced Auto Build's 1201 keys, 372 were pure markup, 316 were
`$vanilla_key$` passthrough, and another 315 were families differing only by a
number — 883 strings of actual prose, and about 6000 words. Count what is left
after stripping `[...]`, `$...$`, `@icon!` and `#code`, not lines.

**Audit before translating.** Four checks, each cheap and each has caught
something:

1. Parse every language the mod ships and compare key sets. Equal sets mean the
   English is a complete translation and can be the source; a gap means the
   other language is the original and has to be consulted for those keys.
2. Collect every key its `.gui` files and scripts reference — `text`, `tooltip`,
   `raw_tooltip`, `custom_tooltip`, and `$...$` inside other values — and check
   each is defined. A dangling one renders raw in *every* language, and is the
   mod's bug rather than yours.
3. Derive the CMM keys from its registration effects (see
   [Mod Menu settings](#mod-menu-settings-cmm)) and check those too. This is
   where a real mod is likeliest to be missing one.
4. Look for keys that are not the mod's own. A mod may redefine a vanilla or CMF
   key, and translating it changes what every other mod says.

**Ask the game what it calls its own concepts.** A mod's prose names game
concepts in plain text — advances, levies, bureaucracy — and inventing a word for
them produces exactly the disease the translation is meant to cure: a private
term sitting in the middle of the game's own interface. The game's localization
answers it: match the English value against `localization/english`, read the
Russian value of the same key. In EU5 1.3.10 advances are «Улучшения», not
«достижения», which is what a session guessed before the game's files were in the
repository. `mods/nd_ru/tools/term.py` is that lookup.

Inside `[advances|e]` and other concept links the game substitutes the name
itself, so the word only has to be chosen where the mod writes it as prose.

**What must not be translated.** Each of these looks like text and is not:

| Looks like | Is | If translated |
| --- | --- | --- |
| `gold` under `<element>_color` | a CMF palette name | the action bar button vanishes |
| `@production_panel!` | a texticon | renders as literal text |
| `$farming_village$` | a reference to the game's own key | breaks; it was already in the player's language |
| `[GetPlayer.MakeScope...]` | a data function | `ERROR:` on screen |
| `#G ... #!` | a colour code | the colour is lost, or the text is |

Passthrough is the happy case: a mod that names its buildings
`$vanilla_key$` needs none of them translated.

**A mod of a hundred thousand words is a different job.** `auto_build_ru` was
6000 words and fitted in one sitting. National Destinies is 688 617 words of
prose across 220 files, which no subscription pays for in full. What that
changes:

- **Measure before promising.** Count prose words after stripping markup, not
  keys and not lines. Then convert to sessions: one session of steady work moved
  about 25 000 words, tooling and mistakes included. That number is the only
  honest basis for "how long will this take".
- **The order of work is a deliverable.** A file like `priority.txt` naming the
  stems in the order they matter — for a player, the region they actually play —
  lets any later session pick up without re-deciding anything.
- **Translate in layers, not files.** Names first (short, low judgement, most
  visible), then the events a player reads, then descriptions. A layer finished
  across the whole mod is worth more than a few files finished completely.
- **Look for the cheap thousands.** `nd_bureaucracy_impact_modifier_types` holds
  1770 keys built from three sentences; `nd_event_guards` holds 144 keys built
  from one. Both were generated from templates in minutes and fixed their line
  for every country at once. Before translating by hand, group the file's values
  by shape and see how many distinct sentences there really are.

**A key of a country need not live in that country's file.** Westphalia had 88
keys in `nd_wes` and 10 more in a shared modifier file. Checking one file and
declaring the country done is how a gap survives. Search every file for the tag.

**`_entry` keys are usually passthrough.** `nd_wes.1.entry: "$nd_wes.1.t$"` is a
reference to the event title, so translating the title makes the log entry
Russian by itself. Translating the entry as well is wasted work.

**Overriding another mod's localization works, and stacks with a third.** A
separate mod loaded later replaces the base mod's values for the same keys —
confirmed in game. That also means a hand translation can sit on top of somebody
else's machine translation of the same mod: theirs below, yours above, and the
player gets your keys where you have them and theirs everywhere else. Two
conditions: the overriding mod must load later, and **its file names must differ**,
because a file of the same name replaces the whole file rather than merging keys.
Naming the generated output `<stem>_ru_generated_l_russian.yml` keeps it clear of
both the base mod and any other translation.

**Generate rather than hand-write the final file.** Keep the prose in a source
file and emit the game's `.yml` from it, with the source checked against the
base mod's English: every key covered, no key invented, and the markup of each
value identical in both. That last check is the one that earns its keep — it
catches a bracket eaten while rewording, which is otherwise found by the player.
It also turns a base-mod update into one run that names the keys that moved.

**Families collapse.** Keys differing only by a number — twenty template slots,
step buttons, per-ordinal rows — are worth writing once with a placeholder and
expanding over the numbers the base mod actually uses. Collapse only when the
*values* match too: `eu5ab_building_age_1..6` share a key shape and are six
different ages.
