#!/usr/bin/env python3
"""Every word this mod puts on screen, in each of the eleven EU5 languages.

The mod's Russian is 1123 keys, but a language does not cost 1123 translations.
Almost every hint line is an opener, a `$key$` reference the game resolves in
whatever language the player runs, and a number — so what a language actually
needs is the openers. That is the table below, and it is about fifty short
strings.

**The fourteen category nouns are not in it.** "Religious aspect", "Advance",
"Subject type" and the rest are *game concepts*: the game defines
`game_concept_religious_aspect` in all eleven of its localization folders, and
`[religious_aspect|e]` renders that in the player's language with the
encyclopedia link attached. So the category is not translated here at all — it
is asked of the game, which also means the mod uses the game's own word rather
than a synonym. That fixed seven Russian terms that were synonyms: the game
calls an advance «Улучшение», not «Достижение», and a subject type «Тип
ленника», not «Тип вассала».

The eleven languages are the folders every mod in `reference/mods/` ships:
Community Mod Framework, Glorp UI and Construction Manager all carry exactly
these, and the game's own `main_menu/localization/` is a subset of them.

`russian` is the language the mod shipped in and the only one confirmed on
screen. The other ten have never been seen in game by anybody; they are written
against the game's own terminology where a concept exists and are otherwise a
careful translation of the Russian. Read [`../README.md`](../README.md) before
correcting one — the openers are the *only* place a language may differ, and a
correction belongs here rather than in a generated `.yml`.
"""

from __future__ import annotations

# In the order the folders are listed; `english` first because it is the
# language every other one is derived from.
LANGUAGES = [
    "english", "french", "german", "spanish", "braz_por", "polish",
    "russian", "turkish", "simp_chinese", "japanese", "korean",
]

# The category a catalogue line opens with, as a game concept rather than as a
# translated noun. Every id here is a `game_concept_<id>` key the game defines
# in all eleven of its localization folders — checked by generate.py against
# `reference/game/main_menu/localization/`, so a concept the game renames fails
# the run instead of printing a raw token on screen.
#
# `building_types` is the one exception and is not in this table: its pushes are
# all `capital_country_modifier`, so the line has to say *build it in the
# capital* rather than merely "building type", and that is a real phrase in
# `build_in_capital` below.
CATALOG_CONCEPTS = {
    "employment_systems": "employment_system",
    "religious_aspects": "religious_aspect",
    "religious_schools": "religious_school",
    "parliament_issues": "parliament_issue",
    "chivalric_orders": "chivalric_order",
    "subject_types": "subject_type",
    "estates": "estate",
    "cabinet_actions": "cabinet_action",
    "international_organizations": "international_organization",
    "international_organization_special_statuses": "special_status",
    "advances": "advance",
    "missions": "mission",
    "parliament_types": "parliament_type",
}

# The tooltip registry each catalogue source lives in, which is what makes the
# object name hoverable. Registry names are the game's own `#TOOLTIP:` tokens.
CATALOG_REGISTRIES = {
    "employment_systems": "EMPLOYMENT_SYSTEM",
    "building_types": "BUILDING_TYPE",
    "religious_aspects": "RELIGIOUS_ASPECT",
    "religious_schools": "RELIGIOUS_SCHOOL",
    "parliament_issues": "PARLIAMENT_ISSUE",
    "chivalric_orders": "CHIVALRIC_ORDER",
    "subject_types": "SUBJECT_TYPE",
    "estates": "ESTATE_TYPE",
    "cabinet_actions": "CABINET_ACTION",
    "international_organizations": "INTERNATIONAL_ORGANIZATION",
    "international_organization_special_statuses": "SPECIAL_STATUS",
    "advances": "ADVANCE_DEFINITION",
    "missions": "MISSION",
    "parliament_types": "PARLIAMENT_TYPE",
}

# What a scaled modifier is called. Always in force, magnitude growing with the
# state of the country, so the number printed is the maximum.
SCALED_KEYS = [
    "fort_maintenance_mod", "army_maintenance_mod", "navy_maintenance_mod",
    "army_experience", "navy_experience", "army_tradition", "navy_tradition",
    "current_army_size", "current_navy_size", "average_control",
    "average_development", "average_literacy", "num_of_market_centers_in_country",
    "trade_vs_tax", "burghers_percentage_in_country",
    "peasants_percentage_in_country", "soldier_percentage_in_country",
    "state_religion_clergy_ratio", "proper_culture_nobles_ratio",
]

# Switched on whole by a condition, so the number printed is exact and the
# label is the condition itself.
CONDITIONAL_KEYS = [
    "is_bankrupt", "at_peace", "at_war", "attacker_in_war", "defender_in_war",
    "over_fort_limit", "below_half_fort_limit", "larger_than_expected_army",
    "high_legitimacy", "high_republican_tradition", "positive_self_control",
    "negative_self_control", "parliament_in_capital", "parliament_outside_capital",
    "ruler_is_general", "ruler_is_admiral", "ruler_has_general_trait",
    "ruler_has_admiral_trait", "heir_is_general", "heir_is_admiral",
    "regent_is_general", "regent_is_admiral",
]


