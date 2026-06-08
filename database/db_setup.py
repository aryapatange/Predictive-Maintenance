# Purpose: Connect to MySQL and create the sensor_readings table

from sqlalchemy import (
    create_engine, Column, Integer, Float,
    String, text
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# ─────────────────────────────────────────
# 1. DATABASE CONNECTION CONFIGURATION
# ─────────────────────────────────────────

DB_USER     = "pred_user"
DB_PASSWORD = "pred1234"
DB_HOST     = "localhost"
DB_PORT     = "3306"
DB_NAME     = "predictive_maintenance"

# SQLAlchemy connection string for MySQL using PyMySQL driver
# Format: mysql+pymysql://user:password@host:port/database
CONNECTION_STRING = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the engine — this is the core connection object
# echo=True prints every SQL statement SQLAlchemy executes — useful for learning
engine = create_engine(CONNECTION_STRING, echo=True)

# ─────────────────────────────────────────
# 2. TABLE SCHEMA DEFINITION
# ─────────────────────────────────────────

# Base is the parent class all table definitions inherit from
Base = declarative_base()

class SensorReading(Base):
    """
    Maps directly to the AI4I 2020 dataset columns.
    Each attribute = one column in the MySQL table.
    """
    __tablename__ = "sensor_readings"

    # Primary key — maps to UDI in dataset
    id                  = Column(Integer, primary_key=True, autoincrement=True)

    # Product information
    product_id          = Column(String(10),  nullable=False)
    type                = Column(String(5),   nullable=False)   # L / M / H

    # Sensor readings
    air_temperature     = Column(Float,       nullable=False)   # Kelvin
    process_temperature = Column(Float,       nullable=False)   # Kelvin
    rotational_speed    = Column(Integer,     nullable=False)   # RPM
    torque              = Column(Float,       nullable=False)   # Nm
    tool_wear           = Column(Integer,     nullable=False)   # Minutes

    # Failure labels
    machine_failure     = Column(Integer,     nullable=False)   # 0 or 1
    twf                 = Column(Integer,     nullable=False)   # Tool Wear Failure
    hdf                 = Column(Integer,     nullable=False)   # Heat Dissipation Failure
    pwf                 = Column(Integer,     nullable=False)   # Power Failure
    osf                 = Column(Integer,     nullable=False)   # Overstrain Failure
    rnf                 = Column(Integer,     nullable=False)   # Random Failure

    def __repr__(self):
        return (
            f"<SensorReading(id={self.id}, "
            f"type={self.type}, "
            f"tool_wear={self.tool_wear}, "
            f"machine_failure={self.machine_failure})>"
        )

# ─────────────────────────────────────────
# 3. CREATE TABLE + VERIFY
# ─────────────────────────────────────────

def setup_database():
    """
    Creates the sensor_readings table in MySQL.
    If table already exists, it is left unchanged (checkfirst=True).
    """
    print("\n⚙️  Connecting to MySQL...")
    
    # Test connection first
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE()"))
        db_name = result.fetchone()[0]
        print(f"✅ Connected to database: {db_name}")

    print("\n⚙️  Creating table: sensor_readings...")
    
    # Creates all tables defined above — skips if already exists
    Base.metadata.create_all(engine, checkfirst=True)
    
    print("✅ Table 'sensor_readings' created successfully")

    # Verify by checking table exists in MySQL
    with engine.connect() as connection:
        result = connection.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"\n📋 Tables in '{DB_NAME}' database: {tables}")


if __name__ == "__main__":
    setup_database()