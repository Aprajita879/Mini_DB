class QueryExecutor:

    def __init__(self, database):

        self.database = database

    # ==================================================
    # MAIN EXECUTOR
    # ==================================================

    def execute(self, query):

        command = query["command"]

        if command == "CREATE":

            return self.execute_create(
                query
            )

        elif command == "CREATE_INDEX":

            return self.execute_create_index(
                query
            )

        elif command == "DROP_INDEX":

            return self.execute_drop_index(
                query
            )

        elif command == "DROP":

            return self.execute_drop(
                query
            )

        elif command == "SHOW":

            return self.execute_show(
                query
            )

        elif command == "DESCRIBE":

            return self.execute_describe(
                query
            )

        elif command == "ALTER":

            return self.execute_alter(
                query
            )

        elif command == "SELECT":

            return self.execute_select(
                query
            )

        elif command == "INSERT":

            return self.execute_insert(
                query
            )

        elif command == "UPDATE":

            return self.execute_update(
                query
            )

        elif command == "DELETE":

            return self.execute_delete(
                query
            )

        else:

            raise ValueError(
                f"Unsupported command: {command}"
            )

    # ==================================================
    # GET TABLE
    # ==================================================

    def get_table(
        self,
        table_name
    ):

        table = self.database.get_table(
            table_name
        )

        if table is None:

            raise ValueError(
                f"Table '{table_name}' does not exist"
            )

        return table

    # ==================================================
    # CREATE TABLE
    # ==================================================

    def execute_create(
        self,
        query
    ):

        table_name = query["table"]

        self.database.create_table(

            table_name,

            query["columns"],

            query["column_types"],

            query["constraints"]
        )

        return (
            f"Table '{table_name}' "
            f"created successfully"
        )

    # ==================================================
    # CREATE INDEX
    # ==================================================

    def execute_create_index(
        self,
        query
    ):

        table = self.get_table(
            query["table"]
        )

        table.create_index(

            query["index"],

            query["column"]
        )

        return (
            f"Index '{query['index']}' "
            f"created successfully on "
            f"{query['table']}("
            f"{query['column']})"
        )

    # ==================================================
    # DROP INDEX
    # ==================================================

    def execute_drop_index(
        self,
        query
    ):

        table = self.get_table(
            query["table"]
        )

        table.drop_index(
            query["index"]
        )

        return (
            f"Index '{query['index']}' "
            f"dropped successfully"
        )

    # ==================================================
    # DROP TABLE
    # ==================================================

    def execute_drop(
        self,
        query
    ):

        table_name = query["table"]

        if self.database.get_table(
            table_name
        ) is None:

            raise ValueError(
                f"Table '{table_name}' does not exist"
            )

        del self.database.tables[
            table_name
        ]

        self.database.save()

        return (
            f"Table '{table_name}' "
            f"dropped successfully"
        )

    # ==================================================
    # SHOW TABLES
    # ==================================================

    def execute_show(
        self,
        query
    ):

        tables = list(
            self.database.tables.keys()
        )

        if not tables:

            return "No tables found"

        return tables

    # ==================================================
    # DESCRIBE
    # ==================================================

    def execute_describe(
        self,
        query
    ):

        table = self.get_table(
            query["table"]
        )

        result = []

        for column in table.columns:

            result.append([

                column,

                table.column_types[
                    column
                ],

                table.constraints[
                    column
                ]
            ])

        return result

    # ==================================================
    # ALTER TABLE
    # ==================================================

    def execute_alter(
        self,
        query
    ):

        table = self.get_table(
            query["table"]
        )

        column = query["column"]

        data_type = query["data_type"]

        constraints = query["constraints"]

        if "PRIMARY KEY" in constraints:

            for existing_column in table.columns:

                if (
                    "PRIMARY KEY"
                    in table.constraints[
                        existing_column
                    ]
                ):

                    raise ValueError(
                        "Table already has a PRIMARY KEY"
                    )

        table.add_column(

            column,

            data_type,

            constraints
        )

        return (
            f"Column '{column}' "
            f"added successfully "
            f"as {data_type}"
        )

    # ==================================================
    # SELECT
    # ==================================================

    def execute_select(
        self,
        query
    ):

        # JOIN
        if query.get("join"):

            return self.execute_join(
                query
            )

        table = self.get_table(
            query["table"]
        )

        condition = query.get(
            "condition"
        )

        filtered_rows = []

        for row in table.rows:

            if table.check_conditions(
                row,
                condition
            ):

                filtered_rows.append(
                    row
                )

        # GROUP BY
        if query.get("group_by"):

            return self.execute_group_by(

                table,

                query,

                filtered_rows
            )

        columns = query["columns"]

        # AGGREGATE
        if self.contains_aggregate(
            columns
        ):

            return self.execute_aggregate(

                table,

                columns,

                filtered_rows
            )

        if columns == ["*"]:

            columns = None

        return table.select(

            columns=columns,

            condition=condition,

            order_by=query.get(
                "order_by"
            ),

            limit=query.get(
                "limit"
            ),

            offset=query.get(
                "offset",
                0
            )
        )

    # ==================================================
    # CHECK AGGREGATE
    # ==================================================

    def contains_aggregate(
        self,
        columns
    ):

        for column in columns:

            if isinstance(
                column,
                dict
            ):

                if column.get(
                    "type"
                ) == "aggregate":

                    return True

        return False

    # ==================================================
    # AGGREGATE
    # ==================================================

    def execute_aggregate(
        self,
        table,
        columns,
        rows
    ):

        result = []

        for column in columns:

            if not isinstance(
                column,
                dict
            ):

                raise ValueError(
                    "Normal columns cannot be mixed "
                    "with aggregate functions without "
                    "GROUP BY"
                )

            function = column[
                "function"
            ]

            target_column = column[
                "column"
            ]

            value = table.aggregate(

                function,

                target_column,

                rows
            )

            result.append(
                value
            )

        return [result]

    # ==================================================
    # GROUP BY
    # ==================================================

    def execute_group_by(
        self,
        table,
        query,
        rows
    ):

        group_column = query[
            "group_by"
        ]

        if group_column not in table.columns:

            raise ValueError(
                f"Column '{group_column}' "
                f"does not exist"
            )

        group_index = table.columns.index(
            group_column
        )

        groups = {}

        for row in rows:

            key = row[
                group_index
            ]

            if key not in groups:

                groups[key] = []

            groups[key].append(
                row
            )

        result = []

        for group_value, group_rows in groups.items():

            having = query.get(
                "having"
            )

            if having:

                aggregate_value = (
                    table.aggregate(

                        having["function"],

                        having["column"],

                        group_rows
                    )
                )

                if not self.compare(

                    aggregate_value,

                    having["operator"],

                    having["value"]
                ):

                    continue

            output_row = []

            for column in query[
                "columns"
            ]:

                if isinstance(
                    column,
                    dict
                ):

                    value = table.aggregate(

                        column["function"],

                        column["column"],

                        group_rows
                    )

                    output_row.append(
                        value
                    )

                elif column == group_column:

                    output_row.append(
                        group_value
                    )

                elif column in table.columns:

                    column_index = (
                        table.columns.index(
                            column
                        )
                    )

                    output_row.append(
                        group_rows[0][
                            column_index
                        ]
                    )

                else:

                    raise ValueError(
                        f"Column '{column}' "
                        f"does not exist"
                    )

            result.append(
                output_row
            )

        # ORDER BY
        order_by = query.get(
            "order_by"
        )

        if order_by:

            order_column, direction = (
                order_by
            )

            if order_column in table.columns:

                order_index = (
                    table.columns.index(
                        order_column
                    )
                )

                result.sort(

                    key=lambda row: (

                        row[order_index]

                        if row[order_index]
                        is not None

                        else 0
                    ),

                    reverse=(
                        direction == "DESC"
                    )
                )

        # OFFSET
        offset = query.get(
            "offset",
            0
        )

        if offset:

            result = result[
                offset:
            ]

        # LIMIT
        limit = query.get(
            "limit"
        )

        if limit is not None:

            result = result[
                :limit
            ]

        return result

    # ==================================================
    # COMPARE
    # ==================================================

    def compare(
        self,
        left,
        operator,
        right
    ):

        if left is None:

            return False

        if operator == ">":

            return left > right

        elif operator == "<":

            return left < right

        elif operator == ">=":

            return left >= right

        elif operator == "<=":

            return left <= right

        elif operator == "==":

            return left == right

        elif operator == "!=":

            return left != right

        else:

            raise ValueError(
                f"Unsupported operator: {operator}"
            )

    # ==================================================
    # INNER JOIN
    # ==================================================

    def execute_join(
        self,
        query
    ):

        left_table = self.get_table(
            query["table"]
        )

        right_table = self.get_table(
            query["join"]["table"]
        )

        left_reference = query[
            "join"
        ]["left"]

        right_reference = query[
            "join"
        ]["right"]

        left_table_name, left_column = (
            left_reference.split(".")
        )

        right_table_name, right_column = (
            right_reference.split(".")
        )

        if left_table_name != left_table.name:

            raise ValueError(
                "JOIN left table does not match "
                "FROM table"
            )

        if right_table_name != right_table.name:

            raise ValueError(
                "JOIN right table does not match "
                "joined table"
            )

        if left_column not in left_table.columns:

            raise ValueError(
                f"Column '{left_column}' "
                f"does not exist"
            )

        if right_column not in right_table.columns:

            raise ValueError(
                f"Column '{right_column}' "
                f"does not exist"
            )

        left_index = (
            left_table.columns.index(
                left_column
            )
        )

        right_index = (
            right_table.columns.index(
                right_column
            )
        )

        joined_rows = []

        for left_row in left_table.rows:

            for right_row in right_table.rows:

                if (
                    left_row[left_index]
                    ==
                    right_row[right_index]
                ):

                    combined = (
                        left_row
                        +
                        right_row
                    )

                    joined_rows.append(
                        combined
                    )

        combined_columns = []

        for column in left_table.columns:

            combined_columns.append(

                f"{left_table.name}."
                f"{column}"
            )

        for column in right_table.columns:

            combined_columns.append(

                f"{right_table.name}."
                f"{column}"
            )

        # WHERE
        condition = query.get(
            "condition"
        )

        if condition:

            filtered_rows = []

            for row in joined_rows:

                if self.check_join_condition(

                    row,

                    combined_columns,

                    condition
                ):

                    filtered_rows.append(
                        row
                    )

            joined_rows = filtered_rows

        result = []

        for row in joined_rows:

            selected_row = []

            for column in query[
                "columns"
            ]:

                if column == "*":

                    selected_row.extend(
                        row
                    )

                    continue

                if isinstance(
                    column,
                    dict
                ):

                    raise ValueError(
                        "Aggregate functions with JOIN "
                        "are not supported in this version"
                    )

                if column not in combined_columns:

                    raise ValueError(
                        f"Column '{column}' "
                        f"does not exist in joined result"
                    )

                index = combined_columns.index(
                    column
                )

                selected_row.append(
                    row[index]
                )

            result.append(
                selected_row
            )

        # ORDER BY
        order_by = query.get(
            "order_by"
        )

        if order_by:

            order_column, direction = (
                order_by
            )

            if order_column not in combined_columns:

                raise ValueError(
                    f"Column '{order_column}' "
                    f"does not exist in joined result"
                )

            order_index = combined_columns.index(
                order_column
            )

            result.sort(

                key=lambda row: (

                    row[order_index]

                    if row[order_index]
                    is not None

                    else 0
                ),

                reverse=(
                    direction == "DESC"
                )
            )

        # OFFSET
        offset = query.get(
            "offset",
            0
        )

        if offset:

            result = result[
                offset:
            ]

        # LIMIT
        limit = query.get(
            "limit"
        )

        if limit is not None:

            result = result[
                :limit
            ]

        return result

    # ==================================================
    # JOIN CONDITION
    # ==================================================

    def check_join_condition(
        self,
        row,
        columns,
        condition
    ):

        if isinstance(
            condition,
            tuple
        ):

            column, operator, value = (
                condition
            )

            if column not in columns:

                raise ValueError(
                    f"Column '{column}' "
                    f"does not exist"
                )

            index = columns.index(
                column
            )

            row_value = row[index]

            if operator == "IS NULL":

                return row_value is None

            if operator == "IS NOT NULL":

                return row_value is not None

            if (
                row_value is None
                or value is None
            ):

                return False

            return self.compare(

                row_value,

                operator,

                value
            )

        if isinstance(
            condition,
            list
        ):

            logical_operator, conditions = (
                condition[0]
            )

            results = []

            for cond in conditions:

                results.append(

                    self.check_join_condition(

                        row,

                        columns,

                        cond
                    )
                )

            if logical_operator == "AND":

                return all(results)

            if logical_operator == "OR":

                return any(results)

        return False

    # ==================================================
    # INSERT
    # ==================================================

    def execute_insert(
        self,
        query
    ):

        table = self.get_table(
            query["table"]
        )

        table.insert(
            query["values"]
        )

        return (
            "Row inserted successfully"
        )

    # ==================================================
    # UPDATE
    # ==================================================

    def execute_update(
        self,
        query
    ):

        table = self.get_table(
            query["table"]
        )

        updated_count = table.update(

            query["condition"],

            query["column"],

            query["value"]
        )

        return (
            f"{updated_count} "
            f"row(s) updated"
        )

    # ==================================================
    # DELETE
    # ==================================================

    def execute_delete(
        self,
        query
    ):

        table = self.get_table(
            query["table"]
        )

        deleted_count = table.delete(
            query["condition"]
        )

        return (
            f"{deleted_count} "
            f"row(s) deleted"
        )