def _language(hint, catalog, build_in_capital, scales, up_to, cabinet,
              cabinet_scales, titles, menu, scaled, conditional):
    """One language's table, with the two list orders checked as it is built."""
    assert list(scaled) == SCALED_KEYS, "scaled labels out of order"
    assert list(conditional) == CONDITIONAL_KEYS, "conditional labels out of order"
    return {
        "hint": hint,
        "catalog": catalog,
        "build_in_capital": build_in_capital,
        "scales": scales,
        "up_to": up_to,
        "cabinet": cabinet,
        "cabinet_scales": cabinet_scales,
        "titles": titles,
        "menu": menu,
        "scaled": scaled,
        "conditional": conditional,
    }


def _pairs(keys, values):
    return dict(zip(keys, values))


PHRASES: dict[str, dict] = {}

# --- english ---------------------------------------------------------------
# The three hint openers are Glorp UI's own English, character for character,
# concept tokens and all: this mod has no business rewording the language the
# file it derives from is already written in.
PHRASES["english"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "Grant {ref}",
        "GOVERNMENT_REFORM": "Add the {ref} [government_reform|e]",
        "POLICY": "Enact the {ref} [policy]",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="Build in the capital",
    scales="scales",
    up_to="up to ",
    cabinet="Point the cabinet at this value",
    cabinet_scales="scales with cabinet efficiency",
    titles={
        "SVX_ALSO_PUSHES": "Also pushes towards this:",
        "SVX_REACHABLE": "Becomes available under these conditions:",
        "SVX_EVERYTHING": "Pushes towards this (unfiltered):",
    },
    menu={
        "svx_name": "Societal Value Hints",
        "svx_desc": "Adds to the societal value tooltip the sources Glorp UI's "
                    "list does not read, and drops from it what your country "
                    "cannot take.",
        "svx__main_name": "Lists",
        "svx__main__lists_name": "Filtering",
        "svx__show_all_name": "Show everything, unfiltered",
        "svx__show_all_desc":
            "Normally the list drops what your country cannot take: "
            "organizations you cannot join, missions in a game with missions "
            "switched off, parliament issues of an estate you do not have. Turn "
            "this on to see the whole set at once — for instance when you mean "
            "to fight your way to something that is out of reach today.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "Fort maintenance", "Army maintenance", "Navy maintenance",
        "Army experience", "Navy experience", "Army tradition", "Navy tradition",
        "Army size", "Navy size", "Average control", "Average development",
        "Average literacy", "Number of market centres",
        "Share of trade in income", "Share of burghers in the population",
        "Share of peasants in the population", "Share of soldiers in the population",
        "Share of state religion clergy", "Share of primary culture nobles",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "While bankrupt", "In peacetime", "In wartime", "Attacker in a war",
        "Defender in a war", "Over the fort limit",
        "Below half the fort limit", "Army larger than expected",
        "High legitimacy", "High republican tradition",
        "Ruler with high self-control", "Ruler with low self-control",
        "Parliament in the capital", "Parliament outside the capital",
        "Ruler is a general", "Ruler is an admiral",
        "Ruler has a general's trait", "Ruler has an admiral's trait",
        "Heir is a general", "Heir is an admiral",
        "Regent is a general", "Regent is an admiral",
    ]),
)

