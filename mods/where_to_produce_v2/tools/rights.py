#!/usr/bin/env python3
"""Городские права специализации: расчёт, снятый с карты Construction Manager.

**Формула не наша.** Она прочитана из
`reference/mods/<CM dev>/in_game/common/{script_values,scripted_effects}/cm_town_right_map_mode_*`
и воспроизведена здесь один в один, потому что владелец сказал прямо: CM делает
это правильно с большей вероятностью, чем мы. Что именно она считает:

1. **Покрытие товара** -- какую долю сырья лучшего из его методов провинция
   даёт своими РГО. Доли берутся из `eu5data.Method.shares()`, то есть из той же
   дроби, что и выгода РГО: `сырьё, которое даёт провинция / всё сырьё метода`.
   Сырьё, которого РГО не даёт никогда, остаётся в знаменателе.
2. **Лучший метод, а не сумма**: домик один, метод у него один.
3. **Поправки по локации**: здание должно тут помещаться (`location_potential`);
   если РГО самой локации -- этот же товар, она считается ещё одним полностью
   покрытым производителем, `(покрытие+1)/2`; плюс уже стоящее усиление товара в
   локации, переведённое в ту же шкалу делением на «единицу РГО» (0.1 плюс два
   продвижения), минус вклад права, если город его уже держит.
4. **Счёт права = среднее покрытий его товаров.** Ровно как у CM: без веса на
   силу модификатора. Снаряжение даёт 0.3, ювелирное 0.2, и CM этой разницы не
   видит -- отход от этого был бы нашей выдумкой, а не его расчётом.
5. **Побеждает наибольший**, счёт и номер упакованы в `round(счёт*1000)*10+номер`.

## Чем мы от CM отличаемся, и это названо нарочно

**Первое: набор методов выбирает эпоха, а не генератор.** У CM в списке
снаряжения три метода, у нас десять -- его генератор чем-то их отсеивает, и чем
именно, из сборки не видно. Вместо угадывания мы спрашиваем эпоху:

  «Текущая эпоха» -- методы, чьё здание держава уже может строить и которое ей
  ещё не заменили; «Последняя эпоха» -- методы, чьё здание не заменяет ничто.

**Второе: считаем только выбранную землю и только по нажатию.** CM считает весь
мир на загрузке. Владелец отказался от CM именно из-за производительности.

**Штраф права не считается вовсе**, и это его решение: право штрафует всё
остальное производство локации одинаково, поэтому на выбор между правами он не
влияет.
"""

from __future__ import annotations

import re
from pathlib import Path

# Порядок номеров в упаковке: больший номер выигрывает ничью, поэтому
# он обратный приоритету. Список и цвета сняты с карты CM.
RIGHT_ORDER = (
    ("royal_tooling_rights", 9, "hsv { 0.62 0.3 0.08 }"),
    ("royal_jewelry_rights", 8, "hsv { 0.085 0.95 1 }"),
    ("royal_naval_rights", 7, "rgb { 0.11 0.17 0.4 }"),
    ("royal_textile_rights", 6, "rgb { 183 169 155 }"),
    ("royal_weaponry_rights", 5, "rgb { 202 204 206 }"),
    ("royal_book_rights", 4, "rgb { 0.9 0.86 0.71 }"),
    ("royal_artisan_rights", 3, "rgb { 160 192 192 }"),
    ("royal_brewing_rights", 2, "hsv { 0.9 0.8 0.2 }"),
    ("royal_masonry_rights", 1, "hsv360 { 26 70 25 }"),
)

# `local_<товар>_output_modifier` -- имя модификатора, который право двигает.
def modifier_of(good: str) -> str:
    return f"local_{good}_output_modifier"


