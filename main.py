from database import Database
from query_parser import QueryParser
from query_executor import QueryExecutor


db = Database()

parser = QueryParser()
executor = QueryExecutor(db)


print("================================")
print("        MiniDB Database")
print("================================")
print("Type 'exit' to quit.")
print()


while True:

    query = input("MiniDB> ")

    if query.lower() == "exit":

        print("Goodbye!")

        break

    try:

        parsed_query = parser.parse(
            query
        )

        result = executor.execute(
            parsed_query
        )

        if isinstance(result, list):

            for row in result:

                print(row)

        else:

            print(result)

    except Exception as error:

        print("Error:", error)