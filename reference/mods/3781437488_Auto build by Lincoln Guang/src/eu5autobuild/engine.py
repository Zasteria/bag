"""Pure Python decision engine for the bounded EU5AB regional economy loop."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
import math
from typing import Callable

from .policy import BuildingCatalog, Policy
from .rules import AutomationRules, WORKFORCE_FORECAST_MAX_MONTHS


class PauseReason(StrEnum):
    NONE = "none"
    BANNED_BUILDING = "banned_building"
    NOT_ALLOWED = "not_allowed"
    NOT_UNLOCKED = "not_unlocked"
    SUPERSEDED_BUILDING = "superseded_building"
    PRIORITY_DISABLED = "priority_disabled"
    LABOR_SHORTAGE = "labor_shortage"
    INPUT_SHORTAGE = "input_shortage"
    POPULATION_SHORTAGE = "population_shortage"
    SPECIAL_BUILDING_DISABLED = "special_building_disabled"
    CASH_RESERVE = "cash_reserve"
    PRICE_OUT_OF_RANGE = "price_out_of_range"
    BUDGET_EXHAUSTED = "budget_exhausted"
    CONSTRUCTION_QUEUE = "construction_queue"
    COOLDOWN = "cooldown"
    FAILURE_COOLDOWN = "failure_cooldown"
    RGO_DISABLED = "rgo_disabled"
    RGO_UTILIZATION = "rgo_utilization"
    RGO_QUOTA = "rgo_quota"
    VANILLA_REJECTED = "vanilla_rejected"
    NO_CANDIDATE = "no_candidate"


class WorkforceState(StrEnum):
    CURRENT_SUFFICIENT = "current_sufficient"
    WITHIN_DEADLINE = "within_deadline"
    BEYOND_DEADLINE = "beyond_deadline"
    NO_PROMOTION_PATH = "no_promotion_path"
    ZERO_PROMOTION_RATE = "zero_promotion_rate"
    TARGET_CAP = "target_cap"
    PREDICTION_UNAVAILABLE = "prediction_unavailable"


@dataclass(frozen=True)
class WorkforceRequirement:
    pop_type: str
    current_unfilled_jobs: float = 0.0
    new_jobs: float = 0.0
    queued_reserved_jobs: float = 0.0
    immediately_employable: float = 0.0
    promotion_capacity: float | None = None

    @property
    def demand(self) -> float:
        return max(
            0.0,
            self.current_unfilled_jobs + self.new_jobs + self.queued_reserved_jobs,
        )

    @property
    def gap(self) -> float:
        return max(0.0, self.demand - self.immediately_employable)


@dataclass(frozen=True)
class PromotionSource:
    id: str
    pop_type: str
    population: float
    monthly_amount: float
    promote_to: tuple[str, ...]


@dataclass(frozen=True)
class WorkforceAssessment:
    state: WorkforceState
    deadline_months: int
    months_to_fill: int | None
    total_demand: float
    total_gap: float
    slowest_pop_type: str | None
    source_population: float
    monthly_promotion: float
    reliable: bool

    @property
    def within_deadline(self) -> bool:
        return self.state in {
            WorkforceState.CURRENT_SUFFICIENT,
            WorkforceState.WITHIN_DEADLINE,
        }


class NativeInputMethod(StrEnum):
    NONE = "none"
    PROXY = "proxy"
    EXACT = "exact"


@dataclass(frozen=True)
class NativeInputAssessment:
    method: NativeInputMethod
    score: int
    coverage: float
    matched_inputs: tuple[str, ...]
    total_raw_input: float
    shortage_factor: float
    output_factor: float
    utilization_factor: float
    access_factor: float
    control_factor: float


def _promotion_flow(
    requirements: tuple[WorkforceRequirement, ...],
    sources: tuple[PromotionSource, ...],
    months: int,
) -> float:
    """Return a bounded bipartite max-flow without double-counting sources."""

    gaps: dict[str, float] = {}
    for requirement in requirements:
        gaps[requirement.pop_type] = gaps.get(requirement.pop_type, 0.0) + requirement.gap
    active_targets = tuple(sorted(pop_type for pop_type, gap in gaps.items() if gap > 0))
    active_sources = tuple(
        source
        for source in sources
        if source.population > 0
        and source.monthly_amount > 0
        and set(source.promote_to) & set(active_targets)
    )
    source_nodes = tuple(f"source:{index}" for index in range(len(active_sources)))
    graph: dict[str, dict[str, float]] = {}

    def add_edge(start: str, end: str, capacity: float) -> None:
        graph.setdefault(start, {})[end] = max(0.0, capacity)
        graph.setdefault(end, {}).setdefault(start, 0.0)

    for index, source in enumerate(active_sources):
        source_node = source_nodes[index]
        capacity = min(source.population, source.monthly_amount * months)
        add_edge("start", source_node, capacity)
        for target in active_targets:
            if target in source.promote_to:
                add_edge(source_node, f"target:{target}", capacity)
    for target in active_targets:
        add_edge(f"target:{target}", "end", gaps[target])

    total = 0.0
    epsilon = 1e-9
    while True:
        parents: dict[str, str | None] = {"start": None}
        queue: deque[str] = deque(["start"])
        while queue and "end" not in parents:
            current = queue.popleft()
            for neighbor, capacity in graph.get(current, {}).items():
                if capacity > epsilon and neighbor not in parents:
                    parents[neighbor] = current
                    queue.append(neighbor)
        if "end" not in parents:
            break
        amount = float("inf")
        current = "end"
        while parents[current] is not None:
            previous = parents[current]
            amount = min(amount, graph[previous][current])
            current = previous
        current = "end"
        while parents[current] is not None:
            previous = parents[current]
            graph[previous][current] -= amount
            graph[current][previous] += amount
            current = previous
        total += amount
    return total


def assess_workforce(
    requirements: tuple[WorkforceRequirement, ...],
    sources: tuple[PromotionSource, ...],
    deadline_months: int,
    *,
    prediction_reliable: bool = True,
    diagnostic_horizon_months: int = 120,
) -> WorkforceAssessment:
    """Classify current, forecast-fillable, and unsafe workforce states.

    Only direct vanilla promote_to edges supplied by callers are considered.
    Source capacity is shared through max-flow, so one source population cannot
    be counted once for every requested target class.
    """

    if not isinstance(deadline_months, int) or isinstance(deadline_months, bool):
        raise ValueError("Workforce fill deadline must be an integer")
    if not 0 <= deadline_months <= WORKFORCE_FORECAST_MAX_MONTHS:
        raise ValueError(
            "Workforce fill deadline must be between 0 and "
            f"{WORKFORCE_FORECAST_MAX_MONTHS} months"
        )
    if not isinstance(diagnostic_horizon_months, int) or isinstance(
        diagnostic_horizon_months, bool
    ):
        raise ValueError("Diagnostic workforce horizon must be an integer")
    if diagnostic_horizon_months < deadline_months:
        raise ValueError("Diagnostic workforce horizon cannot be below the deadline")
    if any(
        not math.isfinite(value)
        for requirement in requirements
        for value in (
            requirement.current_unfilled_jobs,
            requirement.new_jobs,
            requirement.queued_reserved_jobs,
            requirement.immediately_employable,
        )
    ):
        raise ValueError("Workforce requirements must contain finite populations")
    if any(
        value < 0
        for requirement in requirements
        for value in (
            requirement.current_unfilled_jobs,
            requirement.new_jobs,
            requirement.queued_reserved_jobs,
            requirement.immediately_employable,
        )
    ):
        raise ValueError("Workforce requirements cannot contain negative populations")
    if any(
        requirement.promotion_capacity is not None
        and not math.isfinite(requirement.promotion_capacity)
        for requirement in requirements
    ):
        raise ValueError("Workforce promotion capacity must be finite")
    if any(
        requirement.promotion_capacity is not None
        and requirement.promotion_capacity < 0
        for requirement in requirements
    ):
        raise ValueError("Workforce promotion capacity cannot be negative")
    if any(
        not math.isfinite(source.population) or not math.isfinite(source.monthly_amount)
        for source in sources
    ):
        raise ValueError("Promotion sources must contain finite populations and rates")
    if any(source.population < 0 or source.monthly_amount < 0 for source in sources):
        raise ValueError("Promotion sources cannot contain negative populations or rates")

    total_demand = sum(requirement.demand for requirement in requirements)
    total_gap = sum(requirement.gap for requirement in requirements)
    eligible_sources = tuple(
        source
        for source in sources
        if any(
            requirement.gap > 0 and requirement.pop_type in source.promote_to
            for requirement in requirements
        )
    )
    source_population = sum(source.population for source in eligible_sources)
    monthly_promotion = sum(source.monthly_amount for source in eligible_sources)
    slowest_pop_type = None
    positive_requirements = tuple(
        requirement for requirement in requirements if requirement.gap > 0
    )
    if positive_requirements:
        def target_month_ratio(requirement: WorkforceRequirement) -> float:
            rate = sum(
                source.monthly_amount
                for source in eligible_sources
                if requirement.pop_type in source.promote_to
            )
            return float("inf") if rate <= 0 else requirement.gap / rate

        slowest_pop_type = max(
            positive_requirements,
            key=lambda requirement: (
                target_month_ratio(requirement),
                requirement.pop_type,
            ),
        ).pop_type

    def result(
        state: WorkforceState,
        months_to_fill: int | None,
        reliable: bool,
    ) -> WorkforceAssessment:
        return WorkforceAssessment(
            state=state,
            deadline_months=deadline_months,
            months_to_fill=months_to_fill,
            total_demand=total_demand,
            total_gap=total_gap,
            slowest_pop_type=slowest_pop_type,
            source_population=source_population,
            monthly_promotion=monthly_promotion,
            reliable=reliable,
        )

    if total_gap <= 1e-9:
        return result(WorkforceState.CURRENT_SUFFICIENT, 0, True)
    if not prediction_reliable:
        return result(WorkforceState.PREDICTION_UNAVAILABLE, None, False)
    if any(
        requirement.promotion_capacity is not None
        and requirement.promotion_capacity + 1e-9 < requirement.gap
        for requirement in positive_requirements
    ):
        return result(WorkforceState.TARGET_CAP, None, True)
    if any(
        not any(
            source.population > 0 and requirement.pop_type in source.promote_to
            for source in sources
        )
        for requirement in positive_requirements
    ):
        return result(WorkforceState.NO_PROMOTION_PATH, None, True)
    if any(
        not any(
            source.population > 0
            and source.monthly_amount > 0
            and requirement.pop_type in source.promote_to
            for source in sources
        )
        for requirement in positive_requirements
    ):
        return result(WorkforceState.ZERO_PROMOTION_RATE, None, True)

    earliest = next(
        (
            months
            for months in range(1, diagnostic_horizon_months + 1)
            if _promotion_flow(requirements, sources, months) + 1e-9 >= total_gap
        ),
        None,
    )
    if earliest is not None and earliest <= deadline_months:
        return result(WorkforceState.WITHIN_DEADLINE, earliest, True)
    return result(WorkforceState.BEYOND_DEADLINE, earliest, True)


def workforce_risk_penalty(
    assessment: WorkforceAssessment,
    *,
    max_penalty: int,
    strategic_relief: float = 1.0,
) -> int:
    if max_penalty < 0:
        raise ValueError("Maximum workforce penalty cannot be negative")
    if not 0 < strategic_relief <= 1:
        raise ValueError("Strategic workforce relief must be in (0, 1]")
    if assessment.state is WorkforceState.CURRENT_SUFFICIENT:
        return 0
    if assessment.state is not WorkforceState.WITHIN_DEADLINE:
        return -max_penalty
    demand_fraction = min(
        1.0,
        assessment.total_gap / max(assessment.total_demand, 1.0),
    )
    time_fraction = min(
        1.0,
        (assessment.months_to_fill or assessment.deadline_months)
        / max(assessment.deadline_months, 1),
    )
    return -round(max_penalty * demand_fraction * time_fraction * strategic_relief)


def assess_native_input_fit(
    input_quantities: dict[str, float],
    raw_input_goods: frozenset[str],
    province_raw_goods: frozenset[str],
    *,
    priority: int,
    max_bonus: int,
    shortage_goods: frozenset[str] = frozenset(),
    output_ratio: float = 1.0,
    raw_input_utilization: float = 0.0,
    market_access: float = 1.0,
    control: float = 1.0,
    exact_vanilla_coverage: float | None = None,
    is_rgo: bool = False,
    shortage_discount: float = 0.5,
    high_utilization_discount: float = 0.5,
    low_output_floor: float = 0.25,
    access_control_floor: float = 0.5,
) -> NativeInputAssessment:
    """Return one bounded PM-dependent native-input score.

    exact_vanilla_coverage, when available, replaces the proxy rather than being
    added to it. This prevents double-counting the same vanilla efficiency.
    """

    if not isinstance(priority, int) or isinstance(priority, bool):
        raise ValueError("Native-input priority must be an integer")
    if not 0 <= priority <= 10:
        raise ValueError("Native-input priority must be between 0 and 10")
    if not isinstance(max_bonus, int) or isinstance(max_bonus, bool):
        raise ValueError("Native-input maximum bonus must be an integer")
    if max_bonus < 0:
        raise ValueError("Native-input maximum bonus cannot be negative")
    if any(
        not isinstance(quantity, (int, float))
        or isinstance(quantity, bool)
        or not math.isfinite(quantity)
        for quantity in input_quantities.values()
    ):
        raise ValueError("Production-method input quantities must be finite numbers")
    if any(quantity < 0 for quantity in input_quantities.values()):
        raise ValueError("Production-method input quantities cannot be negative")
    numeric_factors = (
        (output_ratio, "output ratio"),
        (raw_input_utilization, "raw-input utilization"),
        (market_access, "market access"),
        (control, "control"),
        (shortage_discount, "shortage discount"),
        (high_utilization_discount, "utilization discount"),
        (low_output_floor, "output floor"),
        (access_control_floor, "access/control floor"),
    )
    for value, name in numeric_factors:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise ValueError(f"Native-input {name} must be a finite number")
    if exact_vanilla_coverage is not None and (
        not isinstance(exact_vanilla_coverage, (int, float))
        or isinstance(exact_vanilla_coverage, bool)
        or not math.isfinite(exact_vanilla_coverage)
    ):
        raise ValueError("Native-input exact coverage must be a finite number")
    for value, name in (
        (shortage_discount, "shortage discount"),
        (high_utilization_discount, "utilization discount"),
        (low_output_floor, "output floor"),
        (access_control_floor, "access/control floor"),
    ):
        if not 0 <= value <= 1:
            raise ValueError(f"Native-input {name} must be between 0 and 1")

    raw_inputs = {
        good: quantity
        for good, quantity in input_quantities.items()
        if good in raw_input_goods and quantity > 0
    }
    total_raw_input = sum(raw_inputs.values())
    matched_inputs = tuple(sorted(set(raw_inputs) & province_raw_goods))
    empty = NativeInputAssessment(
        method=NativeInputMethod.NONE,
        score=0,
        coverage=0.0,
        matched_inputs=(),
        total_raw_input=total_raw_input,
        shortage_factor=1.0,
        output_factor=1.0,
        utilization_factor=1.0,
        access_factor=1.0,
        control_factor=1.0,
    )
    if is_rgo or priority == 0 or total_raw_input <= 0:
        return empty

    if exact_vanilla_coverage is not None:
        method = NativeInputMethod.EXACT
        coverage = max(0.0, min(1.0, exact_vanilla_coverage))
    else:
        method = NativeInputMethod.PROXY
        coverage = sum(raw_inputs[good] for good in matched_inputs) / total_raw_input

    shortage_weight = sum(
        quantity for good, quantity in raw_inputs.items() if good in shortage_goods
    )
    shortage_factor = 1.0 - (
        (1.0 - shortage_discount) * shortage_weight / total_raw_input
    )
    output_factor = max(low_output_floor, min(1.0, output_ratio))
    utilization = max(0.0, min(1.0, raw_input_utilization))
    utilization_factor = 1.0 - utilization * (1.0 - high_utilization_discount)
    access_factor = access_control_floor + (
        1.0 - access_control_floor
    ) * max(0.0, min(1.0, market_access))
    control_factor = access_control_floor + (
        1.0 - access_control_floor
    ) * max(0.0, min(1.0, control))
    score = round(
        max_bonus
        * (priority / 10)
        * coverage
        * shortage_factor
        * output_factor
        * utilization_factor
        * access_factor
        * control_factor
    )
    return NativeInputAssessment(
        method=method,
        score=max(0, min(max_bonus, score)),
        coverage=coverage,
        matched_inputs=matched_inputs,
        total_raw_input=total_raw_input,
        shortage_factor=shortage_factor,
        output_factor=output_factor,
        utilization_factor=utilization_factor,
        access_factor=access_factor,
        control_factor=control_factor,
    )


@dataclass(frozen=True)
class BuildingCandidate:
    id: str
    output_goods: tuple[str, ...]
    cost: int
    price_ratio: float
    labor_available: bool = True
    inputs_available: bool = True
    input_shortages: tuple[str, ...] = ()
    local_pop_available: bool = True
    is_special: bool = False
    base_score: int = 0
    input_goods: tuple[str, ...] = ()
    potential_profit: float = 0.0
    available_workers: float | None = None
    existing_levels: int = 0
    strategic_tags: tuple[str, ...] = ()
    is_rgo: bool = False
    rgo_utilization: float = 1.0
    rgo_expansion_space: int = 0
    consecutive_expansions: int = 0
    expected_output_value: float | None = None
    expected_input_cost: float | None = None
    construction_cost: float | None = None
    unlocked: bool = True
    newer_replacement_unlocked: bool = False
    upgradeable_predecessor_levels: int = 0
    workforce_assessment: WorkforceAssessment | None = None
    native_input_assessment: NativeInputAssessment | None = None


@dataclass(frozen=True)
class GoodsMarketState:
    supply: float
    demand: float
    price_ratio: float = 1.0
    stockpile: float = 0.0

    @property
    def supply_ratio(self) -> float:
        if self.demand <= 0:
            return float("inf")
        return self.supply / self.demand


@dataclass(frozen=True)
class MarketState:
    goods: dict[str, GoodsMarketState] = field(default_factory=dict)
    food_stockpile_ratio: float = 1.0
    monthly_food_balance: float = 0.0
    projected_food_exhaustion: bool = False


@dataclass(frozen=True)
class CountryState:
    at_war: bool = False
    manpower_ratio: float = 1.0
    sailors_ratio: float = 1.0
    monthly_balance: float = 0.0
    active_mod_constructions: int = 0


@dataclass(frozen=True)
class LocationState:
    id: str = ""
    covered: bool = True
    civil_constructions: int = 0
    cooldown_months: int = 0
    failure_cooldown_months: int = 0
    market_access: float = 1.0
    control: float = 1.0
    population: float = 0.0
    development: float = 0.0
    unemployed_workers: float = 0.0
    total_building_levels: int = 0
    recently_built: bool = False
    waiting_months: int = 0
    template_role_match: bool = False
    critical_shortage: bool = False
    emergency: bool = False


@dataclass(frozen=True)
class AutomationContext:
    market: MarketState = field(default_factory=MarketState)
    country: CountryState = field(default_factory=CountryState)
    location: LocationState = field(default_factory=LocationState)


@dataclass(frozen=True)
class BuildDecision:
    building_id: str | None
    reason: PauseReason
    score: int = 0

    @property
    def should_build(self) -> bool:
        return self.building_id is not None and self.reason is PauseReason.NONE


@dataclass(frozen=True)
class LocationScore:
    location_id: str
    score: int
    components: dict[str, int]
    emergency: bool = False


@dataclass(frozen=True)
class RankedCandidate:
    candidate: BuildingCandidate
    score: int
    components: dict[str, int]


@dataclass(frozen=True)
class BuildExecution:
    building_id: str | None
    reason: PauseReason
    attempted_buildings: tuple[str, ...] = ()
    rejected_buildings: tuple[str, ...] = ()
    score: int = 0
    budget_spent: int = 0
    cooldown_months: int = 0
    quota_used: int = 0
    rgo_quota_used: int = 0

    @property
    def succeeded(self) -> bool:
        return self.building_id is not None and self.reason is PauseReason.NONE


def calculate_monthly_quota(
    covered_locations: int,
    *,
    user_hard_cap: int,
    budget_remaining: int,
    cash_available: int,
    min_cash_reserve: int,
    active_mod_constructions: int,
    rules: AutomationRules,
) -> int:
    """Return free slots using only this Mod's projects, budget, and cash rules."""
    if covered_locations <= 0:
        return 0
    concurrent_target = min(
        max(0, user_hard_cap) + 1,
        rules.cadence.max_country_concurrent_projects,
    )
    quota = min(
        max(0, concurrent_target - max(0, active_mod_constructions)),
        covered_locations,
    )
    if budget_remaining <= 0 or cash_available <= min_cash_reserve:
        return 0
    return quota


