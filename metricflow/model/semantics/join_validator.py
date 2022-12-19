from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional
from collections import defaultdict

from metricflow.instances import DataSourceReference, DataSourceElementReference, IdentifierInstance, InstanceSet
from metricflow.model.objects.elements.identifier import IdentifierType, Identifier
from metricflow.object_utils import pformat_big_objects
from metricflow.protocols.semantics import DataSourceSemanticsAccessor
from metricflow.references import IdentifierReference
from metricflow.model.objects.data_source import DataSource

MAX_JOIN_HOPS = 2


@dataclass(frozen=True)
class DataSourceIdentifierJoinType:
    """Describe a type of join between data sources where identifiers are of the listed types."""

    left_identifier_type: IdentifierType
    right_identifier_type: IdentifierType


@dataclass(frozen=True)
class DataSourceIdentifierJoin:
    """How to join one data source onto another, using a specific identifer and join type."""

    right_data_source_reference: DataSourceReference
    identifier_reference: IdentifierReference  # do we need both identifier names? with the prefix? or is the local name enough?
    join_type: DataSourceIdentifierJoinType


@dataclass(frozen=True)
class DataSourceLink:
    """The valid join path to link two data sources. Might include multiple joins."""

    left_data_source_reference: DataSourceReference
    join_path: List[DataSourceIdentifierJoin]


