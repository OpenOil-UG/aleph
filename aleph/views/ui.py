import os
import uuid
from flask import render_template, request, make_response

from aleph import authz
from aleph.core import app


def angular_templates():
    partials_dir = os.path.join(app.static_folder, 'templates')
    for (root, dirs, files) in os.walk(partials_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'rb') as fh:
                file_name = file_path[len(partials_dir) + 1:]
                yield (file_name, fh.read().decode('utf-8'))



@app.route('/')
def ui(**kwargs):
    # cookie
    is_new_user = 'oo_search_user' not in request.cookies
    user_id = request.cookies.get('oo_search_user', str(uuid.uuid4()))
    rsp =  make_response(
        render_template("layout.html",
                        templates=angular_templates(),
                        is_new_user = is_new_user,
                        user_id = user_id   
                                     ))
    if is_new_user:
        rsp.set_cookie('oo_search_user',
                            value=user_id,
                            max_age=60 * 60 * 24 * 365, # 1 year
                            )
    return rsp


@app.route('/sources/<path:slug>')
@app.route('/sources')
def ui_admin(**kwargs):
    authz.require(authz.is_admin())
    return render_template("layout.html", templates=angular_templates())