def low_cost_location_reason(location: LocationState, rules: AutomationRules) -> PauseReason:
    """Perform only checks that do not enumerate building types or market recipes."""
    if not location.covered:
        return PauseReason.NOT_ALLOWED
    if location.civil_constructions >= rules.cadence.max_location_civil_constructions:
        return PauseReason.CONSTRUCTION_QUEUE
    if location.cooldown_months > 0:
        return PauseReason.COOLDOWN
    if location.failure_cooldown_months > 0:
        return PauseReason.FAILURE_COOLDOWN
    return PauseReason.NONE


def score_location(location: LocationState, rules: AutomationRules) -> LocationScore:
    weights = rules.location_scores
    components = {
        "emergency": weights.emergency if location.emergency else 0,
        "critical_shortage": weights.critical_shortage if location.critical_shortage else 0,
        "template_role": weights.template_role if location.template_role_match else 0,
        "workforce": (
            weights.workforce
            if location.unemployed_workers >= rules.thresholds.minimum_unemployed_workers
            else 0
        ),
        "population": round(weights.population * min(1.0, location.population / 100_000)),
        "development": round(weights.development * min(1.0, location.development / 50)),
        "control": round(weights.control * max(0.0, min(1.0, location.control))),
        "market_access": round(
            weights.market_access * max(0.0, min(1.0, location.market_access))
        ),
        "existing_levels": location.total_building_levels * weights.existing_levels_penalty,
        "recent_build": weights.recent_build_penalty if location.recently_built else 0,
        "waiting": location.waiting_months * weights.waiting_per_month,
    }
    return LocationScore(
        location_id=location.id,
        score=sum(components.values()),
        components=components,
        emergency=location.emergency,
    )