class DataSourceJoinValidator:
    """Checks to see if a join between two data sources should be allowed."""

    # Valid joins are the non-fanout joins.
    _VALID_IDENTIFIER_JOINS = (
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.PRIMARY, right_identifier_type=IdentifierType.NATURAL
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.PRIMARY, right_identifier_type=IdentifierType.PRIMARY
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.PRIMARY, right_identifier_type=IdentifierType.UNIQUE
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.UNIQUE, right_identifier_type=IdentifierType.NATURAL
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.UNIQUE, right_identifier_type=IdentifierType.PRIMARY
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.UNIQUE, right_identifier_type=IdentifierType.UNIQUE
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.FOREIGN, right_identifier_type=IdentifierType.NATURAL
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.FOREIGN, right_identifier_type=IdentifierType.PRIMARY
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.FOREIGN, right_identifier_type=IdentifierType.UNIQUE
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.NATURAL, right_identifier_type=IdentifierType.PRIMARY
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.NATURAL, right_identifier_type=IdentifierType.UNIQUE
        ),
    )

    _INVALID_IDENTIFIER_JOINS = (
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.PRIMARY, right_identifier_type=IdentifierType.FOREIGN
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.UNIQUE, right_identifier_type=IdentifierType.FOREIGN
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.FOREIGN, right_identifier_type=IdentifierType.FOREIGN
        ),
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.NATURAL, right_identifier_type=IdentifierType.FOREIGN
        ),
        # Natural -> Natural joins are not allowed due to hidden fanout or missing value concerns with
        # multiple validity windows in play
        DataSourceIdentifierJoinType(
            left_identifier_type=IdentifierType.NATURAL, right_identifier_type=IdentifierType.NATURAL
        ),
    )

    def __init__(self, data_source_semantics: DataSourceSemanticsAccessor) -> None:  # noqa: D
        self._data_source_semantics = data_source_semantics

    def _get_remaining_hops_of_joinable_data_sources(
        self,
        left_data_source: DataSource,
        current_join_path: List[DataSourceIdentifierJoin],
        known_data_source_joins: Dict[str, DataSourceLink],
        join_hops_remaining: int,
    ) -> None:
        left_data_source_reference = DataSourceReference(data_source_name=left_data_source.name)
        data_source_reference_to_join_to = (
            current_join_path[-1].right_data_source_reference if current_join_path else left_data_source_reference
        )
        print("data source we're checking:", data_source_reference_to_join_to)

        # Get all joinable data sources in this hop before recursing
        identifiers_to_join_paths: Dict[Identifier, List[List[DataSourceIdentifierJoin]]] = defaultdict(list)
        for identifier in left_data_source.identifiers:
            identifier_reference = IdentifierReference(element_name=identifier.name)
            identifier_data_sources = self._data_source_semantics.get_data_sources_for_identifier(
                identifier_reference=identifier_reference
            )

            for right_data_source in identifier_data_sources:
                # Check if we've seen this data source already
                if (
                    right_data_source.name == left_data_source_reference.data_source_name
                    or right_data_source.name in known_data_source_joins
                ):
                    print("seen already:", right_data_source.name)
                    continue

                print("haven't seen!", right_data_source.name)
                # Check if there is a valid way to join this data source to existing join path
                right_data_source_reference = DataSourceReference(data_source_name=right_data_source.name)
                valid_join_type = self.get_valid_data_source_identifier_join_type(
                    left_data_source_reference=data_source_reference_to_join_to,
                    right_data_source_reference=right_data_source_reference,
                    on_identifier_reference=identifier_reference,
                )
                if valid_join_type is None:
                    continue

                join_path_for_data_source = current_join_path + [
                    DataSourceIdentifierJoin(
                        right_data_source_reference=right_data_source_reference,
                        identifier_reference=identifier_reference,
                        join_type=valid_join_type,
                    )
                ]
                identifiers_to_join_paths[identifier].append(join_path_for_data_source)
                known_data_source_joins[right_data_source_reference.data_source_name] = DataSourceLink(
                    left_data_source_reference=left_data_source_reference, join_path=join_path_for_data_source
                )

        join_hops_remaining -= 1
        if not join_hops_remaining:
            print("returning early?")
            return
        print("not returning early!")
        for identifier, join_paths in identifiers_to_join_paths.items():
            for join_path in join_paths:
                self._get_remaining_hops_of_joinable_data_sources(
                    left_data_source=left_data_source,
                    current_join_path=join_path,
                    known_data_source_joins=known_data_source_joins,
                    join_hops_remaining=join_hops_remaining,
                )

    def get_joinable_data_sources(
        self, left_data_source_reference: DataSourceReference, include_multi_hop: bool = False
    ) -> Dict[str, DataSourceLink]:
        """List all data sources that can join to given data source, and the identifiers to join them (max 2-hop joins)."""
        left_data_source = self._data_source_semantics.get_by_reference(
            data_source_reference=left_data_source_reference
        )
        assert left_data_source is not None

        data_source_joins: Dict[str, DataSourceLink] = {}
        self._get_remaining_hops_of_joinable_data_sources(
            left_data_source=left_data_source,
            current_join_path=[],
            known_data_source_joins=data_source_joins,
            join_hops_remaining=(MAX_JOIN_HOPS if include_multi_hop else 1),
        )
        return data_source_joins

    def get_valid_data_source_identifier_join_type(
        self,
        left_data_source_reference: DataSourceReference,
        right_data_source_reference: DataSourceReference,
        on_identifier_reference: IdentifierReference,
    ) -> Optional[DataSourceIdentifierJoinType]:
        """Get valid join type used to join data sources on given identifier, if exists."""
        left_identifier = self._data_source_semantics.get_identifier_in_data_source(
            DataSourceElementReference.create_from_references(left_data_source_reference, on_identifier_reference)
        )

        right_identifier = self._data_source_semantics.get_identifier_in_data_source(
            DataSourceElementReference.create_from_references(right_data_source_reference, on_identifier_reference)
        )
        if left_identifier is None or right_identifier is None:
            return None

        left_data_source = self._data_source_semantics.get_by_reference(left_data_source_reference)
        right_data_source = self._data_source_semantics.get_by_reference(right_data_source_reference)
        assert left_data_source, "Type refinement. If you see this error something has refactored wrongly"
        assert right_data_source, "Type refinement. If you see this error something has refactored wrongly"

        if left_data_source.has_validity_dimensions and right_data_source.has_validity_dimensions:
            # We cannot join two data sources with validity dimensions due to concerns with unexpected fanout
            # due to the key structure of these data sources. Applying multi-stage validity window filters can
            # also lead to unexpected removal of interim join keys. Note this will need to be updated if we enable
            # measures in such data sources, since those will need to be converted to a different type of data source
            # to support measure computation.
            return None

        if right_identifier.type is IdentifierType.NATURAL:
            if not right_data_source.has_validity_dimensions:
                # There is no way to refine this to a single row per key, so we cannot support this join
                return None

        join_type = DataSourceIdentifierJoinType(left_identifier.type, right_identifier.type)

        if join_type in DataSourceJoinValidator._VALID_IDENTIFIER_JOINS:
            return join_type
        elif join_type in DataSourceJoinValidator._INVALID_IDENTIFIER_JOINS:
            return None

        raise RuntimeError(f"Join type not handled: {join_type}")

    def is_valid_data_source_join(
        self,
        left_data_source_reference: DataSourceReference,
        right_data_source_reference: DataSourceReference,
        on_identifier_reference: IdentifierReference,
    ) -> bool:
        """Return true if we should allow a join with the given parameters to resolve a query."""
        return (
            self.get_valid_data_source_identifier_join_type(
                left_data_source_reference=left_data_source_reference,
                right_data_source_reference=right_data_source_reference,
                on_identifier_reference=on_identifier_reference,
            )
            is not None
        )

    @staticmethod
    def _data_source_of_identifier_in_instance_set(
        instance_set: InstanceSet,
        identifier_reference: IdentifierReference,
    ) -> DataSourceReference:
        """Return the data source where the identifier was defined in the instance set."""
        matching_instances: List[IdentifierInstance] = []
        for identifier_instance in instance_set.identifier_instances:
            assert len(identifier_instance.defined_from) == 1
            if (
                len(identifier_instance.spec.identifier_links) == 0
                and identifier_instance.spec.reference == identifier_reference
            ):
                matching_instances.append(identifier_instance)

        assert len(matching_instances) == 1, (
            f"Not exactly 1 matching identifier instances found: {matching_instances} for {identifier_reference} in "
            f"{pformat_big_objects(instance_set)}"
        )
        return matching_instances[0].origin_data_source_reference.data_source_reference

    def is_valid_instance_set_join(
        self,
        left_instance_set: InstanceSet,
        right_instance_set: InstanceSet,
        on_identifier_reference: IdentifierReference,
    ) -> bool:
        """Return true if the instance sets can be joined using the given identifier."""
        return self.is_valid_data_source_join(
            left_data_source_reference=DataSourceJoinValidator._data_source_of_identifier_in_instance_set(
                instance_set=left_instance_set, identifier_reference=on_identifier_reference
            ),
            right_data_source_reference=DataSourceJoinValidator._data_source_of_identifier_in_instance_set(
                instance_set=right_instance_set,
                identifier_reference=on_identifier_reference,
            ),
            on_identifier_reference=on_identifier_reference,
        )
