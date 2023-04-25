from __future__ import annotations

import datetime
import logging
import os
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple, Sequence, List, Union

import dateutil.parser
import pandas as pd
import yaml

from metricflow.dataflow.sql_table import SqlTable
from metricflow.model.objects.base import FrozenBaseModel
from metricflow.object_utils import hash_items, assert_values_exhausted
from metricflow.protocols.sql_client import SqlClient
from metricflow.sql_clients.sql_utils import make_df

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SqlTableSnapshotHash:
    """A hash that can be used to compare whether a SQL table snapshot has changed."""
    str_value: str

    @staticmethod
    def create_from_hashes(hashes: Sequence[SqlTableSnapshotHash]) -> SqlTableSnapshotHash:  # noqa: D
        return SqlTableSnapshotHash(hash_items(tuple(one_hash.str_value for one_hash in hashes)))


class SqlTableColumnType(Enum):  # noqa: D
    STRING = "STRING"
    TIME = "TIME"
    FLOAT = "FLOAT"
    INT = "INT"
    BOOLEAN = "BOOLEAN"


class SqlTableColumnDefinition(FrozenBaseModel):
    """Pydantic class to help parse column definitions in a table snapshots that are defined in YAML."""

    # Pydantic feature to throw errors on extra fields.
    class Config:  # noqa: D
        extra = "forbid"

    name: str
    type: SqlTableColumnType


class SqlTableSnapshotTypeException(Exception):  # noqa: D
    pass


class SqlTableSnapshot(FrozenBaseModel):
    """Pydantic class to help parse table snapshots that are defined in YAML."""

    # Pydantic feature to throw errors on extra fields.
    class Config:  # noqa: D
        extra = "forbid"

    name: str
    column_definitions: Tuple[SqlTableColumnDefinition, ...]
    rows: Tuple[Tuple[str, ...], ...]
    file_path: Path

    @property
    def snapshot_hash(self) -> SqlTableSnapshotHash:
        """Return a hash that can be used to summarize the schema and data of the snapshot."""
        return SqlTableSnapshotHash(
            hash_items(
                (
                    self.name,
                ) + tuple(
                    column_definition.name for column_definition in self.column_definitions
                ) + tuple(
                    column_definition.type.name for column_definition in self.column_definitions
                ) + tuple(
                    cell for row in self.rows for cell in row
                )
            )
        )

    @staticmethod
    def _parse_bool_str(bool_str: str) -> bool:  # noqa: D
        if bool_str.lower() == "false":
            return False
        elif bool_str.lower() == "true":
            return True
        else:
            raise RuntimeError(f"Invalid string representation of a boolean: {bool_str}")

    @property
    def as_df(self) -> pd.DataFrame:  # noqa: D
        """Return this snapshot as represented by an equivalent dataframe"""
        # In the YAML files, all values are strings, but they need to be converted to defined type so that it can be
        # properly represented in a dataframe

        type_converted_rows = []
        for row in self.rows:
            type_converted_row: List[Union[str, datetime.datetime, int, float, bool]] = []
            for column_num, column_value in enumerate(row):
                column_type = self.column_definitions[column_num].type
                if column_type is SqlTableColumnType.STRING:
                    type_converted_row.append(column_value)
                elif column_type is SqlTableColumnType.TIME:
                    type_converted_row.append(dateutil.parser.parse(column_value))
                elif column_type is SqlTableColumnType.INT:
                    type_converted_row.append(int(column_value))
                elif column_type is SqlTableColumnType.FLOAT:
                    type_converted_row.append(float(column_value))
                elif column_type is SqlTableColumnType.BOOLEAN:
                    type_converted_row.append(SqlTableSnapshot._parse_bool_str(column_value))
                else:
                    assert_values_exhausted(column_type)
            type_converted_rows.append(type_converted_row)

        return pd.DataFrame(
            columns=[column_definition.name for column_definition in self.column_definitions],
            data=type_converted_rows,
        )