# --- russian ---------------------------------------------------------------
# The language the mod shipped in and the only one confirmed on screen. Only the
# fourteen category nouns changed when the concept tokens went in, and they
# changed towards the game's own vocabulary rather than away from it.
PHRASES["russian"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "Даровать привилегию {ref}",
        "GOVERNMENT_REFORM": "Принять реформу правления {ref}",
        "POLICY": "Ввести политику {ref}",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="Построить в столице",
    scales="масштабируется",
    up_to="до ",
    cabinet="Направить совет на эту ценность",
    cabinet_scales="масштабируется от эффективности совета",
    titles={
        "SVX_ALSO_PUSHES": "Также влияет на смещение:",
        "SVX_REACHABLE": "Станет доступно при условиях:",
        "SVX_EVERYTHING": "Влияет на смещение (без фильтра):",
    },
    menu={
        "svx_name": "Подсказки общественных ценностей",
        "svx_desc": "Дополняет подсказку общественной ценности источниками, "
                    "которых нет в списке Glorp UI, и убирает из неё то, что "
                    "вашей державе недоступно.",
        "svx__main_name": "Списки",
        "svx__main__lists_name": "Фильтрация",
        "svx__show_all_name": "Показывать всё без фильтра",
        "svx__show_all_desc":
            "Обычно из списка убрано то, чего держава взять не может: "
            "организации, куда не вступить, миссии при выключенных миссиях, "
            "вопросы парламента не вашего сословия. Включите, чтобы увидеть "
            "весь набор целиком — например, если собираетесь пробиваться туда, "
            "где сейчас вам ничего не доступно.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "Содержание крепостей", "Содержание армии", "Содержание флота",
        "Опыт армии", "Опыт флота", "Традиции армии", "Традиции флота",
        "Размер армии", "Размер флота", "Средний контроль", "Среднее развитие",
        "Средняя грамотность", "Число рыночных центров",
        "Доля торговли в доходах", "Доля горожан в населении",
        "Доля крестьян в населении", "Доля солдат в населении",
        "Доля духовенства госрелигии", "Доля знати основной культуры",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "Во время банкротства", "В мирное время", "Во время войны",
        "Нападающая сторона в войне", "Обороняющаяся сторона в войне",
        "Превышен лимит крепостей", "Крепостей меньше половины лимита",
        "Армия больше ожидаемой", "Высокая легитимность",
        "Высокие республиканские традиции", "Высокое самообладание правителя",
        "Низкое самообладание правителя", "Парламент в столице",
        "Парламент вне столицы", "Правитель - генерал", "Правитель - адмирал",
        "У правителя черта генерала", "У правителя черта адмирала",
        "Наследник - генерал", "Наследник - адмирал",
        "Регент - генерал", "Регент - адмирал",
    ]),
)

# --- french ----------------------------------------------------------------
PHRASES["french"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "Accorder le privilège {ref}",
        "GOVERNMENT_REFORM": "Adopter la réforme {ref}",
        "POLICY": "Promulguer la politique {ref}",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="Construire dans la capitale",
    scales="variable",
    up_to="jusqu'à ",
    cabinet="Orienter le cabinet vers cette valeur",
    cabinet_scales="varie avec l'efficacité du cabinet",
    titles={
        "SVX_ALSO_PUSHES": "Pousse également dans ce sens :",
        "SVX_REACHABLE": "Deviendra disponible sous conditions :",
        "SVX_EVERYTHING": "Pousse dans ce sens (sans filtre) :",
    },
    menu={
        "svx_name": "Indices de valeurs sociétales",
        "svx_desc": "Ajoute à l'infobulle de valeur sociétale les sources que la "
                    "liste de Glorp UI ne lit pas, et en retire ce que votre pays "
                    "ne peut pas obtenir.",
        "svx__main_name": "Listes",
        "svx__main__lists_name": "Filtrage",
        "svx__show_all_name": "Tout afficher, sans filtre",
        "svx__show_all_desc":
            "Normalement la liste retire ce que votre pays ne peut pas obtenir : "
            "les organisations que vous ne pouvez pas rejoindre, les missions "
            "dans une partie où elles sont désactivées, les questions "
            "parlementaires d'un ordre que vous n'avez pas. Activez cette option "
            "pour voir l'ensemble d'un coup — par exemple si vous comptez vous "
            "frayer un chemin vers ce qui est hors de portée aujourd'hui.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "Entretien des forts", "Entretien de l'armée", "Entretien de la flotte",
        "Expérience de l'armée", "Expérience de la flotte",
        "Tradition militaire", "Tradition navale",
        "Taille de l'armée", "Taille de la flotte", "Contrôle moyen",
        "Développement moyen", "Alphabétisation moyenne",
        "Nombre de centres commerciaux", "Part du commerce dans les revenus",
        "Part des bourgeois dans la population",
        "Part des paysans dans la population",
        "Part des soldats dans la population",
        "Part du clergé de la religion d'État",
        "Part des nobles de la culture principale",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "En cas de banqueroute", "En temps de paix", "En temps de guerre",
        "Assaillant dans une guerre", "Défenseur dans une guerre",
        "Au-dessus de la limite de forts",
        "En dessous de la moitié de la limite de forts",
        "Armée plus grande que prévu", "Légitimité élevée",
        "Tradition républicaine élevée", "Souverain très maître de lui",
        "Souverain peu maître de lui", "Parlement dans la capitale",
        "Parlement hors de la capitale", "Le souverain est un général",
        "Le souverain est un amiral", "Le souverain a un trait de général",
        "Le souverain a un trait d'amiral", "L'héritier est un général",
        "L'héritier est un amiral", "Le régent est un général",
        "Le régent est un amiral",
    ]),
)

