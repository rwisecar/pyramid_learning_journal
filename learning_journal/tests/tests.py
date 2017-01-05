import pytest
import transaction

from pyramid import testing

from ..models import Entry, get_tm_session
from ..models.meta import Base

import faker
import random
import datetime


@pytest.fixture(scope="session")
def configuration(request):
    """Set up an instance of the Configurator object.
    It sets a pointer to the db location.
    It incorporates models from your app's model package.
    Then it tears everything down so you don't have weird things persisting
    beyond the session. This config will persist for the session duration."""
    settings = {'sqlalchemy.url': 'postgres:///test_lj'}
    config = testing.setUp(settings=settings)
    config.include('..models')
    config.include('..routes')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture
def db_session(configuration, request):
    """Create a new session to interact with the test database.
    Here, we use the dbsession_factory on the configurator instance to make new
    db sessions. The dbsession_factory binds the session to an available engine
    and returns a new session each time the dummy_request object is called."""
    SessionFactory = configuration.registry['dbsession_factory']
    session = SessionFactory()
    engine = session.bind
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def teardown():
        """Allow rollback of session changes."""
        session.transaction.rollback()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    """Set up a dummy request object by instantiating DummyRequest class.
    Scope is function level. Each test will have its own db session."""
    return testing.DummyRequest(dbsession=db_session)


@pytest.fixture
def add_dummy_model(dummy_request):
    """Add model instances to the database.
    Scope is session level. 
    Every test that includes this fixture will add new entries to the db."""
    return dummy_request.dbsession.add_all(ENTRIES)


# Instantiate faker
fake = faker.Faker()

# Use Faker to create new fake, random entries
ENTRIES = [Entry(
    title=fake.sentence(),
    creation_date=datetime.datetime.now(),
    body=fake.text(),
    ) for i in range(5)]


@pytest.fixture
def set_auth_credentials():
    """Make a username/pw combo for testing purposes."""
    import os
    from passlib.apps import custom_app_context as pwd_context

    os.environ["AUTH_USERNAME"] = "testme"
    os.environ["AUTH_PASSWORD"] = pwd_context.hash("secrettime")




# =========== UNIT TESTS =========== #
"""Testing that model is creating Entry class objects and pushing to db."""
def test_new_entries_are_added(db_session):
    """Test that new entries are added to the database."""
    db_session.add_all(ENTRIES)
    query = db_session.query(Entry).all()
    assert len(query) == len(ENTRIES)


def test_list_view_returns_correct_number_of_entries(dummy_request, add_dummy_model):
    """Test that list view has db entries on it."""
    from ..views.default import my_view
    result = my_view(dummy_request)
    assert len(result["entries"]) == 5

# =========== FUNCTIONAL TESTS =========== #

@pytest.fixture
def testapp():
    """Create a session."""
    from webtest import TestApp
    from learning_journal import main

    app = main({}, **{"sqlalchemy.url": 'sqlite:///:memory:'})
    testapp = TestApp(app)

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    return testapp


@pytest.fixture
def fill_the_db(testapp):
    """Fill the session DB with the ENTRIES created above."""
    SessionFactory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        dbsession.add_all(ENTRIES)


def test_create_view_has_form(testapp):
    """Test that the edit view has a form on it."""
    response = testapp.get('/journal/new-entry', status=200)
    html = response.html
    assert len(html.find_all("form")) == 1


def test_edit_view_has_form(testapp):
    """Test that the edit view has a form on it."""
    response = testapp.get('/journal/3/edit-entry', status=200)
    html = response.html
    assert len(html.find_all("form")) == 1
