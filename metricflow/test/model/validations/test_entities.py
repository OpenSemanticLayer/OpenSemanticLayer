import copy
import re
import textwrap
from typing import Callable

import more_itertools
import pytest

from dbt_semantic_interfaces.objects.aggregation_type import AggregationType
from metricflow.model.model_validator import ModelValidator
from dbt_semantic_interfaces.objects.common import YamlConfigFile
from dbt_semantic_interfaces.objects.data_source import DataSource, Mutability, MutabilityType
from dbt_semantic_interfaces.objects.elements.dimension import Dimension, DimensionType, DimensionTypeParams
from dbt_semantic_interfaces.objects.elements.entity import EntityType, Entity, CompositeSubEntity
from dbt_semantic_interfaces.objects.elements.measure import Measure
from dbt_semantic_interfaces.objects.metric import MetricType, MetricTypeParams
from dbt_semantic_interfaces.objects.user_configured_model import UserConfiguredModel
from dbt_semantic_interfaces.parsing.dir_to_model import parse_yaml_files_to_validation_ready_model
from metricflow.model.validations.entities import (
    EntityConfigRule,
    EntityConsistencyRule,
    NaturalEntityConfigurationRule,
    OnePrimaryEntityPerDataSourceRule,
)
from metricflow.model.validations.validator_helpers import ModelValidationException
from metricflow.test.model.validations.helpers import (
    data_source_with_guaranteed_meta,
    metric_with_guaranteed_meta,
    base_model_file,
)
from metricflow.test.test_utils import find_data_source_with
from dbt_semantic_interfaces.objects.time_granularity import TimeGranularity


def test_data_source_cant_have_more_than_one_primary_identifier(
    simple_model__with_primary_transforms: UserConfiguredModel,
) -> None:  # noqa: D
    """Add an additional primary identifier to a data source and assert that it cannot have two"""
    model = copy.deepcopy(simple_model__with_primary_transforms)
    func: Callable[[DataSource], bool] = lambda data_source: len(data_source.identifiers) > 1

    multiple_identifier_data_source, _ = find_data_source_with(model, func)

    entity_references = set()
    for identifier in multiple_identifier_data_source.identifiers:
        identifier.type = EntityType.PRIMARY
        entity_references.add(identifier.reference)

    model_issues = ModelValidator([OnePrimaryEntityPerDataSourceRule()]).validate_model(model)

    future_issue = (
        f"Data sources can have only one primary entity. The data source"
        f" `{multiple_identifier_data_source.name}` has {len(entity_references)}"
    )

    found_future_issue = False

    if model_issues is not None:
        for issue in model_issues.all_issues:
            if re.search(future_issue, issue.message):
                found_future_issue = True

    assert found_future_issue


def test_invalid_composite_identifiers() -> None:  # noqa:D
    with pytest.raises(ModelValidationException, match=r"If sub entity has same name"):
        dim_name = "time"
        measure_name = "foo"
        measure2_name = "metric_with_no_time_dim"
        identifier_name = "thorium"
        foreign_identifier_name = "composite_thorium"
        model_validator = ModelValidator([EntityConfigRule()])
        model_validator.checked_validations(
            UserConfiguredModel(
                data_sources=[
                    data_source_with_guaranteed_meta(
                        name="dim1",
                        sql_query=f"SELECT {dim_name}, {measure_name}, thorium_id FROM bar",
                        measures=[Measure(name=measure_name, agg=AggregationType.SUM)],
                        dimensions=[
                            Dimension(
                                name=dim_name,
                                type=DimensionType.TIME,
                                type_params=DimensionTypeParams(
                                    is_primary=True,
                                    time_granularity=TimeGranularity.DAY,
                                ),
                            )
                        ],
                        identifiers=[
                            Entity(name=identifier_name, type=EntityType.PRIMARY, expr="thorium_id"),
                            Entity(
                                name=foreign_identifier_name,
                                type=EntityType.FOREIGN,
                                entities=[
                                    CompositeSubEntity(name=identifier_name, expr="not_thorium_id"),
                                ],
                            ),
                        ],
                        mutability=Mutability(type=MutabilityType.IMMUTABLE),
                    ),
                ],
                metrics=[
                    metric_with_guaranteed_meta(
                        name=measure2_name,
                        type=MetricType.MEASURE_PROXY,
                        type_params=MetricTypeParams(measures=[measure_name]),
                    )
                ],
            )
        )


def test_composite_identifiers_nonexistent_ref() -> None:  # noqa:D
    with pytest.raises(ModelValidationException, match=r"Entity ref must reference an existing entity by name"):
        dim_name = "time"
        measure_name = "foo"
        measure2_name = "metric_with_no_time_dim"
        identifier_name = "thorium"
        foreign_identifier_name = "composite_thorium"
        model_validator = ModelValidator([EntityConfigRule()])
        model_validator.checked_validations(
            UserConfiguredModel(
                data_sources=[
                    data_source_with_guaranteed_meta(
                        name="dim1",
                        sql_query=f"SELECT {dim_name}, {measure_name}, thorium_id FROM bar",
                        measures=[Measure(name=measure_name, agg=AggregationType.SUM)],
                        dimensions=[
                            Dimension(
                                name=dim_name,
                                type=DimensionType.TIME,
                                type_params=DimensionTypeParams(
                                    is_primary=True,
                                    time_granularity=TimeGranularity.DAY,
                                ),
                            )
                        ],
                        identifiers=[
                            Entity(name=identifier_name, type=EntityType.PRIMARY, expr="thorium_id"),
                            Entity(
                                name=foreign_identifier_name,
                                type=EntityType.FOREIGN,
                                entities=[
                                    CompositeSubEntity(ref="ident_that_doesnt_exist"),
                                ],
                            ),
                        ],
                        mutability=Mutability(type=MutabilityType.IMMUTABLE),
                    ),
                ],
                metrics=[
                    metric_with_guaranteed_meta(
                        name=measure2_name,
                        type=MetricType.MEASURE_PROXY,
                        type_params=MetricTypeParams(measures=[measure_name]),
                    )
                ],
            )
        )