# --- german ----------------------------------------------------------------
PHRASES["german"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "Privileg {ref} gewähren",
        "GOVERNMENT_REFORM": "Reform {ref} einführen",
        "POLICY": "Politik {ref} erlassen",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="In der Hauptstadt bauen",
    scales="skaliert",
    up_to="bis zu ",
    cabinet="Das Kabinett auf diesen Wert ausrichten",
    cabinet_scales="skaliert mit der Kabinettseffizienz",
    titles={
        "SVX_ALSO_PUSHES": "Verschiebt ebenfalls in diese Richtung:",
        "SVX_REACHABLE": "Wird unter diesen Bedingungen verfügbar:",
        "SVX_EVERYTHING": "Verschiebt in diese Richtung (ungefiltert):",
    },
    menu={
        "svx_name": "Hinweise zu Gesellschaftswerten",
        "svx_desc": "Ergänzt den Gesellschaftswert-Tooltip um die Quellen, die "
                    "Glorp UIs Liste nicht liest, und entfernt daraus, was Euer "
                    "Land nicht nehmen kann.",
        "svx__main_name": "Listen",
        "svx__main__lists_name": "Filterung",
        "svx__show_all_name": "Alles anzeigen, ungefiltert",
        "svx__show_all_desc":
            "Normalerweise entfernt die Liste, was Euer Land nicht nehmen kann: "
            "Organisationen, denen Ihr nicht beitreten könnt, Missionen in einer "
            "Partie ohne Missionen, Parlamentsfragen eines Standes, den Ihr nicht "
            "habt. Schaltet dies ein, um den ganzen Satz auf einmal zu sehen — "
            "etwa wenn Ihr Euch den Weg zu etwas bahnen wollt, das heute außer "
            "Reichweite liegt.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "Festungsunterhalt", "Heeresunterhalt", "Flottenunterhalt",
        "Heereserfahrung", "Flottenerfahrung", "Heerestradition",
        "Flottentradition", "Heeresgröße", "Flottengröße",
        "Durchschnittliche Kontrolle", "Durchschnittliche Entwicklung",
        "Durchschnittliche Alphabetisierung", "Anzahl der Handelszentren",
        "Anteil des Handels an den Einnahmen",
        "Anteil der Bürger an der Bevölkerung",
        "Anteil der Bauern an der Bevölkerung",
        "Anteil der Soldaten an der Bevölkerung",
        "Anteil des Klerus der Staatsreligion",
        "Anteil des Adels der Hauptkultur",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "Während des Staatsbankrotts", "In Friedenszeiten", "In Kriegszeiten",
        "Angreifer in einem Krieg", "Verteidiger in einem Krieg",
        "Über der Festungsgrenze", "Unter der halben Festungsgrenze",
        "Heer größer als erwartet", "Hohe Legitimität",
        "Hohe republikanische Tradition",
        "Herrscher mit hoher Selbstbeherrschung",
        "Herrscher mit geringer Selbstbeherrschung",
        "Parlament in der Hauptstadt", "Parlament außerhalb der Hauptstadt",
        "Herrscher ist General", "Herrscher ist Admiral",
        "Herrscher hat eine Generalseigenschaft",
        "Herrscher hat eine Admiralseigenschaft",
        "Thronfolger ist General", "Thronfolger ist Admiral",
        "Regent ist General", "Regent ist Admiral",
    ]),
)

# --- spanish ---------------------------------------------------------------
PHRASES["spanish"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "Conceder el privilegio {ref}",
        "GOVERNMENT_REFORM": "Adoptar la reforma {ref}",
        "POLICY": "Promulgar la política {ref}",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="Construir en la capital",
    scales="escala",
    up_to="hasta ",
    cabinet="Orientar el gabinete hacia este valor",
    cabinet_scales="escala con la eficiencia del gabinete",
    titles={
        "SVX_ALSO_PUSHES": "También empuja en este sentido:",
        "SVX_REACHABLE": "Estará disponible en estas condiciones:",
        "SVX_EVERYTHING": "Empuja en este sentido (sin filtro):",
    },
    menu={
        "svx_name": "Sugerencias de valores sociales",
        "svx_desc": "Añade a la descripción del valor social las fuentes que la "
                    "lista de Glorp UI no lee, y quita de ella lo que tu país no "
                    "puede obtener.",
        "svx__main_name": "Listas",
        "svx__main__lists_name": "Filtrado",
        "svx__show_all_name": "Mostrar todo, sin filtrar",
        "svx__show_all_desc":
            "Normalmente la lista descarta lo que tu país no puede obtener: "
            "organizaciones a las que no puedes unirte, misiones en una partida "
            "con las misiones desactivadas, cuestiones parlamentarias de un "
            "estamento que no tienes. Actívalo para ver el conjunto completo de "
            "una vez, por ejemplo si piensas abrirte camino hacia algo que hoy "
            "queda fuera de tu alcance.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "Mantenimiento de fuertes", "Mantenimiento del ejército",
        "Mantenimiento de la armada", "Experiencia del ejército",
        "Experiencia de la armada", "Tradición militar", "Tradición naval",
        "Tamaño del ejército", "Tamaño de la armada", "Control medio",
        "Desarrollo medio", "Alfabetización media",
        "Número de centros de mercado", "Proporción del comercio en los ingresos",
        "Proporción de burgueses en la población",
        "Proporción de campesinos en la población",
        "Proporción de soldados en la población",
        "Proporción del clero de la religión estatal",
        "Proporción de nobles de la cultura principal",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "Durante la bancarrota", "En tiempos de paz", "En tiempos de guerra",
        "Atacante en una guerra", "Defensor en una guerra",
        "Por encima del límite de fuertes",
        "Por debajo de la mitad del límite de fuertes",
        "Ejército mayor de lo esperado", "Legitimidad alta",
        "Tradición republicana alta", "Gobernante con mucho autocontrol",
        "Gobernante con poco autocontrol", "Parlamento en la capital",
        "Parlamento fuera de la capital", "El gobernante es general",
        "El gobernante es almirante", "El gobernante tiene un rasgo de general",
        "El gobernante tiene un rasgo de almirante", "El heredero es general",
        "El heredero es almirante", "El regente es general",
        "El regente es almirante",
    ]),
)

