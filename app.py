# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# namespaces
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Integer()
    rating = fields.Str()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@movie_ns.route('/')
class MoviesBased(Resource):

    def get(self):
        req = Movie.query
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            req = req.filter(director_id == Movie.director_id)
        if genre_id:
            req = req.filter(genre_id == Movie.genre_id)
        movies = req.all()
        return movies_schema.dump(movies)

    def post(self):
        req = request.json
        movie = Movie(**req)
        db.session.add(movie)
        db.session.commit()
        return '', 201


@movie_ns.route('/<int:mid>')
class MoviesBased(Resource):

    def get(self, mid):
        movie = Movie.query.get(mid)
        return movie_schema.dump(movie)

    def put(self, mid):
        movie = Movie.query.get(mid)
        req = request.json
        if not movie:
            return '', 404

        movie.title = req.get('title')
        movie.description = req.get('description')
        movie.trailer = req.get('trailer')
        movie.year = req.get('year')
        movie.rating = req.get('rating')
        movie.genre_id = req.get('genre_id')
        movie.director_id = req.get('director_id')
        db.session.add(movie)
        db.session.commit()
        return '', 204

    def delete(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return '', 404
        db.session.delete(movie)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)
