import duckdb
import os


ORDERS_FILE = "data/raw/o2c_orders.csv"
SQL_FILE = "sql/analysis.sql"


print("=" * 70)
print("O2C SQL ANALYSIS")
print("=" * 70)


# Create in-memory DuckDB connection
con = duckdb.connect()


# Load CSV as a SQL table
con.execute(f"""
    CREATE TABLE orders AS
    SELECT *
    FROM read_csv_auto('{ORDERS_FILE}')
""")


print("\nOrders table loaded successfully.")

# Read SQL file
with open(SQL_FILE, "r", encoding="utf-8") as f:
    sql_script = f.read()


# Split individual queries
queries = [
    query.strip()
    for query in sql_script.split(";")
    if query.strip()
]


print(f"Queries found: {len(queries)}")


# Execute queries
for i, query in enumerate(queries, start=1):

    print("\n" + "=" * 70)
    print(f"QUERY {i}")
    print("=" * 70)

    try:

        result = con.execute(query).df()

        print(result.to_string(index=False))

    except Exception as e:

        print("ERROR:")
        print(e)


con.close()

print("\n" + "=" * 70)
print("SQL ANALYSIS COMPLETE")
print("=" * 70)