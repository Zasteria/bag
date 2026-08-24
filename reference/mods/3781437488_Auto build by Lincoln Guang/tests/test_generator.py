from pathlib import Path
import json
import re
import tomllib
import unittest

from src.eu5autobuild.generator import (
    ENGLISH_FALLBACK_LANGUAGES,
    PRESET_TEMPLATE_IDS,
    TEMPLATE_NAME_CHOICES,
    _balanced_script,
    _slot_display_name_expr,
    generated_files,
)
from src.eu5autobuild.policy import load_building_catalog, load_policies
from tests._game_data_fixtures import cached_game_data


ROOT = Path(__file__).resolve().parents[1]


def _blocks_for_token(text: str, token: str) -> list[str]:
    blocks: list[str] = []
    offset = 0
    while True:
        start = text.find(token, offset)
        if start < 0:
            return blocks
        brace = text.find("{", start + len(token))
        if brace < 0:
            raise AssertionError(f"{token!r} is missing an opening brace")
        depth = 0
        in_quote = False
        escaped = False
        for index in range(brace, len(text)):
            char = text[index]
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"':
                in_quote = not in_quote
                continue
            if in_quote:
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start:index + 1])
                    offset = index + 1
                    break
        else:
            raise AssertionError(f"{token!r} has an unbalanced block")