def advance_unlocks(advance_dirs) -> tuple[dict[str, str], dict[str, str]]:
    """Продвижение, открывающее здание, и продвижение, открывающее метод.

    Здания -- `unlock_building`, методы -- `unlock_production_method`. Второе
    гейтит всего десяток методов, остальные едут на открытии своего здания.
    """
    buildings: dict[str, str] = {}
    methods: dict[str, str] = {}
    for folder in advance_dirs:
        for path in sorted(Path(folder).glob("*.txt")):
            text = path.read_text(encoding="utf-8-sig")
            for block in re.finditer(r"^([a-z0-9_]+)\s*=\s*\{(.*?)^\}", text, re.S | re.M):
                name, inner = block.group(1), block.group(2)
                for key in re.findall(r"unlock_building\s*=\s*([a-z0-9_]+)", inner):
                    buildings.setdefault(key, name)
                for key in re.findall(r"unlock_production_method\s*=\s*([a-z0-9_]+)", inner):
                    methods.setdefault(key, name)
    return buildings, methods


class Option:
    """Один метод одного товара: доли сырья, ворота местности, ворота эпохи."""

    __slots__ = ("n", "good", "method", "building", "shares", "potential",
                 "group", "in_end", "adv", "succ_adv")

    def __init__(self, n, good, method, building, shares, potential, group,
                 in_end, adv, succ_adv):
        self.n = n
        self.good = good
        self.method = method
        self.building = building
        self.shares = shares
        self.potential = potential
        self.group = group
        self.in_end = in_end
        self.adv = adv
        self.succ_adv = succ_adv


def collect(game, potentials, adv_building, adv_method):
    """Все варианты по каждому усиливаемому товару, сгруппированные по местности.

    Группа -- это отдельный `location_potential`: у товара может быть здание,
    которое стоит где угодно, и здание, которому нужен лес. Их покрытия нельзя
    складывать в одно число, потому что второе годится не всякой локации, --
    поэтому каждая группа считается отдельно, а локация берёт максимум из тех,
    чьи ворота у неё открыты. Так это устроено и у CM (`cm_trmm_covp_*_g2`).
    """
    rights = {r.key: r for r in game.town_rights if r.general}
    missing = [key for key, _, _ in RIGHT_ORDER if key not in rights]
    if missing:
        raise SystemExit(f"эти права игра больше не даёт всем: {missing}")

    goods: dict[str, float] = {}
    for key, _, _ in RIGHT_ORDER:
        for good, amount in rights[key].output.items():
            goods[good] = max(goods.get(good, 0.0), amount)

    out: dict[str, list[Option]] = {}
    n = 0
    for good in sorted(goods):
        groups: dict[str, int] = {"": 1}
        rows: list[Option] = []
        for method in game.producing(good):
            potential = potentials.get(method.building, ("", False))[0].strip()
            if potential not in groups:
                groups[potential] = len(groups) + 1
            shares = {g: v / 10.0 for g, v in method.shares().items()
                      if g in game.raw_goods}
            if not shares:
                continue
            n += 1
            successor = game.successor.get(method.building)
            rows.append(Option(
                n=n, good=good, method=method.key, building=method.building,
                shares=shares, potential=potential, group=groups[potential],
                in_end=method.building not in game.obsoleted,
                adv=adv_method.get(method.key) or adv_building.get(method.building, ""),
                succ_adv=adv_building.get(successor, "") if successor else "",
            ))
        out[good] = rows
    return rights, goods, out


# --------------------------------------------------------------------------
# Что пишется в мод

HEAD = ("# Generated by mods/where_to_produce_v2/tools/generate.py. "
        "Do not edit by hand.\n#\n")