# --- braz_por --------------------------------------------------------------
PHRASES["braz_por"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "Conceder o privilégio {ref}",
        "GOVERNMENT_REFORM": "Adotar a reforma {ref}",
        "POLICY": "Promulgar a política {ref}",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="Construir na capital",
    scales="escala",
    up_to="até ",
    cabinet="Direcionar o gabinete para este valor",
    cabinet_scales="escala com a eficiência do gabinete",
    titles={
        "SVX_ALSO_PUSHES": "Também empurra nesse sentido:",
        "SVX_REACHABLE": "Ficará disponível nestas condições:",
        "SVX_EVERYTHING": "Empurra nesse sentido (sem filtro):",
    },
    menu={
        "svx_name": "Dicas de valores sociais",
        "svx_desc": "Acrescenta à dica do valor social as fontes que a lista do "
                    "Glorp UI não lê, e remove dela o que o seu país não pode "
                    "obter.",
        "svx__main_name": "Listas",
        "svx__main__lists_name": "Filtragem",
        "svx__show_all_name": "Mostrar tudo, sem filtro",
        "svx__show_all_desc":
            "Normalmente a lista descarta o que o seu país não pode obter: "
            "organizações às quais não pode aderir, missões numa partida com as "
            "missões desligadas, questões parlamentares de um estamento que você "
            "não possui. Ative para ver o conjunto completo de uma vez, por "
            "exemplo se pretende abrir caminho até algo que hoje está fora de "
            "alcance.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "Manutenção de fortes", "Manutenção do exército",
        "Manutenção da marinha", "Experiência do exército",
        "Experiência da marinha", "Tradição militar", "Tradição naval",
        "Tamanho do exército", "Tamanho da marinha", "Controle médio",
        "Desenvolvimento médio", "Alfabetização média",
        "Número de centros de mercado", "Parcela do comércio na receita",
        "Parcela de burgueses na população",
        "Parcela de camponeses na população",
        "Parcela de soldados na população",
        "Parcela do clero da religião oficial",
        "Parcela de nobres da cultura principal",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "Durante a bancarrota", "Em tempos de paz", "Em tempos de guerra",
        "Atacante numa guerra", "Defensor numa guerra",
        "Acima do limite de fortes", "Abaixo de metade do limite de fortes",
        "Exército maior do que o esperado", "Legitimidade alta",
        "Tradição republicana alta", "Governante com muito autocontrole",
        "Governante com pouco autocontrole", "Parlamento na capital",
        "Parlamento fora da capital", "O governante é general",
        "O governante é almirante", "O governante tem um traço de general",
        "O governante tem um traço de almirante", "O herdeiro é general",
        "O herdeiro é almirante", "O regente é general",
        "O regente é almirante",
    ]),
)

