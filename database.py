from table import Table
from storage import Storage


class Database:

    def __init__(self):

        self.storage = Storage()
        self.tables = {}

        self.load()

    # ==================================================
    # CREATE TABLE
    # ==================================================

    def create_table(
        self,
        name,
        columns,
        column_types=None,
        constraints=None
    ):

        if name in self.tables:

            raise ValueError(
                f"Table '{name}' already exists"
            )

        self.tables[name] = Table(
            name,
            columns,
            column_types,
            constraints,
            self
        )

        self.save()

    # ==================================================
    # GET TABLE
    # ==================================================

    def get_table(self, name):

        return self.tables.get(name)

    # ==================================================
    # SAVE DATABASE
    # ==================================================

    def save(self):

        data = {}

        for name, table in self.tables.items():

            data[name] = {

                "columns": table.columns,

                "column_types": table.column_types,

                "constraints": table.constraints,

                "rows": table.rows,

                # Save index definitions
                "indexes": table.indexes
            }

        self.storage.save(data)

    # ==================================================
    # LOAD DATABASE
    # ==================================================

    def load(self):

        data = self.storage.load()

        for name, table_data in data.items():

            columns = table_data["columns"]

            rows = table_data["rows"]

            # ==========================================
            # COLUMN TYPES
            # ==========================================

            if "column_types" in table_data:

                column_types = table_data[
                    "column_types"
                ]

            else:

                column_types = {}

                for index, column in enumerate(columns):

                    inferred_type = "TEXT"

                    for row in rows:

                        value = row[index]

                        if value is not None:

                            if (
                                isinstance(value, int)
                                and not isinstance(
                                    value,
                                    bool
                                )
                            ):

                                inferred_type = "INT"

                            elif isinstance(
                                value,
                                float
                            ):

                                inferred_type = "FLOAT"

                            else:

                                inferred_type = "TEXT"

                            break

                    column_types[column] = inferred_type

            # ==========================================
            # CONSTRAINTS
            # ==========================================

            if "constraints" in table_data:

                constraints = table_data[
                    "constraints"
                ]

            else:

                constraints = {
                    column: []
                    for column in columns
                }

            # ==========================================
            # INDEXES
            # ==========================================

            indexes = table_data.get(
                "indexes",
                {}
            )

            # ==========================================
            # CREATE TABLE
            # ==========================================

            table = Table(
                name,
                columns,
                column_types,
                constraints,
                self,
                indexes
            )

            # Restore rows
            table.rows = rows

            # Rebuild indexes using restored rows
            table.rebuild_indexes()

            self.tables[name] = table