def select_locations_for_deep_scoring(
    locations: list[LocationState],
    rules: AutomationRules,
    *,
    remaining_slots: int | None = None,
) -> tuple[list[LocationScore], dict[PauseReason, int]]:
    """Filter every covered location cheaply, then deeply inspect a bounded pool.

    Emergencies lead the shared pool. Linear waiting compensation is unbounded,
    so a persistently eligible location eventually outranks locations with
    bounded demographic and market scores.
    """
    passed: list[LocationScore] = []
    failures: dict[PauseReason, int] = {}
    for location in locations:
        reason = low_cost_location_reason(location, rules)
        if reason is not PauseReason.NONE:
            failures[reason] = failures.get(reason, 0) + 1
            continue
        passed.append(score_location(location, rules))

    ranked = sorted(passed, key=lambda item: (-item.score, item.location_id))
    emergencies = [item for item in ranked if item.emergency]
    normal = [item for item in ranked if not item.emergency]
    pool_limit = rules.cadence.deep_score_location_limit
    if remaining_slots is not None:
        pool_limit = min(
            pool_limit,
            max(0, remaining_slots) * rules.cadence.deep_score_quota_multiplier,
        )
    return (emergencies + normal)[:pool_limit], failures


def _shortage_level(state: GoodsMarketState | None, rules: AutomationRules) -> int:
    if state is None:
        return 0
    if state.supply_ratio <= rules.thresholds.goods_critical_supply_ratio:
        return 2
    if (
        state.supply_ratio <= rules.thresholds.goods_shortage_supply_ratio
        or state.price_ratio >= rules.thresholds.goods_high_price_ratio
    ):
        return 1
    return 0


