import polars as pl
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.warehouse.loader import batch_insert_dataframe
from app.warehouse.table_manager import ensure_warehouse_table


@pytest.fixture
def sqlite_session(tmp_path):
    db_path = tmp_path / "loader_test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with session_factory() as session:
        yield session, engine


def test_batch_insert_dataframe_loads_rows(sqlite_session):
    session, engine = sqlite_session
    dataframe = pl.DataFrame(
        {
            "id": [1, 2],
            "name": ["Alice", "Bob"],
            "amount": [10.5, 20.0],
        }
    )

    with session.begin():
        inserted = batch_insert_dataframe(
            session=session,
            engine=engine,
            table_name="wh_test_batch",
            dataframe=dataframe,
            batch_size=1,
        )

    assert inserted == 2

    table = ensure_warehouse_table(engine, "wh_test_batch", dataframe)
    with engine.connect() as connection:
        count = connection.execute(select(func.count()).select_from(table)).scalar_one()

    assert count == 2
