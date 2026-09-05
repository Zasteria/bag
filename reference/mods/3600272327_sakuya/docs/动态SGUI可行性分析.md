# 动态SGUI方案可行性分析

## 📋 调查目标

验证动态SGUI方案的技术可行性，特别是：
1. ✅ 变量能否设置和读取
2. ❓ 变量值能否用于条件判断（如 if/else_if）
3. ❓ 变量值能否作为参数传递给 add_pop
4. ❓ 职业类型能否动态选择

---

## ✅ 已确认可行的功能

### 1. 变量的设置和存储

**文档依据**：`effects.log - set_variable`
```
set_variable = { name = X value = Y days = Z }
Where X is the name of the variable used to then access it
Where Y is any event target, bool, value, script value or flag (flag:W)
This variable will be accessible with <type_>var:X
```

**结论**：✅ **完全可行**
- 可以设置数值变量：`set_variable = { name = sakuya_pop_size value = 0.1 }`
- 可以设置标识变量：`set_variable = { name = sakuya_pop_type value = 1 }`

**现有代码验证**：
```
# 文件：sakuya_cheat_sgui.txt 行15-18
set_variable = {
    name = sakuya_marked
    value = yes
}
```

### 2. 变量的检查

**文档依据**：`triggers.log - has_variable`
```
has_variable = name
Checks whether the current scope has the specified variable set
```

**结论**：✅ **完全可行**

**现有代码验证**：
```
# 文件：sakuya_cheat_sgui.txt 行12
NOT = { has_variable = sakuya_marked }
```

### 3. if/else_if 条件语句

**文档依据**：`effects.log`
```
if = { limit = { <triggers> } <effects> }
else_if = { limit = { <triggers> } <effects> }
```

**结论**：✅ **完全可行**

**现有代码验证**：
```
# 文件：sakuya_cheat_sgui.txt 行3252-3287
if = {
    limit = {
        exists = first_spouse
        first_spouse = { is_alive = yes is_male = yes }
    }
    impregnate = first_spouse
}
else_if = {
    limit = {
        scope:sakuya_force_country = {
            exists = ruler
            ruler = { is_alive = yes is_male = yes }
        }
    }
    impregnate = scope:sakuya_force_country.ruler
}
```

---

## ⚠️ 关键发现：参数硬编码的必然性

### 发现：识字率和人口数量很可能必须硬编码

**核心问题**：
尽管游戏引擎支持变量系统，但**没有证据表明变量值可以作为 effect 参数传递**。

**分析依据**：

1. **文档说明**：
   ```
   set_variable 文档：
   "This variable will be accessible with <type_>var:X"

   add_pop 文档：
   "sets up a pop culture/religion/type/literacy/size possible to set."
   ```
   - ✅ 说明了如何**访问**变量
   - ❌ 但未说明变量值能否用作**参数**

2. **现有代码验证**：
   - 搜索整个 `sakuya_cheat_sgui.txt` (15800行)
   - ❌ **未发现任何使用 `var:` 作为参数的例子**
   - ✅ 所有参数都是硬编码或使用 scope 引用

3. **类似功能的实现方式**：
   ```
   # 现有代码中的文化/宗教传递（可行）
   culture = scope:player_country.culture   # scope引用
   religion = scope:player_country.religion # scope引用

   # 尝试的数值传递（疑问）
   size = scope:player_country.var:sakuya_pop_size      # ❓ 未找到先例
   literacy = scope:player_country.var:sakuya_pop_literacy  # ❓ 未找到先例
   ```

4. **关键区别**：
   - `culture` 和 `religion` 是**对象引用**（scope链）
   - `size` 和 `literacy` 是**数值类型**
   - 变量系统可能不支持数值传递给 effect 参数

### 结论：必须使用硬编码

**高度可能性（90%+）**：
- ❌ `size = var:sakuya_pop_size` **不可行**
- ❌ `literacy = var:sakuya_pop_literacy` **不可行**
- ✅ 必须使用 `size = 0.1` 硬编码
- ✅ 必须使用 `literacy = 0.5` 硬编码

