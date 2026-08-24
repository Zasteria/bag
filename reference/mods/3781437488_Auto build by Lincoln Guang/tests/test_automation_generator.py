import json
from pathlib import Path
import unittest

from src.eu5autobuild.generator import generated_files
from src.eu5autobuild.policy import load_building_catalog, load_policies
from src.eu5autobuild.rules import load_automation_rules
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


class AutomationGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        policies = load_policies(ROOT / "policies" / "templates.json")
        cls.catalog = load_building_catalog(ROOT / "policies" / "building_catalog.json")
        cls.building_count = len(cls.catalog.buildings)
        rules = load_automation_rules(ROOT / "policies" / "automation_rules.json")
        cls.input_source_policy_ids = tuple(
            policy.id for policy in policies
            if policy.auto_build_input_sources
        )
        recipes, construction_demands, upgrades, workforce = cached_game_data()
        files = generated_files(
            policies,
            catalog=cls.catalog,
            rules=rules,
            recipes=recipes,
            construction_demands=construction_demands,
            upgrades=upgrades,
            workforce=workforce,
        )
        cls.policy_ids = tuple(policy.id for policy in policies)
        cls.effects = files[
            ROOT / "in_game" / "common" / "scripted_effects" / "eu5ab_scripted_effects.txt"
        ]
        cls.triggers = files[
            ROOT / "in_game" / "common" / "scripted_triggers" / "eu5ab_scripted_triggers.txt"
        ]
        cls.values = files[
            ROOT / "in_game" / "common" / "script_values" / "eu5ab_script_values.txt"
        ]
        cls.scripted_guis = files[
            ROOT / "in_game" / "common" / "scripted_guis" / "eu5ab_scripted_guis.txt"
        ]
        cls.engine_queue_gui = files[
            ROOT / "in_game" / "gui" / "eu5ab_engine_queue_window.gui"
        ]
        cls.construction_demands = json.loads(files[
            ROOT / ".metadata" / "eu5ab_construction_demands.json"
        ])

    def test_country_cadence_uses_cheap_first_pass_and_bounded_deep_scoring(self):
        self.assertNotIn("ordered_owned_location = {", self.effects)
        self.assertIn("order_by = eu5ab_location_need_score", self.effects)
        self.assertIn("eu5ab_scan_regional_development_bucket = {", self.effects)
        self.assertIn("eu5ab_finish_regional_development_scan = {", self.effects)
        self.assertEqual(self.effects.count("var:eu5ab_scan_bucket_day = "), 20)
        self.assertGreaterEqual(self.effects.count("max = 30"), 40)
        self.assertNotIn("var:eu5ab_scan_bucket =", self.effects)
        for bucket in range(1, 21):
            bucket_list = f"eu5ab_scan_bucket_{bucket}_locations"
            self.assertIn(f"add_to_variable_list = {{ name = {bucket_list}", self.effects)
            self.assertEqual(self.effects.count(f"variable = {bucket_list}"), 3)
            self.assertEqual(self.effects.count(f"clear_variable_list = {bucket_list}"), 1)
        self.assertIn(
            "eu5ab_deep_score_attempts < { value = var:eu5ab_deep_score_budget }",
            self.effects,
        )
        self.assertNotIn("max = { value = num_locations }", self.effects)
        self.assertIn("eu5ab_diag_covered_locations", self.effects)
        self.assertIn("eu5ab_diag_preliminary_passed", self.effects)
        self.assertIn("eu5ab_wait_months", self.effects)
        self.assertIn("eu5ab_monthly_build_quota", self.effects)
        self.assertIn(
            "eu5ab_constructions_started_this_tick < { value = var:eu5ab_monthly_build_quota }",
            self.effects,
        )
        self.assertIn("num_civil_constructions < 1", self.effects)
        self.assertIn("eu5ab_build_cooldown value = 3", self.effects)
        self.assertGreaterEqual(self.effects.count("check_range_bounds = no"), 42)

    def test_parallel_worker_is_location_local_and_serial_mode_reuses_it(self):
        worker = _blocks_for_token(
            self.effects, "\neu5ab_run_location_worker = "
        )[0]
        merge = _blocks_for_token(
            self.effects, "\neu5ab_merge_location_worker_results = "
        )[0]
        stage = _blocks_for_token(
            self.effects, "\neu5ab_stage_engine_candidate = "
        )[0]
        scan = _blocks_for_token(
            self.effects, "\neu5ab_scan_regional_development_bucket = "
        )[0]

        self.assertIn("eu5ab_try_construct_policy_candidate = yes", worker)
        self.assertNotIn("construct_building", worker)
        self.assertNotIn("construct_rgo_upgrade", worker)
        self.assertNotIn("eu5ab_global_budget_remaining", worker)
        self.assertNotIn("eu5ab_q_phase_", worker)
        self.assertIn(
            "set_variable = { name = eu5ab_worker_staged value = 0 }",
            worker,
        )
        for counter in (
            "eu5ab_diag_legal_candidates",
            "eu5ab_diag_fail_workforce",
            "eu5ab_diag_fail_inputs",
            "eu5ab_diag_fail_oversupply",
            "eu5ab_diag_fail_no_legal",
            "eu5ab_diag_rgo_checked",
            "eu5ab_diag_rgo_fail_capacity",
            "eu5ab_diag_rgo_fail_location",
            "eu5ab_diag_rgo_fail_disabled",
            "eu5ab_diag_rgo_fail_finance",
            "eu5ab_diag_rgo_fail_utilization",
            "eu5ab_diag_rgo_fail_market_need",
            "eu5ab_diag_rgo_eligible",
        ):
            initialization = (
                f"set_variable = {{ name = eu5ab_worker_{counter} value = 0 }}"
            )
            self.assertIn(initialization, worker)
            self.assertLess(
                worker.index(initialization),
                worker.index("eu5ab_try_construct_policy_candidate = yes"),
            )
        self.assertIn("has_variable = eu5ab_worker_active", stage)
        for phase in range(1, 9):
            self.assertIn(f"eu5ab_worker_phase_{phase}_types", stage)
            self.assertIn(f"eu5ab_q_phase_{phase}_types", merge)
        self.assertIn(
            "trigger_event_silently = { on_action = eu5ab_parallel_location_scan_on_action }",
            scan,
        )
        self.assertIn("else = { eu5ab_run_location_worker = yes }", scan)

    def test_persistent_scan_registry_is_incremental_and_not_monthly_rebuilt(self):
        register = _blocks_for_token(
            self.effects, "\neu5ab_register_location_for_scan = "
        )[0]
        unregister = _blocks_for_token(
            self.effects, "\neu5ab_unregister_location_from_scan = "
        )[0]
        rebuild = _blocks_for_token(
            self.effects, "\neu5ab_rebuild_scan_registry_v1 = "
        )[0]
        recovery = _blocks_for_token(
            self.effects, "\neu5ab_recover_runtime_after_load = "
        )[0]
        monthly = _blocks_for_token(
            self.effects, "\neu5ab_run_regional_development_policy = "
        )[0]
        finish = _blocks_for_token(
            self.effects, "\neu5ab_finish_regional_development_scan = "
        )[0]

        self.assertIn("eu5ab_scan_bucket_assignment add = 1", register)
        self.assertIn("eu5ab_scan_bucket value = owner.var:eu5ab_scan_bucket_assignment", register)
        self.assertIn("eu5ab_scan_registry_schema_version value = 1", register)
        self.assertIn("every_owned_location = {", rebuild)
        self.assertIn("limit = { has_variable = eu5ab_policy_id }", rebuild)
        self.assertIn("remove_variable = eu5ab_scan_bucket", rebuild)
        self.assertIn("eu5ab_register_location_for_scan = yes", rebuild)
        self.assertIn(
            "NOT = { has_variable = eu5ab_scan_registry_schema_version }",
            recovery,
        )
        self.assertIn("eu5ab_rebuild_scan_registry_v1 = yes", recovery)
        for bucket in range(1, 21):
            name = f"eu5ab_scan_bucket_{bucket}_locations"
            self.assertIn(name, register)
            self.assertIn(name, unregister)
            self.assertIn(f"clear_variable_list = {name}", rebuild)
            self.assertNotIn(f"clear_variable_list = {name}", monthly)
            self.assertNotIn(f"clear_variable_list = {name}", finish)
        self.assertNotIn("every_owned_location = {\n\t\tlimit = { has_variable = eu5ab_policy_id }", monthly)

    def test_performance_settings_are_snapshotted_and_bound_work(self):
        monthly = _blocks_for_token(
            self.effects, "\neu5ab_run_regional_development_policy = "
        )[0]
        scan = _blocks_for_token(
            self.effects, "\neu5ab_scan_regional_development_bucket = "
        )[0]
        for snapshot in (
            "eu5ab_scan_parallel",
            "eu5ab_scan_daily_task_limit",
            "eu5ab_scan_max_additions",
            "eu5ab_scan_early_stop",
        ):
            self.assertIn(snapshot, monthly)
        self.assertIn("eu5ab_scan_daily_task_limit min = 1 max = 30", monthly)
        self.assertIn("eu5ab_scan_max_additions min = 0 max = 600", monthly)
        self.assertIn("eu5ab_scan_candidate_target multiply = 2", monthly)
        self.assertIn("eu5ab_scan_candidate_reserve < { value = var:eu5ab_scan_candidate_target }", scan)
    def test_cooldown_is_initialized_and_never_read_while_unset(self):
        start = self.effects.index("eu5ab_run_regional_development_policy = {")
        end = self.effects.index("\n}\n", start) + 3
        run = self.effects[start:end]
        scan = _blocks_for_token(
            self.effects, "\neu5ab_scan_regional_development_bucket = "
        )[0]

        self.assertIn(
            "set_variable = { name = eu5ab_constructions_started_this_tick value = 0 }",
            run,
        )
        self.assertIn("limit = { has_variable = eu5ab_build_cooldown }", scan)
        self.assertIn("limit = { var:eu5ab_build_cooldown <= 0 }", scan)
        self.assertIn("remove_variable = eu5ab_build_cooldown", scan)
        self.assertIn("NOT = { has_variable = eu5ab_build_cooldown }", scan)
        self.assertNotIn(
            "OR = {\n\t\t\t\tNOT = { has_variable = eu5ab_build_cooldown }",
            scan,
        )

        start = self.triggers.index("eu5ab_rgo_location_available = {")
        end = self.triggers.index("\n}\n", start) + 3
        rgo_gate = self.triggers[start:end]
        self.assertIn("NOT = { has_variable = eu5ab_build_cooldown }", rgo_gate)
        self.assertNotIn("var:eu5ab_build_cooldown", rgo_gate)

    def test_active_projects_use_confirmed_location_index_and_old_saves_rebuild_it(self):
        monthly = _blocks_for_token(
            self.effects, "\neu5ab_run_regional_development_policy = "
        )[0]
        self.assertIn("variable = eu5ab_active_project_locations", monthly)
        self.assertNotIn(
            "# Count only the exact building types and RGO projects confirmed by this Mod.\n\tevery_owned_location",
            monthly,
        )
        confirm = _blocks_for_token(
            self.effects, "\neu5ab_confirm_engine_candidate = "
        )[0]
        rgo = _blocks_for_token(
            self.effects, "\neu5ab_try_construct_rgo_need = "
        )[0]
        for block in (confirm, rgo):
            self.assertIn("name = eu5ab_active_project_locations", block)

        migration = _blocks_for_token(
            self.effects, "\neu5ab_migrate_runtime_v2 = "
        )[0]
        recovery = _blocks_for_token(
            self.effects, "\neu5ab_recover_runtime_after_load = "
        )[0]
        self.assertIn("every_owned_location = {", migration)
        self.assertNotIn("remove_variable = eu5ab_scan_bucket", migration)
        self.assertIn("eu5ab_runtime_schema_version value = 2", migration)
        self.assertIn("eu5ab_clear_engine_candidate_queue = yes", recovery)
        self.assertIn("remove_variable = eu5ab_scan_active", recovery)

    def test_location_pre_score_uses_real_people_threshold_and_population_cap(self):
        workforce = _blocks_for_token(
            self.values, "\neu5ab_location_available_workforce_signal = "
        )[0]
        location_score = _blocks_for_token(
            self.values, "\neu5ab_location_need_score = "
        )[0]
        self.assertIn("unemployed_pops_of_pop_type_in_location", workforce)
        self.assertIn("eu5ab_location_available_workforce_signal >= 0.1", location_score)
        self.assertIn("value = population", location_score)
        self.assertIn("max = 60", location_score)
        self.assertNotIn("multiply = 0.0001", location_score)

    def test_all_buildable_iterators_use_an_explicit_candidate_location_scope(self):
        dispatch_adapters = (
            tuple(f"eu5ab_try_construct_{policy_id}" for policy_id in self.policy_ids)
            + tuple(
                f"eu5ab_try_construct_{policy_id}_input_source"
                for policy_id in self.input_source_policy_ids
            )
            + tuple(f"eu5ab_try_construct_template_slot_{slot}" for slot in range(1, 21))
        )
        self.assertEqual(len(dispatch_adapters), 42)
        for function_name in dispatch_adapters:
            with self.subTest(function_name=function_name):
                blocks = _blocks_for_token(self.effects, f"\n{function_name} = ")
                self.assertEqual(len(blocks), 1)
                self.assertRegex(
                    blocks[0],
                    r"eu5ab_try_construct_current_(policy|input_source) = yes",
                )

        staged_feature_names = (
            "eu5ab_stage_current_upgrade_candidates",
            "eu5ab_stage_current_expansion_candidates",
            "eu5ab_stage_current_new_candidates",
            "eu5ab_stage_current_input_upgrade_candidates",
            "eu5ab_stage_current_input_expansion_candidates",
            "eu5ab_stage_current_input_new_candidates",
        )
        self.assertEqual(self.effects.count("ordered_buildable_building_type = {"), 7)
        self.assertGreaterEqual(self.effects.count("save_scope_as = eu5ab_candidate_location"), 6)
        self.assertGreaterEqual(self.effects.count("save_scope_as = eu5ab_candidate_building"), 6)
        for function_name in staged_feature_names:
            with self.subTest(function_name=function_name):
                block = _blocks_for_token(self.effects, f"\n{function_name} = ")[0]
                saved_candidate = block.index("save_scope_as = eu5ab_candidate_location")
                owner_scope = block.index("\n\towner = {")
                iterator = block.index("ordered_buildable_building_type = {")
                saved_building = block.index("save_scope_as = eu5ab_candidate_building")
                self.assertLess(saved_candidate, owner_scope)
                self.assertLess(owner_scope, iterator)
                self.assertLess(iterator, saved_building)
                self.assertIn("max = 3", block)
                self.assertIn("eu5ab_candidate_location_can_build = yes", block)
                self.assertNotIn("position = 0", block)
                self.assertIn("eu5ab_try_construct_saved_building_type = yes", block)
                self.assertNotIn("location_and_owner_can_build =", block)
                self.assertNotIn("construct_building = {", block)
                self.assertNotIn("building_type = scope:eu5ab_candidate_building", block)
                self.assertNotIn("root = { location_and_owner_can_build", block)
                self.assertNotIn("root.owner", block)
                self.assertNotIn("root.var:eu5ab_candidate_cost", block)
                self.assertNotIn("building_type = prev", block)
                self.assertNotIn("prev.building_base_cost_in_gold", block)

        self.assertEqual(self.effects.count("eu5ab_try_construct_saved_building_type = yes"), 6)
        dispatcher_blocks = _blocks_for_token(
            self.effects, "\neu5ab_try_construct_saved_building_type = "
        )
        self.assertEqual(len(dispatcher_blocks), 1)
        dispatcher = dispatcher_blocks[0]
        self.assertIn(
            "scope:eu5ab_candidate_location = { eu5ab_stage_engine_candidate = yes }",
            dispatcher,
        )
        self.assertEqual(dispatcher.count("location_and_owner_can_build = {"), 0)
        self.assertNotIn("construct_building = {", dispatcher)
        self.assertNotIn("building_base_cost_in_gold", dispatcher)
        self.assertEqual(dispatcher.count("NOT = { has_variable = eu5ab_action_taken }"), 1)
        self.assertNotIn("building_type = scope:eu5ab_candidate_building", self.effects)

        can_build_blocks = _blocks_for_token(
            self.triggers, "\neu5ab_candidate_location_can_build = "
        )
        self.assertEqual(len(can_build_blocks), 1)
        can_build = can_build_blocks[0]
        self.assertEqual(
            can_build.count("scope:eu5ab_candidate_location = {"),
            self.building_count,
        )
        self.assertEqual(
            can_build.count("location_and_owner_can_build = {"),
            self.building_count,
        )
        self.assertEqual(can_build.count("this = building_type:"), self.building_count)

    def test_candidate_triggers_and_values_never_read_the_country_root_as_a_location(self):
        self.assertNotIn("root.", self.triggers)
        self.assertNotIn("root.", self.values)
        combined = self.triggers + self.values
        self.assertIn("scope:eu5ab_candidate_location.owner", combined)
        self.assertIn("scope:eu5ab_candidate_location.market", combined)
        self.assertIn(
            "scope:eu5ab_candidate_location.location_unemployed_population_for_building_type(building_type:granary)",
            combined,
        )
        self.assertIn(
            "scope:eu5ab_candidate_location.location_building_level(building_type:granary)",
            combined,
        )
        self.assertNotIn("location_unemployed_population_for_building_type(this)", combined)
        self.assertNotIn("location_building_level(this)", combined)
        self.assertNotIn("(scope:eu5ab_candidate_building)", combined)

    def test_all_templates_share_cmm_controlled_annual_budget(self):
        self.assertIn("current_month = 1", self.effects)
        self.assertIn("eu5ab_sync_cmm_settings = {", self.effects)
        self.assertIn(
            'variable_map(cmm|flag:eu5ab_regional_development__budget_mode)',
            self.effects,
        )
        self.assertIn(
            'variable_map(cmm|flag:eu5ab_regional_development__economic_metric)',
            self.effects,
        )
        self.assertIn("eu5ab_refresh_global_budget = {", self.effects)
        self.assertIn("value = monthly_income_total", self.effects)
        self.assertIn("multiply = 6", self.effects)
        self.assertIn(
            "name = eu5ab_global_budget_remaining value = var:eu5ab_global_budget_limit",
            self.effects,
        )
        self.assertIn(
            "change_variable = { name = eu5ab_global_budget_remaining subtract = scope:eu5ab_candidate_location.var:eu5ab_q_approved_cost }",
            self.effects,
        )
        self.assertNotIn("eu5ab_builtin_budget_remaining", self.effects)

    def test_custom_templates_do_not_store_runtime_rules(self):
        for suffix in (
            "min_cash_reserve",
            "price_min",
            "price_max",
            "annual_budget",
            "budget_mode",
            "budget_multiplier",
            "budget_limit",
            "budget_remaining",
            "rgo_priority",
            "rgo_min_utilization",
            "rgo_monthly_limit",
            "job_fill_deadline_months",
            "native_input_priority",
        ):
            self.assertNotIn(f"name = eu5ab_tpl_1_{suffix} value =", self.effects)
        self.assertIn("name = eu5ab_tpl_1_building_priorities", self.effects)
        self.assertNotIn("name = eu5ab_tpl_1_priority_building_", self.effects)

    def test_basic_needs_use_market_signals_without_building_scope_profit(self):
        for token in (
            "is_projected_to_run_out_of_food_stockpile",
            "market_food_percentage",
            "market_monthly_food_balance",
            "goods_supply_in_market(goods:",
            "goods_demand_in_market(goods:",
            "market_price(goods:",
        ):
            self.assertIn(token, self.values)
        self.assertNotIn("building_potential_profit", self.values)
        self.assertEqual(self.values.count("eu5ab_universal_need_score = {"), 1)
        self.assertEqual(
            self.values.count("\tadd = eu5ab_universal_need_score"),
            len(self.policy_ids) + 21,
        )
        self.assertIn("eu5ab_recipe_expected_output_value = {", self.values)
        self.assertIn("eu5ab_recipe_expected_input_cost = {", self.values)
        self.assertIn("eu5ab_recipe_expected_gross_margin = {", self.values)
        self.assertIn("eu5ab_recipe_economic_efficiency_score = {", self.values)

    def test_building_quality_score_is_bounded_below_need_signals(self):
        self.assertIn("limit = { this = building_type:granary }", self.values)
        self.assertIn("add = 500", self.values)
        self.assertIn("multiply = 50", self.values)
        self.assertLess(500, 6000)
        food_priority_start = self.triggers.index("eu5ab_food_priority_building_allowed = {")
        food_priority_end = self.triggers.index("eu5ab_food_priority_special_building_allowed = {")
        self.assertIn("building_type:fruit_orchard", self.triggers[food_priority_start:food_priority_end])

    def test_candidate_safety_gates_are_active(self):
        for token in (
            "eu5ab_has_local_workforce = yes",
            "eu5ab_inputs_available = yes",
            "eu5ab_output_not_oversupplied = yes",
            "eu5ab_candidate_location_can_build = yes",
        ):
            self.assertIn(token, self.effects)
        self.assertIn("location_unemployed_population_for_building_type", self.values)
        self.assertIn("num_civil_constructions < 1", self.effects)
        combined = self.triggers + self.values
        for invalid_trigger in (
            "building_goods_input",
            "building_produced_goods",
            "building_potential_profit",
        ):
            self.assertNotIn(invalid_trigger, combined)
        self.assertIn("this = building_type:tools_workshop", self.triggers)
        self.assertIn("goods_supply_in_market(goods:iron)", self.triggers)

    def test_no_market_location_skips_ordinary_candidates_but_keeps_rgo_route(self):
        router = _blocks_for_token(
            self.effects, "\neu5ab_try_construct_policy_candidate = "
        )[0]
        first_policy = router.index(
            f"eu5ab_try_construct_{self.policy_ids[0]} = yes"
        )
        first_policy_limit = router.rfind("\tif = {", 0, first_policy)
        self.assertIn(
            "market ?= { always = yes }",
            router[first_policy_limit:first_policy],
        )
        rgo = router.index("eu5ab_stage_rgo_candidate = yes")
        self.assertGreater(rgo, first_policy)
        self.assertNotIn(
            "market ?= { always = yes }",
            router[router.rfind("\tif = {", 0, rgo):rgo],
        )

    def test_workforce_runtime_converts_people_metadata_to_game_thousands(self):
        jobs = _blocks_for_token(
            self.values, "\neu5ab_candidate_jobs_per_level = "
        )[0]
        tools = _blocks_for_token(jobs, "\tif = ")
        tools = next(block for block in tools if "building_type:tools_workshop" in block)
        self.assertIn("add = 0.1", tools)

        rural = next(
            block
            for block in _blocks_for_token(jobs, "\tif = ")
            if "building_type:armory" in block
        )
        self.assertIn("add = 1", rural)

        net_jobs = _blocks_for_token(
            self.values, "\neu5ab_candidate_net_new_jobs = "
        )[0]
        paper = next(
            block
            for block in _blocks_for_token(net_jobs, "\tif = ")
            if "building_type:paper_mill" in block
        )
        self.assertIn("building_type:paper_manufactory", paper)
        self.assertIn("building_type:paper_workshop", paper)
        self.assertIn("subtract = 0.2", paper)
        self.assertIn("subtract = 0.1", paper)

        sufficient = _blocks_for_token(
            self.triggers, "\neu5ab_candidate_projected_workforce_sufficient = "
        )[0]
        self.assertIn("eu5ab_candidate_net_new_jobs <= 0", sufficient)
        self.assertIn(
            "eu5ab_candidate_projected_available_workers >= eu5ab_candidate_net_new_jobs",
            sufficient,
        )
        self.assertNotIn("building_type:granary", sufficient)
        self.assertIn("eu5ab_workforce_prediction_available = {\n\tvalue = 1", self.values)
        self.assertIn("eu5ab_location_combined_pop_promotion_speed = {", self.values)
        self.assertIn("modifier:local_pop_promotion_speed", self.values)
        self.assertIn("modifier:global_pop_promotion_speed", self.values)
        self.assertIn("eu5ab_candidate_promotion_source_pool = {", self.values)
        self.assertIn("max = eu5ab_candidate_promotion_source_pool", self.values)
        self.assertIn("multiply = eu5ab_current_job_fill_deadline_months", self.values)
        self.assertIn("value = 3 # 1 current, 2 fills inside horizon, 3 still short", self.values)
        self.assertIn("eu5ab_current_job_fill_deadline_months = {", self.values)
        self.assertIn("eu5ab_global_job_fill_deadline_months", self.values)
        self.assertNotIn("eu5ab_tpl_1_job_fill_deadline_months", self.values)

        rgo_jobs = _blocks_for_token(
            self.values, "\neu5ab_rgo_jobs_per_expansion = "
        )[0]
        self.assertIn("value = 1", rgo_jobs)
        rgo_current = _blocks_for_token(
            self.values, "\neu5ab_rgo_current_available_workers = "
        )[0]
        self.assertIn(
            "unemployed_pops_of_pop_type_in_location(pop_type:laborers)",
            rgo_current,
        )
        self.assertIn("modifier:allow_rgo_slave_demand = yes", rgo_current)
        self.assertIn(
            "unemployed_pops_of_pop_type_in_location(pop_type:slaves)",
            rgo_current,
        )
        rgo_projection = _blocks_for_token(
            self.values, "\neu5ab_rgo_projected_promotion = "
        )[0]
        self.assertIn("multiply = 1.5", rgo_projection)
        self.assertIn(
            "multiply = owner.var:eu5ab_global_job_fill_deadline_months",
            rgo_projection,
        )
        self.assertIn("max = eu5ab_rgo_promotion_source_pool", rgo_projection)

    def test_workforce_pause_is_a_gate_but_risk_score_always_remains(self):
        gate = _blocks_for_token(
            self.triggers, "\neu5ab_has_local_workforce = "
        )[0]
        self.assertIn("eu5ab_global_pause_low_workforce <= 0", gate)
        self.assertIn("eu5ab_candidate_projected_workforce_sufficient = yes", gate)
        self.assertNotIn("eu5ab_tpl_1_pause_low_workforce", gate)
        self.assertEqual(
            self.values.count("\tadd = eu5ab_labor_risk_penalty"),
            len(self.policy_ids) + 21,
        )
        stage = _blocks_for_token(
            self.effects, "\neu5ab_stage_current_upgrade_candidates = "
        )[0]
        iterator_limit = stage[: stage.index("save_scope_as = eu5ab_candidate_building")]
        self.assertIn("eu5ab_has_local_workforce = yes", iterator_limit)
        fallback = _blocks_for_token(
            self.effects, "\neu5ab_try_construct_current_policy = "
        )[0]
        self.assertIn("max = 1", fallback)
        self.assertIn("NOT = { eu5ab_candidate_projected_workforce_sufficient = yes }", fallback)
        self.assertIn("eu5ab_had_workforce_blocked_candidate", fallback)
        penalty = _blocks_for_token(
            self.values, "\neu5ab_labor_risk_penalty = "
        )[0]
        self.assertIn("eu5ab_global_pause_low_workforce <= 0", penalty)

        rgo_gate = _blocks_for_token(
            self.triggers, "\neu5ab_rgo_workforce_allowed = "
        )[0]
        self.assertIn("owner.var:eu5ab_global_pause_low_workforce <= 0", rgo_gate)
        self.assertIn("eu5ab_rgo_projected_workforce_sufficient = yes", rgo_gate)
        rgo_aggregate = _blocks_for_token(
            self.triggers, "\neu5ab_rgo_expansion_allowed = "
        )[0]
        self.assertIn("eu5ab_rgo_workforce_allowed = yes", rgo_aggregate)
        rgo_penalty = _blocks_for_token(
            self.values, "\neu5ab_rgo_labor_risk_penalty = "
        )[0]
        self.assertIn("owner.var:eu5ab_global_pause_low_workforce <= 0", rgo_penalty)
        self.assertIn("multiply = 1200", rgo_penalty)
        rgo_score = _blocks_for_token(
            self.values, "\neu5ab_rgo_candidate_score = "
        )[0]
        self.assertIn("add = eu5ab_rgo_labor_risk_penalty", rgo_score)

    def test_hidden_gui_bridges_actual_engine_values_and_confirms_queue_growth(self):
        for binding in (
            "GetBuildOrExpandBuildingCost",
            "GetBuildingTypeIncomeToOwnerInLocation",
            "GetBuildingTypeProfitInLocation",
            "CanBuildOrExpandBuilding",
            "BuildOrExpandBuildingDefault",
        ):
            self.assertIn(binding, self.engine_queue_gui)
        for state in (
            "eu5ab_q_validate_candidate",
            "eu5ab_q_probe_approved",
            "eu5ab_q_fire_build",
            "eu5ab_q_confirm_build",
        ):
            self.assertIn(state, self.engine_queue_gui)
        for callback in (
            "eu5ab_gui_queue_try_candidate",
            "eu5ab_gui_queue_sync_check",
            "eu5ab_gui_queue_confirm_candidate",
            "eu5ab_gui_queue_confirm_sync",
        ):
            self.assertIn(callback, self.scripted_guis)

        confirm = _blocks_for_token(
            self.effects, "\neu5ab_confirm_engine_candidate = "
        )[0]
        self.assertIn(
            "num_civil_constructions > var:eu5ab_q_queue_before",
            confirm,
        )
        self.assertIn("eu5ab_commit_engine_candidate_budget = yes", confirm)
        self.assertIn("eu5ab_release_engine_candidate_reservation = yes", confirm)
        self.assertNotIn("construct_building = {", self.effects)

        probe = _blocks_for_token(
            self.scripted_guis, "\neu5ab_gui_queue_probe_approved = "
        )[0]
        self.assertIn(
            "has_variable = eu5ab_q_active NOT = { has_variable = eu5ab_q_fire }",
            probe,
        )
        self.assertNotIn(
            "has_variable = eu5ab_q_active has_variable = eu5ab_q_fire",
            probe,
        )

    def test_actual_cost_controls_reservations_budget_cash_and_economic_gate(self):
        metric_gate = _blocks_for_token(
            self.triggers, "\neu5ab_engine_candidate_passes_selected_metric = "
        )[0]
        emergency = _blocks_for_token(
            self.triggers, "\neu5ab_engine_candidate_uses_emergency_override = "
        )[0]
        economic = _blocks_for_token(
            self.triggers, "\neu5ab_engine_candidate_economically_sound = "
        )[0]
        self.assertIn("scope:eu5ab_engine_cost > 0", economic)
        self.assertIn("scope:eu5ab_engine_income", metric_gate)
        self.assertIn("scope:eu5ab_engine_profit", metric_gate)
        self.assertIn("eu5ab_recipe_expected_output_value <= 0", economic)
        self.assertIn("eu5ab_engine_candidate_passes_selected_metric = yes", economic)
        self.assertIn("eu5ab_engine_candidate_uses_emergency_override = yes", economic)
        for metric in range(1, 5):
            self.assertIn(
                f"var:eu5ab_global_economic_metric = {metric}", metric_gate
            )
        self.assertEqual(metric_gate.count("multiply = 0.05"), 2)
        self.assertEqual(metric_gate.count("divide = 12"), 2)
        self.assertNotIn("eu5ab_universal_need_score", emergency + economic)

        for setting in (
            "emergency_food_exhaustion_override",
            "emergency_food_stockpile_override",
            "emergency_construction_goods_override",
            "emergency_wartime_military_override",
            "emergency_strategic_input_override",
        ):
            self.assertIn(f"eu5ab_global_{setting}", emergency)
        self.assertIn("is_projected_to_run_out_of_food_stockpile = yes", emergency)
        self.assertIn("market_food_percentage <= 0.25", emergency)
        self.assertIn("at_war = yes", emergency)
        self.assertIn("multiply = 0.65", emergency)
        self.assertIn("any_location_in_market = {", emergency)
        self.assertIn("any_buildings_in_location = {", emergency)
        self.assertIn("owner = scope:eu5ab_engine_country", emergency)
        self.assertIn("is_opened = yes", emergency)
        self.assertIn("is_lacking_goods = yes", emergency)

        budget = _blocks_for_token(
            self.triggers, "\neu5ab_engine_candidate_has_actual_budget = "
        )[0]
        self.assertIn("value = scope:eu5ab_engine_cost", budget)
        self.assertIn("add = var:eu5ab_q_planned_budget", budget)
        self.assertNotIn("eu5ab_q_planned_builtin_budget", budget)
        self.assertNotIn("eu5ab_q_planned_tpl_1", budget)

        cash = _blocks_for_token(
            self.triggers, "\neu5ab_engine_candidate_keeps_actual_cash_reserve = "
        )[0]
        self.assertIn("add = var:eu5ab_q_planned_spend", cash)
        self.assertIn(
            "add = scope:eu5ab_candidate_location.eu5ab_current_min_cash_reserve",
            cash,
        )

        approve = _blocks_for_token(
            self.effects, "\neu5ab_approve_engine_candidate = "
        )[0]
        self.assertIn("value = scope:eu5ab_engine_cost", approve)
        self.assertIn("eu5ab_reserve_engine_candidate = yes", approve)
        self.assertNotIn("budget_remaining subtract", approve)

        settle = _blocks_for_token(
            self.effects, "\neu5ab_commit_engine_candidate_budget = "
        )[0]
        self.assertIn(
            "subtract = scope:eu5ab_candidate_location.var:eu5ab_q_approved_cost",
            settle,
        )

    def test_construction_material_gate_uses_vanilla_mix_and_same_cycle_commitments(self):
        tools = next(
            item
            for item in self.construction_demands["buildings"]
            if item["building_id"] == "tools_workshop"
        )
        self.assertEqual(tools["demand_id"], "workshop_construction")
        self.assertEqual(tools["goods"]["masonry"], 1.0)

        masonry = _blocks_for_token(
            self.values, "\neu5ab_construction_demand_masonry = "
        )[0]
        self.assertIn("this = building_type:tools_workshop", masonry)
        self.assertIn("add = 1", masonry)
        self.assertIn("MARKET_CONSTRUCTION_NEEDS_BLOCK_FACTOR", self.values)
        self.assertIn("eu5ab_q_market_committed_masonry", self.values)

        gate = _blocks_for_token(
            self.triggers, "\neu5ab_engine_construction_materials_available = "
        )[0]
        self.assertIn("eu5ab_market_masonry_projected_construction_overage < 0", gate)
        self.assertIn('"market_price(goods:masonry)"', gate)
        self.assertIn('"default_price(goods:masonry)"', gate)
        self.assertIn("multiply = 1.5", gate)

        reserve = _blocks_for_token(
            self.effects, "\neu5ab_commit_candidate_construction_demand = "
        )[0]
        self.assertIn("eu5ab_q_market_committed_masonry", reserve)
        self.assertIn("change_local_variable", reserve)
        self.assertIn("eu5ab_reset_committed_construction_demand = yes", self.effects)

    def test_queue_coordinator_stages_validates_executes_and_recovers(self):
        monthly = _blocks_for_token(self.effects, "\neu5ab_run_regional_development_policy = ")[0]
        scan = _blocks_for_token(self.effects, "\neu5ab_scan_regional_development_bucket = ")[0]
        finish_scan = _blocks_for_token(self.effects, "\neu5ab_finish_regional_development_scan = ")[0]
        self.assertIn("eu5ab_prepare_engine_candidate_queue = yes", monthly)
        self.assertNotIn("ordered_owned_location = {", monthly)
        self.assertNotIn("ordered_owned_location = {", scan)
        self.assertIn("ordered_in_list = {", scan)
        self.assertIn("eu5ab_start_engine_candidate_queue = yes", finish_scan)
        self.assertLess(
            self.effects.index("eu5ab_prepare_engine_candidate_queue = yes"),
            self.effects.index("eu5ab_start_engine_candidate_queue = yes"),
        )

        stage = _blocks_for_token(
            self.effects, "\neu5ab_stage_engine_candidate = "
        )[0]
        for phase in range(1, 9):
            self.assertEqual(
                stage.count(
                    f"add_to_variable_list = {{ name = eu5ab_q_phase_{phase}_types"
                ),
                1,
            )
            self.assertIn(
                f"name = eu5ab_q_phase_{phase}_unsorted_locations",
                stage,
            )
        self.assertIn("set_variable = eu5ab_location_candidate_staged", stage)
        sort_regular = _blocks_for_token(
            self.effects, "\neu5ab_sort_candidate_queue = "
        )[0]
        self.assertIn("order_by = var:eu5ab_cached_location_need_score", sort_regular)
        self.assertIn("name = eu5ab_cached_location_need_score", self.effects)
        self.assertNotIn("GetList('eu5ab_q_locations')", self.engine_queue_gui)
        self.assertNotIn("GetList('eu5ab_q_building_types')", self.engine_queue_gui)
        for phase in range(1, 9):
            self.assertIn(
                f"GetList('eu5ab_q_phase_{phase}_locations')",
                self.engine_queue_gui,
            )
            self.assertIn(
                f"GetList('eu5ab_q_phase_{phase}_types')",
                self.engine_queue_gui,
            )
            self.assertEqual(
                self.engine_queue_gui.count(
                    f"GetList('eu5ab_q_phase_{phase}_types')"
                ),
                1,
            )

        validate = _blocks_for_token(
            self.scripted_guis, "\neu5ab_gui_queue_try_candidate = "
        )[0]
        self.assertIn("NOT = { has_variable = eu5ab_q_location_approved }", validate)
        self.assertIn("eu5ab_engine_candidate_economically_sound = yes", validate)
        self.assertIn("eu5ab_engine_construction_materials_available = yes", validate)
        self.assertIn("eu5ab_engine_candidate_uses_emergency_override = yes", validate)
        self.assertIn("set_variable = eu5ab_q_approved_emergency_override", validate)
        self.assertIn("eu5ab_approve_engine_candidate = yes", validate)
        self.assertIn("eu5ab_diag_engine_probes", validate)

        self.assertIn("eu5ab_q_stall_rounds >= 12", self.scripted_guis)
        self.assertIn("eu5ab_q_confirm_stall_rounds >= 12", self.scripted_guis)
        self.assertIn("eu5ab_diag_queue_recoveries", self.scripted_guis)
        for invalid_comparison in (
            "var:eu5ab_q_processed >= var:eu5ab_q_expected",
            "var:eu5ab_q_seen >= var:eu5ab_q_approved",
            "var:eu5ab_q_progress_now > var:eu5ab_q_progress_last",
            "var:eu5ab_q_confirmed >= var:eu5ab_q_approved",
        ):
            self.assertNotIn(invalid_comparison, self.scripted_guis)
        finish = _blocks_for_token(
            self.effects, "\neu5ab_finish_engine_candidate_queue = "
        )[0]
        self.assertIn("eu5ab_clear_engine_candidate_queue = yes", finish)
        self.assertIn("NOT = { var:eu5ab_diag_queue_state = 5 }", finish)
        self.assertIn("one frame late", finish)
        self.assertNotIn("remove_variable = eu5ab_q_phase", finish)
        self.assertNotIn("remove_variable = eu5ab_q_expected", finish)

    def test_empty_monthly_check_resets_stale_results_and_queue_display(self):
        monthly = _blocks_for_token(
            self.effects, "\neu5ab_run_regional_development_policy = "
        )[0]
        self.assertIn(
            "set_variable = { name = eu5ab_diag_quota_used value = 0 }",
            monthly,
        )
        self.assertIn(
            "set_variable = { name = eu5ab_diag_previous_month_added value = var:eu5ab_diag_quota_used }",
            monthly,
        )
        self.assertLess(
            monthly.index("name = eu5ab_diag_previous_month_added"),
            monthly.index("name = eu5ab_diag_quota_used value = 0"),
        )
        self.assertNotIn(
            "name = eu5ab_diag_previous_month_added value = 0",
            monthly,
        )
        self.assertIn("remove_variable = eu5ab_diag_queue_state", monthly)
        self.assertLess(
            monthly.index("eu5ab_prepare_engine_candidate_queue = yes"),
            monthly.index("remove_variable = eu5ab_diag_queue_state"),
        )

    def test_unsafe_settlement_lifecycle_building_is_not_a_candidate(self):
        self.assertNotIn("settlement_building", self.catalog.buildings)
        self.assertNotIn("building_type:settlement_building", self.effects)
        self.assertNotIn("building_type:settlement_building", self.triggers)

    def test_candidate_feature_order_uses_eight_exact_rank_phases(self):
        current_phase = _blocks_for_token(
            self.triggers,
            "\neu5ab_engine_candidate_in_current_priority_phase = ",
        )[0]
        rgo_phase = _blocks_for_token(
            self.triggers,
            "\neu5ab_rgo_in_current_priority_phase = ",
        )[0]

        for rank in range(1, 5):
            feature_rank = _blocks_for_token(
                self.triggers,
                f"\neu5ab_engine_candidate_feature_rank_{rank} = ",
            )[0]
            for classifier in (
                "eu5ab_candidate_is_upgrade",
                "eu5ab_candidate_is_new_build",
                "eu5ab_candidate_is_expansion",
            ):
                self.assertIn(f"{classifier} = yes", feature_rank)
            for feature in ("upgrade", "new", "expand"):
                self.assertIn(
                    f"eu5ab_candidate_priority_{feature} = {rank}",
                    feature_rank,
                )

            self.assertIn(
                f"eu5ab_q_phase = {rank} "
                "eu5ab_engine_candidate_is_food_emergency = yes "
                f"eu5ab_engine_candidate_feature_rank_{rank} = yes",
                current_phase,
            )
            self.assertIn(
                f"eu5ab_q_phase = {rank + 4} "
                "NOT = { eu5ab_engine_candidate_is_food_emergency = yes } "
                f"eu5ab_engine_candidate_feature_rank_{rank} = yes",
                current_phase,
            )
            self.assertIn(
                f"owner.var:eu5ab_q_phase = {rank} "
                f"owner.var:eu5ab_candidate_priority_rgo = {rank} "
                "eu5ab_rgo_food_emergency_enabled = yes",
                rgo_phase,
            )
            self.assertIn(
                f"owner.var:eu5ab_q_phase = {rank + 4} "
                f"owner.var:eu5ab_candidate_priority_rgo = {rank} "
                "NOT = { eu5ab_rgo_food_emergency_enabled = yes }",
                rgo_phase,
            )

        advance = _blocks_for_token(
            self.effects, "\neu5ab_advance_engine_priority_phase = "
        )[0]
        self.assertIn("var:eu5ab_q_phase < 8", advance)
        self.assertNotIn("feature_before_rgo", self.triggers)
        self.assertNotIn("feature_after_rgo", self.triggers)

    def test_feature_rank_is_exhausted_before_advancing_to_the_next_rank(self):
        confirm_sync = _blocks_for_token(
            self.scripted_guis, "\neu5ab_gui_queue_confirm_sync = "
        )[0]
        self.assertIn(
            "eu5ab_constructions_started_this_tick < { value = var:eu5ab_monthly_build_quota }",
            confirm_sync,
        )
        self.assertIn("eu5ab_restart_engine_priority_phase = yes", confirm_sync)
        self.assertIn("has_variable = eu5ab_q_retry_phase", confirm_sync)
        self.assertIn("eu5ab_advance_engine_priority_phase = yes", confirm_sync)

        restart = _blocks_for_token(
            self.effects, "\neu5ab_restart_engine_priority_phase = "
        )[0]
        clear_phase = _blocks_for_token(
            self.effects, "\neu5ab_clear_engine_priority_phase = "
        )[0]
        self.assertNotIn("clear_variable_list = eu5ab_q_failed_types", restart)
        self.assertIn("clear_variable_list = eu5ab_q_failed_types", clear_phase)

        confirm = _blocks_for_token(
            self.effects, "\neu5ab_confirm_engine_candidate = "
        )[0]
        self.assertIn("add_to_variable_list = { name = eu5ab_q_failed_types", confirm)
        self.assertIn("set_variable = eu5ab_q_retry_phase", confirm)
        validate = _blocks_for_token(
            self.scripted_guis, "\neu5ab_gui_queue_try_candidate = "
        )[0]
        self.assertIn("name = eu5ab_q_failed_types", validate)

        validation_sync = _blocks_for_token(
            self.scripted_guis, "\neu5ab_gui_queue_sync_check = "
        )[0]
        for queue_variable in (
            "eu5ab_q_active",
            "eu5ab_q_processed",
            "eu5ab_q_expected",
            "eu5ab_q_approved",
            "eu5ab_q_seen",
            "eu5ab_q_phase",
            "eu5ab_constructions_started_this_tick",
            "eu5ab_monthly_build_quota",
        ):
            self.assertIn(f"has_variable = {queue_variable}", validation_sync)
        self.assertIn("limit = { var:eu5ab_q_approved <= 0 }", validation_sync)
        self.assertIn("eu5ab_advance_engine_priority_phase = yes", validation_sync)
        for queue_variable in (
            "eu5ab_q_active",
            "eu5ab_q_confirmed",
            "eu5ab_q_approved",
            "eu5ab_q_confirm_stall_rounds",
            "eu5ab_constructions_started_this_tick",
            "eu5ab_monthly_build_quota",
        ):
            self.assertIn(f"has_variable = {queue_variable}", confirm_sync)

    def test_two_food_switches_feed_one_hard_emergency_layer(self):
        food_emergency = _blocks_for_token(
            self.triggers, "\neu5ab_food_emergency_enabled = "
        )[0]
        self.assertEqual(
            self.triggers.count("\neu5ab_food_emergency_enabled = {"), 1
        )
        self.assertEqual(
            food_emergency.count("eu5ab_global_emergency_food_exhaustion_override"),
            1,
        )
        self.assertEqual(
            food_emergency.count("eu5ab_global_emergency_food_stockpile_override"),
            1,
        )
        self.assertIn("is_projected_to_run_out_of_food_stockpile = yes", food_emergency)
        self.assertIn("market_food_percentage <= 0.25", food_emergency)

        ordinary_food = _blocks_for_token(
            self.triggers, "\neu5ab_engine_candidate_is_food_emergency = "
        )[0]
        rgo_food = _blocks_for_token(
            self.triggers, "\neu5ab_rgo_food_emergency_enabled = "
        )[0]
        self.assertIn("eu5ab_food_emergency_enabled = yes", ordinary_food)
        self.assertIn("eu5ab_candidate_produces_food = yes", ordinary_food)
        self.assertIn("eu5ab_food_emergency_enabled = yes", rgo_food)
        self.assertIn("raw_material = goods:", rgo_food)

    def test_native_input_proxy_is_weighted_bounded_and_not_used_for_rgo(self):
        coverage = _blocks_for_token(
            self.values, "\neu5ab_native_input_coverage_percent = "
        )[0]
        tools = next(
            block
            for block in _blocks_for_token(coverage, "\tif = ")
            if "building_type:tools_workshop" in block
        )
        self.assertIn("raw_material = goods:iron", tools)
        self.assertIn("add = 100", tools)
        foundry = next(
            block
            for block in _blocks_for_token(coverage, "\tif = ")
            if "building_type:iron_foundry" in block
        )
        self.assertIn("raw_material = goods:coal", foundry)
        self.assertIn("raw_material = goods:iron", foundry)
        self.assertIn("add = 20.0012", foundry)
        self.assertIn("add = 79.9988", foundry)
        self.assertIn("province = {", coverage)
        self.assertIn("any_location_in_province = {", coverage)

        fit = _blocks_for_token(
            self.values, "\neu5ab_native_input_fit_proxy_score = "
        )[0]
        self.assertIn("multiply = eu5ab_current_native_input_priority", fit)
        self.assertIn("divide = 10", fit)
        self.assertIn("market_access", fit)
        self.assertIn("local_control", fit)
        self.assertIn("eu5ab_native_input_shortage_factor", fit)
        self.assertIn("eu5ab_global_native_input_priority", self.values)
        self.assertNotIn("eu5ab_tpl_1_native_input_priority", self.values)
        self.assertEqual(
            self.values.count("\tadd = eu5ab_native_input_fit_proxy_score"),
            len(self.policy_ids) + 21,
        )
        exact_mentions = [
            line
            for line in self.values.splitlines()
            if "GetBuildingProductionEfficiency" in line
        ]
        self.assertTrue(exact_mentions)
        self.assertTrue(all(line.startswith("#") for line in exact_mentions))
        rgo_score = _blocks_for_token(
            self.values, "\neu5ab_rgo_candidate_score = "
        )[0]
        self.assertNotIn("eu5ab_native_input_fit", rgo_score)

    def test_candidate_diagnostics_expose_labor_and_native_input_details(self):
        for rank in range(1, 4):
            for suffix in (
                "labor_pop_type",
                "labor_jobs",
                "labor_current",
                "labor_source_types",
                "labor_deadline",
                "labor_prediction_available",
                "labor_result",
                "labor_penalty",
                "native_method",
                "native_coverage",
                "native_score",
            ):
                self.assertIn(f"eu5ab_diag_top_{rank}_{suffix}", self.effects)

    def test_only_latest_unlocked_replacement_is_scored_and_upgrades_are_preferred(self):
        self.assertEqual(
            self.effects.count("eu5ab_candidate_is_latest_unlocked = yes"),
            7,
        )
        latest = _blocks_for_token(
            self.triggers, "\neu5ab_candidate_is_latest_unlocked = "
        )[0]
        self.assertIn("this = building_type:tools_guild", latest)
        self.assertIn("can_build_building = building_type:tools_workshop", latest)
        self.assertIn("can_build_building = building_type:iron_foundry", latest)

        upgrade = _blocks_for_token(
            self.triggers, "\neu5ab_candidate_replaces_existing_building = "
        )[0]
        self.assertIn("this = building_type:paper_mill", upgrade)
        self.assertIn("building_type = building_type:paper_manufactory", upgrade)
        self.assertIn("building_type = building_type:paper_workshop", upgrade)
        self.assertIn("building_can_be_upgraded_by =", upgrade)

        self.assertIn(
            "limit = { eu5ab_candidate_replaces_existing_building = yes }",
            self.values,
        )
        self.assertIn(
            f"add = {load_automation_rules(ROOT / 'policies' / 'automation_rules.json').thresholds.upgrade_replacement_bonus}",
            self.values,
        )
        self.assertIn(
            "set_variable = { name = eu5ab_diag_last_build_kind value = 2 }",
            self.effects,
        )

    def test_shared_runtime_toggles_do_not_expand_per_template_slot(self):
        for global_variable in (
            "eu5ab_global_allow_special_buildings",
            "eu5ab_global_pause_low_workforce",
            "eu5ab_global_stop_input_shortage",
        ):
            self.assertIn(global_variable, self.triggers)
        for slot in range(1, 21):
            for suffix in (
                "allow_special_buildings",
                "pause_low_workforce",
                "stop_input_shortage",
            ):
                variable = f"eu5ab_tpl_{slot}_{suffix}"
                self.assertNotIn(variable, self.triggers)

    def test_input_shortage_has_a_real_upstream_recovery_pass(self):
        shared_input_source = _blocks_for_token(
            self.effects,
            "\neu5ab_try_construct_current_input_source = ",
        )[0]
        for feature in ("upgrade", "expansion", "new"):
            self.assertIn(
                f"eu5ab_stage_current_input_{feature}_candidates = yes",
                shared_input_source,
            )
            feature_block = _blocks_for_token(
                self.effects,
                f"\neu5ab_stage_current_input_{feature}_candidates = ",
            )[0]
            self.assertIn(
                "eu5ab_current_input_source_building_allowed = yes",
                feature_block,
            )
            self.assertIn("eu5ab_upstream_output_shortage = yes", feature_block)
        self.assertIn("eu5ab_current_policy_auto_builds_input_sources = yes", self.effects)
        self.assertIn("eu5ab_upstream_output_shortage = {", self.triggers)
        self.assertIn("goods_supply_in_market(goods:iron)", self.triggers)
        self.assertIn("market_price(goods:iron)", self.triggers)
        self.assertIn("add = 3200", self.values)

    def test_rgo_is_deferred_to_strict_feature_order_and_has_independent_quota(self):
        router = self.effects.index("eu5ab_try_construct_policy_candidate = {")
        policy_call = self.effects.index(f"eu5ab_try_construct_{self.policy_ids[0]} = yes", router)
        staged_rgo = self.effects.index("eu5ab_stage_rgo_candidate = yes", policy_call)
        self.assertGreater(staged_rgo, policy_call)
        self.assertNotIn("eu5ab_rgo_candidate_score >", self.effects)
        self.assertIn("eu5ab_q_phase value = 1", self.effects)
        self.assertIn("var:eu5ab_q_phase < 8", self.effects)
        self.assertIn("eu5ab_advance_engine_priority_phase = yes", self.scripted_guis)
        self.assertIn("eu5ab_gui_queue_try_rgo = {", self.scripted_guis)
        self.assertIn("eu5ab_q_validate_rgo", self.engine_queue_gui)
        self.assertIn("eu5ab_rgo_in_current_priority_phase = yes", self.scripted_guis)
        self.assertIn("eu5ab_rgo_started_this_tick", self.effects)
        self.assertIn("construct_rgo_upgrade = { }", self.effects)
        self.assertIn(
            "limit = { num_civil_constructions > var:eu5ab_queue_before_attempt }",
            self.effects,
        )
        rgo_utilization = _blocks_for_token(
            self.triggers, "\neu5ab_rgo_utilization_allowed = "
        )[0]
        self.assertIn("rgo_workers >= {", rgo_utilization)
        self.assertIn("value = eu5ab_rgo_current_capacity", rgo_utilization)
        self.assertNotIn("max_rgo_workers", rgo_utilization)
        self.assertIn("eu5ab_global_allow_rgo", self.triggers)
        self.assertNotIn("eu5ab_global_rgo_monthly_limit", self.triggers)
        self.assertNotIn("eu5ab_tpl_1_allow_rgo", self.triggers)
        self.assertNotIn("eu5ab_tpl_1_rgo_monthly_limit", self.triggers)
        stage_rgo = _blocks_for_token(
            self.effects, "\neu5ab_stage_rgo_candidate = "
        )[0]
        for phase in range(1, 9):
            self.assertEqual(
                stage_rgo.count(
                    f"add_to_variable_list = {{ name = eu5ab_q_phase_{phase}_rgo_unsorted_locations"
                ),
                1,
            )
            self.assertEqual(
                self.engine_queue_gui.count(
                    f"GetList('eu5ab_q_phase_{phase}_rgo_locations')"
                ),
                1,
            )
        rgo_order = _blocks_for_token(
            self.values, "\neu5ab_rgo_queue_order_score = "
        )[0]
        self.assertIn("value = eu5ab_location_need_score", rgo_order)
        self.assertIn("add = eu5ab_rgo_candidate_score", rgo_order)
        self.assertNotIn("eu5ab_global_rgo_priority", rgo_order)
        sort_rgo = _blocks_for_token(
            self.effects, "\neu5ab_sort_rgo_candidate_queue = "
        )[0]
        self.assertIn("ordered_in_list = {", sort_rgo)
        self.assertIn("order_by = var:eu5ab_cached_rgo_queue_score", sort_rgo)
        for phase in range(1, 9):
            self.assertIn(
                f"variable = eu5ab_q_phase_{phase}_rgo_unsorted_locations",
                sort_rgo,
            )
            self.assertIn(
                f"add_to_variable_list = {{ name = eu5ab_q_phase_{phase}_rgo_locations",
                sort_rgo,
            )
        self.assertIn(
            "set_variable = { name = eu5ab_cached_rgo_queue_score value = eu5ab_rgo_queue_order_score }",
            self.effects,
        )
        rgo_gate = _blocks_for_token(
            self.triggers, "\neu5ab_rgo_expansion_allowed = "
        )[0]
        for gate in (
            "capacity_available",
            "location_available",
            "enabled",
            "finance_available",
            "utilization_allowed",
            "market_need_present",
        ):
            self.assertIn(f"eu5ab_rgo_{gate} = yes", rgo_gate)
        self.assertNotIn("eu5ab_current_custom_rgo_priority > 0", rgo_gate)
        current_capacity = _blocks_for_token(
            self.values, "\neu5ab_rgo_current_capacity = "
        )[0]
        self.assertIn("value = rgo_level", current_capacity)
        self.assertIn("min = 1", current_capacity)
        utilization_ratio = _blocks_for_token(
            self.values, "\neu5ab_rgo_utilization_ratio = "
        )[0]
        self.assertIn("value = rgo_workers", utilization_ratio)
        self.assertIn("divide = eu5ab_rgo_current_capacity", utilization_ratio)
        self.assertNotIn("max_rgo_workers", utilization_ratio)
        rgo_score = _blocks_for_token(
            self.values, "\neu5ab_rgo_candidate_score = "
        )[0]
        self.assertIn("value = eu5ab_rgo_utilization_ratio", rgo_score)
        self.assertNotIn("divide = max_rgo_workers", rgo_score)
        reserve = _blocks_for_token(
            self.values, "\neu5ab_current_min_cash_reserve = "
        )[0]
        self.assertIn("owner.var:eu5ab_global_min_cash_reserve", reserve)
        self.assertNotIn("var:eu5ab_policy_id", reserve)
        self.assertNotIn("eu5ab_tpl_1_min_cash_reserve", reserve)
        rgo_cash = _blocks_for_token(
            self.values, "\neu5ab_rgo_cash_required = "
        )[0]
        self.assertIn("add = eu5ab_current_min_cash_reserve", rgo_cash)
        self.assertNotIn("add = var:eu5ab_min_cash_reserve", rgo_cash)

    def test_preset_location_settings_are_not_monthly_backfilled(self):
        monthly = _blocks_for_token(
            self.effects, "\neu5ab_run_regional_development_policy = "
        )[0]
        for variable in (
            "eu5ab_min_cash_reserve",
            "eu5ab_allow_special_buildings",
            "eu5ab_pause_low_workforce",
            "eu5ab_job_fill_deadline_months",
            "eu5ab_native_input_priority",
        ):
            self.assertNotIn(f"NOT = {{ has_variable = {variable} }}", monthly)
        self.assertNotIn(
            "add = scope:eu5ab_candidate_location.var:eu5ab_min_cash_reserve",
            self.values,
        )

    def test_diagnostics_and_independent_managers_are_generated(self):
        for token in (
            "eu5ab_diag_last_run_year",
            "eu5ab_diag_last_run_day",
            "eu5ab_diag_covered_locations",
            "eu5ab_diag_preliminary_passed",
            "eu5ab_diag_deep_scored",
            "eu5ab_diag_legal_candidates",
            "eu5ab_diag_top_1_score",
            "eu5ab_diag_top_2_score",
            "eu5ab_diag_top_3_score",
            "eu5ab_diag_fail_workforce",
            "eu5ab_diag_fail_inputs",
            "eu5ab_diag_fail_oversupply",
            "eu5ab_diag_fail_budget",
            "eu5ab_diag_fail_cash",
            "eu5ab_diag_fail_engine_economics",
            "eu5ab_diag_fail_construction_materials",
            "eu5ab_diag_fail_vanilla",
            "eu5ab_diag_fail_no_legal",
            "eu5ab_diag_run_state",
            "eu5ab_diag_active_mod_projects",
            "eu5ab_diag_concurrent_limit_state",
            "eu5ab_diag_built_this_run",
            "eu5ab_diag_has_run",
            "eu5ab_diag_base_quota",
            "eu5ab_diag_hard_cap_result",
            "eu5ab_diag_final_quota",
            "eu5ab_diag_rgo_quota_used",
            "eu5ab_diag_workforce_prediction_mode",
            "eu5ab_diag_queue_state",
            "eu5ab_diag_queue_recoveries",
            "eu5ab_diag_emergency_overrides_used",
            "eu5ab_diag_rgo_checked",
            "eu5ab_diag_rgo_fail_capacity",
            "eu5ab_diag_rgo_fail_location",
            "eu5ab_diag_rgo_fail_disabled",
            "eu5ab_diag_rgo_fail_finance",
            "eu5ab_diag_rgo_fail_utilization",
            "eu5ab_diag_rgo_fail_workforce",
            "eu5ab_diag_rgo_fail_market_need",
            "eu5ab_diag_rgo_eligible",
        ):
            self.assertIn(token, self.effects)
        router = _blocks_for_token(
            self.effects, "\neu5ab_try_construct_policy_candidate = "
        )[0]
        self.assertIn(
            "change_variable = { name = eu5ab_worker_eu5ab_diag_rgo_checked add = 1 }",
            router,
        )
        for result in (
            "fail_capacity",
            "fail_location",
            "fail_disabled",
            "fail_finance",
            "fail_utilization",
            "fail_workforce",
            "fail_market_need",
            "eligible",
        ):
            self.assertEqual(
                router.count(
                    f"change_variable = {{ name = eu5ab_worker_eu5ab_diag_rgo_{result} add = 1 }}"
                ),
                1,
            )
        self.assertEqual(router.count("eu5ab_stage_rgo_candidate = yes"), 1)
        self.assertNotIn("eu5ab_run_town_rights_manager", self.effects)
        self.assertNotIn("eu5ab_run_production_method_manager", self.effects)
        self.assertNotIn("eu5ab_pm_switch_cooldown", self.effects)
        self.assertNotIn("eu5ab_town_rights_cooldown", self.effects)
        self.assertNotIn("eu5ab_town_rights_grants_this_year", self.effects)
        self.assertNotIn("eu5ab_diag_top_locked", self.effects)
        self.assertNotIn("eu5ab_diag_top_location_score", self.effects)
        self.assertIn(
            "has_variable = eu5ab_worker_top_1_kind "
            "has_variable = eu5ab_worker_top_1_priority",
            self.effects,
        )
        self.assertIn(
            "name = eu5ab_diag_top_3_location value = var:eu5ab_diag_top_2_location",
            self.effects,
        )
        self.assertIn(
            "scope:eu5ab_candidate_location = { NOT = { has_variable = eu5ab_action_taken } }",
            self.effects,
        )
        self.assertNotIn("eu5ab_diag_pm_api_available", self.effects)
        self.assertNotIn("set_production_method =", self.effects)
        self.assertIn(
            "limit = { var:eu5ab_diag_run_state = 0 var:eu5ab_diag_covered_locations <= 0 }",
            self.effects,
        )
        self.assertNotIn("eu5ab_active_construction", self.effects)
        self.assertIn("has_variable_list = eu5ab_active_building_types", self.effects)
        self.assertIn("eu5ab_active_building_baselines", self.effects)
        self.assertIn("location_building_level(scope:eu5ab_active_project_building_type)", self.effects)
        self.assertIn("building_levels_under_construction > 0", self.effects)
        self.assertIn("set_variable = eu5ab_active_rgo_construction", self.effects)
        self.assertIn("eu5ab_active_rgo_baseline_workers", self.effects)
        self.assertIn("eu5ab_rgos_under_construction > 0", self.effects)
        self.assertIn(
            "change_variable = { name = eu5ab_monthly_build_quota add = 1 }",
            self.effects,
        )
        self.assertIn(
            "change_variable = { name = eu5ab_monthly_build_quota subtract = var:eu5ab_diag_active_mod_projects }",
            self.effects,
        )
        self.assertIn(
            "limit = { var:eu5ab_diag_active_mod_projects >= { value = var:eu5ab_diag_base_quota } }",
            self.effects,
        )
        self.assertIn(
            "set_variable = { name = eu5ab_diag_concurrent_limit_state value = 1 }",
            self.effects,
        )
        self.assertIn(
            "set_variable = { name = eu5ab_diag_workforce_prediction_mode value = 1 }",
            self.effects,
        )
        self.assertIn(
            "set_variable = { name = eu5ab_diag_last_run_day value = 22 }",
            self.effects,
        )
        self.assertIn(
            "set_variable = { name = eu5ab_diag_final_quota value = var:eu5ab_monthly_build_quota }",
            self.effects,
        )
        self.assertIn(
            "change_variable = { name = eu5ab_deep_score_budget multiply = 8 }",
            self.effects,
        )
        self.assertIn("max = 600", self.effects)
        self.assertNotIn("var:eu5ab_diag_covered_locations > 50", self.effects)
        self.assertNotIn("var:eu5ab_diag_covered_locations > 200", self.effects)
        self.assertNotIn("var:eu5ab_diag_covered_locations > 500", self.effects)
        self.assertNotIn("eu5ab_diag_queue_throttled", self.effects)
        self.assertIn(
            "change_variable = { name = eu5ab_diag_fail_vanilla add = 1 }",
            self.scripted_guis,
        )
        self.assertIn(
            "change_variable = { name = eu5ab_diag_emergency_overrides_used add = 1 }",
            self.effects,
        )
        confirm = _blocks_for_token(
            self.effects, "\neu5ab_confirm_engine_candidate = "
        )[0]
        self.assertLess(
            confirm.index("num_civil_constructions > var:eu5ab_q_queue_before"),
            confirm.index("eu5ab_diag_emergency_overrides_used"),
        )
        for snapshot_default in [
            "set_variable = { name = eu5ab_diag_run_state value = 5 }",
            "set_variable = { name = eu5ab_diag_concurrent_limit_state value = 2 }",
            "set_variable = { name = eu5ab_diag_built_this_run value = 2 }",
            "set_variable = { name = eu5ab_worker_top_1_reason value = 8 }",
            "set_variable = { name = eu5ab_diag_last_build_kind value = 3 }",
        ]:
            self.assertIn(snapshot_default, self.effects)

    def test_failure_diagnostics_are_cleared_for_each_monthly_check(self):
        monthly = _blocks_for_token(
            self.effects, "\neu5ab_run_regional_development_policy = "
        )[0]
        for key in (
            "workforce",
            "inputs",
            "oversupply",
            "budget",
            "cash",
            "engine_economics",
            "construction_materials",
            "vanilla",
            "no_legal",
        ):
            self.assertIn(
                f"set_variable = {{ name = eu5ab_diag_fail_{key} value = 0 }}",
                monthly,
            )
        self.assertNotIn("eu5ab_diag_failure_window", self.effects)
        self.assertNotIn("eu5ab_record_failure_", self.effects)


if __name__ == "__main__":
    unittest.main()
