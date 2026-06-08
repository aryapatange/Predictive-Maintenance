# Purpose: Load CSV into MySQL, retrieve it back as a DataFrame

import pandas as pd
from sqlalchemy import create_engine, text
import os

# ─────────────────────────────────────────
# 1. DATABASE CONNECTION
# ─────────────────────────────────────────

DB_USER     = "pred_user"
DB_PASSWORD = "pred1234"
DB_HOST     = "localhost"
DB_PORT     = "3306"
DB_NAME     = "predictive_maintenance"

CONNECTION_STRING = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(CONNECTION_STRING, echo=False)
# echo=False this time — we don't need to see every SQL statement now


# ─────────────────────────────────────────
# 2. LOAD CSV INTO MYSQL
# ─────────────────────────────────────────

def load_csv_to_mysql():
    """
    Reads the raw CSV and pushes it into the sensor_readings table.
    Skips loading if data already exists — prevents duplicate rows.
    """

    # ── Check if data already exists in table ──
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM sensor_readings"))
        count  = result.fetchone()[0]

    if count > 0:
        print(f"⚠️  Table already contains {count} rows. Skipping CSV load.")
        print("    Delete the rows first if you want to reload fresh data.")
        return

    # ── Build path to CSV ──
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "ai4i2020.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"CSV not found at: {csv_path}\n"
            f"Make sure ai4i2020.csv is inside the data/ folder."
        )

    print(f"📂 Reading CSV from: {csv_path}")

    # ── Read CSV into DataFrame ──
    df = pd.read_csv(csv_path)
    print(f"✅ CSV loaded into memory — Shape: {df.shape}")
    print(f"   Columns: {df.columns.tolist()}")

    # ── Rename columns to match our MySQL schema ──
    df.rename(columns={
        "UDI"                        : "id",
        "Product ID"                 : "product_id",
        "Type"                       : "type",
        "Air temperature [K]"        : "air_temperature",
        "Process temperature [K]"    : "process_temperature",
        "Rotational speed [rpm]"     : "rotational_speed",
        "Torque [Nm]"                : "torque",
        "Tool wear [min]"            : "tool_wear",
        "Machine failure"            : "machine_failure",
        "TWF"                        : "twf",
        "HDF"                        : "hdf",
        "PWF"                        : "pwf",
        "OSF"                        : "osf",
        "RNF"                        : "rnf"
    }, inplace=True)

    print("\n⚙️  Pushing data to MySQL table: sensor_readings...")

    # ── Push DataFrame to MySQL ──
    # if_exists='append' — adds rows to existing table (schema already created)
    # index=False        — don't write pandas index as a column
    df.to_sql(
        name      = "sensor_readings",
        con       = engine,
        if_exists = "append",
        index     = False
    )

    print(f"✅ Successfully pushed {len(df)} rows to MySQL")


# ─────────────────────────────────────────
# 3. RETRIEVE DATA FROM MYSQL
# ─────────────────────────────────────────

def get_data_from_mysql():
    """
    Retrieves all rows from sensor_readings table.
    Returns a clean pandas DataFrame ready for EDA and modeling.
    """
    print("\n⚙️  Retrieving data from MySQL...")

    query = "SELECT * FROM sensor_readings"

    df = pd.read_sql(query, con=engine)

    print(f"✅ Data retrieved successfully — Shape: {df.shape}")
    print(f"\n📋 First 3 rows:")
    print(df.head(3))
    print(f"\n📋 Data types:")
    print(df.dtypes)
    print(f"\n📋 Null values per column:")
    print(df.isnull().sum())

    return df


# ─────────────────────────────────────────
# 4. MAIN — RUN BOTH FUNCTIONS
# ─────────────────────────────────────────

if __name__ == "__main__":

    # Step 1 — Push CSV to MySQL
    print("=" * 50)
    print("STEP 1: LOADING CSV INTO MYSQL")
    print("=" * 50)
    load_csv_to_mysql()

    # Step 2 — Pull data back from MySQL
    print("\n" + "=" * 50)
    print("STEP 2: RETRIEVING DATA FROM MYSQL")
    print("=" * 50)
    df = get_data_from_mysql()

    # Step 3 — Final confirmation
    print("\n" + "=" * 50)
    print("DATA READY FOR EDA AND MODELING")
    print("=" * 50)
    print(f"  Rows    : {df.shape[0]}")
    print(f"  Columns : {df.shape[1]}")