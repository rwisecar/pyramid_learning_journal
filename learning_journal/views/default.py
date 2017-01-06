from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from sqlalchemy.exc import DBAPIError

from ..models import Entry
from ..security import check_credentials
import datetime


@view_config(route_name='list', renderer='../templates/list.jinja2', require_csrf=False)
def my_view(request):
    """Show list view of all entries."""
    try:
        entries = request.dbsession.query(Entry).all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    if request.method == "POST":
        new_title = request.POST["title"]
        new_post = request.POST["post"]
        new_model = Entry(title=new_title,
                          body=new_post,
                          creation_date=datetime.datetime.now())
        request.dbsession.add(new_model)
        return HTTPFound(location=request.route_url('list'))
    return {'entries': entries}


@view_config(route_name='detail', renderer='../templates/detail.jinja2', require_csrf=False)
def detail_view(request):
    """Show detail view for selected entry."""
    entry = request.dbsession.query(Entry).get(int(request.matchdict["id"]))
    if not entry:
        return Response("Not Found", content_type='text/plain', status=404)
    return {'entry': entry}


@view_config(
    route_name='create',
    renderer='../templates/create.jinja2',
    permission="add"
    )
def create_view(request):
    """Show and enable create page for selected entry."""
    if request.method == "POST":
        new_title = request.POST["title"]
        new_post = request.POST["post"]
        new_model = Entry(title=new_title,
                          body=new_post,
                          creation_date=datetime.datetime.now())
        request.dbsession.add(new_model)
        return HTTPFound(location=request.route_url('list'))
    return {}


@view_config(
    route_name='edit',
    renderer='../templates/edit.jinja2',
    permission="add")
def edit_view(request):
    """Show and enable edit page for selected entry."""
    if request.method == "POST":
        try:
            new_title = request.POST["title"]
            new_post = request.POST["post"]
            query = request.dbsession.query(Entry)
            entry = query.filter(Entry.id == request.matchdict["id"])
            entry.update({"title": new_title,
                          "body": new_post,
                          "creation_date": datetime.datetime.now()})
            return HTTPFound(location=request.route_url('list'))
        except DBAPIError:
            return Response(db_err_msg, content_type='text/plain', status=500)
    query = request.dbsession.query(Entry)
    entry = query.filter(Entry.id == request.matchdict["id"]).first()
    new = {"title": entry.title,
           "creation_date": entry.creation_date,
           "body": entry.body}
    return {"entry": new}


@view_config(
    route_name='about',
    renderer='../templates/about.jinja2',
    require_csrf=False)
def about_view(request):
    """Show about page."""
    return {}


@view_config(
    route_name='portfolio',
    renderer='../templates/portfolio.jinja2',
    require_csrf=False)
def portfolio_view(request):
    """Show portfolio page."""
    return {}


@view_config(route_name="delete", permission="delete", require_csrf=False)
def delete_view(request):
    """Delete individual entries."""
    try:
        entry = request.dbsession.query(Entry).get(request.matchdict["id"])
        request.dbsession.delete(entry)
        return HTTPFound(request.route_url("list"))
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)


@view_config(
    route_name='login',
    renderer='../templates/login.jinja2',
    require_csrf=False)
def login_view(request):
    """Enable user login."""
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        if check_credentials(username, password):
            auth_head = remember(request, username)
            return HTTPFound(
                location=request.route_url("list"),
                headers=auth_head
            )
    return {}


@view_config(route_name="logout", require_csrf=False)
def logout_view(request):
    """Enable user logout."""
    auth_head = forget(request)
    return HTTPFound(location=request.route_url("list"), headers=auth_head)


@forbidden_view_config()
def forbidden_view(request):
    """Control view on 403 error."""
    return HTTPFound(location=request.route_url("login"))


@view_config(route_name="api_list", renderer="json")
def api_list_view(request):
    """Return a list of blog entries in json format."""
    entries = request.dbsession.query(Entry).all()
    output = [entry.to_json() for entry in entries]
    return output


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning_journal_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