def _candidate_groups(candidate: BuildingCandidate, rules: AutomationRules) -> frozenset[str]:
    return frozenset(candidate.strategic_tags) | rules.building_groups_for(candidate.id)


def _addresses_critical_need(
    candidate: BuildingCandidate,
    context: AutomationContext | None,
    rules: AutomationRules | None,
) -> bool:
    if context is None or rules is None:
        return False
    outputs = set(candidate.output_goods)
    if outputs & rules.food_goods and (
        context.market.projected_food_exhaustion
        or context.market.food_stockpile_ratio <= rules.thresholds.food_emergency_ratio
        or context.market.monthly_food_balance < 0
    ):
        return True
    return any(
        good in rules.essential_goods
        and _shortage_level(context.market.goods.get(good), rules) == 2
        for good in outputs
    )


def _goods_need_score(
    candidate: BuildingCandidate,
    context: AutomationContext,
    rules: AutomationRules,
) -> int:
    scores = rules.scores
    output_goods = set(candidate.output_goods)
    components: list[int] = []

    if output_goods & rules.food_goods:
        if context.market.projected_food_exhaustion:
            components.append(scores.food_projected_exhaustion)
        elif context.market.food_stockpile_ratio <= rules.thresholds.food_emergency_ratio:
            components.append(scores.food_emergency)
        elif context.market.food_stockpile_ratio <= rules.thresholds.food_low_ratio:
            components.append(scores.food_low)
        if context.market.monthly_food_balance < 0:
            components.append(scores.food_negative_balance)

    construction_goods = rules.construction_goods
    population_goods = set(rules.goods_groups["population_basic"])
    military_goods = set(rules.goods_groups["military"])
    for good in output_goods:
        shortage = _shortage_level(context.market.goods.get(good), rules)
        if shortage == 0:
            continue
        if good in construction_goods:
            components.append(
                scores.critical_construction_good if shortage == 2 else scores.short_construction_good
            )
        elif good in population_goods:
            components.append(
                scores.critical_population_good if shortage == 2 else scores.short_population_good
            )
        elif good in military_goods:
            components.append(
                scores.critical_military_good if shortage == 2 else scores.short_military_good
            )
        else:
            components.append(scores.critical_generic_good if shortage == 2 else scores.short_generic_good)

    # Only the two strongest market signals count. This prevents a broad output list
    # from winning merely because it enumerates more goods than a focused producer.
    need_score = sum(sorted(components, reverse=True)[:2])
    if context.country.at_war and output_goods & military_goods:
        need_score += scores.wartime_military_bonus
    return need_score


