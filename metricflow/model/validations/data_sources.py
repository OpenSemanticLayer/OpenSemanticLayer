import logging
from typing import List

from dbt_semantic_interfaces.objects.data_source import DataSource
from dbt_semantic_interfaces.type_enums.dimension_type import DimensionType
from dbt_semantic_interfaces.objects.elements.entity import EntityType
from dbt_semantic_interfaces.objects.user_configured_model import UserConfiguredModel
from dbt_semantic_interfaces.references import DataSourceReference
from metricflow.model.validations.validator_helpers import (
    DataSourceContext,
    FileContext,
    ModelValidationRule,
    ValidationIssue,
    ValidationError,
    validate_safely,
)

logger = logging.getLogger(__name__)


class DataSourceTimeDimensionWarningsRule(ModelValidationRule):
    """Checks time dimensions in data sources."""

    @staticmethod
    @validate_safely(whats_being_done="running model validation ensuring time dimensions are defined properly")
    def validate_model(model: UserConfiguredModel) -> List[ValidationIssue]:  # noqa: D
        issues: List[ValidationIssue] = []

        for data_source in model.data_sources:
            issues.extend(DataSourceTimeDimensionWarningsRule._validate_data_source(data_source=data_source))
        return issues

    @staticmethod
    @validate_safely(whats_being_done="checking validity of the data source's time dimensions")
    def _validate_data_source(data_source: DataSource) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        primary_time_dimensions = []

        for dim in data_source.dimensions:
            if dim.type == DimensionType.TIME and dim.type_params is not None and dim.type_params.is_primary:
                primary_time_dimensions.append(dim)

        # A data source must have a primary time dimension if it has
        # any measures that don't have an `agg_time_dimension` set
        if (
            len(primary_time_dimensions) == 0
            and len(data_source.measures) > 0
            and any(measure.agg_time_dimension is None for measure in data_source.measures)
        ):
            issues.append(
                ValidationError(
                    context=DataSourceContext(
                        file_context=FileContext.from_metadata(metadata=data_source.metadata),
                        data_source=DataSourceReference(data_source_name=data_source.name),
                    ),
                    message=f"No primary time dimension in data source with name ({data_source.name}). Please add one",
                )
            )

        if len(primary_time_dimensions) > 1:
            for primary_time_dimension in primary_time_dimensions:
                issues.append(
                    ValidationError(
                        context=DataSourceContext(
                            file_context=FileContext.from_metadata(metadata=data_source.metadata),
                            data_source=DataSourceReference(data_source_name=data_source.name),
                        ),
                        message=f"In data source {data_source.name}, "
                        f"Primary time dimension with name: {primary_time_dimension.name} "
                        f"is one of many defined as primary.",
                    )
                )

        return issues


class DataSourceValidityWindowRule(ModelValidationRule):
    """Checks validity windows in data sources to ensure they comply with runtime requirements"""

    @staticmethod
    @validate_safely(whats_being_done="checking correctness of the time dimension validity parameters in the model")
    def validate_model(model: UserConfiguredModel) -> List[ValidationIssue]:
        """Checks the validity param definitions in every data source in the model"""
        issues: List[ValidationIssue] = []

        for data_source in model.data_sources:
            issues.extend(DataSourceValidityWindowRule._validate_data_source(data_source=data_source))

        return issues

    @staticmethod
    @validate_safely(
        whats_being_done="checking the data source's validity parameters for compatibility with runtime requirements"
    )
    def _validate_data_source(data_source: DataSource) -> List[ValidationIssue]:
        """Runs assertions on data sources with validity parameters set on one or more time dimensions"""

        issues: List[ValidationIssue] = []

        validity_param_dims = [dim for dim in data_source.dimensions if dim.validity_params is not None]

        if not validity_param_dims:
            return issues

        context = DataSourceContext(
            file_context=FileContext.from_metadata(metadata=data_source.metadata),
            data_source=DataSourceReference(data_source_name=data_source.name),
        )
        requirements = (
            "Data sources using dimension validity params to define a validity window must have exactly two time "
            "dimensions with validity params specified - one marked `is_start` and the other marked `is_end`."
        )
        validity_param_dimension_names = [dim.name for dim in validity_param_dims]
        start_dim_names = [
            dim.name for dim in validity_param_dims if dim.validity_params and dim.validity_params.is_start
        ]
        end_dim_names = [dim.name for dim in validity_param_dims if dim.validity_params and dim.validity_params.is_end]
        num_start_dims = len(start_dim_names)
        num_end_dims = len(end_dim_names)

        if len(validity_param_dims) == 1 and num_start_dims == 1 and num_end_dims == 1:
            # Defining a single point window, such as one might find in a daily snapshot table keyed on date,
            # is not currently supported.
            error = ValidationError(
                context=context,
                message=(
                    f"Data source {data_source.name} has a single validity param dimension that defines its window: "
                    f"`{validity_param_dimension_names[0]}`. This is not a currently supported configuration! "
                    f"{requirements} If you have one column defining a window, as in a daily snapshot table, you can "
                    f"define a separate dimension and increment the time value in the `expr` field as a work-around."
                ),
            )
            issues.append(error)
        elif len(validity_param_dims) != 2:
            error = ValidationError(
                context=context,
                message=(
                    f"Data source {data_source.name} has {len(validity_param_dims)} dimensions defined with validity "
                    f"params. They are: {validity_param_dimension_names}. There must be either zero or two! "
                    f"If you wish to define a validity window for this data source, please follow these requirements: "
                    f"{requirements}"
                ),
            )
            issues.append(error)
        elif num_start_dims != 1 or num_end_dims != 1:
            # Validity windows must define both a start and an end, and there should be exactly one
            start_dim_names = []
            error = ValidationError(
                context=context,
                message=(
                    f"Data source {data_source.name} has two validity param dimensions defined, but does not have "
                    f"exactly one each marked with is_start and is_end! Dimensions: {validity_param_dimension_names}. "
                    f"is_start dimensions: {start_dim_names}. is_end dimensions: {end_dim_names}. {requirements}"
                ),
            )
            issues.append(error)

        primary_or_unique_entities = [
            entity for entity in data_source.identifiers if entity.type in (EntityType.PRIMARY, EntityType.UNIQUE)
        ]
        if not any([entity.type is EntityType.NATURAL for entity in data_source.identifiers]):
            error = ValidationError(
                context=context,
                message=(
                    f"Data source {data_source.name} has validity param dimensions defined, but does not have an "
                    f"entity with type `natural` set. The natural key for this data source is what we use to "
                    f"process a validity window join. Primary or unique identifiers, if any, might be suitable for "
                    f"use as natural keys: ({[entity.name for entity in primary_or_unique_entities]})."
                ),
            )
            issues.append(error)

        if primary_or_unique_entities:
            error = ValidationError(
                context=context,
                message=(
                    f"Data source {data_source.name} has validity param dimensions defined and also has one or more "
                    f"entities designated as `primary` or `unique`. This is not yet supported, as we do not "
                    f"currently process joins against these key types for data sources with validity windows "
                    f"specified."
                ),
            )
            issues.append(error)

        if data_source.measures:
            # Temporarily block measure definitions in data sources with validity windows set
            measure_names = [measure.name for measure in data_source.measures]
            error = ValidationError(
                context=context,
                message=(
                    f"Data source {data_source.name} has both measures and validity param dimensions defined. This "
                    f"is not currently supported! Please remove either the measures or the validity params. "
                    f"Measure names: {measure_names}. Validity param dimension names: "
                    f"{validity_param_dimension_names}."
                ),
            )
            issues.append(error)

        return issues
