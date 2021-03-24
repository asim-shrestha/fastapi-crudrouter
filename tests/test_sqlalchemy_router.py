import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Float, Integer, String

from fastapi_crudrouter import SQLAlchemyCRUDRouter
from tests import Carrot, CarrotUpdate, Potato
from tests import test_router
from tests.implementations.sqlalchemy_ import _setup_base_app


def get_app():
    app, engine, Base, session = _setup_base_app()

    class PotatoModel(Base):
        __tablename__ = "potatoes"
        id = Column(Integer, primary_key=True, index=True)
        thickness = Column(Float)
        mass = Column(Float)
        color = Column(String)
        type = Column(String)

    class CarrotModel(Base):
        __tablename__ = "carrots"
        id = Column(Integer, primary_key=True, index=True)
        length = Column(Float)
        color = Column(String)

    Base.metadata.create_all(bind=engine)
    app.include_router(
        SQLAlchemyCRUDRouter(
            schema=Potato,
            db_model=PotatoModel,
            db=session,
            create_schema=Potato,
            prefix="potato",
        )
    )
    app.include_router(
        SQLAlchemyCRUDRouter(
            schema=Carrot,
            db_model=CarrotModel,
            db=session,
            update_schema=CarrotUpdate,
            prefix="carrot",
        )
    )

    return app


def test_integrity_error():
    client = TestClient(get_app())
    potato = dict(id=1, thickness=2, mass=5, color="red", type="russet")

    args = client, "/potato", potato
    test_router.test_post(*args)
    with pytest.raises(AssertionError):
        test_router.test_post(*args)

    # No integrity error here because of the create_schema
    args = client, "/carrot", dict(id=1, length=2, color="red")
    test_router.test_post(*args)
    test_router.test_post(*args, expected_length=2)