**实际影响**：
```
原计划：
- 8个职业选择 SGUI
- 6个人数选择 SGUI
- 5个识字率选择 SGUI
- 1个执行 SGUI
= 20个 SGUI

实际需求：
- 8个职业选择 SGUI（设置布尔变量）
- 6×5 = 30个"人数+识字率"组合 SGUI（每个包含8个职业分支）
= 8 + 30 = 38个 SGUI
```

### 为什么仍然值得这样做？

尽管需要38个SGUI，但相比240个SGUI（8×6×5）的暴力方案：
- ✅ 减少了 **84%** 的代码量（38 vs 240）
- ✅ 职业逻辑集中管理（只需修改8个SGUI）
- ✅ 数量/识字率组合复用（30个SGUI覆盖所有职业）

---

## ❓ 需要验证的功能（已降低优先级）

### 1. 变量值的数值比较 ⚠️

**问题**：如何检查变量 `sakuya_pop_type` 的值是否等于 1、2、3？

**查找结果**：
- ❌ 未找到 `check_variable` 触发器
- ❌ 未找到类似 `variable_equals` 的触发器
- ✅ 找到 `compare_value`，但仅用于 `value` 类型的scope

**可能的解决方案**：
1. **方案A**：使用多个布尔变量代替数值
   ```
   set_variable = { name = pop_is_laborers value = yes }
   set_variable = { name = pop_is_burghers value = no }
   ...
   ```

2. **方案B**：使用 `switch` 语句（如果支持变量）
   ```
   switch = {
       trigger = var:sakuya_pop_type
       case_1 = { ... }
       case_2 = { ... }
   }
   ```
   ⚠️ **问题**：文档显示 `switch` 需要 `simple_assign_trigger`，不确定是否支持变量

### 2. 变量值作为参数传递 ⚠️

**问题**：`add_pop` 的 `size` 和 `literacy` 参数能否使用变量？

**文档依据**：`effects.log - add_pop`
```
sets up a pop culture/religion/type/literacy/size possible to set.
```

**测试需求**：
```
add_pop = {
    culture = scope:player_country.culture
    religion = scope:player_country.religion
    type = pop_type:laborers
    size = scope:player_country.var:sakuya_pop_size     # ❓ 是否可行？
    literacy = scope:player_country.var:sakuya_pop_literacy  # ❓ 是否可行？
}
```

**风险评估**：
- 文档中 `set_variable` 提到：`This variable will be accessible with <type_>var:X`
- 但未明确说明变量值能否用于 effect 参数
- 需要实际测试验证

### 3. 职业类型的动态选择 ⚠️

**问题**：`type = pop_type:xxx` 中的 `xxx` 能否动态化？

**当前设计**：
```
if = {
    limit = { ... sakuya_pop_type = 1 ... }
    add_pop = { type = pop_type:laborers ... }
}
else_if = {
    limit = { ... sakuya_pop_type = 2 ... }
    add_pop = { type = pop_type:burghers ... }
}
```

**问题点**：
- `pop_type:laborers` 是硬编码的字符串
- 无法做到 `type = pop_type:var:sakuya_pop_type_name`
- **必须使用 if/else_if 分支**

---

## 🔧 替代方案

### 方案1：布尔变量组（最保险） ✅

**设计**：
```
# 职业选择
set_variable = { name = pop_is_laborers value = yes }
set_variable = { name = pop_is_burghers value = no }
...

# 执行
if = {
    limit = { has_variable_value = { name = pop_is_laborers value = yes } }
    add_pop = {
        type = pop_type:laborers
        size = 0.1  # 硬编码
        literacy = 0.5  # 硬编码
    }
}
```

**优点**：
- ✅ 肯定可行（布尔变量检查）
- ✅ 逻辑清晰

**缺点**：
- ❌ 需要 8 个布尔变量（职业）
- ❌ size 和 literacy 仍需硬编码或使用多个SGUI

### 方案2：预定义组合SGUI（当前MOD使用的方案） ✅

**设计**：
```
# 为每个常用组合创建一个SGUI
sakuya_add_pop_laborers_100_literacy_10 = { ... }
sakuya_add_pop_laborers_1000_literacy_30 = { ... }
sakuya_add_pop_burghers_100_literacy_50 = { ... }
...
```

