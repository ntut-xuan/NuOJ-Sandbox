import pytest

from app import create_app
from setting.util import Setting, SettingBuilder

@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    
    with app.app_context():
        app.config["setting"] = SettingBuilder().from_mapping({"sandbox_number": 1})

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()
