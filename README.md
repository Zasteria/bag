# EU5 mods

Two mods for Europa Universalis V, both about the same blind spot: the game
knows which buildings gain production efficiency from raw materials in their
province, badges them with a shovel, and then gives you no way to search on it.

Each folder is a complete mod — copy the folder itself into
`Documents/Paradox Interactive/Europa Universalis V/mod/`.

| Folder | What it does |
| --- | --- |
| [`rgo_bonus_filter/`](rgo_bonus_filter/) | Two filter chips that cut both building lists down to what gains from local raw materials. Working. |
| [`where_to_produce/`](where_to_produce/) | Pick a good, get a shortlist of the best places in your realm to produce it. In progress. |

Both depend on the [Community Mod Framework](https://steamcommunity.com/workshop/)
(`community_mod_framework` 2.\*) for their settings.

## Shared notes

[`docs/RESEARCH.md`](docs/RESEARCH.md) collects what the EU5 mod format turned
out to be — the folder layout, the declarative filter system and what a filter
trigger really receives, how view objects are scoped, the CMF and CMM APIs, and
where the RGO bonus lives in the game data. Most of it was learnt the hard way;
read it before assuming anything about how a panel can be extended.

The formula behind the shovel badge, recovered by matching the game's own
tooltips, is written up in
[`where_to_produce/README.md`](where_to_produce/README.md).
