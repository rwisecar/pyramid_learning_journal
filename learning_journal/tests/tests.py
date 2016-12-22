import pytest
import transaction

from pyramid import testing

from ..models import Entry, get_tm_session
from ..models.meta import Base

import faker
import datetime


@pytest.fixture
def configuration():
    settings = {'sqlalchemy.url': 'sqlite:///:memory:'}
    config = testing.setUp(settings=settings)
    config.include('..models')
    yield config
    testing.tearDown()


@pytest.fixture
def db_session(configuration, request):
    """A fixture to create a new session based off of Nick's Expense Tracker"""
    SessionFactory = configuration.registry['dbsession_factory']
    session = SessionFactory()
    engine = session.bind
    Base.metadata.create_all(engine)

    def teardown():
        """Allow rollback of session changes."""
        session.transaction.rollback()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    """Set up a dummy request object by instantiating DummyRequest class."""
    return testing.DummyRequest(db_session=db_session)


@pytest.fixture
def add_dummy_model(dummy_request):
    dummy_request.dbsession.add_all(ENTRIES)


@pytest.fixture
def testapp():
    """Create an instance of our app for testing."""
    from webtest import TestApp
    from learning_journal import main
    app = main({})
    return TestApp(app)


fake = faker.Faker()


ENTRIES = [Entry(
    title=fake.sentence(),
    creation_date=datetime.datetime.now(),
    body=fake.text(),
    ) for i in range(5)]


# =========== UNIT TESTS =========== #

def test_new_entries_are_added(db_session):
    """Test that new entries are added to the database."""
    db_session.add_all(ENTRIES)
    query = db_session.query(Entry).all()
    assert len(query) == len(ENTRIES)

def test_list_view_returns_empty_when_empty(dummy_request, add_dummy_model):
    """Test that list view has no data when db is empty."""
    from ..views.default import my_view
    result = my_view(dummy_request)
    assert len(result["entries"]) == 0