def values_file(game, rights, goods, options) -> str:
    """Доли сырья, покрытия, счёт каждого права и упаковка ответа."""
    out = [HEAD, "# Scope: см. комментарий над каждым значением.\n\n"]

    out.append("""# Единица РГО -- на сколько процентов выхода тянет одна единица усиления.
# Списана с `cm_trmm_rgo_unit`: база из `common/auto_modifiers/country.txt`,
# плюс два продвижения. Делением на неё уже стоящее усиление товара переводится
# в ту же шкалу, что и покрытие.
# Scope: location
bag_wtp2_tr_rgo_unit = {
\tvalue = 0.1
\tif = {
\t\tlimit = { exists = owner owner = { has_advance = rgo_logistics_discovery } }
\t\tadd = 0.025
\t}
\tif = {
\t\tlimit = { exists = owner owner = { has_advance = rgo_logistics_mil_choice } }
\t\tadd = 0.025
\t}
}

""")

    # ---- варианты: доля сырья одного метода -------------------------------
    out.append("# Один метод -- какую долю его сырья даёт провинция своими РГО.\n"
               "# Ворота эпохи стоят в каждой ветке: недоступный метод -- ноль.\n"
               "# Scope: province_definition\n\n")
    for good in sorted(options):
        for opt in options[good]:
            inputs = ", ".join(f"{g} {v:.3f}" for g, v in sorted(opt.shares.items()))
            out.append(f"# {opt.method} ({opt.building}): {inputs}\n")
            out.append(f"bag_wtp2_tr_opt{opt.n} = {{\n\tvalue = 0\n")
            for raw, share in sorted(opt.shares.items()):
                out.append(
                    f"\tif = {{\n"
                    f"\t\tlimit = {{\n"
                    f"\t\t\texists = global_var:bag_wtp2_tr_m{opt.n}\n"
                    f"\t\t\tany_location_in_province_definition = {{ raw_material ?= goods:{raw} }}\n"
                    f"\t\t}}\n"
                    f"\t\tadd = {share:.4f}\n"
                    f"\t}}\n")
            out.append("}\n")
        out.append("\n")

    # ---- покрытия: читаются с провинции, поправляются локацией -------------
    out.append("""# Покрытие товара в этой локации: число с провинции, ворота местности,
# своя РГО и уже стоящее усиление. Порядок важен -- усиление добавляется
# последним, иначе усреднение своей РГО делит и его пополам.
# Scope: location

""")
    for good in sorted(options):
        groups = sorted({o.group for o in options[good] if o.group > 1})
        for group in groups:
            potential = next(o.potential for o in options[good] if o.group == group)
            out.append(
                f"# {good}: варианты, которым нужна своя местность.\n"
                f"bag_wtp2_tr_covp_{good}_g{group} = {{\n"
                f"\tvalue = 0\n"
                f"\tif = {{\n"
                f"\t\tlimit = {{ province = {{ has_variable = bag_wtp2_tr_c_{good}_g{group} }} }}\n"
                f"\t\tprovince = {{ add = var:bag_wtp2_tr_c_{good}_g{group} }}\n"
                f"\t}}\n}}\n")
        out.append(f"bag_wtp2_tr_cov_{good} = {{\n\tvalue = 0\n")
        # **Группы 1 может не быть вовсе.** У смолы единственный метод -- курня,
        # и ей нужна своя местность, поэтому безусловного покрытия у товара нет.
        # Читать переменную, которую никто не пишет, -- это отказ без записи в
        # лог; `tools/check_script.py` ловит его на сборке.
        if any(o.group == 1 for o in options[good]):
            out.append(
                f"\tif = {{\n"
                f"\t\tlimit = {{ province = {{ has_variable = bag_wtp2_tr_c_{good} }} }}\n"
                f"\t\tprovince = {{ add = var:bag_wtp2_tr_c_{good} }}\n"
                f"\t}}\n")
        for group in groups:
            potential = next(o.potential for o in options[good] if o.group == group)
            building = next(o.building for o in options[good] if o.group == group)
            out.append(
                f"\t# {building}: своя местность.\n"
                f"\tmin = {{\n"
                f"\t\tvalue = 0\n"
                f"\t\tif = {{\n"
                f"\t\t\tlimit = {{\n{_indent(potential, 4)}\n\t\t\t}}\n"
                f"\t\t\tadd = bag_wtp2_tr_covp_{good}_g{group}\n"
                f"\t\t}}\n\t}}\n")
        if good in game.raw_goods:
            out.append(
                f"\t# Право усиливает и саму РГО этого товара, поэтому там, где она\n"
                f"\t# стоит, она считается ещё одним полностью покрытым производителем.\n"
                f"\tif = {{\n"
                f"\t\tlimit = {{ raw_material ?= goods:{good} }}\n"
                f"\t\tadd = 1\n\t\tdivide = 2\n\t}}\n")
        out.append(f"\tadd = bag_wtp2_tr_lm_{good}\n}}\n\n")

    # ---- уже стоящее усиление ---------------------------------------------
    out.append("""# Усиление товара, которое у локации уже есть, в единицах покрытия.
# Вклад самого права вычитается: иначе право хвалило бы город за себя же.
# Пол в нуле -- штрафной модификатор читается отрицательным, а отрицательный
# счёт ломает упаковку ответа.
# Scope: location

""")
    for good in sorted(options):
        out.append(f"bag_wtp2_tr_lm_{good} = {{\n"
                   f"\tvalue = modifier:{modifier_of(good)}\n")
        for right in sorted(game.town_rights, key=lambda r: r.key):
            if good in right.output:
                out.append(
                    f"\tif = {{\n"
                    f"\t\tlimit = {{ has_town_rights = town_rights_type:{right.key} }}\n"
                    f"\t\tsubtract = {right.output[good]:g}\n\t}}\n")
        out.append("\tdivide = bag_wtp2_tr_rgo_unit\n\tmin = 0\n}\n")
    out.append("\n")

    # ---- счёт права и упаковка --------------------------------------------
    out.append("# Счёт права -- среднее покрытий его товаров, ровно как у CM.\n"
               "# Scope: location\n\n")
    for key, index, _ in RIGHT_ORDER:
        boosted = sorted(rights[key].output)
        out.append(f"bag_wtp2_tr_right{index} = {{\n"
                   f"\tvalue = bag_wtp2_tr_cov_{boosted[0]}\n")
        for good in boosted[1:]:
            out.append(f"\tadd = bag_wtp2_tr_cov_{good}\n")
        if len(boosted) > 1:
            out.append(f"\tdivide = {len(boosted)}\n")
        out.append("}\n")
    out.append("\n")

    out.append("# Упаковка: round(счёт*1000)*10 + номер права. Одно число несёт и счёт,\n"
               "# и то, чьё оно, а больший номер выигрывает ничью.\n"
               "# Scope: location\n\n")
    for key, index, _ in RIGHT_ORDER:
        out.append(f"bag_wtp2_tr_enc{index} = {{\n"
                   f"\tvalue = bag_wtp2_tr_right{index}\n"
                   f"\tmultiply = 1000\n\tround = yes\n"
                   f"\tmultiply = 10\n\tadd = {index}\n}}\n")
    out.append("""
# Что печатает строка и чем сортируется список.
# Scope: location
bag_wtp2_tr_show_pct = {
\tvalue = 0
\tif = {
\t\tlimit = { has_variable = bag_wtp2_tr_best_mil }
\t\tadd = var:bag_wtp2_tr_best_mil
\t\tdivide = 10
\t}
\tround = yes
}
bag_wtp2_tr_order = {
\tvalue = 0
\tif = {
\t\tlimit = { has_variable = bag_wtp2_tr_best_mil }
\t\tsubtract = var:bag_wtp2_tr_best_mil
\t}
}
# Scope: country
bag_wtp2_tr_show_rows = { value = global_var:bag_wtp2_tr_row_count }
bag_wtp2_tr_show_locs = { value = global_var:bag_wtp2_tr_loc_count }
bag_wtp2_tr_show_runs = { value = global_var:bag_wtp2_tr_runs }
""")
    return "".join(out)