**优点**：
- ✅ 100% 可行
- ✅ 不需要变量判断

**缺点**：
- ❌ 需要大量SGUI（8×6×5 = 240个）
- ❌ 难以维护

### 方案3：分层SGUI（折衷方案） ⚠️

**设计**：
```
# 第一层：选择职业（设置变量）
sakuya_select_laborers → set variable

# 第二层：选择数量+识字率的组合
sakuya_add_100_literacy_10 = {
    effect = {
        if = { limit = { pop_is_laborers } add_pop { type = pop_type:laborers size = 0.1 literacy = 0.1 } }
        else_if = { limit = { pop_is_burghers } add_pop { type = pop_type:burghers size = 0.1 literacy = 0.1 } }
        ...
    }
}
```

**SGUI数量**：8（职业） + 30（数量×识字率组合） = **38个SGUI**

**前提条件**：
- ✅ 布尔变量检查可行
- ❌ 变量值作为 size/literacy 参数**不可行**

---

## 🎯 最终建议（基于硬编码限制）

基于现有文档和代码验证，以及**识字率/数量必须硬编码**的发现：

### ⭐ **唯一可行方案：分层SGUI + 布尔变量（38个SGUI）** ⭐

```
架构：
第一层 - 职业选择（8个SGUI）：
├─ sakuya_pop_select_laborers   → 设置 pop_is_laborers = yes
├─ sakuya_pop_select_burghers   → 设置 pop_is_burghers = yes
├─ sakuya_pop_select_nobles     → 设置 pop_is_nobles = yes
├─ sakuya_pop_select_clerics    → 设置 pop_is_clerics = yes
├─ sakuya_pop_select_soldiers   → 设置 pop_is_soldiers = yes
├─ sakuya_pop_select_peasants   → 设置 pop_is_peasants = yes
├─ sakuya_pop_select_tribesmen  → 设置 pop_is_tribesmen = yes
└─ sakuya_pop_select_slaves     → 设置 pop_is_slaves = yes

第二层 - 人数+识字率组合（30个SGUI）：
├─ sakuya_add_10_literacy_0     (10人, 0%识字)
├─ sakuya_add_10_literacy_25    (10人, 25%识字)
├─ sakuya_add_10_literacy_50    (10人, 50%识字)
├─ sakuya_add_10_literacy_75    (10人, 75%识字)
├─ sakuya_add_10_literacy_100   (10人, 100%识字)
├─ sakuya_add_100_literacy_0    (100人, 0%识字)
├─ sakuya_add_100_literacy_25   (100人, 25%识字)
├─ ... (共6个数量级别 × 5个识字率 = 30个组合)

总计：8 + 30 = 38个SGUI
```

**每个"人数+识字率"SGUI的内部结构**：
```
sakuya_add_100_literacy_10 = {
    scope = country
    effect = {
        every_owned_location = {
            limit = { has_variable = sakuya_marked }

            if = {
                limit = { scope:player_country = { has_variable = pop_is_laborers } }
                add_pop = {
                    culture = scope:player_country.culture
                    religion = scope:player_country.religion
                    type = pop_type:laborers
                    size = 0.1        # 硬编码
                    literacy = 0.1    # 硬编码
                }
            }
            else_if = {
                limit = { scope:player_country = { has_variable = pop_is_burghers } }
                add_pop = { type = pop_type:burghers size = 0.1 literacy = 0.1 ... }
            }
            # ... 其他6个职业的分支
        }
    }
}
```

**实现示例**：

```
# 职业选择
sakuya_pop_select_laborers = {
    scope = country
    effect = {
        # 清除所有职业标记
        remove_variable = pop_is_laborers
        remove_variable = pop_is_burghers
        ...
        # 设置当前选择
        set_variable = { name = pop_is_laborers value = yes }
    }
}

# 数量+识字率组合
sakuya_add_100_literacy_10 = {
    scope = country
    effect = {
        every_owned_location = {
            limit = { has_variable = sakuya_marked }

            if = {
                limit = { scope:player_country = { has_variable = pop_is_laborers } }
                add_pop = { culture = ... type = pop_type:laborers size = 0.1 literacy = 0.1 }
            }
            else_if = {
                limit = { scope:player_country = { has_variable = pop_is_burghers } }
                add_pop = { culture = ... type = pop_type:burghers size = 0.1 literacy = 0.1 }
            }
            # ... 其他6个职业
        }
    }
}
```

