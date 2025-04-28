import subprocess
from pathlib import Path

import psycopg2

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/stats"
TEST_DB_DUMP_PATH = Path(__file__).parent.parent / "tests" / "test_db_dump.sql"


def reset_database():
    """Manually reset the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DO $$ DECLARE
                    r RECORD;
                    BEGIN
                        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                            EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
                        END LOOP;
                    END $$;
                    """
                )
                conn.commit()

            with open(TEST_DB_DUMP_PATH, encoding="utf-8") as f:
                sql = f.read()
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()

            print("Database reset successfully.")
        finally:
            conn.close()

    except psycopg2.Error as e:
        print(f"Failed to reset the database: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reset the database: {e}")


if __name__ == "__main__":
    reset_database()