def score_candidate_components(
    policy: Policy,
    candidate: BuildingCandidate,
    context: AutomationContext | None = None,
    rules: AutomationRules | None = None,
) -> dict[str, int]:
    components: dict[str, int] = {"base": candidate.base_score}
    if rules is not None:
        effective_building_priority = rules.building_priority_for(candidate.id)
        if (
            effective_building_priority <= rules.building_priorities.minimum
            and candidate.id in policy.allowed_buildings
        ):
            effective_building_priority = 1
        components["building_priority"] = round(
            effective_building_priority * rules.building_priorities.score_per_point
        )
        if candidate.price_ratio > policy.max_price_ratio:
            components["price_above_max"] = rules.scores.high_profit
        if candidate.upgradeable_predecessor_levels > 0:
            components["upgrade_replacement"] = rules.thresholds.upgrade_replacement_bonus
    if context is None or rules is None:
        policy_priority = 0
        for index, good in enumerate(policy.priority_goods):
            if good in candidate.output_goods:
                policy_priority = max(policy_priority, 100 - index)
        components["policy_priority"] = policy_priority
        if policy.role in candidate.output_goods:
            components["role"] = 25
        return components

    components["market_need"] = _goods_need_score(candidate, context, rules)
    priority_scores = [
        max(0, rules.scores.policy_priority_base - index * rules.scores.policy_priority_step)
        for index, good in enumerate(policy.priority_goods)
        if good in candidate.output_goods
    ]
    if priority_scores:
        components["policy_priority"] = max(priority_scores)
    if policy.role in _candidate_groups(candidate, rules):
        components["role"] = rules.scores.role_match

    input_shortage = any(
        state is not None and state.supply_ratio <= rules.thresholds.input_shortage_supply_ratio
        for good in candidate.input_goods
        for state in (context.market.goods.get(good),)
    )
    if input_shortage or not candidate.inputs_available:
        components["input_shortage"] = rules.scores.input_shortage_penalty

    if candidate.workforce_assessment is not None:
        strategic_relief = 1.0
        if (
            candidate.workforce_assessment.state is WorkforceState.WITHIN_DEADLINE
            and _addresses_critical_need(candidate, context, rules)
        ):
            strategic_relief = rules.workforce_model.strategic_relief
        components["labor_risk"] = workforce_risk_penalty(
            candidate.workforce_assessment,
            max_penalty=rules.workforce_model.max_penalty,
            strategic_relief=strategic_relief,
        )
    elif not candidate.labor_available:
        # The runtime fallback remains risky even when a template disables
        # the hard workforce gate.
        components["labor_risk"] = -rules.workforce_model.max_penalty

    if candidate.native_input_assessment is not None:
        components["native_input_fit"] = candidate.native_input_assessment.score

    expected_profit = candidate.potential_profit
    if candidate.expected_output_value is not None and candidate.expected_input_cost is not None:
        expected_profit = candidate.expected_output_value - candidate.expected_input_cost
        construction_cost = candidate.construction_cost or float(candidate.cost)
        if construction_cost > 0:
            components["economic_efficiency"] = round(
                expected_profit / construction_cost * rules.thresholds.economic_score_scale
            )
    if expected_profit >= rules.thresholds.high_profit:
        components["profit_signal"] = rules.scores.high_profit
    elif expected_profit >= rules.thresholds.positive_profit:
        components["profit_signal"] = rules.scores.positive_profit
    else:
        components["profit_signal"] = rules.scores.negative_profit

    components["saturation"] = (
        -candidate.existing_levels * rules.thresholds.saturation_penalty_per_level
    )

    if candidate.is_rgo:
        rgo = rules.rgo_scores
        output_states = [
            context.market.goods[good]
            for good in candidate.output_goods
            if good in context.market.goods
        ]
        if any(_shortage_level(state, rules) > 0 for state in output_states):
            components["rgo_shortage"] = rgo.shortage
        if any(
            state.price_ratio >= rules.thresholds.goods_high_price_ratio
            for state in output_states
        ):
            components["rgo_price"] = rgo.high_price
        components["rgo_utilization"] = round(
            rgo.utilization * max(0.0, min(1.0, candidate.rgo_utilization))
        )
        if candidate.rgo_expansion_space > 0:
            components["rgo_expansion_space"] = rgo.expansion_space
        if (
            set(candidate.output_goods) & rules.essential_goods
            or set(candidate.strategic_tags) & {"food", "construction", "military", "strategic"}
        ):
            components["rgo_strategic"] = rgo.strategic
        components["rgo_cost"] = candidate.cost * rgo.cost_penalty
        components["rgo_consecutive"] = candidate.consecutive_expansions * rgo.consecutive_penalty
        if set(candidate.output_goods) & rules.food_goods and (
            context.market.projected_food_exhaustion
            or context.market.food_stockpile_ratio <= rules.thresholds.food_emergency_ratio
        ):
            components["rgo_food_emergency"] = rgo.food_emergency
    return components