def _indent(text: str, depth: int) -> str:
    """Текст условия игры, выровненный под наш отступ и без пустых строк."""
    tab = "\t" * depth
    return "\n".join(tab + line.strip() for line in text.splitlines() if line.strip())


def triggers_file(game, rights, options) -> str:
    """Ворота эпохи по каждому методу и «город без специализации»."""
    out = [HEAD, "\n"]
    out.append("""# Город не держит ни одного права специализации.
# Scope: location
bag_wtp2_tr_no_spec = {
\tNOR = {
""")
    for key, _, _ in RIGHT_ORDER:
        out.append(f"\t\thas_town_rights = town_rights_type:{key}\n")
    out.append("\t}\n}\n\n")

    out.append("""# «Текущая эпоха» по каждому методу: здание уже открыто державе и её ещё не
# заменили следующей ступенью. Продвижение здания -- `unlock_building`,
# продвижение метода -- `unlock_production_method`; метод, за которым не стоит
# ни то ни другое, доступен с начала игры.
# Scope: country

""")
    for good in sorted(options):
        for opt in options[good]:
            out.append(f"bag_wtp2_tr_m{opt.n}_now = {{\n")
            if opt.adv:
                out.append(f"\thas_advance = {opt.adv}\n")
            if opt.succ_adv:
                out.append(f"\tNOT = {{ has_advance = {opt.succ_adv} }}\n")
            if not opt.adv and not opt.succ_adv:
                out.append("\talways = yes\n")
            out.append("}\n")
    return "".join(out)