---

## ⚠️ 待实际测试验证的问题

1. **变量值是否能作为 add_pop 的参数**
   - 测试代码：`size = scope:player_country.var:sakuya_pop_size`
   - 如果可行：可以减少到 20个SGUI（理想方案）
   - 如果不可行：使用 38个SGUI（折衷方案）

2. **switch 语句是否支持变量**
   - 测试代码：`switch = { trigger = var:sakuya_pop_type ... }`
   - 如果可行：可以简化if/else_if链

3. **has_variable_value 触发器是否存在**
   - 查找：未在文档中找到
   - 替代：使用 `has_variable = name` 检查布尔值

---

## 📝 建议的实施步骤

1. **先实现最小原型**（1个职业，2个数量级别）
   ```
   - 1个职业选择SGUI
   - 2个数量SGUI
   ```

2. **测试关键功能**
   - 变量设置和检查
   - if/else_if 分支
   - add_pop 参数传递

3. **根据测试结果选择最终方案**
   - 如果变量作参数可行 → 使用20个SGUI的理想方案
   - 如果不可行 → 使用38个SGUI的折衷方案

---

## 📊 方案对比总结

| 方案 | SGUI数量 | 代码行数估算 | 可维护性 | 可行性 | 推荐度 |
|------|---------|-------------|---------|--------|--------|
| **暴力方案** | 240个 | ~7200行 | 极差 | ✅ 可行 | ❌ |
| **理想动态方案** | 20个 | ~600行 | 优秀 | ❌ 不可行（变量作参数） | ❌ |
| **折衷方案（推荐）** | **38个** | **~1500行** | **良好** | **✅ 可行** | **⭐⭐⭐** |

### 折衷方案的优势

1. **代码量减少 79%**
   - 暴力方案：240个SGUI
   - 折衷方案：38个SGUI
   - 节省：202个SGUI

2. **逻辑分离清晰**
   ```
   职业逻辑 → 8个SGUI（独立维护）
   数量/识字率 → 30个SGUI（统一格式）
   ```

3. **易于扩展**
   - 新增职业：+1个SGUI（职业选择）+ 修改30个SGUI（添加分支）
   - 新增数量级别：+5个SGUI（新的数量×5个识字率）
   - 新增识字率：+6个SGUI（6个数量×新的识字率）

4. **代码复用**
   - 30个"数量+识字率"SGUI 覆盖所有8种职业
   - 每个SGUI只需修改 size 和 literacy 两个参数

### 代码结构示意

```
sakuya_cheat_sgui.txt
├── [职业选择区块] 约 160行 (8个SGUI × 20行)
│   ├── sakuya_pop_select_laborers
│   ├── sakuya_pop_select_burghers
│   └── ...
│
└── [人数+识字率区块] 约 1350行 (30个SGUI × 45行)
    ├── sakuya_add_10_literacy_0
    │   └── 包含8个if分支
    ├── sakuya_add_10_literacy_25
    │   └── 包含8个if分支
    └── ...

总计：约 1500行
```

---

## 🔬 需要实际测试的内容（可选）

虽然基于分析已经确定了方案，但以下内容仍可通过实际测试验证：

1. **变量值是否能作为参数**（低概率）
   ```
   size = scope:player_country.var:sakuya_pop_size
   ```
   - 如果奇迹般可行 → 可减少到20个SGUI
   - 如果不可行（预期）→ 使用38个SGUI方案

2. **switch语句是否支持变量**（可能性未知）
   ```
   switch = {
       trigger = var:sakuya_pop_type
       case_laborers = { ... }
       case_burghers = { ... }
   }
   ```
   - 如果可行 → 可简化if/else_if链
   - 如果不可行 → 使用if/else_if

3. **布尔变量互斥性验证**
   - 确认设置一个变量时清除其他变量的逻辑正确性

---

**创建日期**：2025-11-30
**最后更新**：2025-11-30
**状态**：分析完成 - 推荐使用38个SGUI的折衷方案