def score_candidate(
    policy: Policy,
    candidate: BuildingCandidate,
    context: AutomationContext | None = None,
    rules: AutomationRules | None = None,
) -> int:
    return sum(score_candidate_components(policy, candidate, context, rules).values())


def first_blocking_reason(
    policy: Policy,
    candidate: BuildingCandidate,
    budget_remaining: int,
    cash_available: int,
    *,
    ignore_allowlist: bool = False,
    ignore_input_shortage: bool = False,
    context: AutomationContext | None = None,
    rules: AutomationRules | None = None,
) -> PauseReason:
    if not candidate.unlocked:
        return PauseReason.NOT_UNLOCKED
    if candidate.newer_replacement_unlocked:
        return PauseReason.SUPERSEDED_BUILDING
    if candidate.id in policy.banned_buildings:
        return PauseReason.BANNED_BUILDING
    if (
        rules is not None
        and rules.building_priority_for(candidate.id) <= rules.building_priorities.minimum
        and candidate.id not in policy.allowed_buildings
    ):
        return PauseReason.PRIORITY_DISABLED
    if not ignore_allowlist and policy.allowed_buildings and candidate.id not in policy.allowed_buildings:
        return PauseReason.NOT_ALLOWED
    if candidate.is_special and not policy.allow_special_buildings:
        return PauseReason.SPECIAL_BUILDING_DISABLED
    if candidate.is_rgo and not policy.rgo.allowed:
        return PauseReason.RGO_DISABLED
    if candidate.is_rgo and candidate.rgo_utilization < policy.rgo.minimum_utilization:
        return PauseReason.RGO_UTILIZATION
    if not candidate.local_pop_available:
        return PauseReason.POPULATION_SHORTAGE
    if context is not None and rules is not None:
        if context.location.civil_constructions >= rules.cadence.max_location_civil_constructions:
            return PauseReason.CONSTRUCTION_QUEUE
        if context.location.cooldown_months > 0:
            return PauseReason.COOLDOWN
    if policy.pause_on_labor_shortage:
        if (
            candidate.workforce_assessment is not None
            and not candidate.workforce_assessment.within_deadline
        ):
            return PauseReason.LABOR_SHORTAGE
        if candidate.workforce_assessment is None:
            if not candidate.labor_available:
                return PauseReason.LABOR_SHORTAGE
            if (
                candidate.available_workers is not None
                and rules is not None
                and candidate.available_workers
                < rules.thresholds.minimum_unemployed_workers
            ):
                return PauseReason.LABOR_SHORTAGE
    if not ignore_input_shortage and policy.pause_on_input_shortage and not candidate.inputs_available:
        return PauseReason.INPUT_SHORTAGE
    # A low output price signals oversupply and may block expansion. A high output
    # price signals scarcity, so the configured upper bound is a priority threshold.
    if candidate.price_ratio < policy.min_price_ratio and not _addresses_critical_need(candidate, context, rules):
        return PauseReason.PRICE_OUT_OF_RANGE
    if candidate.cost > budget_remaining:
        return PauseReason.BUDGET_EXHAUSTED
    if cash_available - candidate.cost < policy.min_cash_reserve:
        return PauseReason.CASH_RESERVE
    return PauseReason.NONE