def test_composite_identifiers_ref_and_name() -> None:  # noqa:D
    with pytest.raises(ModelValidationException, match=r"Both ref and name/expr set in sub entity of entity"):
        dim_name = "time"
        measure_name = "foo"
        measure2_name = "metric_with_no_time_dim"
        identifier_name = "thorium"
        foreign_identifier_name = "composite_thorium"
        foreign_identifier2_name = "shouldnt_have_both"
        model_validator = ModelValidator([EntityConfigRule()])
        model_validator.checked_validations(
            UserConfiguredModel(
                data_sources=[
                    data_source_with_guaranteed_meta(
                        name="dim1",
                        sql_query=f"SELECT {dim_name}, {measure_name}, thorium_id FROM bar",
                        measures=[Measure(name=measure_name, agg=AggregationType.SUM)],
                        dimensions=[
                            Dimension(
                                name=dim_name,
                                type=DimensionType.TIME,
                                type_params=DimensionTypeParams(
                                    is_primary=True,
                                    time_granularity=TimeGranularity.DAY,
                                ),
                            )
                        ],
                        identifiers=[
                            Entity(name=identifier_name, type=EntityType.PRIMARY, expr="thorium_id"),
                            Entity(
                                name=foreign_identifier_name,
                                type=EntityType.FOREIGN,
                                entities=[
                                    CompositeSubEntity(ref="ident_that_doesnt_exist", name=foreign_identifier2_name),
                                ],
                            ),
                        ],
                        mutability=Mutability(type=MutabilityType.IMMUTABLE),
                    ),
                ],
                metrics=[
                    metric_with_guaranteed_meta(
                        name=measure2_name,
                        type=MetricType.MEASURE_PROXY,
                        type_params=MetricTypeParams(measures=[measure_name]),
                    )
                ],
            )
        )


def test_mismatched_identifier(simple_model__with_primary_transforms: UserConfiguredModel) -> None:  # noqa: D
    """Testing two mismatched entities in two data sources

    Add two entities with mismatched sub-entities to two data sources in the model
    Ensure that our composite entities rule catches this incompatibility
    """
    model = copy.deepcopy(simple_model__with_primary_transforms)

    bookings_source, _ = find_data_source_with(
        model=model,
        function=lambda data_source: data_source.name == "bookings_source",
    )
    listings_latest, _ = find_data_source_with(
        model=model,
        function=lambda data_source: data_source.name == "listings_latest",
    )

    identifier_bookings = Entity(
        name="composite_identifier",
        type=EntityType.FOREIGN,
        entities=[CompositeSubEntity(ref="sub_identifier1")],
    )
    bookings_source.identifiers = tuple(more_itertools.flatten([bookings_source.identifiers, [identifier_bookings]]))

    identifier_listings = Entity(
        name="composite_identifier",
        type=EntityType.FOREIGN,
        entities=[CompositeSubEntity(ref="sub_identifier2")],
    )
    listings_latest.identifiers = tuple(more_itertools.flatten([listings_latest.identifiers, [identifier_listings]]))

    model_issues = ModelValidator([EntityConsistencyRule()]).validate_model(model)

    expected_error_message_fragment = "does not have consistent sub-entities"
    error_count = len(
        [issue for issue in model_issues.all_issues if re.search(expected_error_message_fragment, issue.message)]
    )

    assert error_count == 1


def test_multiple_natural_identifiers() -> None:
    """Test validation enforcing that a single data source cannot have more than one natural entity"""
    yaml_contents = textwrap.dedent(
        """\
        data_source:
          name: too_many_natural_identifiers
          sql_table: some_schema.natural_identifier_table
          identifiers:
            - name: natural_key_one
              type: natural
            - name: natural_key_two
              type: natural
          dimensions:
            - name: country
              type: categorical
            - name: window_start
              type: time
              type_params:
                time_granularity: day
                validity_params:
                  is_start: true
            - name: window_end
              type: time
              type_params:
                time_granularity: day
                validity_params:
                  is_end: true
        """
    )
    natural_identifier_file = YamlConfigFile(filepath="inline_for_test", contents=yaml_contents)
    model = parse_yaml_files_to_validation_ready_model([base_model_file(), natural_identifier_file])

    with pytest.raises(ModelValidationException, match="can have at most one natural entity"):
        ModelValidator([NaturalEntityConfigurationRule()]).checked_validations(model.model)


def test_natural_identifier_used_in_wrong_context() -> None:
    """Test validation enforcing that a single data source cannot have more than one natural entity"""
    yaml_contents = textwrap.dedent(
        """\
        data_source:
          name: random_natural_identifier
          sql_table: some_schema.random_natural_identifier_table
          identifiers:
            - name: natural_key
              type: natural
          dimensions:
            - name: country
              type: categorical
        """
    )
    natural_identifier_file = YamlConfigFile(filepath="inline_for_test", contents=yaml_contents)
    model = parse_yaml_files_to_validation_ready_model([base_model_file(), natural_identifier_file])

    with pytest.raises(ModelValidationException, match="use of `natural` entities is currently supported only in"):
        ModelValidator([NaturalEntityConfigurationRule()]).checked_validations(model.model)