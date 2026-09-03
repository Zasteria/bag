# `where_to_produce` — the runs the plan was built on

Split out of [`../TESTLOG.md`](../TESTLOG.md) on 2026-09-03, at its budget. These
are superseded: what they say about the **game** stands, what they say about our
code was rewritten by the runs that followed. `tools/kb.py` still searches them.

**2026-09-03 — `where_to_produce`, два нажатия по чек-листу: три починки
подтверждены, одна оказалась регрессией, а ярусы редкости держит не лестница, а
квота.** Вестфалия / Мюнстер, 48 локаций все городами, 192 места из 192, 8
провинций. Нажатие 1 — «сейчас», нажатие 2 — «на конец».

- **Подтверждено:** `ordered_provs=8` вместо вечного нуля; каждая строка `WTP L`
  названа **одним** именем; `RQ legend` на месте, перед блоком локаций;
  `grantable=` различает «не досталось» и «не для этой державы» — на «в конце» 9
  единиц и 4 нуля, ровно те четыре (Византия, текстильные, две скандинавских).
- **Цена лестницы приемлема.** Кругов 73 («сейчас») и 61 («на конец») против 57;
  ни один проход не упёрся в лимит.
- **Полосатая открытая лестница работает.** На «сейчас» `P36 open800` поставил
  11 зданий и `P37 open600` ещё 2 — тринадцать мест, которые прошлая сборка
  раздавала одним проходом на полосе 0, то есть по порядку списка.
- **Регрессия, и она моя.** Возрастной гейт грамот на «сейчас» оставил Мюнстеру
  **одну** грамоту из тринадцати: у него есть `flemish_cloth_making` и нет
  `town_rights_enable`. Правило «каждый город обязательно получит право» отдало
  эту одну грамоту **всем 48 городам**: сукно встало в 48 локациях из 192, а
  товаров план поставил 30 вместо 35. **Откачено** — план снова считает по
  `potential`, как и список в окне, а открытие печатается в отчёте отдельным
  полем `unlocked=`.
- **Ярусы редкости снова поставили 3 здания из 69 — и порядок проходов тут ни
  при чём.** `P26..P30` (полоса 0, ярусы) при 66 свободных местах поставили
  **ноль**. Держит квота: у семи сырьевых товаров она равна 1, потому что
  область уже добывает это сырьё сама, и ковровая лестница этот единственный
  домик уже израсходовала. `clay` 2 РГО, `coal` 3, `fiber_crops` 3, `iron` 2,
  `salt` 3, `sand` 2, `stone` 3 — при базовой квоте 2.4. **Это правило
  владельца, работающее ровно как он его сформулировал** («там уже есть 2 рго
  глины — тебе нужно всего 3 домика»), а не поломка. Вопрос B закрыт окончательно
  и в третий раз переоткрывать его не надо.
- **План «на конец» вышел числом в число такой же, как у прошлой сборки**:
  192 здания, `fed=143`, `gain_total=112304`, те же строки проходов. То есть
  перестановка лестниц на этой земле не изменила ничего — её проверять надо на
  большой области, где открытый проход раньше ставил 271 здание из 770.
- **Модель квоты сверена на всех товарах обоих отчётов и сходится точно:**
  `q = max(1, PASS quota + что поставили грамоты этому товару − rgo) +
  число кругов открытой лестницы`. Последнее слагаемое теперь печатается как
  `open_sweeps`, а `diag.py` вычитает его сам и называет товары, которых мало
  из-за собственного РГО.

**2026-09-03 — `where_to_produce`, три нажатия после переноса ковровой лестницы
вперёд: гарантия держится, ярусы редкости — нет.** Вестфалия / Мюнстер, 48
локаций, 8 провинций. Нажатия 1 и 2 — все локации городами (192 места из 192),
«на конец» и «сейчас»; нажатие 3 — тумблеры сброшены, 6 настоящих городов, 150
мест. **Это первый прогон «В конце»**, который до сих пор стоял в «никогда не
запускалось».

- **Ковровая лестница работает.** `P1..P5 cover800..cover0` поставили 116 → 123,
  и ни один товар не кончил план с нулём: `stone` получил здание там, где в
  прошлый раз не получил ни одного, оружейная и ювелирная грамоты — по городу
  каждая, а не ноль. Гарантия «все товары производятся» выполняется.
