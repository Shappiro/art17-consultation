## Script (Python) "edit_user"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = container.REQUEST
response =  request.response


request_key = request.form['api_key']
if request_key != container.ACL_MANAGER_API_KEY:
    response.setStatus(403)
    return "Api key is not valid"

username = request.form['username']
password = request.form['password']

if context.acl_users.getUser(username):
    context.acl_users.userFolderEditUser(
            name=username,
            password=password,
            roles=[],
            domains=[]
    )
    return 'ok'
else:
    response.setStatus(404)
    return 'Username does not exist'