def _source_building_ids(policy: Policy, catalog: BuildingCatalog | None, shortages: tuple[str, ...]) -> set[str]:
    if catalog is None or not policy.auto_build_input_sources:
        return set()
    source_ids: set[str] = set()
    for good in shortages:
        source_ids.update(catalog.source_buildings_by_good.get(good, ()))
    return source_ids


def rank_building_candidates(
    policy: Policy,
    candidates: list[BuildingCandidate],
    budget_remaining: int,
    cash_available: int,
    *,
    context: AutomationContext | None = None,
    rules: AutomationRules | None = None,
    limit: int | None = None,
) -> tuple[list[RankedCandidate], dict[PauseReason, int]]:
    """Return a bounded, score-ordered candidate list plus rejection counts."""
    ranked: list[RankedCandidate] = []
    rejected: dict[PauseReason, int] = {}
    for candidate in candidates:
        reason = first_blocking_reason(
            policy,
            candidate,
            budget_remaining,
            cash_available,
            context=context,
            rules=rules,
        )
        if reason is not PauseReason.NONE:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue
        components = score_candidate_components(policy, candidate, context, rules)
        ranked.append(
            RankedCandidate(
                candidate=candidate,
                score=sum(components.values()),
                components=components,
            )
        )

    ranked.sort(key=lambda item: (-item.score, item.candidate.id))
    if limit is None:
        limit = rules.cadence.candidates_per_location if rules is not None else 3
    return ranked[:limit], rejected