- **Ярусы редкости по-прежнему не работают, и теперь измерено, насколько.** Из
  69 зданий, поставленных полосами, ярусные проходы дали **3**; всё остальное —
  пять проходов `tierall`. Причина названа в `plan_gaps.md` (B) и подтверждается
  строкой `o`: у 16 товаров из 35 лучший выигрыш на всей земле ниже 800, то есть
  в верхнюю полосу они не входят нигде — `tools 799`, `stone 372`, `weaponry 187`,
  `cannons 136`, а `iron`, `salt`, `incense`, `jewelry` и `fine_cloth` — ровно 0.
  Так что редкий товар не может обогнать обычный внутри полосы: полосы для него
  нет. **Исправлено в этой сессии** — ярусы стали отдельной фазой до общих
  товаров; в игре не проверено.
- **Открытый проход на этой земле не понадобился** (`P36 open` 192 → 192): её
  добили квоты. На большой области прошлого прогона он ставил 271 здание из 770,
  и там это треть плана без участия выгоды. **Тоже исправлено, тоже не
  проверено.**
- **Грамоты съедают 108 мест из 192** — 48 городов, у каждого связка из 1–3
  зданий. Это ровно то, о чём он просил («каждый такой город обязательно получит
  все здания из его бонуса»), и это же объясняет, почему квота вышла 2.4: делится
  то, что осталось.
- **Четыре грамоты из тринадцати кончили с `given=0`, и отчёт не мог сказать,
  почему.** Три из них Мюнстеру недоступны по происхождению (Византия,
  Скандинавия ×2), а `royal_textile` уступает фламандской: **вестфальские
  культуры входят в `netherlandish_group`** — прочитано в
  `cultures/german.txt`, не вспомнено. Строка `RIGHT` печатает теперь
  `grantable=`.
- **`fed=143 из 192` (74%), средний выигрыш 58.5% от потолка рецепта.** На
  нажатии 3, где земля вдвое просторнее на здание, — 72% и 65.5%: меньше зданий
  кормится, но те, что кормятся, стоят лучше.
- **Найдено в самом отчёте, не в игре:** `ranked_provs` печатал счётчик
  одиночного ранжирования и стоял в нуле на всех трёх нажатиях; локация в блоке
  называлась дважды, и `diag.py` подписывал каждую строку начиная со второй
  двумя именами; строка `RQ legend` терялась целиком. Всё три исправлены.

**2026-09-03 — not a run: the owner asked where a copper tools recipe came from,
and three faults came out of the answer.** «У моей нации был только 1 рецепт, тот
что с оловом… этого метода не должно было быть как кандидата в принципе.»

- **He is right about the recipe, and right about the numbers.** `copper_tools_guild_maintenance`
  is unlocked by `copperworking`, whose `potential` is `is_capital_mesoamerica`.
  What the plan actually chose in Goslar was `bronze_tools_guild_maintenance` —
  copper **and tin**, tin missing, 9.26% of 10 → **926**, which is the 925 in the
  report. My «copper feeds it whole» was wrong; his reading was right.
- **Fault one: a paired method escapes its advance.** A pair's key is
  `base+improvement` and `copperworking` says `unlock_production_method =
  copper_base`, so the lookup missed all four `copper_base+*` jewelry recipes.
  Münster was being offered a Mesoamerican recipe **in the «сейчас» plan**.
- **Fault two: «на конец» assumed every advance is eventually in.** 45 of the 181
  advances that unlock a building or a method are locked to a tag, a culture
  group or a region, and 13 of the mod's 241 methods sit behind one. That is how
  **five porcelain guilds landed in northern Germany** — the kiln wants an
  east-Asian capital. `_reach_<n>` asks the advance's own `potential` now.
- **Fault three, mine, from 2026-09-02.** `hand_cannon_guild` went into
  `ALWAYS_AVAILABLE` as «the first firearms building»; its advance wants an
  east-Asian capital, so that handed a Chinese building to everyone. It is
  `gun_smith` — age 2, no `potential` — and **his original «огнестрел во второй
  эпохе» was right all along.**
