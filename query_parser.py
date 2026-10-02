import re


class QueryParser:

    # ==================================================
    # MAIN PARSER
    # ==================================================

    def parse(self, query):

        query = query.strip()

        if not query:

            raise ValueError(
                "Empty query"
            )

        command = query.split()[0].upper()

        if command == "CREATE":

            if re.match(
                r"CREATE\s+INDEX",
                query,
                re.IGNORECASE
            ):

                return self.parse_create_index(
                    query
                )

            return self.parse_create(
                query
            )

        elif command == "DROP":

            return self.parse_drop(
                query
            )

        elif command == "SHOW":

            return self.parse_show(
                query
            )

        elif command == "DESCRIBE":

            return self.parse_describe(
                query
            )

        elif command == "ALTER":

            return self.parse_alter(
                query
            )

        elif command == "SELECT":

            return self.parse_select(
                query
            )

        elif command == "INSERT":

            return self.parse_insert(
                query
            )

        elif command == "UPDATE":

            return self.parse_update(
                query
            )

        elif command == "DELETE":

            return self.parse_delete(
                query
            )

        else:

            raise ValueError(
                f"Unsupported command: {command}"
            )

    # ==================================================
    # CREATE TABLE
    # ==================================================

    def parse_create(self, query):

        pattern = (
            r"CREATE\s+TABLE\s+(\w+)"
            r"\s*\((.*?)\)"
        )

        match = re.match(
            pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid CREATE TABLE query"
            )

        table = match.group(1)

        columns_text = match.group(2)

        raw_columns = columns_text.split(",")

        columns = []

        column_types = {}

        constraints = {}

        for definition in raw_columns:

            definition = definition.strip()

            parts = definition.split()

            if len(parts) < 1:

                raise ValueError(
                    "Invalid column definition"
                )

            column = parts[0]

            if not re.match(
                r"^[A-Za-z_][A-Za-z0-9_]*$",
                column
            ):

                raise ValueError(
                    f"Invalid column name: '{column}'"
                )

            if column in columns:

                raise ValueError(
                    "Duplicate column names are not allowed"
                )

            if len(parts) >= 2:

                data_type = parts[1].upper()

            else:

                data_type = "TEXT"

            if data_type not in [
                "INT",
                "FLOAT",
                "TEXT"
            ]:

                raise ValueError(
                    f"Unsupported data type: '{data_type}'"
                )

            column_constraints = []

            remaining = [
                part.upper()
                for part in parts[2:]
            ]

            i = 0

            while i < len(remaining):

                if remaining[i] == "PRIMARY":

                    if (
                        i + 1 < len(remaining)
                        and remaining[i + 1] == "KEY"
                    ):

                        column_constraints.append(
                            "PRIMARY KEY"
                        )

                        i += 2

                    else:

                        raise ValueError(
                            "Invalid PRIMARY KEY constraint"
                        )

                elif remaining[i] == "NOT":

                    if (
                        i + 1 < len(remaining)
                        and remaining[i + 1] == "NULL"
                    ):

                        column_constraints.append(
                            "NOT NULL"
                        )

                        i += 2

                    else:

                        raise ValueError(
                            "Invalid NOT NULL constraint"
                        )

                else:

                    raise ValueError(
                        f"Unknown constraint: "
                        f"'{remaining[i]}'"
                    )

            if "PRIMARY KEY" in column_constraints:

                for existing_column in constraints:

                    if (
                        "PRIMARY KEY"
                        in constraints[existing_column]
                    ):

                        raise ValueError(
                            "Only one PRIMARY KEY is supported"
                        )

            columns.append(column)

            column_types[column] = data_type

            constraints[column] = column_constraints

        if not columns:

            raise ValueError(
                "Table must have at least one column"
            )

        return {

            "command": "CREATE",

            "table": table,

            "columns": columns,

            "column_types": column_types,

            "constraints": constraints
        }

    # ==================================================
    # CREATE INDEX
    # ==================================================

    def parse_create_index(self, query):

        pattern = (
            r"CREATE\s+INDEX\s+(\w+)"
            r"\s+ON\s+(\w+)"
            r"\s*\(\s*(\w+)\s*\)"
        )

        match = re.match(
            pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid CREATE INDEX query"
            )

        return {

            "command": "CREATE_INDEX",

            "index": match.group(1),

            "table": match.group(2),

            "column": match.group(3)
        }

    # ==================================================
    # DROP
    # ==================================================

    def parse_drop(self, query):

        # DROP INDEX
        index_pattern = (
            r"DROP\s+INDEX\s+(\w+)"
            r"\s+ON\s+(\w+)"
        )

        index_match = re.match(
            index_pattern,
            query,
            re.IGNORECASE
        )

        if index_match:

            return {

                "command": "DROP_INDEX",

                "index": index_match.group(1),

                "table": index_match.group(2)
            }

        # DROP TABLE
        table_pattern = (
            r"DROP\s+TABLE\s+(\w+)"
        )

        match = re.match(
            table_pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid DROP query"
            )

        return {

            "command": "DROP",

            "table": match.group(1)
        }

    # ==================================================
    # SHOW
    # ==================================================

    def parse_show(self, query):

        pattern = r"SHOW\s+TABLES"

        match = re.match(
            pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid SHOW TABLES query"
            )

        return {
            "command": "SHOW"
        }

    # ==================================================
    # DESCRIBE
    # ==================================================

    def parse_describe(self, query):

        pattern = r"DESCRIBE\s+(\w+)"

        match = re.match(
            pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid DESCRIBE query"
            )

        return {

            "command": "DESCRIBE",

            "table": match.group(1)
        }

    # ==================================================
    # ALTER
    # ==================================================

    def parse_alter(self, query):

        pattern = (
            r"ALTER\s+TABLE\s+(\w+)"
            r"\s+ADD\s+(\w+)"
            r"(?:\s+(INT|FLOAT|TEXT))?"
            r"(?:\s+(PRIMARY\s+KEY|NOT\s+NULL))?"
        )

        match = re.match(
            pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid ALTER TABLE query"
            )

        table = match.group(1)

        column = match.group(2)

        data_type = (
            match.group(3) or "TEXT"
        ).upper()

        constraint_text = match.group(4)

        column_constraints = []

        if constraint_text:

            constraint_text = (
                constraint_text.upper()
            )

            if constraint_text == "PRIMARY KEY":

                column_constraints.append(
                    "PRIMARY KEY"
                )

            elif constraint_text == "NOT NULL":

                column_constraints.append(
                    "NOT NULL"
                )

        return {

            "command": "ALTER",

            "table": table,

            "operation": "ADD",

            "column": column,

            "data_type": data_type,

            "constraints": column_constraints
        }

    # ==================================================
    # SELECT
    # ==================================================

    def parse_select(self, query):

        # ==============================================
        # INNER JOIN
        # ==============================================

        join_pattern = r"""
            SELECT\s+(?P<columns>.+?)
            \s+FROM\s+(?P<table1>\w+)
            \s+INNER\s+JOIN\s+(?P<table2>\w+)
            \s+ON\s+
            (?P<left>\w+\.\w+)
            \s*=\s*
            (?P<right>\w+\.\w+)
            (?:\s+WHERE\s+(?P<where>.*?))?
            (?:\s+ORDER\s+BY\s+
                (?P<order_column>\w+(?:\.\w+)?)
                (?:\s+(?P<direction>ASC|DESC))?
            )?
            (?:\s+LIMIT\s+(?P<limit>\d+))?
            (?:\s+OFFSET\s+(?P<offset>\d+))?
            $
        """

        join_match = re.match(
            join_pattern,
            query,
            re.IGNORECASE | re.VERBOSE
        )

        if join_match:

            columns_text = (
                join_match.group(
                    "columns"
                ).strip()
            )

            columns = self.parse_select_columns(
                columns_text
            )

            condition = None

            where = join_match.group(
                "where"
            )

            if where:

                condition = self.parse_condition(
                    where
                )

            order_by = None

            if join_match.group(
                "order_column"
            ):

                direction = (
                    join_match.group(
                        "direction"
                    )
                    or "ASC"
                )

                order_by = (

                    join_match.group(
                        "order_column"
                    ),

                    direction.upper()
                )

            limit = None

            if join_match.group("limit"):

                limit = int(
                    join_match.group("limit")
                )

            offset = 0

            if join_match.group("offset"):

                offset = int(
                    join_match.group("offset")
                )

            return {

                "command": "SELECT",

                "columns": columns,

                "table": join_match.group(
                    "table1"
                ),

                "condition": condition,

                "order_by": order_by,

                "limit": limit,

                "offset": offset,

                "join": {

                    "type": "INNER",

                    "table": join_match.group(
                        "table2"
                    ),

                    "left": join_match.group(
                        "left"
                    ),

                    "right": join_match.group(
                        "right"
                    )
                }
            }

        # ==============================================
        # GROUP BY
        # ==============================================

        group_pattern = r"""
            SELECT\s+(?P<columns>.+?)
            \s+FROM\s+(?P<table>\w+)
            (?:\s+WHERE\s+(?P<where>.*?))?
            \s+GROUP\s+BY\s+(?P<group_by>\w+)
            (?:\s+HAVING\s+(?P<having>.*?))?
            (?:\s+ORDER\s+BY\s+
                (?P<order_column>\w+)
                (?:\s+(?P<direction>ASC|DESC))?
            )?
            (?:\s+LIMIT\s+(?P<limit>\d+))?
            (?:\s+OFFSET\s+(?P<offset>\d+))?
            $
        """

        group_match = re.match(
            group_pattern,
            query,
            re.IGNORECASE | re.VERBOSE
        )

        if group_match:

            columns = self.parse_select_columns(
                group_match.group(
                    "columns"
                ).strip()
            )

            condition = None

            where = group_match.group(
                "where"
            )

            if where:

                condition = self.parse_condition(
                    where
                )

            having = None

            if group_match.group(
                "having"
            ):

                having = self.parse_having(
                    group_match.group(
                        "having"
                    )
                )

            order_by = None

            if group_match.group(
                "order_column"
            ):

                direction = (
                    group_match.group(
                        "direction"
                    )
                    or "ASC"
                )

                order_by = (

                    group_match.group(
                        "order_column"
                    ),

                    direction.upper()
                )

            limit = None

            if group_match.group("limit"):

                limit = int(
                    group_match.group("limit")
                )

            offset = 0

            if group_match.group("offset"):

                offset = int(
                    group_match.group("offset")
                )

            return {

                "command": "SELECT",

                "columns": columns,

                "table": group_match.group(
                    "table"
                ),

                "condition": condition,

                "order_by": order_by,

                "limit": limit,

                "offset": offset,

                "group_by": group_match.group(
                    "group_by"
                ),

                "having": having,

                "join": None
            }

        # ==============================================
        # NORMAL SELECT
        # ==============================================

        pattern = r"""
            SELECT\s+(?P<columns>.+?)
            \s+FROM\s+(?P<table>\w+)
            (?:\s+WHERE\s+(?P<where>.*?))?
            (?:\s+ORDER\s+BY\s+
                (?P<order_column>\w+)
                (?:\s+(?P<direction>ASC|DESC))?
            )?
            (?:\s+LIMIT\s+(?P<limit>\d+))?
            (?:\s+OFFSET\s+(?P<offset>\d+))?
            $
        """

        match = re.match(
            pattern,
            query,
            re.IGNORECASE | re.VERBOSE
        )

        if not match:

            raise ValueError(
                "Invalid SELECT query"
            )

        columns = self.parse_select_columns(
            match.group(
                "columns"
            ).strip()
        )

        condition = None

        where = match.group(
            "where"
        )

        if where:

            condition = self.parse_condition(
                where
            )

        order_by = None

        if match.group(
            "order_column"
        ):

            direction = (
                match.group(
                    "direction"
                )
                or "ASC"
            )

            order_by = (

                match.group(
                    "order_column"
                ),

                direction.upper()
            )

        limit = None

        if match.group("limit"):

            limit = int(
                match.group("limit")
            )

        offset = 0

        if match.group("offset"):

            offset = int(
                match.group("offset")
            )

        return {

            "command": "SELECT",

            "columns": columns,

            "table": match.group(
                "table"
            ),

            "condition": condition,

            "order_by": order_by,

            "limit": limit,

            "offset": offset,

            "group_by": None,

            "having": None,

            "join": None
        }

    # ==================================================
    # SELECT COLUMNS
    # ==================================================

    def parse_select_columns(
        self,
        columns_text
    ):

        columns = []

        for column in columns_text.split(","):

            column = column.strip()

            aggregate_match = re.fullmatch(
                r"(COUNT|SUM|AVG|MIN|MAX)"
                r"\s*\(\s*(\*|\w+)\s*\)",
                column,
                re.IGNORECASE
            )

            if aggregate_match:

                function = (
                    aggregate_match.group(
                        1
                    ).upper()
                )

                target = aggregate_match.group(
                    2
                )

                columns.append({

                    "type": "aggregate",

                    "function": function,

                    "column": target
                })

                continue

            if column == "*":

                columns.append("*")

                continue

            if "." in column:

                parts = column.split(".")

                if len(parts) != 2:

                    raise ValueError(
                        f"Invalid column: '{column}'"
                    )

                columns.append(column)

                continue

            if not re.match(
                r"^[A-Za-z_][A-Za-z0-9_]*$",
                column
            ):

                raise ValueError(
                    f"Invalid column name: '{column}'"
                )

            columns.append(column)

        if not columns:

            raise ValueError(
                "No columns specified"
            )

        return columns

    # ==================================================
    # HAVING
    # ==================================================

    def parse_having(self, condition):

        pattern = (
            r"^\s*"
            r"(COUNT|SUM|AVG|MIN|MAX)"
            r"\s*\(\s*(\*|\w+)\s*\)"
            r"\s*(>=|<=|!=|=|>|<)"
            r"\s*(.+)"
            r"\s*$"
        )

        match = re.match(
            pattern,
            condition,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid HAVING condition"
            )

        function = match.group(
            1
        ).upper()

        column = match.group(2)

        operator = match.group(3)

        value = self.convert_value(
            match.group(4)
        )

        if operator == "=":

            operator = "=="

        return {

            "function": function,

            "column": column,

            "operator": operator,

            "value": value
        }

    # ==================================================
    # WHERE CONDITION
    # ==================================================

    def parse_condition(
        self,
        condition
    ):

        condition = condition.strip()

        # IS NOT NULL
        match = re.match(
            r"^(\w+)\s+IS\s+NOT\s+NULL$",
            condition,
            re.IGNORECASE
        )

        if match:

            return (
                match.group(1),
                "IS NOT NULL",
                None
            )

        # IS NULL
        match = re.match(
            r"^(\w+)\s+IS\s+NULL$",
            condition,
            re.IGNORECASE
        )

        if match:

            return (
                match.group(1),
                "IS NULL",
                None
            )

        # AND
        if re.search(
            r"\s+AND\s+",
            condition,
            re.IGNORECASE
        ):

            parts = re.split(
                r"\s+AND\s+",
                condition,
                flags=re.IGNORECASE
            )

            conditions = []

            for part in parts:

                conditions.append(
                    self.parse_condition(
                        part
                    )
                )

            return [
                ("AND", conditions)
            ]

        # OR
        if re.search(
            r"\s+OR\s+",
            condition,
            re.IGNORECASE
        ):

            parts = re.split(
                r"\s+OR\s+",
                condition,
                flags=re.IGNORECASE
            )

            conditions = []

            for part in parts:

                conditions.append(
                    self.parse_condition(
                        part
                    )
                )

            return [
                ("OR", conditions)
            ]

        return self.parse_single_condition(
            condition
        )

    # ==================================================
    # SINGLE CONDITION
    # ==================================================

    def parse_single_condition(
        self,
        condition
    ):

        pattern = (
            r"(\w+)\s*"
            r"(>=|<=|!=|=|>|<)\s*"
            r"(.+)"
        )

        match = re.match(
            pattern,
            condition.strip()
        )

        if not match:

            raise ValueError(
                "Invalid WHERE condition"
            )

        column = match.group(1)

        operator = match.group(2)

        value = self.convert_value(
            match.group(3)
        )

        if operator == "=":

            operator = "=="

        return (
            column,
            operator,
            value
        )

    # ==================================================
    # INSERT
    # ==================================================

    def parse_insert(self, query):

        pattern = (
            r"INSERT\s+INTO\s+(\w+)"
            r"\s+VALUES\s*\((.*)\)"
        )

        match = re.match(
            pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid INSERT query"
            )

        table = match.group(1)

        values_text = match.group(2)

        values = []

        for value in values_text.split(","):

            values.append(
                self.convert_value(
                    value.strip()
                )
            )

        return {

            "command": "INSERT",

            "table": table,

            "values": values
        }

    # ==================================================
    # UPDATE
    # ==================================================

    def parse_update(self, query):

        pattern = (
            r"UPDATE\s+(\w+)"
            r"\s+SET\s+(\w+)\s*=\s*(.+?)"
            r"\s+WHERE\s+(.+)"
        )

        match = re.match(
            pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid UPDATE query"
            )

        table = match.group(1)

        column = match.group(2)

        value = self.convert_value(
            match.group(3)
        )

        condition = self.parse_condition(
            match.group(4)
        )

        return {

            "command": "UPDATE",

            "table": table,

            "column": column,

            "value": value,

            "condition": condition
        }

    # ==================================================
    # DELETE
    # ==================================================

    def parse_delete(self, query):

        pattern = (
            r"DELETE\s+FROM\s+(\w+)"
            r"\s+WHERE\s+(.+)"
        )

        match = re.match(
            pattern,
            query,
            re.IGNORECASE
        )

        if not match:

            raise ValueError(
                "Invalid DELETE query"
            )

        table = match.group(1)

        condition = self.parse_condition(
            match.group(2)
        )

        return {

            "command": "DELETE",

            "table": table,

            "condition": condition
        }

    # ==================================================
    # CONVERT VALUE
    # ==================================================

    def convert_value(
        self,
        value
    ):

        value = value.strip()

        if value.upper() == "NULL":

            return None

        if (
            len(value) >= 2
            and value[0] in ["'", '"']
            and value[-1] == value[0]
        ):

            return value[1:-1]

        try:

            return int(value)

        except ValueError:

            pass

        try:

            return float(value)

        except ValueError:

            pass

        return value