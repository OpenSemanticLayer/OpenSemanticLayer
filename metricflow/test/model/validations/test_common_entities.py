import copy
import pytest
import re
from typing import Callable

from dbt_semantic_interfaces.model_validator import ModelValidator
from dbt_semantic_interfaces.objects.data_source import DataSource
from dbt_semantic_interfaces.objects.user_configured_model import UserConfiguredModel
from dbt_semantic_interfaces.validations.common_entities import CommonEntitysRule
from metricflow.specs import EntitySpec
from metricflow.test.test_utils import find_data_source_with


@pytest.mark.skip("TODO: re-enforce after validations improvements")
def test_lonely_identifier_raises_issue(simple_model__with_primary_transforms: UserConfiguredModel) -> None:  # noqa: D
    model = copy.deepcopy(simple_model__with_primary_transforms)
    lonely_identifier_name = "hi_im_lonely"

    func: Callable[[DataSource], bool] = lambda data_source: len(data_source.identifiers) > 0
    data_source_with_identifiers, _ = find_data_source_with(model, func)
    data_source_with_identifiers.identifiers[0].name = EntitySpec.from_name(lonely_identifier_name).element_name
    model_validator = ModelValidator([CommonEntitysRule()])
    model_issues = model_validator.validate_model(model)

    found_warning = False
    warning = (
        f"Entity `{lonely_identifier_name}` only found in one data source `{data_source_with_identifiers.name}` "
        f"which means it will be unused in joins."
    )
    if model_issues is not None:
        for issue in model_issues.all_issues:
            if re.search(warning, issue.message):
                found_warning = True

    assert found_warning