def _function_argument_counts(text: str, function: str) -> list[int]:
    token = f"{function}("
    counts: list[int] = []
    offset = 0
    while True:
        start = text.find(token, offset)
        if start < 0:
            return counts
        depth = 1
        commas = 0
        quote: str | None = None
        escaped = False
        index = start + len(token)
        while index < len(text):
            char = text[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif quote is not None:
                if char == quote:
                    quote = None
            elif char in {"'", '"'}:
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    counts.append(commas + 1)
                    break
            elif char == "," and depth == 1:
                commas += 1
            index += 1
        else:
            raise AssertionError(f"{function!r} has an unbalanced call")
        # Resume just after this call's opening token so nested calls are counted too.
        offset = start + len(token)


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policies = load_policies(ROOT / "policies" / "templates.json")
        cls.catalog = load_building_catalog(ROOT / "policies" / "building_catalog.json")
        cls.building_count = len(cls.catalog.buildings)
        recipes, construction_demands, upgrades, workforce = cached_game_data()
        cls.files = generated_files(
            cls.policies,
            catalog=cls.catalog,
            recipes=recipes,
            construction_demands=construction_demands,
            upgrades=upgrades,
            workforce=workforce,
        )

    def test_builtin_presets_are_maintained_separately_from_custom_names(self):
        self.assertEqual(
            PRESET_TEMPLATE_IDS,
            tuple(policy.id for policy in self.policies),
        )
        custom_name_ids = {name_id for _, name_id in TEMPLATE_NAME_CHOICES}
        self.assertTrue(set(PRESET_TEMPLATE_IDS).isdisjoint(custom_name_ids))

        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        for _, name_id in TEMPLATE_NAME_CHOICES:
            rename_action = _blocks_for_token(
                scripted_guis,
                f"eu5ab_gui_slot_1_name_{name_id} = ",
            )[0]
            self.assertNotIn("priority_building_", rename_action)

        effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        slot_defaults = _blocks_for_token(
            effects,
            "eu5ab_template_slot_1_ensure_defaults = ",
        )[0]
        self.assertNotIn("key = building_type:city_walls", slot_defaults)
        self.assertIn(
            "name = eu5ab_tpl_1_building_priorities key = building_type:granary value = 10",
            slot_defaults,
        )
        self.assertIn("eu5ab_tpl_1_building_priorities_initialized", slot_defaults)

    def test_expected_files_are_generated(self):
        expected = {
            ".metadata/metadata.json",
            ".metadata/eu5ab_building_upgrades.json",
            ".metadata/eu5ab_construction_demands.json",
            ".metadata/eu5ab_production_recipes.json",
            ".metadata/eu5ab_workforce_model.json",
            "in_game/common/generic_actions/eu5ab_development_policy_actions.txt",
            "in_game/common/on_action/eu5ab_on_actions.txt",
            "in_game/events/eu5ab_monthly_events.txt",
            "in_game/gfx/map/map_modes/eu5ab_template_coverage.txt",
            "in_game/common/scripted_effects/eu5ab_scripted_effects.txt",
            "in_game/common/scripted_guis/eu5ab_scripted_guis.txt",
            "in_game/common/scripted_triggers/eu5ab_scripted_triggers.txt",
            "in_game/common/script_values/eu5ab_script_values.txt",
            "in_game/gui/eu5ab_automation_buildings_window.gui",
            "in_game/gui/eu5ab_engine_queue_window.gui",
            "in_game/gui/eu5ab_template_buildings_window.gui",
            "in_game/gui/eu5ab_template_editor_window.gui",
            "in_game/gui/eu5ab_template_rename_window.gui",
            "in_game/gui/eu5ab_template_rules_window.gui",
            "in_game/gui/eu5ab_template_scope_window.gui",
            "in_game/gui/scripted_widgets/eu5ab_scripted_windows.txt",
            "in_game/localization/simp_chinese/eu5ab_l_simp_chinese.yml",
            "main_menu/localization/simp_chinese/eu5ab_l_simp_chinese.yml",
            "in_game/localization/english/eu5ab_l_english.yml",
            "main_menu/localization/english/eu5ab_l_english.yml",
        }
        expected.update(
            f"{game_layer}/localization/{language}/eu5ab_l_{language}.yml"
            for game_layer in ("in_game", "main_menu")
            for language in ENGLISH_FALLBACK_LANGUAGES
        )
        actual = {path.relative_to(ROOT).as_posix() for path in self.files}
        self.assertEqual(actual, expected)

    def test_metadata_declares_cmf_hard_dependency(self):
        payload = json.loads(self.files[ROOT / ".metadata" / "metadata.json"])
        self.assertEqual(payload["name"], "EU5 Advanced Auto Build")
        self.assertEqual(payload["version"], "0.9.2 Beta")
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual(project["version"], "0.9.2b0")
        self.assertEqual(project["requires-python"], ">=3.12")
        self.assertEqual(project["dependencies"], [])
        self.assertEqual(
            payload["short_description"],
            "使用可调整的建造顺序、收益要求和紧急规则，自动发展已应用模板的地点。需要社区模组框架。",
        )
        self.assertEqual(payload["picture"], "thumbnail.png")
        thumbnail = ROOT / ".metadata" / payload["picture"]
        self.assertTrue(thumbnail.is_file())
        self.assertEqual(thumbnail.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        dependency = next(
            relationship
            for relationship in payload["relationships"]
            if relationship["id"] == "community_mod_framework"
        )
        self.assertEqual(dependency["rel_type"], "dependency")
        self.assertEqual(dependency["display_name"], "Community Mod Framework")
        self.assertEqual(dependency["resource_type"], "mod")
        self.assertEqual(dependency["version"], "2.*")
        self.assertIn("需要社区模组框架", payload["short_description"])

    def test_workforce_metadata_records_vanilla_data_and_no_fake_monthly_rate(self):
        payload = json.loads(
            self.files[ROOT / ".metadata" / "eu5ab_workforce_model.json"]
        )
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["source"]["employment_size_unit_people"], 1000)
        self.assertEqual(payload["source"]["rgo_jobs_per_level"], 1000)
        self.assertEqual(payload["source"]["rgo_primary_pop_type"], "laborers")
        self.assertEqual(payload["source"]["rgo_optional_pop_type"], "slaves")
        self.assertEqual(
            payload["source"]["rgo_optional_pop_type_country_modifier"],
            "allow_rgo_slave_demand",
        )
        self.assertFalse(payload["source"]["monthly_script_value_available"])
        self.assertEqual(payload["source"]["fallback"], "current_available_population")
        buildings = {row["building_id"]: row for row in payload["buildings"]}
        self.assertEqual(buildings["tools_workshop"]["jobs_per_level"], 100)
        self.assertEqual(buildings["tools_workshop"]["pop_types"], ["burghers"])
        paths = {row["source_pop_type"]: row for row in payload["promotion_paths"]}
        self.assertIn("burghers", paths["peasants"]["targets"])

    def test_shared_runtime_settings_live_in_cmm_and_templates_keep_priorities(self):
        effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        on_actions = self.files[
            ROOT / "in_game" / "common" / "on_action" / "eu5ab_on_actions.txt"
        ]
        rules_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"
        ]
        localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]

        defaults = _blocks_for_token(
            effects, "eu5ab_template_slot_1_ensure_defaults = "
        )[0]
        load = _blocks_for_token(
            effects, "eu5ab_load_template_slot_1_into_editor = "
        )[0]
        commit = _blocks_for_token(
            effects, "eu5ab_commit_template_editor_to_slot_1 = "
        )[0]
        for suffix in (
            "job_fill_deadline_months",
            "native_input_priority",
            "min_cash_reserve",
            "price_min",
            "annual_budget",
            "allow_special_buildings",
            "auto_build_input_sources",
        ):
            self.assertIn(f"remove_variable = eu5ab_tpl_1_{suffix}", defaults)
            self.assertNotIn(f"eu5ab_edit_{suffix}", load)
            self.assertNotIn(f"eu5ab_edit_{suffix}", commit)
        self.assertIn("eu5ab_tpl_1_building_priorities", defaults)
        self.assertIn("eu5ab_edit_priority_building_granary", load)
        self.assertIn("name = eu5ab_tpl_1_building_priorities key = building_type:granary", commit)

        self.assertIn("cmm_register_bool_setting", on_actions)
        self.assertIn("cmm_register_numeric_setting", on_actions)
        self.assertIn("cmm_register_slider_setting", on_actions)
        self.assertIn("cmm_register_dropdown_setting", on_actions)
        self.assertIn("setting_id = job_fill_deadline_months", on_actions)
        deadline_setting = next(
            block
            for block in _blocks_for_token(
                on_actions, "cmm_register_numeric_setting = "
            )
            if "setting_id = job_fill_deadline_months" in block
        )
        self.assertIn("default_value = 12", deadline_setting)
        self.assertIn("min_value = 0 max_value = 96 step_value = 1", on_actions)
        self.assertIn("setting_id = native_input_priority", on_actions)
        self.assertIn("setting_id = economic_metric", on_actions)
        self.assertIn("eu5ab_sync_cmm_settings = yes", on_actions)
        self.assertIn("eu5ab_refresh_global_budget = yes", on_actions)
        self.assertIn("eu5ab_global_budget_remaining", effects)

        for obsolete_control in (
            "eu5ab_gui_active_job_fill_deadline_dec",
            "eu5ab_gui_active_native_input_priority_dec",
            "eu5ab_gui_active_toggle_allow_special_buildings",
            "eu5ab_gui_active_cash_inc_1k",
        ):
            self.assertNotIn(obsolete_control, scripted_guis)
            self.assertNotIn(obsolete_control, rules_gui)
        self.assertIn("eu5ab_diagnostics_cmm_hint", rules_gui)
        self.assertIn("eu5ab_regional_development_name", localization)
        self.assertIn("eu5ab_regional_development__job_fill_deadline_months_name", localization)
        self.assertIn("0—96 个月", localization)

    def test_generated_scripts_have_balanced_braces(self):
        for path, content in self.files.items():
            if path.suffix in {".txt", ".gui"}:
                with self.subTest(path=path):
                    self.assertTrue(_balanced_script(content))

    def test_performance_tab_presets_and_advanced_settings_are_isolated(self):
        on_actions = self.files[
            ROOT / "in_game" / "common" / "on_action" / "eu5ab_on_actions.txt"
        ]
        chinese = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        english = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]

        self.assertIn("setting_id = performance_preset", on_actions)
        self.assertIn("tab_id = performance group_id = preset", on_actions)
        self.assertIn("default_index = 3 option_count = 4", on_actions)
        warning_settings = (
            "performance_throughput_warning_summary",
            "performance_throughput_warning_action",
        )
        for warning_setting in warning_settings:
            self.assertIn(f"setting_id = {warning_setting}", on_actions)
            self.assertIn(
                "key = flag:eu5ab_regional_development__"
                f"{warning_setting} value = 0",
                on_actions,
            )
            self.assertIn(
                "eu5ab_regional_development__"
                f"{warning_setting}_on_changed = {{",
                scripted_guis,
            )
        self.assertIn(
            '"variable_map(cmm|flag:eu5ab_regional_development__performance_preset)" = 3',
            scripted_guis,
        )
        advanced = {
            "parallel_location_scan": 1,
            "daily_location_task_limit": 30,
            "max_additions_per_run": 0,
            "early_stop_when_candidates_sufficient": 1,
        }
        for setting_id, default in advanced.items():
            match = re.search(
                rf"mod_id = eu5ab_regional_development setting_id = {setting_id}.*?"
                rf"tab_id = performance group_id = advanced.*?default_value = {default}",
                on_actions,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(match, setting_id)
        for daily, maximum in ((10, 30), (20, 50), (30, 0)):
            self.assertIn(
                "key = flag:eu5ab_regional_development__daily_location_task_limit "
                f"value = {daily}",
                on_actions,
            )
            self.assertIn(
                "key = flag:eu5ab_regional_development__max_additions_per_run "
                f"value = {maximum}",
                on_actions,
            )
        self.assertIn(
            "key = flag:eu5ab_regional_development__performance_preset value = 4",
            on_actions,
        )
        self.assertIn('eu5ab_regional_development__performance_name: "性能优化"', chinese)
        self.assertIn('eu5ab_regional_development__performance_preset_option_1_name: "保守"', chinese)
        self.assertIn('eu5ab_regional_development__performance_preset_option_3_name: "效率优先"', chinese)
        self.assertIn(
            "大量地点应用模板可能降低游戏性能。",
            chinese,
        )
        self.assertIn("卡顿时请更换预设或降低「每轮最多新增」（0 为无限）。", chinese)
        self.assertIn('eu5ab_regional_development__performance_preset_option_1_name: "Conservative"', english)
        self.assertIn('eu5ab_regional_development__performance_preset_option_3_name: "Maximum Throughput"', english)
        self.assertIn("Many templated locations can reduce game performance", english)
        self.assertIn("If the game slows down, change preset or cap additions", english)

    def test_generated_files_have_no_trailing_whitespace(self):
        for path, content in self.files.items():
            offending_lines = [
                number for number, line in enumerate(content.splitlines(), 1) if line != line.rstrip()
            ]
            with self.subTest(path=path):
                self.assertEqual(offending_lines, [])

    def test_core_eu5_hooks_are_present(self):
        combined = "\n".join(self.files.values())
        for token in [
            "monthly_country_pulse",
            "construct_building",
            "every_owned_location",
            "scripted_gui",
            "select_trigger",
            "num_pop_type",
            "gold >=",
            "special_building_allowed",
            "input_source_building_allowed",
            "player_automated_category = buildings",
            "show_in_gui_list = no",
            "show_message = no",
            "automation_tick = never",
            "eu5ab_automation_policy_footer",
            "eu5ab_automation_buildings_window",
            "cmf_add_action_bar_element",
            "eu5ab_action_bar",
            "gui/eu5ab_automation_buildings_window.gui = eu5ab_automation_buildings_window",
            "gui/eu5ab_template_editor_window.gui = eu5ab_template_editor_window",
            "gui/eu5ab_template_buildings_window.gui = eu5ab_template_buildings_window",
            "gui/eu5ab_template_rules_window.gui = eu5ab_template_rules_window",
            "gui/eu5ab_template_scope_window.gui = eu5ab_template_scope_window",
            'name = "eu5ab_automation_buildings_window"',
            "GetVariableSystem.Exists('eu5ab_window_open')",
            "owner ?= scope:actor",
            "building_type:granary",
            "eu5ab_candidate_location_can_build = {",
            "eu5ab_choose_location",
            "eu5ab_choose_province",
            "eu5ab_choose_area",
            "eu5ab_apply_template_slot_1_to_selected_location",
            "eu5ab_apply_template_slot_20_to_selected_location",
            "eu5ab_apply_template_slot_1_to_selected_province",
            "eu5ab_apply_template_slot_1_to_selected_area",
            "eu5ab_clear_selected_location_policy",
            "eu5ab_template_editor_window",
            "eu5ab_template_buildings_window",
            "eu5ab_template_rules_window",
            "eu5ab_presets_tab",
            "eu5ab_custom_tab",
            "eu5ab_sidebar_title",
            "eu5ab_detail_title",
            "eu5ab_gui_edit_template_slot_1",
            "eu5ab_gui_open_template_buildings_slot_1",
            "eu5ab_gui_open_template_rules_slot_1",
            "eu5ab_gui_open_template_locations_slot_1",
            "cmm_register_bool_setting",
            "cmm_register_numeric_setting",
            "eu5ab_sync_cmm_settings",
            "eu5ab_global_budget_remaining",
            "eu5ab_gui_toggle_preset_granary_paused",
            "eu5ab_template_slot_1_building_allowed",
            "is_key_in_variable_map = { name = eu5ab_tpl_1_building_priorities target = prev }",
            "eu5ab_gui_active_priority_inc_granary",
            "eu5ab_tpl_1_building_priorities",
            "eu5ab_prepare_template_scope_view",
            "eu5ab_template_slot_1_title",
            "eu5ab_template_slot_20_title",
            "eu5ab_template_editor_title",
            "eu5ab_enter_map_selection",
            "looking_for_a = province",
            "looking_for_a = area",
            "every_location_in_province",
            "every_location_in_area",
            "bg_square_wood_tile",
            "bg_cabinet_card_frame",
            "checkbutton_02_alt",
            "eu5ab_template_slot",
            "eu5ab_tpl_1_min_cash_reserve",
        ]:
            self.assertIn(token, combined)

    def test_monthly_hook_uses_eu5_singular_on_action_directory(self):
        singular = ROOT / "in_game" / "common" / "on_action" / "eu5ab_on_actions.txt"
        plural = ROOT / "in_game" / "common" / "on_actions" / "eu5ab_on_actions.txt"
        events = ROOT / "in_game" / "events" / "eu5ab_monthly_events.txt"
        self.assertIn(singular, self.files)
        self.assertNotIn(plural, self.files)
        self.assertIn(events, self.files)
        hook = self.files[singular]
        self.assertIn("monthly_country_pulse", hook)
        self.assertIn("trigger_event_silently = {", hook)
        self.assertIn("id = eu5ab_monthly.1", hook)
        self.assertIn("days = 1", hook)
        self.assertNotIn("eu5ab_run_regional_development_policy = yes", hook)

        event = self.files[events]
        self.assertIn("namespace = eu5ab_monthly", event)
        self.assertIn("type = country_event", event)
        self.assertIn("title = eu5ab_window_title", event)
        self.assertIn("hidden = yes", event)
        self.assertIn("immediate = {", event)
        self.assertEqual(event.count("eu5ab_reset_policy_budgets_if_needed = yes"), 1)
        self.assertEqual(event.count("eu5ab_run_regional_development_policy = yes"), 1)
        self.assertIn("eu5ab_scan_regional_development_bucket = yes", event)
        self.assertIn("eu5ab_finish_regional_development_scan = yes", event)
        self.assertIn("var:eu5ab_scan_bucket_day < 20", event)
        self.assertEqual(event.count("save_scope_as = actor"), 3)
        self.assertIn("namespace = eu5ab_worker", event)
        self.assertIn("type = location_event", event)
        self.assertIn("eu5ab_run_location_worker = yes", event)
        first_actor = event.index("save_scope_as = actor")
        first_probe = event.index("eu5ab_run_regional_development_policy = yes")
        self.assertLess(first_actor, first_probe)
        second_actor = event.index("save_scope_as = actor", first_actor + 1)
        finish_probe = event.index("eu5ab_finish_regional_development_scan = yes")
        self.assertLess(second_actor, finish_probe)
        worker_actor = event.rindex("save_scope_as = actor")
        self.assertGreater(worker_actor, finish_probe)

    def test_generates_twenty_template_slots(self):
        combined = "\n".join(self.files.values())
        for slot in range(1, 21):
            with self.subTest(slot=slot):
                self.assertIn(f"eu5ab_template_slot_{slot}_title", combined)
                self.assertIn(f"eu5ab_gui_edit_template_slot_{slot}", combined)
                self.assertIn(f"eu5ab_apply_template_slot_{slot}_to_selected_location", combined)
                self.assertIn(f"eu5ab_apply_template_slot_{slot}_to_selected_province", combined)
                self.assertIn(f"eu5ab_apply_template_slot_{slot}_to_selected_area", combined)
                self.assertIn(f"eu5ab_tpl_{slot}_name_id", combined)
                self.assertIn(f"eu5ab_tpl_{slot}_name_selected", combined)
                self.assertIn(f"eu5ab_template_slot_{slot}_building_allowed", combined)

    def test_main_window_is_overview_and_editor_is_separate(self):
        main_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"]
        editor_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_editor_window.gui"]
        buildings_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_buildings_window.gui"]
        rules_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"]
        rename_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_rename_window.gui"]
        scope_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_scope_window.gui"]
        generated_gui = "\n".join(
            self.files[path]
            for path in [
                ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui",
                ROOT / "in_game" / "gui" / "eu5ab_template_editor_window.gui",
                ROOT / "in_game" / "gui" / "eu5ab_template_buildings_window.gui",
                ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui",
                ROOT / "in_game" / "gui" / "eu5ab_template_rename_window.gui",
                ROOT / "in_game" / "gui" / "eu5ab_template_scope_window.gui",
            ]
        )
        self.assertIn("eu5ab_window_title", main_gui)
        self.assertIn("eu5ab_presets_tab", main_gui)
        self.assertIn("eu5ab_custom_tab", main_gui)
        self.assertIn("eu5ab_sidebar_title", main_gui)
        self.assertIn("eu5ab_detail_title", main_gui)
        self.assertIn("size = { 1200 720 }", main_gui)
        self.assertIn("header_main_tabs", main_gui)
        self.assertIn("button_main_tab_alt", main_gui)
        self.assertIn("size = { 520 585 }", main_gui)
        self.assertIn("size = { 500 480 }", main_gui)
        self.assertIn("size = { 500 50 }", main_gui)
        self.assertIn("position = { 530 0 }", main_gui)
        self.assertIn("size = { 640 585 }", main_gui)
        self.assertIn("size = { 620 480 }", main_gui)
        self.assertIn("eu5ab_gui_open_preset_", main_gui)
        self.assertIn("eu5ab_apply_template_slot_1_to_selected_location", main_gui)
        self.assertIn("eu5ab_apply_template_slot_1_to_selected_province", main_gui)
        self.assertIn("eu5ab_apply_template_slot_1_to_selected_area", main_gui)
        self.assertIn("size = { 176 36 }", main_gui)
        self.assertIn("eu5ab_template_name_click_hint", main_gui)
        self.assertNotIn("ExecuteConsoleCommand('gui.", main_gui)
        self.assertIn("eu5ab_tpl_1_custom_name", main_gui)
        self.assertIn("eu5ab_template_name_food_security", main_gui)
        self.assertIn("eu5ab_template_name_food_security", editor_gui)
        self.assertIn("title = \"eu5ab_map_select_location_click\"", main_gui)
        self.assertIn("text = \"eu5ab_map_select_location_click\"", main_gui)
        self.assertIn("GetVariableSystem.Set('eu5ab_template_buildings_visible', '1')", main_gui)
        self.assertIn("GetVariableSystem.Set('eu5ab_template_rules_visible', '1')", main_gui)
        self.assertNotIn("eu5ab_set_locations_button", main_gui)
        self.assertIn("scrollbox", main_gui)
        self.assertNotIn("fontsize = 32", main_gui)
        self.assertNotIn("eu5ab_building_rules_title", main_gui)
        self.assertIn("eu5ab_new_blank_template_button", main_gui)
        self.assertIn("eu5ab_new_recommended_template_button", main_gui)
        self.assertIn("eu5ab_custom_empty_detail", main_gui)
        self.assertIn("Not(Player.MakeScope.GetVariable('eu5ab_tpl_1_exists').IsSet)", main_gui)
        self.assertIn("eu5ab_tpl_1_exists", main_gui)
        self.assertNotIn("gui.createwidget gui/eu5ab_player_templates_window.gui", main_gui)
        self.assertNotIn("gui.createwidget gui/eu5ab_template_locations_window.gui", main_gui)
        self.assertNotIn("action_tooltip =", main_gui)
        self.assertNotIn("click_modifier = ctrl", main_gui)
        self.assertNotIn("click_modifier = shift", main_gui)
        self.assertNotIn("gui/eu5ab_template_locations_window.gui", generated_gui)
        self.assertNotIn("gui/eu5ab_player_templates_window.gui", generated_gui)
        self.assertNotIn("gui.ClearWidgets", generated_gui)
        self.assertNotIn("gui.createwidget", generated_gui)
        self.assertNotIn("action_tooltip_pop_out", main_gui)
        self.assertIn("eu5ab_template_editor_sections_title", editor_gui)
        self.assertNotIn("eu5ab_building_rules_title", editor_gui)
        self.assertNotIn("eu5ab_template_slot_1_buildings_title", buildings_gui)
        self.assertIn("eu5ab_building_granary", buildings_gui)
        self.assertIn("eu5ab_filter_burghers", buildings_gui)
        self.assertIn("eu5ab_gui_active_priority_dec_granary", buildings_gui)
        self.assertIn("eu5ab_gui_active_priority_inc_granary", buildings_gui)
        self.assertIn("eu5ab_edit_priority_building_granary", buildings_gui)
        self.assertNotIn("eu5ab_priority_high_icon", buildings_gui)
        self.assertNotIn("eu5ab_ban_icon", buildings_gui)
        self.assertNotIn("eu5ab_gui_active_pm_default", rules_gui)
        self.assertNotIn('text = "eu5ab_pm_default"', rules_gui)
        self.assertIn("editbox_single", rename_gui)
        self.assertIn("size = { 640 260 }", rename_gui)
        self.assertIn("size = { 580 48 }", rename_gui)
        self.assertIn("maximumsize = { 580 48 }", rename_gui)
        self.assertIn('name = "eu5ab_template_rename_window"', rename_gui)
        self.assertIn('datacontext = "[GetPlayer]"', rename_gui)
        self.assertIn("filter_mouse = none", rename_gui)
        self.assertIn("focus_on_visible = yes", rename_gui)
        self.assertIn("focuspolicy = all", rename_gui)
        self.assertIn("alwaystransparent = no", rename_gui)
        self.assertNotIn("ExecuteConsoleCommand('gui.", rename_gui)
        self.assertIn("eu5ab_tpl_1_custom_name", rename_gui)
        self.assertIn("eu5ab_gui_slot_1_name_custom", rename_gui)
        self.assertNotIn("eu5ab_gui_slot_1_name_food_security", rename_gui)
        name_scripted_guis = self.files[ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"]
        for name_id in [
            "food_security",
            "mining_development",
            "port_trade",
            "urban_industry",
            "military_frontier",
            "custom",
        ]:
            self.assertIn(f"eu5ab_gui_slot_1_name_{name_id}", name_scripted_guis)
        self.assertIn("eu5ab_template_name_custom", main_gui)
        scripted_guis = self.files[ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"]
        self.assertIn("set_variable = { name = eu5ab_tpl_1_name_id value = 6 }", scripted_guis)
        self.assertIn("set_variable = { name = eu5ab_tpl_1_name_selected value = 1 }", scripted_guis)
        self.assertIn("set_variable = { name = eu5ab_edit_name_selected value = 1 }", scripted_guis)
        self.assertIn('datamodel = "[Player.GetProvinces]"', scope_gui)
        self.assertIn('datamodel = "[Province.GetLocations]"', scope_gui)
        self.assertIn("Province.GetCapital.GetArea.GetNameWithNoTooltip", scope_gui)
        self.assertIn("eu5ab_scope_current_summary", scope_gui)

    def test_template_custom_name_marks_saved_state_and_updates_session_display(self):
        effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        main_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"
        ]
        rename_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_template_rename_window.gui"
        ]
        defaults = _blocks_for_token(effects, "eu5ab_template_slot_1_ensure_defaults = ")[0]
        load = _blocks_for_token(effects, "eu5ab_load_template_slot_1_into_editor = ")[0]
        commit = _blocks_for_token(effects, "eu5ab_commit_template_editor_to_slot_1 = ")[0]

        self.assertIn("eu5ab_tpl_1_name_selected", defaults)
        self.assertIn(
            "name = eu5ab_edit_name_selected value = var:eu5ab_tpl_1_name_selected",
            load,
        )
        self.assertIn(
            "name = eu5ab_tpl_1_name_selected value = var:eu5ab_edit_name_selected",
            commit,
        )
        self.assertIn(
            "GetVariableSystem.Set('eu5ab_tpl_1_custom_name', GetVariableSystem.Get('eu5ab_template_name_input'))",
            rename_gui,
        )
        self.assertIn("GetVariableSystem.Get('eu5ab_tpl_1_custom_name')", main_gui)

    def test_deleting_player_template_clears_its_settings_and_linked_locations(self):
        effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        main_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"
        ]

        clear_location = _blocks_for_token(
            effects, "eu5ab_clear_location_policy = "
        )[0]
        for variable in [
            "eu5ab_policy_id",
            "eu5ab_template_slot",
            "eu5ab_policy_decoupled",
            "eu5ab_min_cash_reserve",
            "eu5ab_allow_special_buildings",
            "eu5ab_pause_low_workforce",
            "eu5ab_job_fill_deadline_months",
            "eu5ab_native_input_priority",
        ]:
            self.assertIn(f"remove_variable = {variable}", clear_location)

        delete = _blocks_for_token(
            scripted_guis, "eu5ab_gui_delete_template_slot_1 = "
        )[0]
        self.assertIn("every_owned_location = {", delete)
        self.assertIn("var:eu5ab_template_slot = 1", delete)
        self.assertIn("eu5ab_clear_location_policy = yes", delete)
        self.assertIn("eu5ab_load_blank_template_into_editor = yes", delete)
        self.assertIn(
            "eu5ab_commit_template_editor_to_slot_1_and_refresh_budget = yes",
            delete,
        )
        for variable in ["eu5ab_tpl_1_exists", "eu5ab_tpl_1_saved", "eu5ab_tpl_1_paused"]:
            self.assertIn(f"remove_variable = {variable}", delete)
        self.assertIn("eu5ab_select_first_player_template = yes", delete)

        compatibility_loader = _blocks_for_token(
            effects, "eu5ab_load_new_template_into_editor = "
        )[0]
        self.assertIn(
            "eu5ab_load_recommended_template_into_editor = yes",
            compatibility_loader,
        )
        recommended = _blocks_for_token(
            effects, "eu5ab_load_recommended_template_into_editor = "
        )[0]
        blank = _blocks_for_token(
            effects, "eu5ab_load_blank_template_into_editor = "
        )[0]
        self.assertNotIn("eu5ab_edit_budget_mode", recommended)
        self.assertNotIn("eu5ab_edit_min_cash_reserve", recommended)
        self.assertIn(
            "name = eu5ab_edit_priority_building_granary value = 10",
            recommended,
        )
        self.assertEqual(
            len(re.findall(r"name = eu5ab_edit_priority_building_\w+ value = 0", blank)),
            self.building_count,
        )
        self.assertIn("eu5ab_gui_delete_template_slot_1", main_gui)
        self.assertIn("GetVariableSystem.Clear('eu5ab_tpl_1_custom_name')", main_gui)
        self.assertIn("GetVariableSystem.Clear('eu5ab_selected_template_slot')", main_gui)
        self.assertIn("eu5ab_delete_template_button", main_gui)
        self.assertIn('tooltip = "eu5ab_delete_template_tooltip"', main_gui)

    def test_template_footer_confirms_delete_and_toggles_real_pause_state(self):
        main_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"
        ]
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        scripted_triggers = self.files[
            ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"
        ]
        scripted_effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]

        self.assertIn("button_regular_alt_yellow = {", main_gui)
        self.assertIn("button_regular_alt_green = {", main_gui)
        self.assertIn("button_regular_alt_red = {", main_gui)
        self.assertIn("eu5ab_pause_template_button", main_gui)
        self.assertIn("eu5ab_resume_template_button", main_gui)
        self.assertIn("eu5ab_template_paused_badge", main_gui)
        self.assertIn("eu5ab_delete_template_confirm_prompt", main_gui)
        self.assertIn("eu5ab_delete_template_confirm_button", main_gui)
        self.assertIn("eu5ab_delete_template_cancel_button", main_gui)

        open_delete = main_gui.index('text = "eu5ab_delete_template_button"')
        open_delete_block = main_gui[open_delete:open_delete + 500]
        self.assertIn(
            "GetVariableSystem.Set('eu5ab_delete_confirmation_slot', '1')",
            open_delete_block,
        )
        self.assertNotIn("eu5ab_gui_delete_template_slot_1", open_delete_block)

        confirm_delete = main_gui.index('text = "eu5ab_delete_template_confirm_button"')
        confirm_delete_block = main_gui[confirm_delete:confirm_delete + 700]
        self.assertIn("eu5ab_gui_delete_template_slot_1", confirm_delete_block)
        self.assertIn(
            "GetVariableSystem.Clear('eu5ab_delete_confirmation_slot')",
            confirm_delete_block,
        )

        pause = _blocks_for_token(
            scripted_guis, "eu5ab_gui_toggle_template_slot_1_paused = "
        )[0]
        self.assertIn("has_variable = eu5ab_tpl_1_paused", pause)
        self.assertIn("remove_variable = eu5ab_tpl_1_paused", pause)
        self.assertIn("name = eu5ab_tpl_1_paused value = 1", pause)
        preset_pause = _blocks_for_token(
            scripted_guis, "eu5ab_gui_toggle_preset_granary_paused = "
        )[0]
        self.assertIn("has_variable = eu5ab_preset_granary_paused", preset_pause)
        self.assertIn("remove_variable = eu5ab_preset_granary_paused", preset_pause)
        self.assertIn(
            "name = eu5ab_preset_granary_paused value = 1",
            preset_pause,
        )

        slot_one_footer = main_gui[
            main_gui.index("button_regular_alt_yellow = {"):
            main_gui.index('text = "eu5ab_delete_template_button"')
        ]
        self.assertIn(
            "visible = \"[Not(Player.MakeScope.GetVariable('eu5ab_tpl_1_paused').IsSet)]\"",
            slot_one_footer,
        )
        self.assertIn(
            "visible = \"[Player.MakeScope.GetVariable('eu5ab_tpl_1_paused').IsSet]\"",
            slot_one_footer,
        )
        self.assertIn('text = "eu5ab_pause_template_button"', slot_one_footer)
        self.assertIn('text = "eu5ab_resume_template_button"', slot_one_footer)

        not_paused = _blocks_for_token(
            scripted_triggers, "eu5ab_location_template_not_paused = "
        )[0]
        self.assertIn("var:eu5ab_template_slot = 1", not_paused)
        self.assertIn("owner = { has_variable = eu5ab_tpl_1_paused }", not_paused)
        self.assertIn("var:eu5ab_template_slot = 20", not_paused)
        self.assertIn("owner = { has_variable = eu5ab_preset_granary_paused }", not_paused)
        self.assertGreaterEqual(
            scripted_effects.count("eu5ab_location_template_not_paused = yes"),
            41,
        )

    def test_template_list_and_footer_controls_use_fixed_bottom_layout(self):
        main_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"
        ]

        left_scrollbox = main_gui.index("size = { 500 480 }")
        blank_template = main_gui.index('text = "eu5ab_new_blank_template_button"')
        recommended_template = main_gui.index(
            'text = "eu5ab_new_recommended_template_button"'
        )
        detail_column = main_gui.index("position = { 530 0 }")
        detail_scrollbox = main_gui.index("size = { 620 480 }")
        delete_footer = main_gui.index('text = "eu5ab_delete_template_button"')

        self.assertLess(left_scrollbox, blank_template)
        self.assertLess(blank_template, recommended_template)
        self.assertLess(recommended_template, detail_column)
        self.assertLess(detail_scrollbox, delete_footer)
        self.assertIn("layoutpolicy_vertical = fixed", main_gui)
        self.assertIn("ignoreinvisible = yes", main_gui)
        self.assertGreaterEqual(main_gui.count("minimumsize = { 500 50 }"), 20)
        self.assertGreaterEqual(main_gui.count("maximumsize = { 500 50 }"), 20)
        left_list = main_gui[left_scrollbox:blank_template]
        self.assertIn("layoutpolicy_vertical = fixed", left_list)
        self.assertNotIn("layoutpolicy_vertical = preferred", left_list)
        self.assertGreaterEqual(main_gui.count('tooltip = "eu5ab_select_template_tooltip"'), 20)
        self.assertEqual(main_gui.count("Localize('eu5ab_template_paused_badge')"), 20)
        self.assertGreater(
            main_gui.index('tooltip = "eu5ab_template_name_click_tooltip"'),
            detail_column,
        )

    def test_scope_window_can_clear_every_location_shown_for_current_template(self):
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        scope_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_template_scope_window.gui"
        ]
        clear_scope = _blocks_for_token(
            scripted_guis, "eu5ab_gui_clear_current_template_scope = "
        )[0]

        self.assertIn("var:eu5ab_scope_location_count > 0", clear_scope)
        self.assertIn("every_owned_location = {", clear_scope)
        self.assertIn("root = { var:eu5ab_scope_view_mode = 1 }", clear_scope)
        self.assertIn("var:eu5ab_template_slot = root.var:eu5ab_scope_view_value", clear_scope)
        self.assertIn("root = { var:eu5ab_scope_view_mode = 2 }", clear_scope)
        self.assertIn("var:eu5ab_policy_id = root.var:eu5ab_scope_view_value", clear_scope)
        self.assertEqual(clear_scope.count("eu5ab_clear_location_policy = yes"), 2)
        self.assertIn("eu5ab_prepare_template_scope_view = yes", clear_scope)
        self.assertIn("eu5ab_gui_clear_current_template_scope", scope_gui)
        self.assertIn("eu5ab_scope_clear_all", scope_gui)
        self.assertIn('tooltip = "eu5ab_scope_clear_all_tt"', scope_gui)
        self.assertIn("size = { 44 36 }", scope_gui)
        self.assertIn("size = { 310 36 }", scope_gui)
        self.assertIn("size = { 36 36 }", scope_gui)
        self.assertIn("size = { 310 34 }", scope_gui)
        self.assertIn("size = { 112 28 }", scope_gui)
        self.assertNotIn("margin = { 38 2 }", scope_gui)

    def test_scripted_windows_register_independent_gui_files(self):
        scripted_windows = self.files[ROOT / "in_game" / "gui" / "scripted_widgets" / "eu5ab_scripted_windows.txt"]
        for relative_path, window in [
            ("eu5ab_automation_buildings_window.gui", "eu5ab_automation_buildings_window"),
            ("eu5ab_template_editor_window.gui", "eu5ab_template_editor_window"),
            ("eu5ab_template_buildings_window.gui", "eu5ab_template_buildings_window"),
            ("eu5ab_template_rules_window.gui", "eu5ab_template_rules_window"),
            ("eu5ab_template_rename_window.gui", "eu5ab_template_rename_window"),
            ("eu5ab_template_scope_window.gui", "eu5ab_template_scope_window"),
        ]:
            self.assertIn(f"gui/{relative_path} = {window}", scripted_windows)
            gui = self.files[ROOT / "in_game" / "gui" / relative_path]
            self.assertRegex(gui, rf'(?m)^window = \{{\n\s*name = "{window}"$')
            self.assertNotIn(f"type {window} = window", gui)

    def test_main_tabs_choose_default_detail(self):
        scripted_gui = self.files[ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"]
        effects = self.files[ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"]
        on_actions = self.files[ROOT / "in_game" / "common" / "on_action" / "eu5ab_on_actions.txt"]
        main_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"]
        self.assertIn("eu5ab_gui_open_presets_tab", scripted_gui)
        self.assertIn("set_variable = { name = eu5ab_active_preset_policy value = 1 }", scripted_gui)
        self.assertIn("remove_variable = eu5ab_custom_templates_empty", scripted_gui)
        self.assertIn("eu5ab_gui_open_player_templates", scripted_gui)
        self.assertIn("eu5ab_select_first_player_template = yes", scripted_gui)
        select_first = _blocks_for_token(
            effects, "eu5ab_select_first_player_template = "
        )[0]
        self.assertIn("NOT = { has_variable = eu5ab_active_template_slot }", select_first)
        self.assertIn("set_variable = { name = eu5ab_custom_templates_empty value = 1 }", select_first)
        self.assertIn("set_variable = eu5ab_cmf_window_requested", on_actions)
        callback = on_actions[on_actions.index("eu5ab_on_cmf_callback = {"):]
        self.assertIn("remove_variable = eu5ab_active_preset_policy", callback)
        self.assertIn("eu5ab_select_first_player_template = yes", callback)
        self.assertNotIn(
            "set_variable = { name = eu5ab_active_preset_policy value = 1 }",
            callback.split("# CMM auto-apply", 1)[0],
        )
        self.assertIn("GetVariableSystem.Set('eu5ab_selected_preset', '1')", main_gui)
        self.assertIn("GetVariableSystem.Set('eu5ab_selected_template_slot', '1')", main_gui)
        custom_default = (
            "Or(Not(GetVariableSystem.Exists('eu5ab_main_tab')), "
            "GetVariableSystem.HasValue('eu5ab_main_tab', '2'))"
        )
        flavor_default = (
            "Or(Not(GetVariableSystem.Exists('eu5ab_main_tab')), "
            "GetVariableSystem.HasValue('eu5ab_main_tab', '1'))"
        )
        self.assertIn(custom_default, main_gui)
        self.assertNotIn(flavor_default, main_gui)
        self.assertIn(
            "Or(Not(GetVariableSystem.Exists('eu5ab_selected_template_slot')), "
            "GetVariableSystem.HasValue('eu5ab_selected_template_slot', '1'))",
            main_gui,
        )

    def test_custom_tab_precedes_built_in_presets_and_explains_both_modes(self):
        main_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"]
        zh_localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        en_localization = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]

        self.assertLess(
            main_gui.index('text = "eu5ab_custom_tab"'),
            main_gui.index('text = "eu5ab_presets_tab"'),
        )
        self.assertIn('tooltip = "eu5ab_custom_tab_tooltip"', main_gui)
        self.assertIn('tooltip = "eu5ab_presets_tab_tooltip"', main_gui)
        self.assertIn('eu5ab_presets_tab: "内置预设"', zh_localization)
        self.assertIn('eu5ab_presets_tab_tooltip: "按不同发展目标提供只读的建筑优先级。"', zh_localization)
        self.assertIn('eu5ab_custom_tab_tooltip: "自行设置建筑优先级和应用范围。"', zh_localization)
        self.assertIn('eu5ab_presets_tab: "Built-in Presets"', en_localization)
        self.assertIn(
            'eu5ab_custom_tab_tooltip: "Set your own building priorities and coverage."',
            en_localization,
        )

    def test_main_panel_selection_and_detail_layout_are_synchronized(self):
        main_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"]
        preset_selection = "GetVariableSystem.HasValue('eu5ab_selected_preset', '1')"
        template_selection = "GetVariableSystem.HasValue('eu5ab_selected_template_slot', '1')"

        self.assertGreaterEqual(main_gui.count(preset_selection), 2)
        self.assertGreaterEqual(main_gui.count(template_selection), 2)
        self.assertNotIn("GetVariable('eu5ab_active_preset_policy').GetValue", main_gui)
        self.assertNotIn("GetVariable('eu5ab_active_template_slot').GetValue", main_gui)
        self.assertIn(
            'visible = "[Not(Player.MakeScope.GetVariable(\'eu5ab_tpl_1_exists\').IsSet)]"',
            main_gui,
        )
        self.assertIn(
            'visible = "[And(Player.MakeScope.GetVariable(\'eu5ab_tpl_1_exists\').IsSet, Not(Player.MakeScope.GetVariable(\'eu5ab_tpl_2_exists\').IsSet))]"',
            main_gui,
        )
        self.assertIn("GetVariableSystem.Set('eu5ab_selected_template_slot', '20')", main_gui)
        self.assertNotIn("size = { 500 -1 }", main_gui)
        self.assertNotIn("size = { 620 -1 }", main_gui)
        scrollbox_roots = re.findall(
            r'blockoverride "scrollbox_content" \{\s+vbox = \{\s+'
            r'layoutpolicy_horizontal = expanding\s+'
            r'layoutpolicy_vertical = preferred',
            main_gui,
        )
        self.assertEqual(len(scrollbox_roots), 1)
        self.assertRegex(
            main_gui,
            r'blockoverride "scrollbox_content" \{\s+vbox = \{\s+'
            r'layoutpolicy_horizontal = expanding\s+'
            r'layoutpolicy_vertical = fixed',
        )

    def test_main_panel_clicks_use_state_only_after_window_creation(self):
        gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"]
        self.assertNotIn("gui.ClearWidgets eu5ab_automation_buildings_window", gui)
        self.assertNotIn("gui.createwidget gui/eu5ab_automation_buildings_window.gui", gui)
        for gui_id in [
            "eu5ab_gui_open_preset_granary",
            "eu5ab_gui_open_player_templates",
            "eu5ab_gui_open_player_template_slot_1",
            "eu5ab_gui_new_blank_player_template",
            "eu5ab_gui_new_recommended_player_template",
            "eu5ab_gui_open_template_rules_slot_1",
        ]:
            start = gui.index(f"GetScriptedGui('{gui_id}')")
            self.assertNotIn("ExecuteConsoleCommand('gui.", gui[start:start + 500])

    def test_location_target_scopes_are_null_safe(self):
        combined = "\n".join(
            self.files[path]
            for path in [
                ROOT / "in_game" / "common" / "generic_actions" / "eu5ab_development_policy_actions.txt",
                ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt",
            ]
        )
        self.assertIn("scope:target_location ?=", combined)
        self.assertIn("scope:actor ?=", combined)
        self.assertNotIn("scope:target_location =", combined)

    def test_removed_custom_template_variables_are_not_read(self):
        generated = "\n".join(self.files.values())
        for stale_var in [
            "eu5ab_allow_building_granary",
            "eu5ab_ban_building_granary",
            "eu5ab_price_min",
            "eu5ab_price_max",
            "eu5ab_pm_mode",
            "eu5ab_template_paused",
            "eu5ab_stop_input_shortage",
            "eu5ab_auto_import_inputs",
        ]:
            self.assertIsNone(re.search(rf"(?<![A-Za-z0-9_]){re.escape(stale_var)}(?![A-Za-z0-9_])", generated))

    def test_removed_auto_import_feature_is_not_generated(self):
        generated = "\n".join(self.files.values())
        for stale_token in [
            "auto_import_inputs",
            "allow_auto_import",
            "eu5ab_toggle_auto_import_inputs",
            "Automatic Input Imports",
            "自动进口",
        ]:
            self.assertNotIn(stale_token, generated)

    def test_ui_state_variables_stay_out_of_scripted_guis(self):
        scripted = "\n".join(
            self.files[path]
            for path in [
                ROOT / "in_game" / "common" / "generic_actions" / "eu5ab_development_policy_actions.txt",
                ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt",
                ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt",
            ]
        )
        for variable in [
            "eu5ab_main_tab",
            "eu5ab_detail_mode",
            "eu5ab_selected_preset",
            "eu5ab_selected_template_slot",
            "eu5ab_building_filter",
            "eu5ab_location_filter",
            "eu5ab_template_buildings_visible",
            "eu5ab_template_rules_visible",
        ]:
            self.assertNotIn(variable, scripted)

    def test_cmf_action_bar_opens_scripted_widget_without_external_type_overrides(self):
        gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"]
        scripted_windows = self.files[ROOT / "in_game" / "gui" / "scripted_widgets" / "eu5ab_scripted_windows.txt"]
        on_actions = self.files[ROOT / "in_game" / "common" / "on_action" / "eu5ab_on_actions.txt"]
        scripted_guis = self.files[ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"]

        self.assertIn("cmf_on_mod_registration", on_actions)
        self.assertIn("cmf_add_action_bar_element = { element = eu5ab_action_bar }", on_actions)
        self.assertIn("cmf_register_scripted_gui = { element = eu5ab_action_bar }", on_actions)
        self.assertIn("cmf_on_callback", on_actions)
        self.assertIn("var:cmf_callback = flag:eu5ab_action_bar", on_actions)
        self.assertIn("set_variable = eu5ab_cmf_window_requested", on_actions)
        self.assertIn("on_game_load_after_lobby_human_country", on_actions)
        self.assertIn("eu5ab_on_cmf_after_load", on_actions)
        self.assertIn("remove_variable = eu5ab_cmf_window_requested", on_actions)
        self.assertIn("eu5ab_action_bar = {", scripted_guis)
        self.assertIn("remove_variable = eu5ab_cmf_window_requested", scripted_guis)
        self.assertIn("Player.MakeScope.GetVariable('eu5ab_cmf_window_requested').IsSet", gui)
        self.assertIn("GetVariableSystem.Clear('eu5ab_window_open')", gui)
        self.assertIn("gui/eu5ab_automation_buildings_window.gui = eu5ab_automation_buildings_window", scripted_windows)
        self.assertNotIn("EU5ABGlorpLeftPanelTypes", gui)
        self.assertNotIn("type button_panel_tab_ideas", gui)
        self.assertNotIn("type button_panel_tab_uniqueevents", gui)
        self.assertNotIn("gui.ClearWidgets", gui)
        self.assertNotIn("gui.createwidget", gui)
        self.assertNotIn("GUI.ClearWidgets ideas_window", gui)

    def test_generator_does_not_emit_old_console_widget_commands(self):
        generator_source = (ROOT / "src" / "eu5autobuild" / "generator.py").read_text(encoding="utf-8")
        self.assertNotIn("gui.ClearWidgets", generator_source)
        self.assertNotIn("gui.createwidget", generator_source)

    def test_localization_covers_policy_keys(self):
        localization = self.files[ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"]
        english_localization = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]
        main_menu_localization = self.files[ROOT / "main_menu" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"]
        self.assertEqual(localization, main_menu_localization)
        keys = set(re.findall(r"^ ([A-Za-z0-9_]+):", localization, flags=re.MULTILINE))
        for policy in self.policies:
            self.assertIn(policy.name_key, keys)
            self.assertIn(policy.description_key, keys)
        for rendered_localization in (localization, english_localization):
            for line in rendered_localization.splitlines()[1:]:
                if line:
                    self.assertRegex(line, r"^ [A-Za-z0-9_]+:")

    def test_non_chinese_languages_use_english_localization(self):
        english = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]
        _, separator, english_body = english.partition("\n")
        self.assertTrue(separator)
        for language in ENGLISH_FALLBACK_LANGUAGES:
            expected = f"l_{language}:\n{english_body}"
            for game_layer in ("in_game", "main_menu"):
                with self.subTest(language=language, game_layer=game_layer):
                    fallback = self.files[
                        ROOT
                        / game_layer
                        / "localization"
                        / language
                        / f"eu5ab_l_{language}.yml"
                    ]
                    self.assertEqual(fallback, expected)

    def test_windows_use_eu5_1_3_close_contract_and_player_context(self):
        for filename in [
            "eu5ab_automation_buildings_window.gui",
            "eu5ab_template_editor_window.gui",
            "eu5ab_template_buildings_window.gui",
            "eu5ab_template_rules_window.gui",
            "eu5ab_template_rename_window.gui",
            "eu5ab_template_scope_window.gui",
        ]:
            gui = self.files[ROOT / "in_game" / "gui" / filename]
            with self.subTest(filename=filename):
                self.assertNotIn('blockoverride "close_onclick"', gui)
                self.assertIn('blockoverride "close_on_action"', gui)
                self.assertIn('datacontext = "[GetPlayer]"', gui)
                close_blocks = _blocks_for_token(gui, 'blockoverride "close_on_action"')
                self.assertEqual(len(close_blocks), 1)
                self.assertIn("on_action =", close_blocks[0])
                self.assertNotIn("onclick =", close_blocks[0])
                close_buttons = _blocks_for_token(gui, "button_close_alt")
                self.assertEqual(len(close_buttons), 1)
                self.assertNotIn('input_action = "cancel"', close_buttons[0])
                self.assertNotIn("use_global_input_instance", close_buttons[0])

    def test_building_window_uses_native_scrollarea_with_compacting_rows(self):
        gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_buildings_window.gui"]
        description = next(
            block
            for block in _blocks_for_token(gui, "text_multi = ")
            if 'text = "eu5ab_building_rules_desc"' in block
        )
        self.assertIn("layoutpolicy_horizontal = expanding", description)
        self.assertIn("layoutpolicy_vertical = fixed", description)
        self.assertIn("size = { -1 44 }", description)
        self.assertIn("autoresize = no", description)
        self.assertNotIn("autoresize = yes", description)
        self.assertEqual(gui.count("scrollarea = {"), 1)
        self.assertEqual(gui.count("scrollwidget = {"), 1)
        self.assertEqual(gui.count("scrollbox = {"), 0)
        scrollarea = _blocks_for_token(gui, "scrollarea = ")[0]
        self.assertIn("layoutpolicy_horizontal = expanding", scrollarea)
        self.assertIn("layoutpolicy_vertical = fixed", scrollarea)
        self.assertIn("size = { -1 430 }", scrollarea)
        self.assertIn("scrollbarpolicy_horizontal = always_off", scrollarea)
        self.assertIn("scrollbarpolicy_vertical = as_needed", scrollarea)
        self.assertIn("scrollbar_vertical = { using = Scrollbar_Vertical }", scrollarea)
        self.assertIn("vbox = {", scrollarea)
        self.assertIn("ignoreinvisible = yes", scrollarea)
        self.assertIn(
            "vbox = { layoutpolicy_vertical = expanding }",
            scrollarea,
        )
        for forbidden in (
            'blockoverride "scrollbox_content"',
            "parentanchor = top|hcenter",
            "set_parent_size_to_minimum",
            "minimumsize = { 1110",
            "maximumsize = { 1110",
        ):
            self.assertNotIn(forbidden, gui)
        rows = [
            block
            for block in _blocks_for_token(gui, "hbox = ")
            if "using = bg_number_container_bckg" in block
        ]
        self.assertEqual(len(rows), self.building_count)
        for row in rows:
            self.assertIn("layoutpolicy_horizontal = expanding", row)
            self.assertIn("layoutpolicy_vertical = fixed", row)
            self.assertIn("size = { -1 44 }", row)
            self.assertNotIn("minimumsize = { 1110", row)
            self.assertNotIn("maximumsize = { 1110", row)
        self.assertIn('text = "eu5ab_building_armory"', gui)

    def test_rules_window_is_diagnostics_only_and_cmm_owns_shared_rules(self):
        gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"]
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        on_actions = self.files[
            ROOT / "in_game" / "common" / "on_action" / "eu5ab_on_actions.txt"
        ]
        effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        main_menu_localization = self.files[
            ROOT / "main_menu" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        english = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]
        main_menu_english = self.files[
            ROOT / "main_menu" / "localization" / "english" / "eu5ab_l_english.yml"
        ]

        self.assertEqual(gui.count("scrollarea = {"), 1)
        self.assertEqual(gui.count("scrollwidget = {"), 1)
        self.assertIn('text = "eu5ab_diagnostics_cmm_hint"', gui)
        for removed_page_or_control in (
            "eu5ab_rules_page_finance",
            "eu5ab_rules_page_automation",
            "eu5ab_gui_rules_page_finance",
            "eu5ab_gui_rules_page_automation",
            "eu5ab_gui_active_cash_dec_10k",
            "eu5ab_gui_active_budget_mode_fixed",
            "eu5ab_gui_active_toggle_allow_special_buildings",
            "eu5ab_edit_budget_mode",
            "eu5ab_edit_price_min",
        ):
            self.assertNotIn(removed_page_or_control, gui)
            self.assertNotIn(removed_page_or_control, scripted_guis)

        for registration in (
            "cmm_register_bool_setting",
            "cmm_register_numeric_setting",
            "cmm_register_slider_setting",
            "cmm_register_dropdown_setting",
            "cmm_register_settings_list",
            "setting_id = enabled",
            "setting_id = monthly_build_hard_cap",
            "setting_id = budget_mode",
            "setting_id = economic_metric",
            "setting_id = candidate_priority",
            "setting_id = emergency_food_exhaustion_override",
            "setting_id = emergency_food_stockpile_override",
            "setting_id = emergency_construction_goods_override",
            "setting_id = emergency_wartime_military_override",
            "setting_id = emergency_strategic_input_override",
            "setting_id = fixed_annual_budget",
            "setting_id = min_cash_reserve",
            "setting_id = price_min",
            "setting_id = price_max",
            "setting_id = allow_rgo",
            "setting_id = native_input_priority",
        ):
            self.assertIn(registration, on_actions)

        slider_blocks = _blocks_for_token(
            on_actions, "cmm_register_slider_setting = "
        )
        self.assertEqual(len(slider_blocks), 3)
        sliders = "\n".join(slider_blocks)
        self.assertIn("setting_id = monthly_build_hard_cap", sliders)
        self.assertIn("setting_id = fixed_annual_budget", sliders)
        self.assertIn("setting_id = min_cash_reserve", sliders)
        self.assertIn("min_value = 0 max_value = 599 step_value = 1", sliders)
        self.assertIn("min_value = 0 max_value = 999999 step_value = 100", sliders)
        self.assertIn("min_value = 0 max_value = 100000 step_value = 100", sliders)
        numeric_blocks = "\n".join(
            _blocks_for_token(on_actions, "cmm_register_numeric_setting = ")
        )
        self.assertNotIn("setting_id = monthly_build_hard_cap", numeric_blocks)
        self.assertNotIn("setting_id = fixed_annual_budget", numeric_blocks)
        self.assertNotIn("setting_id = min_cash_reserve", numeric_blocks)
        self.assertNotIn("cmm_set_dropdown_multiselector", on_actions)
        self.assertIn(
            "cmm_add_scripted_gui = {\n"
            "\t\t\tmod_id = eu5ab_regional_development setting_id = fixed_annual_budget",
            on_actions,
        )
        fixed_visibility = _blocks_for_token(
            scripted_guis,
            "eu5ab_regional_development__fixed_annual_budget_on_changed = ",
        )[0]
        self.assertIn(
            '"variable_map(cmm|flag:eu5ab_regional_development__budget_mode)" = 1',
            fixed_visibility,
        )
        self.assertIn("add = 1000 max = 999999", on_actions)
        self.assertIn("subtract = 1000 min = 0", on_actions)
        self.assertIn("add = 10 max = 599", on_actions)
        self.assertIn("subtract = 10 min = 0", on_actions)
        priority_lists = _blocks_for_token(
            on_actions, "cmm_register_settings_list = "
        )
        self.assertEqual(len(priority_lists), 1)
        self.assertIn("setting_id = candidate_priority", priority_lists[0])
        self.assertIn("tab_id = automation", priority_lists[0])
        self.assertIn("item_count = 4", priority_lists[0])
        self.assertIn("is_ordered = 1", priority_lists[0])
        for item, feature in enumerate(
            (
                "eu5ab_feature_upgrade_building",
                "eu5ab_feature_expand_building",
                "eu5ab_feature_expand_rgo",
                "eu5ab_feature_new_building",
            ),
            1,
        ):
            self.assertIn(
                f"item = {item} value = flag:{feature}",
                on_actions,
            )
        self.assertIn(
            "cmm_build_list_ordered_values = { setting = "
            "eu5ab_regional_development__candidate_priority "
            "list_name = eu5ab_candidate_priority_features }",
            effects,
        )
        self.assertIn(
            "eu5ab_regional_development__candidate_priority_on_changed = {",
            scripted_guis,
        )
        self.assertIn(
            "cmm_apply_list_change = { setting = "
            "eu5ab_regional_development__candidate_priority }",
            scripted_guis,
        )
        self.assertLess(
            on_actions.index("setting_id = candidate_priority"),
            on_actions.index("setting_id = allow_special_buildings"),
        )
        self.assertLess(
            on_actions.index("setting_id = economic_metric"),
            on_actions.index("setting_id = emergency_food_exhaustion_override"),
        )
        self.assertLess(
            on_actions.index("setting_id = enabled"),
            on_actions.index("setting_id = candidate_priority"),
        )
        self.assertLess(
            on_actions.index("setting_id = candidate_priority"),
            on_actions.index("setting_id = budget_mode"),
        )
        self.assertLess(
            on_actions.index("setting_id = emergency_strategic_input_override"),
            on_actions.index("setting_id = native_input_priority"),
        )
        for setting_id in (
            "emergency_food_exhaustion_override",
            "emergency_food_stockpile_override",
            "emergency_construction_goods_override",
            "emergency_wartime_military_override",
            "emergency_strategic_input_override",
        ):
            registration = next(
                block
                for block in _blocks_for_token(
                    on_actions, "cmm_register_bool_setting = "
                )
                if f"setting_id = {setting_id}" in block
            )
            self.assertIn("tab_id = general group_id = returns", registration)
            self.assertIn("default_value = 1", registration)
            self.assertIn(
                f"variable_map(cmm|flag:eu5ab_regional_development__{setting_id})",
                effects,
            )
        self.assertIn(
            "eu5ab_regional_development__min_cash_reserve_format",
            localization,
        )
        self.assertIn(
            'eu5ab_regional_development__fixed_annual_budget_format: "[CMMV(\'eu5ab_regional_development__fixed_annual_budget\')]@gold!"',
            localization,
        )
        for price_setting in ("price_min", "price_max"):
            self.assertIn(
                f"eu5ab_regional_development__{price_setting}_format: "
                f"\"[CMMV('eu5ab_regional_development__{price_setting}')]%\"",
                localization,
            )
        shift_step_settings = (
            "monthly_build_hard_cap",
            "fixed_annual_budget",
            "min_cash_reserve",
        )
        for rendered in (localization, english):
            self.assertIn("CMM_NUMERIC_INCREASE_MAX", rendered)
            self.assertIn("CMM_NUMERIC_DECREASE_MIN", rendered)
            for setting_id in shift_step_settings:
                self.assertIn(
                    "EqualTo_string(Scope.GetFlagName, "
                    f"'eu5ab_regional_development__{setting_id}')",
                    rendered,
                )
            self.assertIn("eu5ab_cmm_shift_increase_10", rendered)
            self.assertIn("eu5ab_cmm_shift_decrease_10", rendered)
            self.assertIn("eu5ab_cmm_shift_increase_1000", rendered)
            self.assertIn("eu5ab_cmm_shift_decrease_1000", rendered)
            self.assertIn("eu5ab_cmm_shift_increase_max", rendered)
            self.assertIn("eu5ab_cmm_shift_decrease_min", rendered)
        self.assertIn('eu5ab_cmm_shift_increase_10: "增加 10"', localization)
        self.assertIn('eu5ab_cmm_shift_decrease_1000: "减少 1000"', localization)
        self.assertIn('eu5ab_cmm_shift_increase_10: "Increase by 10"', english)
        self.assertIn('eu5ab_cmm_shift_decrease_1000: "Decrease by 1000"', english)
        self.assertNotIn("Shift 点击加减按钮时每次增减", localization)
        self.assertNotIn("Shift-click the plus or minus button", english)
        self.assertEqual(on_actions.count("name = eu5ab_cmm_shift_step value"), 6)
        for global_variable in (
            "eu5ab_global_monthly_build_hard_cap",
            "eu5ab_global_fixed_annual_budget",
            "eu5ab_global_min_cash_reserve",
        ):
            guard = f"limit = {{ has_variable = {global_variable} }}"
            first_read = f"value = var:{global_variable}"
            self.assertIn(guard, on_actions)
            self.assertLess(on_actions.index(guard), on_actions.index(first_read))
        self.assertIn(
            "value = var:eu5ab_global_monthly_build_hard_cap add = 10 max = 599",
            on_actions,
        )
        self.assertIn(
            "value = var:eu5ab_global_fixed_annual_budget add = 1000 max = 999999",
            on_actions,
        )
        self.assertIn(
            "value = var:eu5ab_global_min_cash_reserve add = 1000 max = 100000",
            on_actions,
        )
        self.assertIn(
            'eu5ab_regional_development__economic_metric_option_1_name: "@income! 收入"',
            localization,
        )
        self.assertIn(
            'eu5ab_regional_development__economic_metric_option_3_name: "@efficiency! 收入回报率"',
            localization,
        )
        self.assertIn(
            'eu5ab_regional_development__economic_metric_option_4_name: "@efficiency! 利润回报率"',
            localization,
        )
        self.assertNotIn("投资回报率（收入）", localization)
        self.assertNotIn("投资回报率（利润）", localization)
        self.assertNotIn("业主税收", localization)
        self.assertIn(
            'eu5ab_regional_development__rgo_min_utilization_format: "[CMMV(\'eu5ab_regional_development__rgo_min_utilization\')]%"',
            localization,
        )
        self.assertNotIn("rgo_priority", localization)
        self.assertNotIn("rgo_monthly_limit", localization)
        self.assertNotIn("rgo_priority", english)
        self.assertNotIn("rgo_monthly_limit", english)

        self.assertEqual(localization, main_menu_localization)
        self.assertEqual(english, main_menu_english)
        localization_keys = set(
            re.findall(r"^ ([A-Za-z0-9_]+):", localization, flags=re.MULTILINE)
        )
        english_keys = set(
            re.findall(r"^ ([A-Za-z0-9_]+):", english, flags=re.MULTILINE)
        )
        self.assertEqual(localization_keys, english_keys)
        registered_settings = set(
            re.findall(
                r"mod_id = eu5ab_regional_development setting_id = ([a-z0-9_]+)",
                on_actions,
            )
        )
        self.assertEqual(len(registered_settings), 29)
        for setting_id in registered_settings:
            for suffix in ("name", "desc"):
                key = f"eu5ab_regional_development__{setting_id}_{suffix}"
                self.assertIn(key, localization_keys)
                self.assertIn(key, english_keys)
        for tab_id, group_id in set(
            re.findall(r"tab_id = ([a-z0-9_]+) group_id = ([a-z0-9_]+)", on_actions)
        ):
            tab_key = f"eu5ab_regional_development__{tab_id}_name"
            self.assertIn(tab_key, localization_keys)
            self.assertIn(tab_key, english_keys)
            for suffix in ("name", "desc"):
                group_key = (
                    f"eu5ab_regional_development__{tab_id}__{group_id}_{suffix}"
                )
                self.assertIn(group_key, localization_keys)
                self.assertIn(group_key, english_keys)
        for option in range(1, 5):
            budget_option_key = (
                "eu5ab_regional_development__budget_mode_"
                f"option_{option}_name"
            )
            self.assertIn(budget_option_key, localization_keys)
            self.assertIn(budget_option_key, english_keys)
            for suffix in ("name", "desc"):
                metric_option_key = (
                    "eu5ab_regional_development__economic_metric_"
                    f"option_{option}_{suffix}"
                )
                self.assertIn(metric_option_key, localization_keys)
                self.assertIn(metric_option_key, english_keys)
            for suffix in ("name", "desc"):
                priority_item_key = (
                    "eu5ab_regional_development__candidate_priority_"
                    f"i{option}_{suffix}"
                )
                self.assertIn(priority_item_key, localization_keys)
                self.assertIn(priority_item_key, english_keys)
        priority_column_key = (
            "eu5ab_regional_development__candidate_priority_item_column_name"
        )
        self.assertIn(priority_column_key, localization_keys)
        self.assertIn(priority_column_key, english_keys)
        for key in (
            "eu5ab_regional_development_name",
            "eu5ab_regional_development__enabled_name",
            "eu5ab_regional_development__budget_mode_name",
            "eu5ab_regional_development__economic_metric_name",
            "eu5ab_regional_development__native_input_priority_name",
            "eu5ab_diagnostics_cmm_hint",
        ):
            self.assertIn(key, localization_keys)
            self.assertIn(key, english_keys)

        gui_localization_keys = set(
            re.findall(
                r'(?:text|tooltip|title)\s*=\s*"(eu5ab_[A-Za-z0-9_]+)"',
                gui,
            )
        )
        self.assertFalse(gui_localization_keys - localization_keys)
        gui_bindings = set(
            re.findall(r"GetScriptedGui\('(eu5ab_gui_[A-Za-z0-9_]+)'\)", gui)
        )
        for binding in gui_bindings:
            self.assertIn(f"\n{binding} = {{", scripted_guis)
        self.assertIn("GetVariableSystem.Clear('eu5ab_template_rules_visible')", gui)
        self.assertIn("GetVariableSystem.Set('eu5ab_window_open', '1')", gui)

    def test_building_rows_are_generated_once_for_active_template(self):
        gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_buildings_window.gui"]
        self.assertEqual(
            gui.count("eu5ab_gui_active_priority_dec_"), self.building_count * 3
        )
        self.assertEqual(
            gui.count("eu5ab_gui_active_priority_inc_"), self.building_count * 3
        )
        self.assertNotIn("eu5ab_tpl_1_priority_building_", gui)
        self.assertNotIn("eu5ab_gui_save_active_template", gui)
        self.assertNotIn("eu5ab_gui_reset_active_template", gui)
    def test_template_mutations_commit_immediately_without_global_save_reset(self):
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        generated_gui = "\n".join(
            self.files[ROOT / "in_game" / "gui" / filename]
            for filename in [
                "eu5ab_automation_buildings_window.gui",
                "eu5ab_template_editor_window.gui",
                "eu5ab_template_buildings_window.gui",
                "eu5ab_template_rules_window.gui",
            ]
        )
        for gui_id in [
            "eu5ab_gui_active_priority_inc_granary",
            "eu5ab_gui_active_priority_dec_granary",
        ]:
            block = _blocks_for_token(scripted_guis, f"{gui_id} = ")[0]
            self.assertIn("eu5ab_commit_active_template_editor = yes", block, gui_id)
        for removed_gui_id in [
            "eu5ab_gui_active_toggle_allow_special_buildings",
            "eu5ab_gui_active_cash_inc_1k",
            "eu5ab_gui_active_price_min_inc_1",
        ]:
            self.assertNotIn(removed_gui_id, scripted_guis)
            self.assertNotIn(removed_gui_id, generated_gui)
        for stale_id in [
            "eu5ab_gui_save_active_template",
            "eu5ab_gui_reset_active_template",
            "eu5ab_gui_save_template_slot_1",
            "eu5ab_gui_reset_template_slot_1",
        ]:
            self.assertNotIn(stale_id, scripted_guis)
            self.assertNotIn(stale_id, generated_gui)
        self.assertNotIn("eu5ab_reset_active_template_editor", effects)
        self.assertNotIn("eu5ab_template_slot_1_reset", effects)

        localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        self.assertEqual(localization.count('editor_title: "编辑本模板"'), 20)
        self.assertNotIn("编辑模板槽位", localization)
        for stale_key in [
            "eu5ab_template_save_title",
            "eu5ab_template_saved_state",
            "eu5ab_save_template_button",
            "eu5ab_reset_template_button",
        ]:
            self.assertNotIn(stale_key, localization)


    def test_priority_is_zero_to_ten_in_tenths_without_old_state_migration(self):
        effects = self.files[ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"]
        triggers = self.files[ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"]
        values = self.files[ROOT / "in_game" / "common" / "script_values" / "eu5ab_script_values.txt"]
        scripted_guis = self.files[ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"]
        self.assertIn("One building-type-keyed map replaces hundreds of scalar checks", effects)
        self.assertIn("name = eu5ab_tpl_1_building_priorities key = building_type:granary value = 10", effects)
        self.assertNotIn("key = building_type:fruit_orchard value = 0", effects)
        self.assertNotIn("key = building_type:porcelain_manufactory value = 0", effects)
        ensure_block = _blocks_for_token(
            effects, "eu5ab_template_slot_1_ensure_defaults = "
        )[0]
        initialized = "eu5ab_tpl_1_building_priorities_initialized"
        self.assertIn(f"NOT = {{ has_variable = {initialized} }}", ensure_block)
        self.assertIn(
            "NOT = { has_variable_map = eu5ab_tpl_1_building_priorities }",
            ensure_block,
        )
        self.assertLess(
            ensure_block.index(f"NOT = {{ has_variable = {initialized} }}"),
            ensure_block.index("NOT = { has_variable_map = eu5ab_tpl_1_building_priorities }"),
        )
        self.assertIn(f"set_variable = {{ name = {initialized} value = 1 }}", ensure_block)
        commit_block = _blocks_for_token(
            effects, "eu5ab_commit_template_editor_to_slot_1 = "
        )[0]
        self.assertIn(f"set_variable = {{ name = {initialized} value = 1 }}", commit_block)
        self.assertLess(
            commit_block.index(f"set_variable = {{ name = {initialized} value = 1 }}"),
            commit_block.index("set_variable = { name = eu5ab_tpl_1_exists value = 1 }"),
        )
        self.assertNotIn("priority_migrated", ensure_block)
        self.assertNotIn("divide = 10", ensure_block)
        self.assertIsNone(re.search(r"eu5ab_tpl_\d+_(?:allow|ban)_building_", effects))
        self.assertNotIn("scope:eu5ab_candidate_location.owner.var:eu5ab_tpl_1_ban_building_granary", triggers)
        self.assertIn("is_key_in_variable_map = { name = eu5ab_tpl_1_building_priorities target = prev }", triggers)
        self.assertIn('value = "variable_map(eu5ab_tpl_1_building_priorities|prev)"', values)
        self.assertIn("multiply = 50", values)
        self.assertIn("limit = { this = building_type:granary }", values)
        self.assertIn("add = 500", values)
        self.assertIn("add = var:eu5ab_priority_adjust_step", scripted_guis)
        self.assertIn("subtract = var:eu5ab_priority_adjust_step", scripted_guis)
        self.assertIn("value = 0.1", scripted_guis)
        self.assertIn("value = 0.5", scripted_guis)
        self.assertIn("value = 1", scripted_guis)
        copy_block = _blocks_for_token(effects, "eu5ab_copy_template_slot_1_to_slot_2 =")[0]
        self.assertLessEqual(len(copy_block.splitlines()), 4)
        self.assertIn("eu5ab_load_template_slot_1_into_editor", copy_block)
        self.assertIn("eu5ab_commit_template_editor_to_slot_2", copy_block)

    def test_scope_cache_and_hierarchy_are_generated(self):
        effects = self.files[ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"]
        actions = self.files[ROOT / "in_game" / "common" / "generic_actions" / "eu5ab_development_policy_actions.txt"]
        scripted_guis = self.files[ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"]
        editor_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"]
        scope_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_scope_window.gui"]
        map_mode = self.files[ROOT / "in_game" / "gfx" / "map" / "map_modes" / "eu5ab_template_coverage.txt"]
        localization = self.files[ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"]
        english_localization = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]

        self.assertNotIn("eu5ab_recalculate_template_scope_cache", "\n".join(self.files.values()))
        prepare_blocks = _blocks_for_token(effects, "eu5ab_prepare_template_scope_view = ")
        self.assertEqual(len(prepare_blocks), 1)
        prepare = prepare_blocks[0]
        for count_var in [
            "eu5ab_scope_location_count",
            "eu5ab_scope_province_count",
            "eu5ab_scope_area_count",
        ]:
            self.assertIn(count_var, prepare)
        self.assertEqual(prepare.count("every_owned_location = {"), 1)
        self.assertNotIn("every_province = {", prepare)
        self.assertNotIn("every_area = {", prepare)
        self.assertIn("add_to_temporary_list = eu5ab_scope_selected_provinces", prepare)
        self.assertIn("add_to_temporary_list = eu5ab_scope_selected_areas", prepare)
        self.assertIn("is_in_list = eu5ab_scope_selected_provinces", prepare)
        self.assertIn("is_in_list = eu5ab_scope_selected_areas", prepare)
        self.assertEqual(prepare.count("every_in_list = {"), 2)
        self.assertIn("list = eu5ab_scope_selected_provinces", prepare)
        self.assertIn("list = eu5ab_scope_selected_areas", prepare)
        self.assertIn("eu5ab_scope_view_selected", prepare)
        self.assertNotIn("eu5ab_tpl_1_scope_location_count", effects)
        self.assertNotIn("eu5ab_preset_granary_scope_location_count", effects)
        self.assertNotIn("eu5ab_prepare_template_scope_view = yes", actions)

        slot_scope = _blocks_for_token(scripted_guis, "eu5ab_gui_open_template_scope_slot_1 = ")[0]
        self.assertIn("eu5ab_scope_view_mode value = 1", slot_scope)
        self.assertIn("eu5ab_scope_view_value value = 1", slot_scope)
        self.assertIn("eu5ab_prepare_template_scope_view = yes", slot_scope)
        preset_scope = _blocks_for_token(scripted_guis, "eu5ab_gui_open_preset_scope_granary = ")[0]
        self.assertIn("eu5ab_scope_view_mode value = 2", preset_scope)
        self.assertIn("eu5ab_prepare_template_scope_view = yes", preset_scope)
        province_visibility = _blocks_for_token(
            scripted_guis, "eu5ab_gui_active_template_has_locations_in_province = "
        )[0]
        self.assertIn("any_location_in_province", province_visibility)
        self.assertIn("scope = location", province_visibility)
        self.assertNotIn("saved_scopes =", province_visibility)
        self.assertIn("province = {", province_visibility)
        self.assertNotIn("eu5ab_template_slot", province_visibility)
        self.assertNotIn("eu5ab_policy_id", province_visibility)

        self.assertIn('datamodel = "[Player.GetProvinces]"', scope_gui)
        self.assertEqual(scope_gui.count('datamodel = "[Province.GetLocations]"'), 1)
        self.assertIn("Province.GetCapital.GetArea.GetNameWithNoTooltip", scope_gui)
        self.assertNotIn("eu5ab_scope_expanded_province", scope_gui)
        self.assertIn("Province.GetCapital.MakeScope.GetVariable('eu5ab_scope_view_expanded').IsSet", scope_gui)
        self.assertNotIn("Province.MakeScope", scope_gui)
        self.assertIn("eu5ab_gui_expand_scope_province", scope_gui)
        self.assertIn("eu5ab_gui_collapse_scope_province", scope_gui)
        self.assertIn("button_square_plus", scope_gui)
        self.assertIn("button_square_minus", scope_gui)
        self.assertNotIn('raw_text = "+"', scope_gui)
        self.assertNotIn('raw_text = "−"', scope_gui)
        self.assertNotIn("action_tooltip = {", scope_gui)
        self.assertEqual(scope_gui.count("onclick = \"[GetScriptedGui('eu5ab_gui_expand_scope_province')"), 1)
        self.assertEqual(scope_gui.count("onclick = \"[GetScriptedGui('eu5ab_gui_collapse_scope_province')"), 1)
        for gui_id, effect_line in [("expand", "set_variable"), ("collapse", "remove_variable")]:
            block = _blocks_for_token(scripted_guis, f"eu5ab_gui_{gui_id}_scope_province = ")[0]
            self.assertIn("scope = location", block)
            self.assertNotIn("saved_scopes =", block)
            self.assertNotIn("scope:target_province", block)
            self.assertNotIn("\n\t\tprovince = {", block)
            self.assertIn(f"{effect_line} = ", block)
        self.assertIn(
            "GuiScope.SetRoot(Province.GetCapital.MakeScope).End",
            scope_gui,
        )
        self.assertIn("Location.MakeScope.GetVariable('eu5ab_scope_view_selected').IsSet", scope_gui)
        self.assertEqual(scope_gui.count("scrollbox = {"), 1)
        self.assertEqual(scope_gui.count('blockoverride "scrollbox_content"'), 1)
        self.assertNotIn("scrollarea = {", scope_gui)
        self.assertNotIn("scrollwidget = {", scope_gui)
        self.assertNotIn("parentanchor = top|hcenter", scope_gui)
        self.assertNotIn("set_parent_size_to_minimum", scope_gui)
        self.assertIn("layoutpolicy_vertical = expanding", scope_gui)
        self.assertIn("ignoreinvisible = yes", scope_gui)
        self.assertGreaterEqual(scope_gui.count("size = { 1200 720 }"), 2)
        self.assertIn("eu5ab_gui_clear_location_template", scope_gui)
        self.assertIn("eu5ab_gui_clear_location_template", scripted_guis)
        clear_scope = _blocks_for_token(
            scripted_guis, "eu5ab_gui_clear_location_template = "
        )[0]
        self.assertIn("scope = country", clear_scope)
        self.assertIn("saved_scopes = { target_location }", clear_scope)
        self.assertIn("scope:target_location ?=", clear_scope)
        self.assertIn("eu5ab_prepare_template_scope_view = yes", clear_scope)
        self.assertNotIn("eu5ab_scope_location_count subtract = 1", clear_scope)
        self.assertNotIn("eu5ab_scope_province_count subtract = 1", clear_scope)
        self.assertNotIn("eu5ab_scope_area_count subtract = 1", clear_scope)
        self.assertNotIn("any_location_in_province", clear_scope)
        self.assertNotIn("any_location_in_area", clear_scope)
        self.assertIn(
            "GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('target_location', Location.MakeScope).End",
            scope_gui,
        )

        for target, parent_scope in [
            ("location", None),
            ("province", "province"),
            ("area", "area"),
        ]:
            action = _blocks_for_token(
                actions,
                f"eu5ab_apply_template_slot_1_to_selected_{target} = ",
            )[0]
            self.assertIn("interaction_source_list = {", action)
            self.assertIn("scope:actor = {", action)
            self.assertIn("every_owned_location = {", action)
            self.assertIn("limit = { NOT = { has_variable = eu5ab_policy_id } }", action)
            self.assertIn("eu5ab_register_location_for_scan = yes", action)
            self.assertNotIn("source = actor", action)
            self.assertNotIn("eu5ab_template_slot_1_ensure_defaults", action)
            self.assertNotIn("eu5ab_template_slot_1_save", action)
            if parent_scope is None:
                self.assertIn("add_to_list = source", action)
            else:
                self.assertIn(f"{parent_scope} = {{", action)
                self.assertIn("is_in_list = source", action)
                parent = _blocks_for_token(action, f"{parent_scope} = ")[0]
                self.assertIn("if = {", parent)
                self.assertNotRegex(parent, rf"^\s*{parent_scope}\s*=\s*\{{\s*limit\s*=",)
                self.assertIn(
                    "owner ?= scope:actor NOT = { has_variable = eu5ab_policy_id }",
                    action,
                )
        for action_id in [
            "eu5ab_decouple_selected_location",
            "eu5ab_clear_selected_location_policy",
        ]:
            action = _blocks_for_token(actions, f"{action_id} = ")[0]
            self.assertIn("limit = { has_variable = eu5ab_policy_id }", action)
        self.assertIn("eu5ab_gui_open_preset_scope_granary", editor_gui)
        self.assertIn("eu5ab_scope_current_summary", localization)
        self.assertNotIn("eu5ab_preset_granary_scope_summary", localization)

        mapmode_lines = [
            line for line in localization.splitlines() if "MAPMODE_EU5AB_TEMPLATE_COVERAGE:" in line
        ]
        self.assertEqual(len(mapmode_lines), 1)
        self.assertIn(r"\n亮色地点", mapmode_lines[0])
        english_mapmode_lines = [
            line
            for line in english_localization.splitlines()
            if "MAPMODE_EU5AB_TEMPLATE_COVERAGE:" in line
        ]
        self.assertEqual(len(english_mapmode_lines), 1)
        self.assertIn(r"\nBright locations", english_mapmode_lines[0])

        self.assertIn("eu5ab_template_coverage = {", map_mode)
        self.assertIn("category = geography", map_mode)
        self.assertIn("index = 3", map_mode)
        self.assertIn("map_color = {", map_mode)
        self.assertIn("tooltip_key = {", map_mode)
        self.assertIn("owner ?= { is_human = yes }", map_mode)
        self.assertEqual(
            map_mode.count("has_variable = eu5ab_scope_view_mode"),
            4,
        )
        self.assertEqual(
            map_mode.count("has_variable = eu5ab_scope_view_value"),
            4,
        )
        self.assertIn("var:eu5ab_scope_view_mode = 1", map_mode)
        self.assertIn("var:eu5ab_template_slot = owner.var:eu5ab_scope_view_value", map_mode)
        self.assertNotIn("scope:actor", map_mode)
        self.assertNotIn("refresh_colors_on_selection_change", map_mode)
        self.assertIn("define:NMapColors|MAP_COLOR_HIGH", map_mode)
        self.assertIn("define:NMapColors|MAP_COLOR_LOW", map_mode)
        self.assertIn("color_refresh_counters = { Day }", map_mode)
        self.assertIn("mapmode_eu5ab_template_coverage_name", localization)
        self.assertIn("MAPMODE_EU5AB_TEMPLATE_COVERAGE", localization)
        self.assertIn('mapmode_eu5ab_template_coverage_name: "高级自动建造覆盖"', localization)
        self.assertNotIn("模板覆盖地图", localization)
        self.assertIn("按「地区 › 省份 › 地点」排列。", localization)
        self.assertNotIn("展开一个省份后才加载其地点", localization)
        self.assertNotIn("左上角主面板", localization)
        self.assertNotRegex(localization, r"[“”‘’]")
        self.assertIn("个地点 /", localization)
        self.assertIn("个省份 /", localization)
        self.assertIn("个地区", localization)

    def test_building_filters_ages_and_special_availability_are_generated(self):
        gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_buildings_window.gui"]
        scripted_guis = self.files[ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"]
        self.assertNotIn("GetVariableSystem.Set('eu5ab_building_filter'", gui)
        self.assertNotIn("size = { -1 470 }", gui)
        open_block = _blocks_for_token(
            scripted_guis, "eu5ab_gui_open_template_buildings_slot_1 = "
        )[0]
        self.assertIn("eu5ab_edit_building_filter value = 0", open_block)
        self.assertIn("eu5ab_edit_building_age value = 0", open_block)
        self.assertIn(
            "clamp_variable = { name = eu5ab_edit_building_filter min = 0 max = 5 }",
            open_block,
        )
        for value in range(6):
            self.assertIn(f"eu5ab_gui_active_building_filter_{value}", gui)
            self.assertIn(f"eu5ab_gui_active_building_filter_{value}", scripted_guis)
        for gui_id, text_key, expected_size in [
            ("eu5ab_gui_active_building_filter_0", "eu5ab_filter_all", "size = { 180 40 }"),
            ("eu5ab_gui_active_building_age_0", "eu5ab_age_all", "size = { 154 40 }"),
        ]:
            blocks = [
                block
                for block in _blocks_for_token(gui, "checkbutton_02_alt = ")
                if gui_id in block
            ]
            self.assertEqual(len(blocks), 1)
            self.assertNotIn("hbox = {", blocks[0])
            self.assertIn(expected_size, blocks[0])
            self.assertIn("margin = { 8 7 }", blocks[0])
            self.assertIn('default_format = "#high"', blocks[0])
            self.assertIn("using = Font_Size_Small", blocks[0])
            self.assertNotIn("size = { 100% 100% }", blocks[0])
            self.assertNotIn("parentanchor = center", blocks[0])
            self.assertIn(f'text = "{text_key}"', blocks[0])
        for age in range(1, 7):
            self.assertIn(f"eu5ab_gui_active_building_age_{age}", gui)
            self.assertIn(f'eu5ab_building_age_{age}', gui)
            self.assertNotIn(f'name = "eu5ab_building_age_group_{age}"', gui)
        self.assertEqual(gui.count('name = "eu5ab_building_age_group_'), 0)
        self.assertEqual(gui.count("size = { 170 36 }"), self.building_count)
        self.assertEqual(gui.count("size = { 130 36 }"), self.building_count)
        self.assertIn('visible = "[And(Or(', gui)
        for building_id in ["caravanserai", "funduq"]:
            self.assertIn(f"eu5ab_gui_special_building_available_{building_id}", gui)
            self.assertIn(
                f"GetScriptedGui('eu5ab_gui_special_building_available_{building_id}')"
                ".IsShown(GuiScope.SetRoot(Player.MakeScope)"
                ".AddScope('actor', Player.MakeScope).End)",
                gui,
            )
            self.assertIn(f"eu5ab_gui_special_building_available_{building_id}", scripted_guis)
            self.assertIn(
                f"location_and_owner_can_build = {{ building_type = {building_id} }}",
                scripted_guis,
            )

    def test_priority_buttons_route_default_ctrl_and_shift_steps(self):
        gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_template_buildings_window.gui"
        ]
        localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        english = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        self.assertIn('eu5ab_priority_scale_hint: "0 = 禁止"', localization)
        self.assertIn('eu5ab_priority_scale_hint: "0 disables"', english)
        self.assertNotIn("0 = 禁止；单击", localization)
        self.assertNotIn("0 disables; click", english)
        button = next(
            block
            for block in _blocks_for_token(gui, "button_regular = ")
            if "eu5ab_gui_active_priority_dec_granary" in block
        )
        for modifier, step_id in [
            ("default", "default"),
            ("ctrl", "ctrl"),
            ("shift", "shift"),
        ]:
            self.assertIn(f"click_modifier = {modifier}", button)
            self.assertIn(f"on{modifier} =", button)
            self.assertIn(f"eu5ab_gui_priority_step_{step_id}", button)
        self.assertIn("click_modifiers = {", button)
        self.assertNotIn("\n\t\t\tonclick =", button)

        for step_id, value in [("default", "0.1"), ("ctrl", "0.5"), ("shift", "1")]:
            step = _blocks_for_token(
                scripted_guis,
                f"eu5ab_gui_priority_step_{step_id} = ",
            )[0]
            self.assertIn(f"name = eu5ab_priority_adjust_step value = {value}", step)

        for direction, operation in [("dec", "subtract"), ("inc", "add")]:
            action = _blocks_for_token(
                scripted_guis,
                f"eu5ab_gui_active_priority_{direction}_granary = ",
            )[0]
            self.assertIn(
                f"change_variable = {{ name = eu5ab_edit_priority_building_granary {operation} = var:eu5ab_priority_adjust_step }}",
                action,
            )
            self.assertIn(
                "clamp_variable = { name = eu5ab_edit_priority_building_granary min = 0 max = 10 }",
                action,
            )
            self.assertIn("remove_variable = eu5ab_priority_adjust_step", action)
            self.assertEqual(action.count("eu5ab_commit_active_template_editor = yes"), 1)

    def test_clear_current_list_matches_visible_category_age_and_special_rows(self):
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        clear = _blocks_for_token(
            scripted_guis,
            "eu5ab_gui_clear_visible_priorities = ",
        )[0]
        conditions = _blocks_for_token(clear, "\t\tif = ")

        laborer_age_two = next(
            block
            for block in conditions
            if "eu5ab_edit_priority_building_protected_harbor value = 0" in block
        )
        self.assertIn(
            "OR = { var:eu5ab_edit_building_filter = 0 var:eu5ab_edit_building_filter = 2 }",
            laborer_age_two,
        )
        self.assertIn(
            "OR = { var:eu5ab_edit_building_age = 0 var:eu5ab_edit_building_age = 2 }",
            laborer_age_two,
        )
        self.assertNotIn("any_owned_location", laborer_age_two)

        special_age_two = next(
            block
            for block in conditions
            if "eu5ab_edit_priority_building_bajang_ratu value = 0" in block
        )
        self.assertIn(
            "OR = { var:eu5ab_edit_building_filter = 0 var:eu5ab_edit_building_filter = 5 }",
            special_age_two,
        )
        self.assertIn(
            "OR = { var:eu5ab_edit_building_age = 0 var:eu5ab_edit_building_age = 2 }",
            special_age_two,
        )
        self.assertIn("any_owned_location = {", special_age_two)
        self.assertIn(
            "location_and_owner_can_build = { building_type = bajang_ratu }",
            special_age_two,
        )
        self.assertEqual(clear.count("eu5ab_commit_active_template_editor = yes"), 1)
        self.assertGreater(
            clear.rfind("eu5ab_commit_active_template_editor = yes"),
            clear.rfind("value = 0"),
        )

    def test_template_slot_display_expression_has_balanced_parentheses(self):
        expression = _slot_display_name_expr(1)
        self.assertEqual(expression.count("("), expression.count(")"))

    def test_generated_gui_and_or_calls_are_binary(self):
        gui = "\n".join(
            content
            for path, content in self.files.items()
            if path.suffix == ".gui"
        )
        for function in ["And", "Or"]:
            counts = _function_argument_counts(gui, function)
            self.assertTrue(counts, f"expected at least one {function} call")
            self.assertTrue(
                all(count == 2 for count in counts),
                f"{function} calls must be binary, got {counts}",
            )
        self.assertNotIn("Not([", gui)

    def test_template_price_band_is_explained_and_used(self):
        triggers = self.files[ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"]
        values = self.files[ROOT / "in_game" / "common" / "script_values" / "eu5ab_script_values.txt"]
        rules_gui = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"]
        localization = self.files[ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"]
        self.assertIn("eu5ab_global_price_min_ratio", triggers)
        self.assertIn("eu5ab_global_price_min_ratio", values)
        self.assertIn("market_price(goods:", triggers)
        self.assertIn("eu5ab_global_price_max_ratio", values)
        self.assertIn("market_price(goods:", values)
        self.assertNotIn("eu5ab_tpl_1_price_min", values)
        self.assertNotIn("eu5ab_tpl_1_price_max", values)
        granary_score = next(
            block
            for block in _blocks_for_token(values, "eu5ab_score_granary = ")
            if '"market_price(goods:wheat)"' in block
        )
        self.assertIn("multiply = eu5ab_global_price_max_ratio", granary_score)
        self.assertIn("add = 180", granary_score)
        self.assertNotIn("template EU5ABRulesHelp_eu5ab_price_section_title", rules_gui)
        self.assertNotIn('text = "eu5ab_price_section_desc"', rules_gui)
        self.assertIn("eu5ab_regional_development__price_min_name", localization)
        self.assertIn("eu5ab_regional_development__price_max_name", localization)
        self.assertIn("低于最低值时", localization)
        self.assertIn("高于最高值时", localization)
        self.assertNotIn("原产月度上限", localization)
        self.assertIn("不再设置额外权重或月度上限", localization)
        self.assertIn('eu5ab_rgo_section_title: "原产"', localization)
        self.assertIn("游戏原版自动化面板中的", localization)
        self.assertIn("自动扩建原产", localization)
        self.assertIn("不要同时开启两套自动化", localization)
        self.assertNotIn("RGO", localization)
        self.assertNotIn("ROG", localization)

    def test_candidate_diagnostics_store_and_render_each_location_name(self):
        effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        rules_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"
        ]
        localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        english = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]
        for rank in range(1, 4):
            self.assertIn(f"name = eu5ab_diag_top_{rank}_location", effects)
            self.assertIn(f"eu5ab_diag_top_{rank}_kind", effects)
            self.assertIn(f"eu5ab_diag_top_{rank}_priority", effects)
            self.assertIn(f'eu5ab_diag_candidate_{rank}_location_value', rules_gui)
            self.assertIn(f'eu5ab_diag_candidate_{rank}_rgo_scores_value', rules_gui)
            self.assertIn(
                f"GetVariable('eu5ab_diag_top_{rank}_location').GetLocation.GetName",
                localization,
            )
        self.assertNotIn("eu5ab_diag_candidate_location_value", rules_gui)
        self.assertNotIn("eu5ab_diag_top_locked", effects)
        self.assertNotIn("eu5ab_diag_top_location_score", effects)
        self.assertNotIn(
            "value = scope:eu5ab_candidate_location.var:eu5ab_worker_top_2_",
            effects,
        )
        self.assertNotRegex(
            effects,
            r"set_variable = \{ name = eu5ab_worker_top_[23]_",
        )
        self.assertIn("eu5ab_candidate_updates_worker_top", effects)
        self.assertIn(
            "name = eu5ab_candidate_diag_priority value = "
            "owner.var:eu5ab_candidate_priority_upgrade",
            effects,
        )
        self.assertIn(
            "name = eu5ab_candidate_diag_priority add = 4",
            effects,
        )
        self.assertIn(
            "var:eu5ab_diag_top_1_priority > { value = "
            "scope:eu5ab_candidate_location.var:eu5ab_worker_top_1_priority }",
            effects,
        )
        self.assertIn(
            "name = eu5ab_diag_top_3_location value = var:eu5ab_diag_top_2_location",
            effects,
        )
        self.assertIn("name = eu5ab_worker_top_1_kind value = 2", effects)
        self.assertIn(
            "name = eu5ab_worker_top_1_labor_jobs value = { "
            "value = eu5ab_rgo_jobs_per_expansion multiply = 1000 }",
            effects,
        )
        self.assertIn(
            "name = eu5ab_worker_top_1_labor_projected value = { "
            "value = eu5ab_rgo_projected_available_workers multiply = 1000 }",
            effects,
        )
        self.assertIn(
            "eu5ab_worker_top_1_priority > { value = "
            "var:eu5ab_rgo_diag_priority }",
            effects,
        )
        self.assertIn("eu5ab_diag_candidate_rgo_value", rules_gui)
        self.assertIn("eu5ab_diag_candidate_empty_value", rules_gui)
        self.assertIn("eu5ab_diag_top_1_kind", rules_gui)
        self.assertIn("空槽：没有候选项目", localization)
        self.assertIn("Empty slot: no candidate", english)
        self.assertIn("每个地点只保留", localization)
        self.assertIn("Candidates from distinct locations", english)
        self.assertIn("新增一级的劳动力预测不足", localization)
        self.assertIn("Next-Level Workforce Forecast Too Low", english)
        self.assertIn("1,000个岗位", localization)
        self.assertIn("1,000 jobs", english)
        self.assertIn('text = "eu5ab_diag_candidates_not_scanned_full"', rules_gui)
        self.assertIn("eu5ab_diag_concurrent_limit_state", rules_gui)
        self.assertIn("本轮同时建造名额已满，因此没有扫描新的候选项目", localization)
        self.assertIn("The concurrent construction limit was full", english)

    def test_rgo_diagnostics_help_has_matching_rules_tooltip_template(self):
        rules_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"
        ]

        self.assertIn(
            "template EU5ABRulesHelp_eu5ab_diag_rgo_title",
            rules_gui,
        )
        self.assertIn(
            "tooltipwidget = { using = EU5ABRulesHelp_eu5ab_diag_rgo_title }",
            rules_gui,
        )

    def test_quota_diagnostics_are_compacted_to_one_summary_row(self):
        rules_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"
        ]
        localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        self.assertEqual(
            rules_gui.count('text = "eu5ab_diag_label_capacity_summary"'),
            1,
        )
        self.assertIn('text = "eu5ab_diag_capacity_summary_value"', rules_gui)
        for removed_row in (
            "eu5ab_diag_label_base_quota",
            "eu5ab_diag_label_hard_cap_result",
            "eu5ab_diag_label_final_quota",
        ):
            self.assertNotIn(removed_row, rules_gui)
        self.assertNotIn('text = "eu5ab_diag_label_used_quota"', rules_gui)
        self.assertEqual(
            rules_gui.count('text = "eu5ab_diag_label_previous_month_added"'),
            1,
        )
        self.assertEqual(
            rules_gui.count('text = "eu5ab_diag_label_expected_this_run"'),
            1,
        )
        self.assertIn("在建 [GetPlayer.MakeScope.GetVariable", localization)
        self.assertIn("本轮最多新增", localization)
        self.assertIn("上个月新增", localization)
        self.assertIn("本轮预计新增", localization)

    def test_preset_allowlist_overrides_global_zero_priority(self):
        triggers = self.files[
            ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"
        ]
        values = self.files[
            ROOT / "in_game" / "common" / "script_values" / "eu5ab_script_values.txt"
        ]
        expected_core_buildings = {
            "eu5ab_naval_base_building_allowed": ("shipyard", "naval_base", "dry_dock"),
            "eu5ab_frontier_building_allowed": ("stockade", "castle"),
            "eu5ab_shipbuilding_building_allowed": ("shipyard", "dry_dock"),
            "eu5ab_luxury_goods_building_allowed": (
                "mercury_patio",
                "perfumery",
                "porcelain_manufactory",
            ),
        }
        for trigger_name, building_ids in expected_core_buildings.items():
            block = next(
                block
                for block in _blocks_for_token(triggers, f"{trigger_name} = ")
                if all(f"building_type:{building_id}" in block for building_id in building_ids)
            )
            self.assertTrue(block)

        naval_score = _blocks_for_token(values, "eu5ab_score_naval_base = ")[0]
        self.assertIn("limit = { this = building_type:shipyard }", naval_score)
        self.assertIn("add = 50", naval_score)

    def test_copy_preset_materializes_an_independent_player_template(self):
        effects = self.files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        scripted_guis = self.files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        triggers = self.files[
            ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"
        ]
        values = self.files[
            ROOT / "in_game" / "common" / "script_values" / "eu5ab_script_values.txt"
        ]
        main_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_automation_buildings_window.gui"
        ]
        rules_gui = self.files[
            ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"
        ]

        loader = next(
            block
            for block in _blocks_for_token(
                effects,
                "eu5ab_load_preset_naval_base_into_editor = ",
            )
            if "eu5ab_edit_priority_building_shipyard" in block
        )
        for expected in [
            "name = eu5ab_edit_name_selected value = 0",
            "name = eu5ab_edit_preset_origin value = 4",
            "name = eu5ab_edit_priority_building_shipyard value = 1",
            "name = eu5ab_edit_priority_building_lumber_mill value = 8",
        ]:
            self.assertIn(expected, loader)
        for removed_runtime_setting in (
            "eu5ab_edit_min_cash_reserve",
            "eu5ab_edit_price_min",
            "eu5ab_edit_price_max",
            "eu5ab_edit_annual_budget",
            "eu5ab_edit_budget_mode",
            "eu5ab_edit_budget_multiplier",
            "eu5ab_edit_auto_build_input_sources",
        ):
            self.assertNotIn(removed_runtime_setting, loader)

        copy_action = next(
            block
            for block in _blocks_for_token(
                scripted_guis,
                "eu5ab_gui_copy_preset_naval_base_to_player_template = ",
            )
            if "eu5ab_commit_template_editor_to_slot_1_and_refresh_budget" in block
        )
        self.assertIn("eu5ab_load_preset_naval_base_into_editor = yes", copy_action)
        self.assertIn(
            "eu5ab_commit_template_editor_to_slot_1_and_refresh_budget = yes",
            copy_action,
        )
        self.assertIn(
            "GetScriptedGui('eu5ab_gui_copy_preset_naval_base_to_player_template')",
            main_gui,
        )

        # Built-in preset sources are separate from the six player-facing name choices.
        self.assertIn("Localize('eu5ab_policy_naval_base')", main_gui)
        self.assertIn("eu5ab_tpl_1_preset_origin", main_gui)
        self.assertIn("eu5ab_gui_slot_1_name_custom", scripted_guis)
        self.assertNotIn("eu5ab_gui_slot_1_name_naval_base", scripted_guis)

        self.assertNotIn("eu5ab_edit_auto_build_input_sources", rules_gui)
        self.assertNotIn("eu5ab_tpl_1_auto_build_input_sources", triggers)
        self.assertIn("eu5ab_global_auto_build_input_sources", triggers)
        self.assertIn("eu5ab_template_slot_1_building_allowed = yes", triggers)
        self.assertIn("eu5ab_tpl_1_preset_origin", values)

        for gui_id, loader in [
            (
                "eu5ab_gui_new_blank_player_template",
                "eu5ab_load_blank_template_into_editor",
            ),
            (
                "eu5ab_gui_new_recommended_player_template",
                "eu5ab_load_recommended_template_into_editor",
            ),
            ("eu5ab_gui_new_player_template", "eu5ab_load_new_template_into_editor"),
        ]:
            new_template = _blocks_for_token(
                scripted_guis,
                f"{gui_id} = ",
            )[0]
            self.assertLess(
                new_template.index(f"{loader} = yes"),
                new_template.index(
                    "eu5ab_commit_template_editor_to_slot_1_and_refresh_budget = yes"
                ),
            )

    def test_failure_statistics_explain_the_monthly_reset_scope(self):
        localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        english = self.files[
            ROOT / "in_game" / "localization" / "english" / "eu5ab_l_english.yml"
        ]
        self.assertIn('eu5ab_diag_failure_title: "上次月度检查：失败统计"', localization)
        self.assertIn("仅显示上一次月度检查的结果", localization)
        self.assertIn("不会跨月累计", localization)
        self.assertNotIn("最近 5 年失败统计", localization)
        self.assertIn(
            'eu5ab_diag_failure_title: "Previous Monthly Check: Failures"',
            english,
        )
        self.assertIn("counts do not carry into later months", english)

    def test_native_input_tooltip_explains_the_player_facing_effect(self):
        localization = self.files[
            ROOT / "in_game" / "localization" / "simp_chinese" / "eu5ab_l_simp_chinese.yml"
        ]
        tooltip = next(
            line
            for line in localization.splitlines()
            if line.startswith(" eu5ab_native_input_priority_desc:")
        )
        self.assertIn("「本地」指建筑所在的省份", tooltip)
        self.assertIn("原料在配方中占比越高", tooltip)
        self.assertIn("0 表示不考虑本地原料", tooltip)
        self.assertIn("只改变备选建筑的排序", tooltip)
        self.assertIn("不比较原产等级或实际产量", tooltip)
        self.assertIn("原产本身不会获得这项加分", tooltip)
        for unclear_or_inaccurate_phrase in (
            "不是硬性命令",
            "代理估算",
            "原产越多，加分越高",
        ):
            self.assertNotIn(unclear_or_inaccurate_phrase, tooltip)

    def test_custom_goods_checks_do_not_expand_per_template_slot(self):
        triggers = self.files[ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"]
        values = self.files[ROOT / "in_game" / "common" / "script_values" / "eu5ab_script_values.txt"]
        self.assertGreater(triggers.count("eu5ab_global_price_min_ratio"), 1)
        self.assertLessEqual(
            triggers.count("eu5ab_global_price_min_ratio"),
            self.building_count,
        )
        self.assertNotIn("eu5ab_current_custom_rgo_priority", triggers)
        self.assertNotIn("eu5ab_tpl_1_price_min", triggers)
        self.assertNotIn("eu5ab_tpl_1_rgo_priority", triggers)
        self.assertEqual(values.count("eu5ab_tpl_1_price_min"), 0)
        self.assertEqual(values.count("eu5ab_tpl_1_rgo_priority"), 0)
        self.assertIn("eu5ab_global_price_min_ratio", values)
        self.assertNotIn("eu5ab_global_rgo_priority", values)
        self.assertLess(
            len(triggers.splitlines()),
            10000 + self.building_count * 800,
        )


    def test_candidate_goods_checks_use_static_catalog_and_rgo_effect_uses_1_3_syntax(self):
        effects = self.files[ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"]
        triggers = self.files[ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"]
        values = self.files[ROOT / "in_game" / "common" / "script_values" / "eu5ab_script_values.txt"]
        for invalid_trigger in (
            "building_goods_input",
            "building_produced_goods",
            "building_potential_profit",
        ):
            self.assertNotIn(invalid_trigger, triggers + values)
        self.assertIn("this = building_type:tools_workshop", triggers)
        self.assertIn("goods_supply_in_market(goods:iron)", triggers)
        self.assertNotIn("construct_rgo_upgrade = yes", effects)
        self.assertIn("construct_rgo_upgrade = { }", effects)

    def test_generated_gui_buttons_have_tooltips(self):
        for path, gui in self.files.items():
            if path.suffix != ".gui":
                continue
            for token in ["button_regular = ", "checkbutton_02_alt = ", "action_button = "]:
                for block in _blocks_for_token(gui, token):
                    with self.subTest(path=path.name, token=token):
                        self.assertTrue(
                            "tooltip =" in block or "tooltipwidget =" in block,
                            f"missing tooltip in {path.name}: {token}",
                        )

    def test_rules_layout_children_do_not_use_parent_anchors(self):
        rules = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"]
        scope = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_scope_window.gui"]
        self.assertNotIn("parentanchor = vcenter texture", rules)
        self.assertNotIn("parentanchor = vcenter", scope)

    def test_generated_size_regression_limits(self):
        buildings = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_buildings_window.gui"]
        values = self.files[ROOT / "in_game" / "common" / "script_values" / "eu5ab_script_values.txt"]
        triggers = self.files[ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"]
        rules = self.files[ROOT / "in_game" / "gui" / "eu5ab_template_rules_window.gui"]
        effects = self.files[ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"]
        scripted_guis = self.files[ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"]
        self.assertLess(
            len(buildings.encode("utf-8")), self.building_count * 5_000
        )
        self.assertLess(len(buildings.splitlines()), self.building_count * 120)
        self.assertLess(len(rules.encode("utf-8")), 250_000)
        self.assertLess(
            len(effects.encode("utf-8")), self.building_count * 19_000
        )
        self.assertLess(
            len(scripted_guis.encode("utf-8")), self.building_count * 3_200
        )
        self.assertLess(
            len(values.encode("utf-8")), self.building_count * 8_000
        )
        self.assertLess(
            len(triggers.encode("utf-8")), self.building_count * 9_000
        )
        self.assertLess(
            sum(len(text.encode("utf-8")) for text in (effects, values, triggers)),
            self.building_count * 28_000,
        )

    def test_optional_script_docs_smoke(self):
        docs = Path.home() / "Documents" / "Paradox Interactive" / "Europa Universalis V" / "docs"
        if not docs.exists():
            self.skipTest("EU5 script_docs not found on this machine")
        docs_text = "\n".join(path.read_text(errors="ignore") for path in docs.glob("*.log"))
        for token in ["construct_building", "monthly_country_pulse", "every_owned_location", "num_pop_type"]:
            self.assertIn(token, docs_text)


if __name__ == "__main__":
    unittest.main()