def execute_ranked_candidates(
    policy: Policy,
    candidates: list[BuildingCandidate],
    budget_remaining: int,
    cash_available: int,
    queue_count_before: int,
    attempt: Callable[[BuildingCandidate], int],
    *,
    rgo_quota_used: int = 0,
    context: AutomationContext | None = None,
    rules: AutomationRules,
) -> BuildExecution:
    """Try up to three candidates and commit state only after queue growth.

    The callback returns the observed queue size after the vanilla construction
    effect. A hidden vanilla rejection therefore falls through to the next
    candidate without spending budget, consuming quota, or applying cooldown.
    """
    ranked, rejections = rank_building_candidates(
        policy,
        candidates,
        budget_remaining,
        cash_available,
        context=context,
        rules=rules,
    )
    attempted: list[str] = []
    vanilla_rejected: list[str] = []

    for item in ranked:
        candidate = item.candidate
        attempted.append(candidate.id)
        queue_count_after = attempt(candidate)
        if queue_count_after > queue_count_before:
            return BuildExecution(
                building_id=candidate.id,
                reason=PauseReason.NONE,
                attempted_buildings=tuple(attempted),
                rejected_buildings=tuple(vanilla_rejected),
                score=item.score,
                budget_spent=candidate.cost,
                cooldown_months=rules.cadence.location_cooldown_months,
                quota_used=1,
                rgo_quota_used=1 if candidate.is_rgo else 0,
            )
        vanilla_rejected.append(candidate.id)

    if vanilla_rejected:
        reason = PauseReason.VANILLA_REJECTED
    elif rejections:
        reason = next(iter(rejections))
    else:
        reason = PauseReason.NO_CANDIDATE
    return BuildExecution(
        building_id=None,
        reason=reason,
        attempted_buildings=tuple(attempted),
        rejected_buildings=tuple(vanilla_rejected),
    )


def choose_building(
    policy: Policy,
    candidates: list[BuildingCandidate],
    budget_remaining: int,
    cash_available: int,
    catalog: BuildingCatalog | None = None,
    context: AutomationContext | None = None,
    rules: AutomationRules | None = None,
) -> BuildDecision:
    best: tuple[int, BuildingCandidate] | None = None
    fallback_reason = PauseReason.NO_CANDIDATE

    for candidate in candidates:
        reason = first_blocking_reason(
            policy,
            candidate,
            budget_remaining,
            cash_available,
            context=context,
            rules=rules,
        )
        if reason is PauseReason.INPUT_SHORTAGE and policy.auto_build_input_sources:
            source_ids = _source_building_ids(policy, catalog, candidate.input_shortages)
            source_candidates = [item for item in candidates if item.id in source_ids]
            source_decision = choose_input_source_building(
                policy,
                source_candidates,
                budget_remaining,
                cash_available,
                context=context,
                rules=rules,
            )
            if source_decision.should_build:
                return source_decision

        if reason is not PauseReason.NONE:
            if fallback_reason is PauseReason.NO_CANDIDATE:
                fallback_reason = reason
            continue
        score = score_candidate(policy, candidate, context, rules)
        if best is None or score > best[0]:
            best = (score, candidate)

    if best is None:
        return BuildDecision(None, fallback_reason)
    return BuildDecision(best[1].id, PauseReason.NONE, best[0])


def choose_input_source_building(
    policy: Policy,
    candidates: list[BuildingCandidate],
    budget_remaining: int,
    cash_available: int,
    context: AutomationContext | None = None,
    rules: AutomationRules | None = None,
) -> BuildDecision:
    best: tuple[int, BuildingCandidate] | None = None
    fallback_reason = PauseReason.NO_CANDIDATE
    for candidate in candidates:
        reason = first_blocking_reason(
            policy,
            candidate,
            budget_remaining,
            cash_available,
            ignore_allowlist=True,
            ignore_input_shortage=True,
            context=context,
            rules=rules,
        )
        if reason is not PauseReason.NONE:
            if fallback_reason is PauseReason.NO_CANDIDATE:
                fallback_reason = reason
            continue
        source_bonus = rules.scores.upstream_source_bonus if rules is not None else 50
        score = score_candidate(policy, candidate, context, rules) + source_bonus
        if best is None or score > best[0]:
            best = (score, candidate)

    if best is None:
        return BuildDecision(None, fallback_reason)
    return BuildDecision(best[1].id, PauseReason.NONE, best[0])


def apply_province_template(
    location_policy_ids: dict[str, str | None],
    province_locations: list[str],
    policy_id: str,
    decoupled_locations: set[str],
) -> dict[str, str | None]:
    updated = dict(location_policy_ids)
    for location_id in province_locations:
        if location_id not in decoupled_locations:
            updated[location_id] = policy_id
    return updated
