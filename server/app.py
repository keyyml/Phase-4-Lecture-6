from flask import request, make_response

from werkzeug.exceptions import NotFound

from config import app

from models import db, User, NationalPark, UserVisitedPark

# unique error message upon nonexistent server-side route
@app.errorhandler(NotFound)
def route_not_found(e):
    response = make_response(
        "That route does not exist!",
        404
    )
    
    return response

@app.route('/')
def home():
    return ""

@app.route('/users', methods = ['GET', 'POST'])
def users():

    if request.method == 'GET':
        users = User.query.all()
        #rules removes park of the list displayed or object 
        users_dict = [user.to_dict(rules = ('-user_visited_park', '-password' )) for user in users]

        return make_response(users_dict, 200)
    
    elif request.method == 'POST':
        form_data = request.get_json()

        try:

            new_user_obj = User(
                username = form_data['username'],
                passowrd = form_data['password']
            )

            db.session.add(new_user_obj)

            db.session.commit()
            
            new_user_obj_dict = new_user_obj.to_dict()

            return make_response(new_user_obj_dict, 201)
        
        except ValueError:

            return make_response({ "Username must be between 4 and 14 characrters long, inclusive!" : None }, 403)

@app.route('/national_parks', methods = ['GET'])
def national_parks():
    national_parks = NationalPark.query.all()

    national_parks_dict = [national_park.to_dict() for national_park in national_parks]

    return make_response(national_parks_dict, 200)

@app.route('/users/<int:id>', methods = ['GET', 'PATCH'])
def user_by_id(id):
    user_by_id = User.query.filter_by(id = id).first()
    #User.query.filter(User.id == id).first()
    if user_by_id:
        if request.method == 'GET':
            user_dict = user_by_id.to_dict(rules = ('-user_visited_park', '-password' ))

            return make_response(user_dict, 200)
            #return make_response(user_by_id.to_dict(), 200)

        elif request.method == 'PATCH':
            form_data = request.get_json()

            try:
                for attr in form_data:
                    setattr(user_by_id, attr, form_data.get(attr))
                
                db.session.commit()

                return make_response(user_by_id.to_dict(), 201)
            
            except ValueError:

                return make_response({ "Username must be between 4 and 14 characrters long, inclusive!" : None }, 403)
    else: 
        return make_response("User not found!", 404)
    
@app.route('/national_parks/<int:id>', methods = ['DELETE'])
def national_park_by_id(id):
    park_by_id = NationalPark.query.filter_by(id = id).first()

    if park_by_id:

        associated_visits = UserVisitedPark.query.filter(UserVisitedPark.park_id == id).all()

        for associated_visit in associated_visits:
            db.session.delete(associated_visit)

        db.session.delete(park_by_id)

        db.session.commit()

        return make_response({}, 202)
    else:
        return make_response("Park not found!", 404)


if __name__ == '__main__':
    app.run(port = 5555, debug = True)