def effects_file(game, rights, goods, options) -> str:
    """Проход: доступность методов, покрытия по провинции, ответ по локации."""
    out = [HEAD, "\n"]

    # ---- доступность методов ----------------------------------------------
    out.append("""# Какие методы считаются в этот раз. Пишется глобалками, потому что доли
# сырья считаются в скоупе провинции, а «может ли держава» -- вопрос к стране:
# глобальная переменная переносит ответ через эту границу.
# `bag_wtp2_tr_end` = 1 -- «Последняя эпоха».
# Scope: country
bag_wtp2_tr_set_avail = {
""")
    for good in sorted(options):
        for opt in options[good]:
            branches = []
            if opt.in_end:
                branches.append("AND = { global_var:bag_wtp2_tr_end = 1 }")
            branches.append(
                "AND = {\n\t\t\t\tNOT = { global_var:bag_wtp2_tr_end = 1 }\n"
                f"\t\t\t\tbag_wtp2_tr_m{opt.n}_now = yes\n\t\t\t}}")
            out.append(
                f"\tif = {{\n\t\tlimit = {{\n\t\t\tOR = {{\n\t\t\t\t"
                + "\n\t\t\t".join(branches)
                + f"\n\t\t\t}}\n\t\t}}\n"
                f"\t\tset_global_variable = {{ name = bag_wtp2_tr_m{opt.n} value = 1 }}\n"
                f"\t}}\n"
                f"\telse = {{ remove_global_variable = bag_wtp2_tr_m{opt.n} }}\n")
    out.append("}\n\n")

    # ---- покрытия по определению провинции --------------------------------
    out.append("""# Покрытия этого определения провинции, посчитанные один раз и разложенные
# по всем её кускам.
#
# **Переменная на самом `province_definition` не читается обратно** -- это
# правило первой версии и то же делает CM: всё считается в локальных, а пишется
# в каждую провинцию определения (`every_province_in_province_definition`).
# Локация потом читает своё через `province = { var:... }`.
# Scope: province_definition
bag_wtp2_tr_definition = {
""")
    for good in sorted(options):
        by_group: dict[int, list] = {}
        for opt in options[good]:
            by_group.setdefault(opt.group, []).append(opt)
        for group, rows in sorted(by_group.items()):
            name = f"g{good}_{group}"
            out.append(f"\tset_local_variable = {{ name = {name} value = bag_wtp2_tr_opt{rows[0].n} }}\n")
            for opt in rows[1:]:
                out.append(
                    f"\tif = {{\n"
                    f"\t\tlimit = {{ bag_wtp2_tr_opt{opt.n} > local_var:{name} }}\n"
                    f"\t\tset_local_variable = {{ name = {name} value = bag_wtp2_tr_opt{opt.n} }}\n"
                    f"\t}}\n")
    out.append("\n\tevery_province_in_province_definition = {\n")
    for good in sorted(options):
        for group in sorted({o.group for o in options[good]}):
            var = f"bag_wtp2_tr_c_{good}" + ("" if group == 1 else f"_g{group}")
            out.append(f"\t\tset_variable = {{ name = {var} value = local_var:g{good}_{group} }}\n")
    out.append("\t}\n}\n\n")

    # ---- ответ по локации --------------------------------------------------
    out.append("""# Лучшее право этой локации. Считается после того, как покрытия разложены.
# Ноль по всем девяти -- переменных не остаётся вовсе, и карта такую локацию не
# красит: «этой земле ни одно право ничего не даёт» -- это ответ, а не пустота.
# Scope: location
bag_wtp2_tr_score_location = {
""")
    first = RIGHT_ORDER[0][1]
    out.append(f"\tset_local_variable = {{ name = enc value = bag_wtp2_tr_enc{first} }}\n")
    for key, index, _ in RIGHT_ORDER[1:]:
        out.append(
            f"\tif = {{\n"
            f"\t\tlimit = {{ bag_wtp2_tr_enc{index} > local_var:enc }}\n"
            f"\t\tset_local_variable = {{ name = enc value = bag_wtp2_tr_enc{index} }}\n"
            f"\t}}\n")
    out.append("""\tif = {
\t\tlimit = { local_var:enc >= 10 }
\t\tset_variable = {
\t\t\tname = bag_wtp2_tr_best_idx
\t\t\tvalue = { value = local_var:enc modulo = 10 }
\t\t}
\t\tset_variable = {
\t\t\tname = bag_wtp2_tr_best_mil
\t\t\tvalue = {
\t\t\t\tvalue = local_var:enc
\t\t\t\tsubtract = var:bag_wtp2_tr_best_idx
\t\t\t\tdivide = 10
\t\t\t}
\t\t}
\t}
\telse = {
\t\tremove_variable = bag_wtp2_tr_best_idx
\t\tremove_variable = bag_wtp2_tr_best_mil
\t}
}

""")
    return "".join(out)