class SqlTableSnapshotRestorer:
    """Restores a snapshot of a table into the SQL engine."""

    def __init__(self, sql_client: SqlClient, schema_name: str) -> None:  # noqa: D
        self._sql_client = sql_client
        self._schema_name = schema_name

    def restore(self, table_snapshot: SqlTableSnapshot) -> None:  # noqa: D
        self._sql_client.create_table_from_dataframe(
            sql_table=SqlTable(schema_name=self._schema_name, table_name=table_snapshot.name),
            df=table_snapshot.as_df,
        )

class TableSnapshotParseException(Exception):  # noqa: D
    pass


class SqlTableSnapshotRepository:
    """Stores integration test cases generated by parsing YAML files."""

    def __init__(self, config_directory: Path) -> None:
        """Constructor.

        Args:
            config_directory: directory that should be searched for YAML files containing test cases.
        """
        self._config_directory = config_directory
        self._yaml_paths = SqlTableSnapshotRepository._find_all_yaml_file_paths(self._config_directory)
        self._table_snapshots: OrderedDict[str, SqlTableSnapshot] = OrderedDict()

        for file_path in self._yaml_paths:
            table_snapshots = SqlTableSnapshotRepository._parse_config_yaml(file_path)
            for table_snapshot in table_snapshots:
                if table_snapshot.name in self._table_snapshots:
                    raise ValueError(f"Table with duplicate name found: {table_snapshot.name}")
                self._table_snapshots[table_snapshot.name] = table_snapshot

    @staticmethod
    def _parse_config_yaml(file_path: Path) -> Sequence[SqlTableSnapshot]:
        """Parse the YAML file at the given path into test cases."""
        results = []
        document_key = "table_snapshot"
        with open(file_path) as f:
            file_contents = f.read()
            for config_document in yaml.load_all(stream=file_contents, Loader=yaml.SafeLoader):
                # The config document can be None if there is nothing but white space between two `---`
                # this isn't really an issue, so lets just swallow it
                if config_document is None:
                    continue
                if not isinstance(config_document, dict):
                    raise TableSnapshotParseException(
                        f"Table snapshot YAML must be a dict. Got `{type(config_document)}`: {config_document}"
                    )

                keys = tuple(x for x in config_document.keys())
                if len(keys) != 1:
                    raise TableSnapshotParseException(
                        f"Table snapshot document should have one type of key, but this has {len(keys)}. "
                        f"Found keys: {keys} in {file_path}",
                    )

                # retrieve last top-level key as type
                document_type = next(iter(config_document.keys()))
                object_cfg = config_document[document_type]
                if document_type == document_key:
                    try:
                        results.append(SqlTableSnapshot(**object_cfg, file_path=Path(file_path)))
                    except Exception as e:
                        logger.exception(f"Error while parsing: {file_path}")
                        raise TableSnapshotParseException(f"Error while parsing: {file_path}") from e
                else:
                    raise TableSnapshotParseException(f"Expected {document_key}, but got {document_type}")
        return results

    @staticmethod
    def _find_all_yaml_file_paths(directory: Path) -> Sequence[Path]:  # noqa: D
        """Recursively search through the given directory for YAML files."""
        yaml_file_paths = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".yaml"):
                    yaml_file_paths.append(Path(root, file))

        return sorted(yaml_file_paths)

    @property
    def table_snapshots(self) -> Sequence[SqlTableSnapshot]:  # noqa: D
        # tuple(self._table_snapshots.values()) shows a type warning
        return sorted(
            tuple(table_snapshot for table_snapshot in self._table_snapshots.values()),
            key=lambda table_snapshot: table_snapshot.name
        )

    @property
    def source_schema_name(self) -> str:  # noqa: D
        combined_definition_hash = SqlTableSnapshotHash.create_from_hashes(
            tuple(table_snapshot.snapshot_hash for table_snapshot in self.table_snapshots)
        )
        return f"mf_test_src_{combined_definition_hash.str_value[:8]}"


TABLE_SNAPSHOT_REPOSITORY = SqlTableSnapshotRepository(
    Path(os.path.dirname(__file__)),
)
