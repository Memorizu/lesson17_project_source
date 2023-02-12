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


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# namespaces
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


################# Movie

@movie_ns.route('/')
class MoviesBased(Resource):

    def get(self):
        try:
            req = Movie.query
            director_id = request.args.get('director_id')
            genre_id = request.args.get('genre_id')
            if director_id:
                req = req.filter(director_id == Movie.director_id)
            if genre_id:
                req = req.filter(genre_id == Movie.genre_id)
            movies = req.all()
            return movies_schema.dump(movies)
        except Exception as e:
            return e

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


############## Director
@director_ns.route('/')
class DirectorBased(Resource):

    def get(self):
        req = Director.query.all()
        return directors_schema.dump(req)

    def post(self):
        director = request.json
        new_director = Director(**director)
        db.session.add(new_director)
        db.session.commit()
        return '', 201


@director_ns.route('/<int:did>')
class DirectorBased(Resource):

    def get(self, did):
        director = Director.query.get(did)
        return director_schema.dump(director)

    def put(self, did):
        req = request.json
        director = Director.query.get(did)

        director.id = req.get('id')
        director.name = req.get('name')
        db.session.add(director)
        db.session.commit()
        return '', 201

    def delete(self, did):
        director = Director.query.get(did)
        db.session.delete(director)
        db.session.commit()
        return '', 201


############## genres
@genre_ns.route('/')
class GenreBased(Resource):

    def get(self):
        genre = Genre.query.all()
        return genres_schema.dump(genre), 200

    def post(self):
        req = request.json
        new_genre = Genre(**req)
        db.session.add(new_genre)
        db.session.commit()
        return '', 201


@genre_ns.route('/<int:gid>')
class GenreBased(Resource):

    def get(self, gid):
        genre = Genre.query.get(gid)
        return genre_schema.dump(genre), 200

    def put(self, gid):
        req = request.json
        genre = Genre.query.get(gid)
        genre.id = req.get('id')
        genre.name = req.get('name')
        db.session.add(genre)
        db.session.commit()
        return '', 204

    def delete(self, gid):
        genre = Genre.query.get(gid)
        db.session.delete(genre)
        db.session.commit()
        return '', 201


if __name__ == '__main__':
    app.run(debug=True)