def mapmode_file(rights) -> str:
    """Режим карты: цвет локации -- цвет её лучшего права.

    **Индекс 4 в категории economy.** Занято: 0 и 1 -- Construction Manager,
    2 -- план первой версии, 3 -- выбор земли этого мода. Два мода на одном
    индексе сталкиваются, поэтому список держится здесь.
    """
    out = [HEAD, "\nbag_wtp2_rights = {\n\tmap_color = {\n"]
    out.append("\t\tif = {\n\t\t\tlimit = { is_land = no }\n"
               "\t\t\tvalue = define:NMapColors|DEFAULT_COLOR\n\t\t}\n")
    out.append("\t\telse_if = {\n"
               "\t\t\tlimit = { NOT = { has_variable = bag_wtp2_tr_best_idx } }\n"
               "\t\t\tvalue = define:NMapColors|DEFAULT_COLOR\n\t\t}\n")
    for key, index, color in RIGHT_ORDER:
        out.append(f"\t\telse_if = {{\n"
                   f"\t\t\tlimit = {{ var:bag_wtp2_tr_best_idx = {index} }}\n"
                   f"\t\t\t# {key}, цвет снят с карты Construction Manager\n"
                   f"\t\t\tvalue = {color}\n\t\t}}\n")
    out.append("\t}\n\n\ttooltip_key = {\n")
    out.append("\t\tif = {\n"
               "\t\t\tlimit = { has_variable = bag_wtp2_tr_best_idx }\n"
               "\t\t\tvalue = bag_wtp2_tr_map_tt\n\t\t}\n"
               "\t\telse = { value = bag_wtp2_tr_map_empty_tt }\n\t}\n\n")
    for key, index, color in RIGHT_ORDER:
        out.append(f"\tlegend_key = {{\n\t\tdesc = bag_wtp2_tr_name{index}\n"
                   f"\t\tcolor = {color}\n\t}}\n")
    out.append("""
\tsmall_map_names = location
\tmedium_map_names = province
\tlarge_map_names = area
\tsmall_tooltip_context = location
\tmedium_tooltip_context = location
\tlarge_tooltip_context = location
\tcategory = economy
\tindex = 4
\tallow_allocate_hotkey = yes
\tflatmap_behaviour = Always
\tfill_in_impassable = no
\tuse_fow = no
\tenable_rivers = yes
\tmap_markers = { all = no }

\tgradient_parameters = {
\t\tzoom_step = 2
\t\tgradient_alpha_inside = 1
\t\tgradient_alpha_outside = 1
\t\tgradient_width = 0.25
\t\tgradient_color_mult = 0.9
\t\tedge_width = 0
\t\tedge_sharpness = 0.01
\t\tedge_alpha = 0
\t\tedge_color_mult = 0
\t\tbefore_lighting_blend = 0.5
\t\tafter_lighting_blend = 0.5
\t}
\tflatmap_gradient_parameters = {
\t\tzoom_step = 12
\t\tgradient_alpha_inside = 1
\t\tgradient_alpha_outside = 1
\t\tgradient_width = 0.25
\t\tgradient_color_mult = 0.9
\t\tedge_width = 0
\t\tedge_sharpness = 0.01
\t\tedge_alpha = 0
\t\tedge_color_mult = 0
\t\tbefore_lighting_blend = 0.5
\t\tafter_lighting_blend = 0.5
\t}
\tcolor_refresh_counters = { Day }
\tcolor_and_names_refresh_counters = { LocationOwnerChanged }
}
""")
    return "".join(out)