- **And the enhancement question, closed by him.** Base is 9.09 of the 10 points
  and the trim is 0.91, so the coincidence he wanted to chase is worth under one
  per cent: «нет смысла рвать задницу ради ~1%». The 10% split is the game's own
  arithmetic and the mod keeps matching it.

**2026-09-03 — `where_to_produce`, пять нажатий, и в них видно, что ковровый
проход не ставил ничего.** Вестфалия / Мюнстер, 48 локаций все городами, «на
конец» (нажатия 1, 3, 5), «сейчас» (2), и одно нажатие по большой области — 233
локации, 41 провинция, квота 16 (4). Разбор целиком в
[`investigations/plan_gaps.md`](investigations/plan_gaps.md).

- **`P31 cover` поставил 0 и `P32 open` поставил 0**, потому что `P30
  band0/tierall` уже добил землю до 192 из 192. Гарантия «все товары
  производятся» не выполнялась: `stone` кончил план с `ng=6 w=6 n=0` — ноль
  зданий там, где шесть локаций его могут сделать.
- **Ни одной печки болотного железа.** `iron ng=4 o=0 q=2 n=1`: выигрыш ноль
  везде (у добывающего здания нет входов-товаров), поэтому железо входит только
  на полосе 0, а к ней его четыре локации заняты.
- **Оружейная грамота одна на всю область и в пустом месте.** В шести городах
  Зауэрлэнда корабельная платит **1000**, оружейная **163**; корабельная взяла
  все шесть в полосе 800, и ковровая лестница грамот, идущая после полос, отдала
  оружейную Эльсфлету, где та стоит **0**. Ювелирная — то же самое, 1 штука.
- **Ярусы редкости не работают:** все ярусные проходы вместе поставили **5
  зданий из 84**, остальные 79 сделали пять проходов `tierall`. Полоса стоит
  снаружи яруса, у редких товаров выигрыш низкий, и до полосы 0 они не ходят.
- **Оценка выданных прав, измеренная:** Зауэрлэнд — корабельная 1000, смоляная
  1000, книжная 896, инструментальная 799, фламандская 454, оружейная 163,
  ювелирная 0. Грамот доступно 9, городов 48, `_rquota = 48 ÷ 9 = 5.33` → по 6
  на грамоту; фламандская взяла 10 (6 + 4 в открытом проходе).
- **Квота грамот теперь честная**, фикс двойного счёта виден: `cloth q=13 n=13`,
  `dyes q=9 n=9` — квота 2 плюс то, что дали грамоты.
- **`diag.py` всё это время отдавал сырой лог.** `render_rq` печатает строку без
  метки `WTP`, предохранитель считал её потерей и срабатывал на каждом отчёте, а
  «коротко» складывалось по всем пяти нажатиям сразу («выдано 263»). Исправлено
  и проверено на этом же файле.
- **Сделано по итогам, ни одно не проверено в игре:** ковровая лестница у товаров
  и у грамот перенесена в начало, до полос.


**2026-09-03 — `where_to_produce`, the covering ladder placed the weaponry charter
and could not place jewelry, and the quota collapsed to 2.** Westphalia, all 48
locations ticked to towns, «на конец».

- **Weaponry went from 0 to 1**, so the covering ladder works. **Jewelry stayed at
  0**, and the cause is one comparison: the winner is taken with `rtry > rbest`
  and `rbest` started at **0**, so a charter the ground pays exactly nothing for
  could never win even when it was the only one left. Westphalia has no precious
  metal, jewelry scored 0 in all 48 towns. `rbest` starts at -1 now.
- **Flemish took 11 against everyone else's 6, and it is not double counted.**
  `fine_cloth` scores 0 on this ground, cloth 908, so flemish is `(908+0)/2 = 454`
  and royal textile `(908+0+0)/3 = 303`. The same cloth, divided by a smaller
  bundle. That is «все права равны», working as he asked for it.
- **The bonus is counted once a province, not once a location.** He asked
  directly; `_b<n>` reads `any_location_in_province_definition`, which is a
  boolean. Five coal locations pay exactly what one pays.
