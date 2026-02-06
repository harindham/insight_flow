import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
load_dotenv()


class DatabaseNotConfiguredError(RuntimeError):
    pass


def _get_db_url() -> str:
    db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
    print("Database URL fetched:", db_url)
    if not db_url:
        raise DatabaseNotConfiguredError(
            "Set SUPABASE_DB_URL or DATABASE_URL to connect to Supabase."
        )
    return db_url


def fetch_table_metadata() -> list[dict]:
    print("Fetching table metadata from database...")
    db_url = _get_db_url()
    print("Connecting to database with URL:", db_url)
    tables_query = """
        select
            n.nspname as table_schema,
            c.relname as table_name,
            d.description as description
        from pg_class c
        join pg_namespace n on n.oid = c.relnamespace
        left join pg_description d on d.objoid = c.oid and d.objsubid = 0
        where c.relkind = 'r'
          and n.nspname not in ('pg_catalog', 'information_schema')
        order by n.nspname, c.relname;
    """
    columns_query = """
        select table_schema, table_name, column_name
        from information_schema.columns
        where table_schema not in ('pg_catalog', 'information_schema')
        order by table_schema, table_name, ordinal_position;
    """
    with psycopg.connect(db_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(tables_query)
            tables = cur.fetchall()
            cur.execute(columns_query)
            columns = cur.fetchall()

    columns_by_table: dict[str, list[str]] = {}
    for row in columns:
        key = f"{row['table_schema']}.{row['table_name']}"
        columns_by_table.setdefault(key, []).append(row["column_name"])

    metadata: list[dict] = []
    for row in tables:
        schema = row["table_schema"]
        name = row["table_name"]
        key = f"{schema}.{name}"
        display_name = name if schema == "public" else key
        metadata.append(
            {
                "table": display_name,
                "description": row["description"] or "",
                "columns": columns_by_table.get(key, []),
            }
        )
    return metadata