def loc_file(rights) -> str:
    """Имя лучшего права клеткой строки -- через диспетчер локализации.

    **Условие внутри значения ключа ломает клетку.** Это правило первой версии:
    выбирать текст по номеру обязан `customizable_localization`, а не `if`
    внутри самой строки.
    """
    out = [HEAD, "\nbag_wtp2_tr_right_name = {\n"]
    for key, index, _ in RIGHT_ORDER:
        out.append(f"\ttext = {{\n"
                   f"\t\ttrigger = {{ var:bag_wtp2_tr_best_idx = {index} }}\n"
                   f"\t\tlocalization_key = bag_wtp2_tr_name{index}\n\t}}\n")
    out.append("\ttext = {\n\t\tlocalization_key = bag_wtp2_tr_name0\n\t}\n}\n")
    return "".join(out)


def loc_keys(language: str, rights) -> list[tuple[str, str]]:
    """Имена девяти прав. Читаются из игры нельзя -- пишем свои, оба языка."""
    names = {
        "russian": {
            "royal_tooling_rights": "Снаряжение",
            "royal_jewelry_rights": "Ювелирное",
            "royal_naval_rights": "Морское",
            "royal_textile_rights": "Текстильное",
            "royal_weaponry_rights": "Оружейное",
            "royal_book_rights": "Книжное",
            "royal_artisan_rights": "Ремесленное",
            "royal_brewing_rights": "Пивоваренное",
            "royal_masonry_rights": "Каменное",
        },
        "english": {
            "royal_tooling_rights": "Tooling",
            "royal_jewelry_rights": "Jewelry",
            "royal_naval_rights": "Naval",
            "royal_textile_rights": "Textile",
            "royal_weaponry_rights": "Weaponry",
            "royal_book_rights": "Book",
            "royal_artisan_rights": "Artisan",
            "royal_brewing_rights": "Brewing",
            "royal_masonry_rights": "Masonry",
        },
    }[language]
    rows = [(f"bag_wtp2_tr_name{index}", names[key]) for key, index, _ in RIGHT_ORDER]
    rows.append(("bag_wtp2_tr_name0", "—" if language == "russian" else "-"))
    return rows
