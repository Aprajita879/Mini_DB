class Table:

    def __init__(
        self,
        name,
        columns,
        column_types=None,
        constraints=None,
        database=None,
        indexes=None
    ):

        self.name = name
        self.columns = columns

        self.column_types = column_types or {
            column: "TEXT"
            for column in columns
        }

        self.constraints = constraints or {
            column: []
            for column in columns
        }

        for column in columns:

            if column not in self.constraints:
                self.constraints[column] = []

        self.rows = []
        self.database = database

        # Index definitions
        self.indexes = indexes or {}

        # Actual in-memory indexes
        # {
        #     "column": {
        #         value: [row_index, row_index]
        #     }
        # }
        self.index_data = {}

        self.rebuild_indexes()

    # ==================================================
    # INDEXING
    # ==================================================

    def create_index(self, index_name, column):

        if index_name in self.indexes:

            raise ValueError(
                f"Index '{index_name}' already exists"
            )

        if column not in self.columns:

            raise ValueError(
                f"Column '{column}' does not exist"
            )

        # Check if another index already exists
        # on the same column
        for existing_name, index_info in self.indexes.items():

            if index_info["column"] == column:

                raise ValueError(
                    f"Column '{column}' is already indexed"
                )

        self.indexes[index_name] = {
            "column": column
        }

        self.rebuild_indexes()

        if self.database:
            self.database.save()

    def drop_index(self, index_name):

        if index_name not in self.indexes:

            raise ValueError(
                f"Index '{index_name}' does not exist"
            )

        del self.indexes[index_name]

        self.rebuild_indexes()

        if self.database:
            self.database.save()

    def rebuild_indexes(self):

        self.index_data = {}

        for index_name, index_info in self.indexes.items():

            column = index_info["column"]

            if column not in self.columns:
                continue

            column_index = self.columns.index(
                column
            )

            value_map = {}

            for row_index, row in enumerate(self.rows):

                value = row[column_index]

                if value not in value_map:

                    value_map[value] = []

                value_map[value].append(
                    row_index
                )

            self.index_data[index_name] = value_map

    def get_indexed_rows(
        self,
        column,
        value
    ):

        for index_name, index_info in self.indexes.items():

            if index_info["column"] == column:

                value_map = self.index_data.get(
                    index_name,
                    {}
                )

                row_indexes = value_map.get(
                    value,
                    []
                )

                return [
                    self.rows[index]
                    for index in row_indexes
                ]

        return None

    # ==================================================
    # TYPE VALIDATION
    # ==================================================

    def validate_type(self, column, value):

        if column not in self.columns:

            raise ValueError(
                f"Column '{column}' does not exist"
            )

        data_type = self.column_types[column]

        if value is None:
            return

        if data_type == "INT":

            if (
                isinstance(value, bool)
                or not isinstance(value, int)
            ):

                raise ValueError(
                    f"Column '{column}' expects INT"
                )

        elif data_type == "FLOAT":

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
            ):

                raise ValueError(
                    f"Column '{column}' expects FLOAT"
                )

        elif data_type == "TEXT":

            if not isinstance(value, str):

                raise ValueError(
                    f"Column '{column}' expects TEXT"
                )

        else:

            raise ValueError(
                f"Unsupported data type: {data_type}"
            )

    # ==================================================
    # NOT NULL
    # ==================================================

    def validate_not_null(self, column, value):

        if "NOT NULL" in self.constraints[column]:

            if value is None:

                raise ValueError(
                    f"Column '{column}' cannot be NULL"
                )

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    def validate_primary_key(
        self,
        column,
        value,
        current_row=None
    ):

        if "PRIMARY KEY" not in self.constraints[column]:
            return

        if value is None:

            raise ValueError(
                f"Primary key '{column}' cannot be NULL"
            )

        column_index = self.columns.index(
            column
        )

        for row in self.rows:

            if (
                current_row is not None
                and row is current_row
            ):
                continue

            if row[column_index] == value:

                raise ValueError(
                    f"Duplicate primary key value: {value}"
                )

    # ==================================================
    # COMPLETE VALIDATION
    # ==================================================

    def validate_value(
        self,
        column,
        value,
        current_row=None
    ):

        self.validate_type(
            column,
            value
        )

        self.validate_not_null(
            column,
            value
        )

        self.validate_primary_key(
            column,
            value,
            current_row
        )

    # ==================================================
    # ADD COLUMN
    # ==================================================

    def add_column(
        self,
        column,
        data_type="TEXT",
        constraints=None
    ):

        if column in self.columns:

            raise ValueError(
                f"Column '{column}' already exists"
            )

        data_type = data_type.upper()

        if data_type not in [
            "INT",
            "FLOAT",
            "TEXT"
        ]:

            raise ValueError(
                f"Unsupported data type: {data_type}"
            )

        constraints = constraints or []

        if "NOT NULL" in constraints and self.rows:

            raise ValueError(
                "Cannot add NOT NULL column "
                "to a table containing existing rows"
            )

        if "PRIMARY KEY" in constraints and self.rows:

            raise ValueError(
                "Cannot add PRIMARY KEY column "
                "to a table containing existing rows"
            )

        self.columns.append(column)

        self.column_types[column] = data_type

        self.constraints[column] = constraints

        for row in self.rows:

            row.append(None)

        self.rebuild_indexes()

        if self.database:
            self.database.save()

    # ==================================================
    # INSERT
    # ==================================================

    def insert(self, row):

        if len(row) != len(self.columns):

            raise ValueError(
                "Number of values does not match "
                "number of columns"
            )

        for index, value in enumerate(row):

            column = self.columns[index]

            self.validate_value(
                column,
                value
            )

        self.rows.append(row)

        self.rebuild_indexes()

        if self.database:
            self.database.save()

    # ==================================================
    # UPDATE
    # ==================================================

    def update(
        self,
        condition,
        column,
        new_value
    ):

        if column not in self.columns:

            raise ValueError(
                f"Column '{column}' does not exist"
            )

        column_index = self.columns.index(
            column
        )

        updated_count = 0

        for row in self.rows:

            if self.check_conditions(
                row,
                condition
            ):

                self.validate_value(
                    column,
                    new_value,
                    current_row=row
                )

                row[column_index] = new_value

                updated_count += 1

        self.rebuild_indexes()

        if self.database:
            self.database.save()

        return updated_count

    # ==================================================
    # DELETE
    # ==================================================

    def delete(self, condition):

        deleted_count = 0

        remaining_rows = []

        for row in self.rows:

            if self.check_conditions(
                row,
                condition
            ):

                deleted_count += 1

            else:

                remaining_rows.append(row)

        self.rows = remaining_rows

        self.rebuild_indexes()

        if self.database:
            self.database.save()

        return deleted_count

    # ==================================================
    # SINGLE CONDITION
    # ==================================================

    def check_condition(self, row, condition):

        column, operator, value = condition

        if column not in self.columns:

            raise ValueError(
                f"Column '{column}' does not exist"
            )

        column_index = self.columns.index(
            column
        )

        row_value = row[column_index]

        if operator == "IS NULL":

            return row_value is None

        if operator == "IS NOT NULL":

            return row_value is not None

        if row_value is None:
            return False

        if value is None:
            return False

        if operator == ">":

            return row_value > value

        elif operator == "<":

            return row_value < value

        elif operator == ">=":

            return row_value >= value

        elif operator == "<=":

            return row_value <= value

        elif operator == "==":

            return row_value == value

        elif operator == "!=":

            return row_value != value

        else:

            raise ValueError(
                f"Unsupported operator: {operator}"
            )

    # ==================================================
    # AND / OR
    # ==================================================

    def check_conditions(self, row, condition):

        if condition is None:
            return True

        if isinstance(condition, tuple):

            return self.check_condition(
                row,
                condition
            )

        if isinstance(condition, list):

            logical_operator, conditions = condition[0]

            results = []

            for cond in conditions:

                results.append(
                    self.check_conditions(
                        row,
                        cond
                    )
                )

            if logical_operator == "AND":

                return all(results)

            elif logical_operator == "OR":

                return any(results)

        return False

    # ==================================================
    # AGGREGATE FUNCTIONS
    # ==================================================

    def aggregate(
        self,
        function,
        column,
        rows=None
    ):

        if rows is None:
            rows = self.rows

        function = function.upper()

        if function == "COUNT":

            if column == "*":

                return len(rows)

            values = []

            column_index = self.columns.index(
                column
            )

            for row in rows:

                if row[column_index] is not None:

                    values.append(
                        row[column_index]
                    )

            return len(values)

        if column not in self.columns:

            raise ValueError(
                f"Column '{column}' does not exist"
            )

        column_index = self.columns.index(
            column
        )

        values = []

        for row in rows:

            value = row[column_index]

            if value is not None:

                values.append(value)

        if not values:
            return None

        if function == "SUM":

            return sum(values)

        elif function == "AVG":

            return sum(values) / len(values)

        elif function == "MIN":

            return min(values)

        elif function == "MAX":

            return max(values)

        else:

            raise ValueError(
                f"Unsupported aggregate function: {function}"
            )

    # ==================================================
    # COUNT
    # ==================================================

    def count(self, condition=None):

        count = 0

        for row in self.rows:

            if self.check_conditions(
                row,
                condition
            ):

                count += 1

        return count

    # ==================================================
    # SELECT
    # ==================================================

    def select(
        self,
        columns=None,
        condition=None,
        order_by=None,
        limit=None,
        offset=0
    ):

        # ==============================================
        # USE INDEX FOR SIMPLE EQUALITY SEARCH
        # ==============================================

        if (
            isinstance(condition, tuple)
            and condition[1] == "=="
        ):

            indexed_rows = self.get_indexed_rows(
                condition[0],
                condition[2]
            )

            if indexed_rows is not None:

                filtered_rows = indexed_rows

            else:

                filtered_rows = []

                for row in self.rows:

                    if self.check_conditions(
                        row,
                        condition
                    ):

                        filtered_rows.append(row)

        else:

            filtered_rows = []

            for row in self.rows:

                if condition is not None:

                    if not self.check_conditions(
                        row,
                        condition
                    ):
                        continue

                filtered_rows.append(row)

        # ==============================================
        # ORDER BY
        # ==============================================

        if order_by is not None:

            order_column, direction = order_by

            if order_column not in self.columns:

                raise ValueError(
                    f"Column '{order_column}' does not exist"
                )

            order_index = self.columns.index(
                order_column
            )

            filtered_rows.sort(
                key=lambda row: (
                    row[order_index]
                    if row[order_index] is not None
                    else 0
                ),
                reverse=(direction == "DESC")
            )

        # ==============================================
        # OFFSET
        # ==============================================

        if offset > 0:

            filtered_rows = filtered_rows[offset:]

        # ==============================================
        # LIMIT
        # ==============================================

        if limit is not None:

            filtered_rows = filtered_rows[:limit]

        # ==============================================
        # SELECT *
        # ==============================================

        if columns is None:

            return filtered_rows

        result = []

        for row in filtered_rows:

            selected_row = []

            for column in columns:

                if column not in self.columns:

                    raise ValueError(
                        f"Column '{column}' does not exist"
                    )

                column_index = self.columns.index(
                    column
                )

                selected_row.append(
                    row[column_index]
                )

            result.append(selected_row)

        return result