# --- polish ----------------------------------------------------------------
PHRASES["polish"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "Nadaj przywilej {ref}",
        "GOVERNMENT_REFORM": "Wprowadź reformę {ref}",
        "POLICY": "Wprowadź politykę {ref}",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="Zbuduj w stolicy",
    scales="skaluje się",
    up_to="do ",
    cabinet="Skieruj gabinet na tę wartość",
    cabinet_scales="skaluje się z efektywnością gabinetu",
    titles={
        "SVX_ALSO_PUSHES": "Również przesuwa w tę stronę:",
        "SVX_REACHABLE": "Stanie się dostępne po spełnieniu warunków:",
        "SVX_EVERYTHING": "Przesuwa w tę stronę (bez filtra):",
    },
    menu={
        "svx_name": "Podpowiedzi wartości społecznych",
        "svx_desc": "Dodaje do podpowiedzi wartości społecznej źródła, których "
                    "lista Glorp UI nie czyta, i usuwa z niej to, czego twój kraj "
                    "nie może wziąć.",
        "svx__main_name": "Listy",
        "svx__main__lists_name": "Filtrowanie",
        "svx__show_all_name": "Pokaż wszystko, bez filtra",
        "svx__show_all_desc":
            "Zwykle lista pomija to, czego twój kraj nie może wziąć: organizacje, "
            "do których nie możesz dołączyć, misje w rozgrywce z wyłączonymi "
            "misjami, sprawy parlamentu stanu, którego nie masz. Włącz, aby "
            "zobaczyć cały zestaw naraz — na przykład gdy zamierzasz przebić się "
            "do czegoś, co dziś jest poza zasięgiem.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "Utrzymanie fortów", "Utrzymanie armii", "Utrzymanie floty",
        "Doświadczenie armii", "Doświadczenie floty", "Tradycja armii",
        "Tradycja floty", "Wielkość armii", "Wielkość floty",
        "Średnia kontrola", "Średni rozwój", "Średnia piśmienność",
        "Liczba centrów handlowych", "Udział handlu w dochodach",
        "Udział mieszczan w ludności", "Udział chłopów w ludności",
        "Udział żołnierzy w ludności",
        "Udział duchowieństwa religii państwowej",
        "Udział szlachty kultury głównej",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "W czasie bankructwa", "W czasie pokoju", "W czasie wojny",
        "Strona atakująca w wojnie", "Strona broniąca się w wojnie",
        "Powyżej limitu fortów", "Poniżej połowy limitu fortów",
        "Armia większa niż oczekiwana", "Wysoka legitymizacja",
        "Wysoka tradycja republikańska", "Władca o dużym opanowaniu",
        "Władca o małym opanowaniu", "Parlament w stolicy",
        "Parlament poza stolicą", "Władca jest generałem",
        "Władca jest admirałem", "Władca ma cechę generała",
        "Władca ma cechę admirała", "Następca jest generałem",
        "Następca jest admirałem", "Regent jest generałem",
        "Regent jest admirałem",
    ]),
)

# --- turkish ---------------------------------------------------------------
PHRASES["turkish"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "{ref} ayrıcalığını tanı",
        "GOVERNMENT_REFORM": "{ref} reformunu benimse",
        "POLICY": "{ref} politikasını uygula",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="Başkentte inşa et",
    scales="ölçeklenir",
    up_to="en fazla ",
    cabinet="Kabineyi bu değere yönlendir",
    cabinet_scales="kabine verimliliğine göre ölçeklenir",
    titles={
        "SVX_ALSO_PUSHES": "Bu yöne de iter:",
        "SVX_REACHABLE": "Şu koşullarda kullanılabilir olacak:",
        "SVX_EVERYTHING": "Bu yöne iter (filtresiz):",
    },
    menu={
        "svx_name": "Toplumsal değer ipuçları",
        "svx_desc": "Toplumsal değer ipucuna Glorp UI listesinin okumadığı "
                    "kaynakları ekler ve ülkenizin alamayacaklarını listeden "
                    "çıkarır.",
        "svx__main_name": "Listeler",
        "svx__main__lists_name": "Filtreleme",
        "svx__show_all_name": "Her şeyi göster, filtresiz",
        "svx__show_all_desc":
            "Liste normalde ülkenizin alamayacaklarını gizler: katılamayacağınız "
            "örgütler, görevlerin kapalı olduğu bir oyunda görevler, sahip "
            "olmadığınız zümrenin parlamento meseleleri. Tümünü bir arada görmek "
            "için açın — örneğin bugün ulaşamadığınız bir şeye doğru yol açmayı "
            "planlıyorsanız.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "Kale bakımı", "Ordu bakımı", "Donanma bakımı", "Ordu tecrübesi",
        "Donanma tecrübesi", "Ordu geleneği", "Donanma geleneği",
        "Ordu büyüklüğü", "Donanma büyüklüğü", "Ortalama kontrol",
        "Ortalama gelişim", "Ortalama okuryazarlık", "Pazar merkezi sayısı",
        "Gelirde ticaretin payı", "Nüfusta burjuvaların payı",
        "Nüfusta köylülerin payı", "Nüfusta askerlerin payı",
        "Devlet dini ruhban sınıfının payı", "Ana kültür soylularının payı",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "İflas sırasında", "Barış zamanında", "Savaş zamanında",
        "Savaşta saldıran taraf", "Savaşta savunan taraf",
        "Kale sınırının üzerinde", "Kale sınırının yarısının altında",
        "Ordu beklenenden büyük", "Yüksek meşruiyet",
        "Yüksek cumhuriyetçi gelenek", "Öz denetimi yüksek hükümdar",
        "Öz denetimi düşük hükümdar", "Başkentte parlamento",
        "Başkent dışında parlamento", "Hükümdar general", "Hükümdar amiral",
        "Hükümdarda general özelliği var", "Hükümdarda amiral özelliği var",
        "Veliaht general", "Veliaht amiral", "Naip general", "Naip amiral",
    ]),
)