- **The weaponry charter landed in Dortmund at 62 and not in Sauerland at 163**
  because by the covering ladder's last band the Sauerland towns were already
  full — they had taken the naval charter, which scores 1000 there.
- **And the quota fell to 2 — but the fault was not the quota, it was double
  counting.** 48 towns all took a charter and the charters ate 109 of the 192
  rooms, so `(rooms − rights) ÷ 35 goods` came out at **2**. That subtraction is
  correct and every good pays it once. What was wrong is that `_pn<n>` — the
  good's own counter, which the allocator reads against that cap — **was never
  cleared of what the charters had put down**, so the same 109 buildings were
  charged a second time, good by good. `tools` entered the allocator at `_pn = 6`
  (all six from the six tooling charters, which landed in the Ruhr at 200 because
  Sauerland's towns had taken the naval charter at 1000) against a cap of 2, and
  could not take a single free room in Sauerland at **799**. It finished the plan
  with the charters' six and none of its own. **Fixed:** `_plan_set_quota` adds
  `_pn<n>` back into `_pq<n>`, so the cap is the good's share of the *free* rooms
  on top of what its charters already built. Not run.


**2026-09-03 — `where_to_produce`, the probe came back thirteen zeroes, and the
level rights work.** Goslar took tooling on «сейчас» and books on «на конец»,
again. «Понятия не имею где конкретно искать строку Гослара.»

- **`WTP RQ` printed `1=0 2=0 … 13=0` on every town, and that is the probe's own
  fault.** `_rqf<k>` asked `_plan_can_town_<n>`, which is a **placement** gate: it
  also asks whether the town still has room and whether the good is already
  standing there. At grant time the town is empty and the gate reduces to «a town
  method for this good won here»; the dump runs after the plan, when every town
  is full, so every clause was false. The twin asks `var:_pm<n> > 0` now — the
  scoring fact, which survives the plan.
- **And the line is rendered rather than printed raw.** `1=0 2=0 3=0` is material
  for an answer, not an answer: `tools/diag.py` now folds it into «права:
  ювелирные 2909 | книгопечатные 2856 ← выдано | …», names from the report's own
  legend, sorted, with the granted one marked.
- **The level rights work and his culture reading was right.** Münster is
  Westphalian, which is in the Netherlandish group, so `flemish_cloth_industries_right`
  is offered — and it took **9 grants against `royal_textile_rights`' 1**. His
  «two towns of one province, one textile one flemish» is the province divisor
  spreading them, which is what it is for. **But the 9:1 is not the level
  arithmetic**: the mod scores both purely on which goods they favour, so flemish
  (cloth, fine cloth) beats textile (cloth, dyes, fine cloth) only because dyes
  drags the average down. Nothing in the code knows five levels beat +20%.
- **Numbers for the next press to be read against**: `jewelry T o=909`,
  `paper 1000`, `dyes 952`, `books 615`, `tools 399`. If Harz has silver, jewelry
  in Goslar should read near 2900 and the RQ line will say whether it did.
- **His design point, and it is a real gap.** «Мод должен проверить есть ли 5
  городов в провинциях с драг металлами, прежде чем забивать эти города какими-то
  другими правами.» Rights are assigned town by town in walk order, each taking
  its best; nothing lets a right only two towns on the map can serve claim those
  two first. The goods have that machinery — `PLAN_TIERS` — and **it was weakened
  on 2026-09-02 to pay for the round guard**: the ladder now runs in the last band
  only, so in bands 800–200 a common good takes a scarce one's ground with no
  contest. Both are open.

**2026-09-02 — not a run: `where_to_produce` was rolled back to the build of the
thirty-eighth load**, and the owner stopped the line. He picked that build by its
own message — the four tests, «большой рывок» — «именно в этом коммите я
почувствовал, что мод выглядит так, как я его задумывал… именно в этом коммите я
хочу начать постройку диагностического инструмента». **The two runs directly
below tested builds that no longer exist**, and so does the funnel probe branch
`claude/glass-sand-cycle-diagnosis-0qhgzw`, which was never merged. What they
measured about the *game* stands — the identical `location_potential` of
`glass_guild` and `rural_glassmaker` above all; what they say about our code no
longer describes the tree. What the thirty-eighth load left open came back with
it, deliberately, and is listed in `investigations/plan_formula.md`, last section.

**2026-09-03 — `where_to_produce`, the locked advances held, and the rights turned
out to have no covering rule.** Westphalia, all 48 locations ticked to towns.

- **The locked-advance gate works, and the two survivors are correct.** Porcelain
  and lacquerware are gone from «сейчас» and stay in «на конец» — he checked and
  both unlock in age 5 for Münster, so that is right, not a leak. Goslar keeps
  tooling on «сейчас» and takes jewelry on «на конец», as predicted.
- **No town got the weaponry charter, on either plan**, and none got jewelry.
  «Какое-то количество оружейных прав должно было выделиться каким-то городам
  обязательно.»
- **The score is right and the rule is missing.** Over those 48 towns the bundle
  reads cannons 136, firearms 166, weaponry 187 — averaged over three, the
  charter is **163** everywhere, against 200–624 for every rival. Westphalia has
  almost no iron (2 buildings of it), so all three are poor; the charter loses
  fairly and **nothing then forces it in**. The goods have had that rule since
  2026-09-01; the rights never did.
- **A covering ladder for the rights**, the goods' `cover` pass in the same
  shape: after the banded passes, the bands run again admitting only charters
  with nothing anywhere, so each takes the town its ground suits best rather than
  whichever town the walk reaches first. Then the open pass as before. Not run.

## `NEXT_SESSION`'s `where_to_produce` section, as it stood 2026-09-02

Superseded by [`../investigations/plan_gaps.md`](../investigations/plan_gaps.md);
its numbers describe builds that no longer exist.

## `where_to_produce`: it works, and what is left is his to choose

**The plan does what it was meant to, and he has seen it** — «на первый взгляд
работает как надо, города получают права и домики из прав», 2026-09-02. The
symptom that cost four runs is measured, named and fixed: the tick is the rank
now (`SETTLED.md`), the charter spam is gone, and **four fifths of placed
buildings earn a bonus where they stand, capturing 78% of their own recipe's
ceiling on average**. All of it is on `main`.

**Read `TESTLOG.md` before anything.** Four runs of 2026-09-02 are in it and they
carry every number this section summarises.

**Three things he named on 2026-09-02 are built and none has been in the game.
One big ground tests all three at once**, and northern Germany — 416 locations,
1312 rooms — is the one that failed before:

- **The round guard is 50 and the pass count is twelve.** 127 locations already
  put the open pass at 11 of 12, and 970 buildings over 32 goods cannot be done
  in fewer than thirty sweeps. What to read on the run: `WTP P<n> sweeps=x/50` in
  the report — a pass at 50 is still being cut off — and whether the rooms come
  out full. **What to watch against it is the hitch** he reported without
  complaint on that ground: twelve passes are fewer than thirty-three, but each
  may now run four times as long.
- **The plan window pages.** `PLAN_ROWS` is still 150 because the datamodel is
  what costs; `PLAN_RANKED` (1500) is how many rows the pass keeps, and «Назад» /
  «Вперёд» under the summary walk them. The summary says «в строках N» beside the location
  count, so the two numbers can be told apart at a glance. If the ground is bigger
  than 1500 used locations the bar says so by the two disagreeing.
- **The province ceiling is gone** — setting, alias, default, both localizations
  and its gate in the allocator.

**What is open, and none of it is a bug:**

- **Nine goods take 45% of the ground.** Coal, sand, beer, cloth, glass, jewelry,
  leather, masonry, pottery — makeable in every location, so each reaches the
  quota and stops at 20. Sixteen town-only goods got 7 or fewer, competing for
  22 towns × 4 slots that the rights have first call on. **The formula working as
  written.** The lever he had for it was `plan_max`, and it went with the province
  ceiling at his word; if he wants one back it should be derived, not typed.
- **The single-good side** has faults he has seen and set aside without naming.

**The diagnosis comes out when the work does.** It is `bag_wtp_diag*`, the `_f*`
counters, the two `_pass*` counters and two buttons; `pitfalls/diagnosis.md` has
what it prints and how to read it, and `tools/diag.py` draws the conclusions so
he does not have to.
