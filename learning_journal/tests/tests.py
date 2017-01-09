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
    # config.include('..security')

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


# @pytest.fixture
# def login_fixture(set_auth_credentials, testapp):
#     """Enable login"""
#     testapp.post("/login", params={
#         "username": "testme",
#         "password": "secrettime"
#     })
#     return 


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


def test_list_view_returns_empty_when_empty(dummy_request):
    """Test that the home view returns as empty when DB is not populated."""
    from ..views.default import my_view
    result = my_view(dummy_request)
    assert len(result["entries"]) == 0


def test_detail_view_returns_one_object(dummy_request, add_dummy_model):
    """Test that the detail view shows one entry."""
    from ..views.default import detail_view
    dummy_request.matchdict["id"] = "4"
    result = detail_view(dummy_request)
    entry = dummy_request.dbsession.query(Entry).get(4)
    assert result["entry"] == entry


def test_detail_view_returns_404_if_not_found(dummy_request):
    """Test that if a 404 error is returned if you look for nonexistent id."""
    from ..views.default import detail_view
    dummy_request.matchdict["id"] = "12345"
    result = detail_view(dummy_request)
    assert result.status_code == 404


def test_create_view_creates_new_object_on_post(dummy_request):
    """When you send a get request to the create view, get empty dict."""
    from ..views.default import create_view
    query = dummy_request.dbsession.query(Entry)
    count = query.count()
    dummy_request.method = "POST"
    dummy_request.POST["title"] = "Some Title"
    dummy_request.POST["creation_date"] = datetime.datetime.now()
    dummy_request.POST["post"] = "Some new post"
    create_view(dummy_request)
    new_count = query.count()
    assert new_count == count + 1


def test_create_view_returns_empty_dictionary(dummy_request):
    """Test that when you post to create view, you get a new entry."""
    from ..views.default import create_view
    assert create_view(dummy_request) == {}


def test_edit_view_returns_data(dummy_request, add_dummy_model):
    """Test that edit view prepopulates form for editing."""
    from ..views.default import edit_view
    dummy_request.matchdict["id"] = 4
    result = edit_view(dummy_request)
    entry = dummy_request.dbsession.query(Entry).get(4)
    assert result["entry"]["title"] == entry.title


# def test_edit_post_actually_edits_post(dummy_request, add_dummy_model):
#     """Test that when you edit a post, it actually edits the object."""
#     from ..views.default import edit_view

#     dummy_request.method = "POST"
#     import pdb; pdb.set_trace()
#     dummy_request.matchdict["id"] = u"2"
#     dummy_request.POST["title"] = u"Edit Title"
#     dummy_request.POST["post"] = u"Edit Post"
#     edit_view(dummy_request)

#     assert dummy_request.dbsession.query(Entry).get(2).title == "Edit Post"


def test_get_login_view_is_empty_dict(dummy_request):
    """Test that the login view is an empty dictionary."""
    from ..views.default import login_view
    assert login_view(dummy_request) == {}


def test_api_list_returns_list_of_dicts(dummy_request, add_dummy_model):
    """Test that api list view shows a list of json dictionaries."""
    from ..views.default import api_list_view
    result = api_list_view(dummy_request)
    for entry in ENTRIES:
        assert entry.to_json() in result

# =========== FUNCTIONAL TESTS =========== #


@pytest.fixture(scope="session")
def testapp(request):
    """Create a webtest's TestApp for testing routes.
    Scope is function-level, so each function gets a new test app."""

    from webtest import TestApp
    from pyramid.config import Configurator
    from learning_journal import main

    app = main({}, **{"sqlalchemy.url": 'postgres:///test_lj'})
    testapp = TestApp(app)

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)

    return testapp


@pytest.fixture
def fill_the_db(testapp):
    """Fill the session DB with the ENTRIES created above."""
    SessionFactory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        dbsession.add_all(ENTRIES)


# def test_home_view_has_article(testapp):
#     """The home page should have an html ul section."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(html.find_all("ul")) == 2


# def test_create_view_has_form(testapp):
#     """Test that the edit view has a form on it."""
#     response = testapp.get('/journal/new-entry', status=200)
#     html = response.html
#     assert len(html.find_all("form")) == 1


# def test_edit_view_has_form(testapp):
#     """Test that the edit view has a form on it."""
#     response = testapp.get('/journal/3/edit-entry', status=200)
#     html = response.html
#     assert len(html.find_all("form")) == 1

# def test_detail_view_shows_nothing_when_no_data(testapp):
#     """Test that the detail route shows a 404 error when no data."""
#     response = testapp.get("/journal/200", status=404)
#     assert response.status_code == 404


# def test_detail_view_shows_one_entry_when_data(testapp):
#     """Test that the detail route shows an entry when data is passed."""
#     session = fill_the_db
#     response = testapp.get("/journal/2")
#     num_items = session.query(Entry).get(2)
#     html = response.html
#     titles = html.find_all("h3")
#     assert len(titles) == num_items + 1