# --- simp_chinese ----------------------------------------------------------
PHRASES["simp_chinese"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "授予特权{ref}",
        "GOVERNMENT_REFORM": "推行改革{ref}",
        "POLICY": "颁布政策{ref}",
    },
    catalog="[{concept}|e]{ref}",
    build_in_capital="在首都建造",
    scales="按比例变化",
    up_to="最多 ",
    cabinet="让内阁推动该价值观",
    cabinet_scales="随内阁效率变化",
    titles={
        "SVX_ALSO_PUSHES": "同样推动该方向：",
        "SVX_REACHABLE": "满足条件后可用：",
        "SVX_EVERYTHING": "推动该方向（无筛选）：",
    },
    menu={
        "svx_name": "社会价值提示",
        "svx_desc": "在社会价值提示中补上 Glorp UI 列表未读取的来源，"
                    "并移除你的国家无法获得的条目。",
        "svx__main_name": "列表",
        "svx__main__lists_name": "筛选",
        "svx__show_all_name": "显示全部，不筛选",
        "svx__show_all_desc":
            "列表通常会隐去你的国家无法获得的内容：无法加入的国际组织、"
            "关闭任务的存档中的任务、你没有的等级所提出的议会议题。"
            "打开此项可一次看到完整集合——例如当你打算一路打到目前够不着的地方时。",
    },
    scaled=_pairs(SCALED_KEYS, [
        "堡垒维护费", "陆军维护费", "海军维护费", "陆军经验", "海军经验",
        "陆军传统", "海军传统", "陆军规模", "海军规模", "平均控制度",
        "平均发展度", "平均识字率", "市场中心数量", "贸易收入占比",
        "市民人口占比", "农民人口占比", "士兵人口占比",
        "国教神职人员占比", "主流文化贵族占比",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "破产期间", "和平时期", "战争时期", "战争中的进攻方", "战争中的防守方",
        "超出堡垒上限", "低于堡垒上限的一半", "陆军规模超出预期",
        "高正统性", "高共和传统", "自制力高的统治者", "自制力低的统治者",
        "议会位于首都", "议会不在首都", "统治者是将军", "统治者是海军将领",
        "统治者拥有将军特质", "统治者拥有海军将领特质",
        "继承人是将军", "继承人是海军将领", "摄政是将军", "摄政是海军将领",
    ]),
)

# --- japanese --------------------------------------------------------------
PHRASES["japanese"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "{ref}を付与",
        "GOVERNMENT_REFORM": "{ref}を採用",
        "POLICY": "{ref}を制定",
    },
    catalog="[{concept}|e]{ref}",
    build_in_capital="首都に建設",
    scales="規模に応じて変動",
    up_to="最大 ",
    cabinet="内閣をこの価値観に向ける",
    cabinet_scales="内閣の効率に応じて変動",
    titles={
        "SVX_ALSO_PUSHES": "この方向にも作用：",
        "SVX_REACHABLE": "条件を満たすと利用可能：",
        "SVX_EVERYTHING": "この方向に作用（フィルタなし）：",
    },
    menu={
        "svx_name": "社会的価値のヒント",
        "svx_desc": "社会的価値のツールチップに Glorp UI の一覧が読み取らない"
                    "要素を追加し、自国が取得できないものを取り除きます。",
        "svx__main_name": "一覧",
        "svx__main__lists_name": "フィルタ",
        "svx__show_all_name": "すべて表示（フィルタなし）",
        "svx__show_all_desc":
            "通常、この一覧は自国が取得できないものを取り除きます。"
            "加入できない国際機関、ミッションを無効にしたゲームでのミッション、"
            "保有していない身分の議会案件などです。"
            "全体を一度に見たい場合はオンにしてください"
            "（今は手の届かない場所へ攻め込む予定があるときなど）。",
    },
    scaled=_pairs(SCALED_KEYS, [
        "要塞維持費", "陸軍維持費", "海軍維持費", "陸軍経験", "海軍経験",
        "陸軍伝統", "海軍伝統", "陸軍規模", "海軍規模", "平均統制",
        "平均開発度", "平均識字率", "市場中心地の数", "収入に占める交易の割合",
        "人口に占める市民の割合", "人口に占める農民の割合",
        "人口に占める兵士の割合", "国教聖職者の割合", "主要文化の貴族の割合",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "破産中", "平時", "戦時", "戦争の攻撃側", "戦争の防衛側",
        "要塞上限を超過", "要塞上限の半分未満", "陸軍が想定より大きい",
        "高い正統性", "高い共和制伝統", "自制心の高い統治者",
        "自制心の低い統治者", "首都に議会", "首都外に議会",
        "統治者が将軍", "統治者が提督", "統治者が将軍の特性を持つ",
        "統治者が提督の特性を持つ", "後継者が将軍", "後継者が提督",
        "摂政が将軍", "摂政が提督",
    ]),
)

