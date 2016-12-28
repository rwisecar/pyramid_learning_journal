from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.exc import DBAPIError

from ..models import Entry
import datetime


@view_config(route_name='list', renderer='../templates/list.jinja2')
def my_view(request):
    try:
        entries = request.dbsession.query(Entry).all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'entries': entries}


@view_config(route_name='detail', renderer='../templates/detail.jinja2')
def detail_view(request):
    try:
        query = request.dbsession.query(Entry)
        the_id = int(request.matchdict["id"])
        entry = query[the_id]
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'entry': entry}


@view_config(route_name='create', renderer='../templates/create.jinja2')
def create_view(request):
    if request.method == "POST":
        new_title = request.POST["title"]
        new_post = request.POST["post"]
        new_date = datetime.datetime.now()
        new_model = Entry(title=new_title, body=new_post, creation_date=new_date)
        request.dbsession.add(new_model)
        return HTTPFound(location=request.route_url('list'))
    return {"data": {"title": "post"}, "creation_date": "creation_date"}


@view_config(route_name='edit', renderer='../templates/edit.jinja2')
def edit_view(request):
    if request.method == "POST":
        try:
            new_title = request.POST["title"]
            new_post = request.POST["post"]
            query = request.dbsession.query(Entry)
            post_dict = query.filter(Entry.id == request.matchdict["id"])
            post_dict.update({"title": new_title,
                              "body": new_post,
                              "creation_date": datetime.datetime.now()})
            return HTTPFound(location=request.route_url('list'))
        except DBAPIError:
            return Response(db_err_msg, content_type='text/plain', status=500)
    query = request.dbsession.query(Entry)
    post_dict = query.filter(Entry.id == request.matchdict["id"]).first()
    new = {"title": post_dict.title,
           "creation_date": post_dict.creation_date,
           "body": post_dict.body}
    return {"entry": new}


@view_config(route_name='about', renderer='../templates/about.jinja2')
def about_view(request):
    return {}


@view_config(route_name='portfolio', renderer='../templates/portfolio.jinja2')
def portfolio_view(request):
    return {}


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
