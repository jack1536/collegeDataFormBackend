from flask import Flask
from flask_restful import Resource, reqparse, Api
from flask_cors import CORS
from step_2 import step_2_main
from querybuilder import build_query
from db_interface import query_to_json

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

from base import Movies, db
db.init_app(app)
app.app_context().push()
db.create_all()

class Movies_List(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('director', type=str, required=False, help='Director of the movie')
    parser.add_argument('genre', type=str, required=False, help='Genre of the movie')
    parser.add_argument('collection', type=int, required=True, help='Gross collection of the movie')
    
    def get(self, movie):
        item = Movies.find_by_title(movie)
        if item:
            return item.json()
        return {'Message': 'Movie is not found'}
    
    def post(self, movie):
        if Movies.find_by_title(movie):
            return {' Message': 'Movie with the  title {} already exists'.format(movie)}
        args = Movies_List.parser.parse_args()
        item = Movies(movie, args['director'], args['genre'], args['collection'])
        item.save_to()
        return item.json()
        
    def put(self, movie):
        args = Movies_List.parser.parse_args()
        item = Movies.find_by_title(movie)
        if item:
            item.collection = args['collection']
            item.save_to()
            return {'Movie': item.json()}
        item = Movies(movie, args['director'], args['genre'], args['collection'])
        item.save_to()
        return item.json()
            
    def delete(self, movie):
        item  = Movies.find_by_title(movie)
        if item:
            item.delete_()
            return {'Message': '{} has been deleted from records'.format(movie)}
        return {'Message': '{} is already not on the list'.format()}


class Email_Data(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('recipient_email', type=str, required=True, help='email to send attachement to')
    parser.add_argument('filter_dict', type=dict, required=True, help='dictionary with all of filter information')
     
    def get(self):
        # make a call for one row of data in order to extract column names
        q = 'SELECT * FROM codetran_collegedata.collegescorecard WHERE school_name="Pomona College"'
        column_names = query_to_json(q)['column_names']

        return {'class': 'Email_Data', 'tablename': "codetran_collegedata.collegescorecard", 'column_names': column_names}


    def post(self):
        args = Email_Data.parser.parse_args()

        # build query
        tablename = "codetran_collegedata.collegescorecard"
        select_col = ["school_name", "school_state"]
        q = build_query(tablename, select_col, args['filter_dict'])
        return {"table": query_to_json(q)}


class All_Movies(Resource):
    def get(self):
        return {'output': "Nothing for now"}
    
api.add_resource(All_Movies, '/')
api.add_resource(Email_Data, '/send-data')
api.add_resource(Movies_List, '/<string:movie>')

if __name__=='__main__':
    
    app.run(debug=True)
