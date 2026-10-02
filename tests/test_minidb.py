import unittest

from database import Database
from query_parser import QueryParser
from query_executor import QueryExecutor


class TestMiniDB(unittest.TestCase):

    # ==================================================
    # SETUP
    # ==================================================

    def setUp(self):
        self.db = Database()
        self.parser = QueryParser()
        self.executor = QueryExecutor(self.db)

        try:
            self.execute_sql("DROP TABLE students")
        except Exception:
            pass

        self.execute_sql(
            "CREATE TABLE students (id INT PRIMARY KEY, name TEXT, marks INT, city TEXT)"
        )

    # ==================================================
    # HELPER
    # ==================================================

    def execute_sql(self, sql):
        query = self.parser.parse(sql)
        return self.executor.execute(query)

    # ==================================================
    # CREATE TABLE / SHOW TABLES
    # ==================================================

    def test_create_table(self):

        result = self.execute_sql("SHOW TABLES")

        self.assertIn("students", result)

    # ==================================================
    # INSERT
    # ==================================================

    def test_insert(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        result = self.execute_sql(
            "SELECT * FROM students"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1], "Aprajita")

    # ==================================================
    # MULTIPLE INSERT
    # ==================================================

    def test_multiple_insert(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(3, "Priya", 92, "Delhi")'
        )

        result = self.execute_sql(
            "SELECT * FROM students"
        )

        self.assertEqual(len(result), 3)

    # ==================================================
    # SELECT
    # ==================================================

    def test_select(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        result = self.execute_sql(
            "SELECT name, marks FROM students"
        )

        self.assertEqual(result[0][0], "Aprajita")
        self.assertEqual(result[0][1], 95)

    # ==================================================
    # WHERE
    # ==================================================

    def test_where(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        result = self.execute_sql(
            "SELECT * FROM students WHERE marks > 80"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Aprajita")

    # ==================================================
    # AND
    # ==================================================

    def test_where_and(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        result = self.execute_sql(
            "SELECT * FROM students WHERE marks > 80 AND id < 3"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Aprajita")

    # ==================================================
    # OR
    # ==================================================

    def test_where_or(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        result = self.execute_sql(
            "SELECT * FROM students WHERE marks > 90 OR city = 'Mumbai'"
        )

        self.assertEqual(len(result), 2)

    # ==================================================
    # ORDER BY
    # ==================================================

    def test_order_by(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(3, "Priya", 92, "Delhi")'
        )

        result = self.execute_sql(
            "SELECT * FROM students ORDER BY marks DESC"
        )

        self.assertEqual(result[0][1], "Aprajita")
        self.assertEqual(result[1][1], "Priya")

    # ==================================================
    # LIMIT
    # ==================================================

    def test_limit(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(3, "Priya", 92, "Delhi")'
        )

        result = self.execute_sql(
            "SELECT * FROM students ORDER BY marks DESC LIMIT 2"
        )

        self.assertEqual(len(result), 2)

    # ==================================================
    # OFFSET
    # ==================================================

    def test_offset(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(3, "Priya", 92, "Delhi")'
        )

        result = self.execute_sql(
            "SELECT * FROM students ORDER BY marks DESC LIMIT 1 OFFSET 1"
        )

        self.assertEqual(result[0][1], "Priya")

    # ==================================================
    # UPDATE
    # ==================================================

    def test_update(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 85, "Delhi")'
        )

        self.execute_sql(
            "UPDATE students SET marks = 95 WHERE id = 1"
        )

        result = self.execute_sql(
            "SELECT * FROM students WHERE id = 1"
        )

        self.assertEqual(result[0][2], 95)

    # ==================================================
    # DELETE
    # ==================================================

    def test_delete(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        self.execute_sql(
            "DELETE FROM students WHERE id = 1"
        )

        result = self.execute_sql(
            "SELECT * FROM students"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Rahul")

    # ==================================================
    # COUNT
    # ==================================================

    def test_count(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        result = self.execute_sql(
            "SELECT COUNT(*) FROM students"
        )

        self.assertEqual(result[0][0], 2)

    # ==================================================
    # SUM
    # ==================================================

    def test_sum(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        result = self.execute_sql(
            "SELECT SUM(marks) FROM students"
        )

        self.assertEqual(result[0][0], 173)

    # ==================================================
    # AVG
    # ==================================================

    def test_avg(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 85, "Mumbai")'
        )

        result = self.execute_sql(
            "SELECT AVG(marks) FROM students"
        )

        self.assertEqual(result[0][0], 90)

    # ==================================================
    # MIN
    # ==================================================

    def test_min(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        result = self.execute_sql(
            "SELECT MIN(marks) FROM students"
        )

        self.assertEqual(result[0][0], 78)

    # ==================================================
    # MAX
    # ==================================================

    def test_max(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        result = self.execute_sql(
            "SELECT MAX(marks) FROM students"
        )

        self.assertEqual(result[0][0], 95)

    # ==================================================
    # GROUP BY
    # ==================================================

    def test_group_by(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(2, "Rahul", 78, "Mumbai")'
        )

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(3, "Priya", 92, "Delhi")'
        )

        result = self.execute_sql(
            "SELECT city, COUNT(*) FROM students GROUP BY city"
        )

        self.assertEqual(len(result), 2)

    # ==================================================
    # SHOW TABLES
    # ==================================================

    def test_show_tables(self):

        result = self.execute_sql(
            "SHOW TABLES"
        )

        self.assertIn("students", result)

    # ==================================================
    # DESCRIBE
    # ==================================================

    def test_describe(self):

        result = self.execute_sql(
            "DESCRIBE students"
        )

        self.assertTrue(len(result) > 0)

    # ==================================================
    # ALTER TABLE
    # ==================================================

    def test_alter_table(self):

        self.execute_sql(
            "ALTER TABLE students ADD age INT"
        )

        result = self.execute_sql(
            "DESCRIBE students"
        )

        column_names = [
            row[0]
            for row in result
        ]

        self.assertIn("age", column_names)

    # ==================================================
    # CREATE INDEX
    # ==================================================

    def test_create_index(self):

        result = self.execute_sql(
            "CREATE INDEX idx_students_city ON students(city)"
        )

        self.assertIsNotNone(result)

    # ==================================================
    # DROP INDEX
    # ==================================================

    def test_drop_index(self):

        self.execute_sql(
            "CREATE INDEX idx_students_city ON students(city)"
        )

        result = self.execute_sql(
            "DROP INDEX idx_students_city ON students"
        )

        self.assertIsNotNone(result)

    # ==================================================
    # PRIMARY KEY DUPLICATE
    # ==================================================

    def test_duplicate_primary_key(self):

        self.execute_sql(
            'INSERT INTO students VALUES '
            '(1, "Aprajita", 95, "Delhi")'
        )

        with self.assertRaises(Exception):
            self.execute_sql(
                'INSERT INTO students VALUES '
                '(1, "Rahul", 80, "Mumbai")'
            )


# ======================================================
# RUN TESTS
# ======================================================

if __name__ == "__main__":
    unittest.main()