# --- korean ----------------------------------------------------------------
PHRASES["korean"] = _language(
    hint={
        "ESTATE_PRIVILEGE": "{ref} 부여",
        "GOVERNMENT_REFORM": "{ref} 채택",
        "POLICY": "{ref} 제정",
    },
    catalog="[{concept}|e] {ref}",
    build_in_capital="수도에 건설",
    scales="규모에 따라 변동",
    up_to="최대 ",
    cabinet="내각을 이 가치에 집중",
    cabinet_scales="내각 효율에 따라 변동",
    titles={
        "SVX_ALSO_PUSHES": "이 방향으로도 작용:",
        "SVX_REACHABLE": "다음 조건에서 이용 가능:",
        "SVX_EVERYTHING": "이 방향으로 작용 (필터 없음):",
    },
    menu={
        "svx_name": "사회적 가치 힌트",
        "svx_desc": "사회적 가치 툴팁에 Glorp UI 목록이 읽지 않는 출처를 "
                    "추가하고, 자국이 취할 수 없는 항목을 제거합니다.",
        "svx__main_name": "목록",
        "svx__main__lists_name": "필터링",
        "svx__show_all_name": "전체 표시 (필터 없음)",
        "svx__show_all_desc":
            "목록은 보통 자국이 취할 수 없는 항목을 제외합니다. 가입할 수 없는 "
            "국제 조직, 임무가 꺼진 게임의 임무, 보유하지 않은 계층의 의회 안건 "
            "등입니다. 전체를 한 번에 보려면 켜십시오 — 예컨대 지금은 닿지 않는 "
            "곳까지 밀고 나갈 계획이라면 유용합니다.",
    },
    scaled=_pairs(SCALED_KEYS, [
        "요새 유지비", "육군 유지비", "해군 유지비", "육군 경험", "해군 경험",
        "육군 전통", "해군 전통", "육군 규모", "해군 규모", "평균 통제도",
        "평균 발전도", "평균 문해율", "시장 중심지 수", "수입 중 교역 비중",
        "인구 중 시민 비중", "인구 중 농민 비중", "인구 중 병사 비중",
        "국교 성직자 비중", "주 문화 귀족 비중",
    ]),
    conditional=_pairs(CONDITIONAL_KEYS, [
        "파산 중", "평시", "전시", "전쟁의 공격 측", "전쟁의 방어 측",
        "요새 한도 초과", "요새 한도의 절반 미만", "예상보다 큰 육군",
        "높은 정통성", "높은 공화정 전통", "자제력이 높은 통치자",
        "자제력이 낮은 통치자", "수도에 의회", "수도 밖에 의회",
        "통치자가 장군", "통치자가 제독", "통치자가 장군 특성 보유",
        "통치자가 제독 특성 보유", "후계자가 장군", "후계자가 제독",
        "섭정이 장군", "섭정이 제독",
    ]),
)

# --- Glorp UI keys this mod repairs -----------------------------------------
# Not hints: four keys of Glorp UI's own interface whose Russian is broken
# grammar. Glorp UI marks all four `# LOCK`, so they are not going to be fixed
# by whatever produced them. Only Russian is affected - the other nine
# translations of these keys are grammatical, so nothing overrides them and
# Glorp UI keeps ownership of its own text there.
#
# `Средняя значение` is a feminine adjective on a neuter noun; `Обновить Средняя
# расстояние` is a nominative adjective where an accusative belongs, on a noun
# the rest of the file calls «досягаемость» rather than «расстояние». The two
# `[concept|e]` lines are rewritten to put the concept first, so the game's own
# capitalised term opens the phrase instead of landing mid-sentence.
GLORP_UI_FIXES = {
    "russian": {
        # "Average [max_control|e]"  -  was "Средняя значение [max_control|e]"
        "GLORP_UI_AVG_CONTROL": "[max_control|e] в среднем",
        # "Average [proximity|e]"  -  was "Средняя [proximity|e]"
        "GLORP_UI_AVG_PROXIMITY": "[proximity|e] в среднем",
        # "Swap to Average Control"  -  was "Переключиться на режим «Средняя»".
        # Glorp UI's own sibling key reads "Переключиться на режим
        # «Максимальный контроль»", so this is the shape it wants.
        "SWAP_TO_AVG_CONTROL": "Переключиться на режим «Средний контроль»",
        # "Refresh Average Proximity"  -  was "Обновить Средняя расстояние"
        "REFRESH_AVG_PROX": "Обновить среднюю досягаемость",
    },
}

assert set(GLORP_UI_FIXES) <= set(LANGUAGES), "a fix for a language that is not one"
assert set(PHRASES) == set(LANGUAGES), "a language is in one list and not the other"
