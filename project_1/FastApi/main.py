from typing import Annotated

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, Relationship, create_engine, select, func, and_, or_, Table, Column, ForeignKey
from fastapi import FastAPI, Depends, Query, HTTPException
import datetime

from starlette.responses import JSONResponse


#fastapi dev main.py


class Director(SQLModel, table=True):
    __tablename__ = 'imdb_director'
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    birth_date: datetime.date
    movies: list['Movie'] = Relationship(back_populates='director')


class ActorMovieLink(SQLModel, table=True):
    __tablename__ = 'imdb_movie_actors'
    movie_id : int = Field(foreign_key='imdb_movie.id', primary_key=True)
    actor_id : int = Field(foreign_key='imdb_actor.id', primary_key=True)


class Actor(SQLModel, table=True):
    __tablename__ = 'imdb_actor'
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    birth_date: datetime.date
    movies: list['Movie'] = Relationship(back_populates='actors', link_model=ActorMovieLink)


class Movie(SQLModel, table=True):
    __tablename__ = 'imdb_movie'
    id: int | None = Field(default=None, primary_key=True)
    title: str
    rating: float
    director_id: int = Field(foreign_key='imdb_director.id')
    date: datetime.date
    director: Director = Relationship(back_populates='movies')
    comments: list['MovieComment'] = Relationship(back_populates='movie')
    actors: list[Actor] = Relationship(back_populates='movies', link_model=ActorMovieLink)


class DirectorShort(BaseModel):
    first_name: str
    last_name: str


class MovieWithDirector(BaseModel):
    title: str
    rating: float
    director: DirectorShort


class MovieShort(BaseModel):
    title: str
    rating: float


class DirectorWithMovie(BaseModel):
    first_name: str
    last_name: str
    movies: list[MovieShort]


class DirectorWithRating(BaseModel):
    first_name: str
    last_name: str
    avg_rating: float
    num_movies: int


class User(SQLModel, table=True):
    __tablename__ = 'auth_user'
    id: int | None = Field(default=None, primary_key=True)
    username: str
    comments: list['MovieComment'] = Relationship(back_populates='author')


class UserShort(BaseModel):
    id: int
    username: str


class MovieComment(SQLModel,table=True):
    __tablename__ = 'imdb_moviecomment'
    id: int | None = Field(default=None, primary_key=True)
    text: str
    movie_id: int = Field(foreign_key='imdb_movie.id')
    author_id: int = Field(foreign_key='auth_user.id')
    created: datetime.datetime
    updated: datetime.datetime

    movie: Movie = Relationship(back_populates='comments')
    author: User = Relationship(back_populates='comments')


class MovieCommentRead(BaseModel):
    id: int
    text: str
    author: UserShort
    created: datetime.datetime


class ActorWithMovie(BaseModel):
    first_name: str
    last_name: str
    movies: list[MovieShort]


sqlite_file_name = "../db.sqlite3"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()


@app.get('/director/list/', response_model=list[Director])
def read_director_list(session: SessionDep) -> list[Director]:
    object_list = session.exec(select(Director)).all()
    return object_list


@app.get('/movie/list/', response_model=list[Movie])
def read_movie_list(session: SessionDep) -> list[Movie]:
    object_list = session.exec(select(Movie)).all()
    return object_list


@app.get('/movie/{pk}/', response_model=Movie)
def read_movie_detail(session: SessionDep, pk: int) -> Movie:
    object = session.get(Movie, pk)
    return object


@app.get('/actor/list/', response_model=list[Actor])
def read_actor_list(session:SessionDep) -> list[Actor]:
    object_list = session.exec(select(Actor)).all()
    return object_list


@app.get('/actor/with/movie/', response_model=list[ActorWithMovie])
def read_actor_with_movie(session:SessionDep) -> list[ActorWithMovie]:
    object_list = session.exec(select(Actor)).all()
    return object_list


@app.get('/movie/with/director/', response_model=list[MovieWithDirector])
def read_movie_with_director(session: SessionDep) -> list[MovieWithDirector]:
    object_list = session.exec(select(Movie)).all()
    return object_list


@app.get('/director/with/movie/', response_model=list[DirectorWithMovie])
def read_director_with_movie(session: SessionDep) -> list[DirectorWithMovie]:
    object_list = session.exec(select(Director)).all()
    return object_list


@app.get('/director/with/rating/', response_model=list[DirectorWithRating])
def read_director_with_rating(session: SessionDep) -> list[DirectorWithRating]:
    # statement = select(Director.first_name, Director.last_name, func.coalesce(func.avg(Movie.rating), 0.0), func.count(Movie.id)).join(Movie, isouter=True).group_by(Director.id)
    statement = (
                select(
                    Director.first_name,
                    Director.last_name,
                    func.coalesce(func.avg(Movie.rating), 0.0),
                    func.count(Movie.id)
                )
                .join(Movie, isouter=True)
                .group_by(Director.id)
                .order_by(Director.last_name)
    )
    object_list = session.exec(statement).all()
    print(object_list)
    response = [DirectorWithRating(first_name=first, last_name=last, avg_rating=rating, num_movies=num_movies) for first, last, rating, num_movies in object_list]
    return response


@app.get('/movie/comment/', response_model=list[MovieComment])
def read_movie_comment(session: SessionDep) -> list[MovieComment]:
    object_list = session.exec(select(MovieComment)).all()
    return object_list


@app.get('/movie/comment/short/', response_model=list[MovieCommentRead])
def read_movie_comment_short(session: SessionDep) -> list[MovieCommentRead]:
    object_list = session.exec(select(MovieComment)).all()
    return object_list


@app.get('/movie/filter/by/rating/', response_model=list[MovieWithDirector])
def read_movie_filter_by_rating(session: SessionDep,
                                min_rating: float = Query(0.0, description='min rate'),
                                max_rating: float = Query(10.0, description='max_rate')
                                ) -> list[MovieWithDirector]:
    statment = select(Movie).where(and_(Movie.rating >= min_rating, Movie.rating <= max_rating))
    object_list = session.exec(statment).all()
    return object_list


@app.get('/director/with/movie/filter/', response_model=list[DirectorWithMovie])
def read_director_with_movie_filter(session: SessionDep,
                                    q: str = Query('', description='search pattern')) -> list[DirectorWithMovie]:
    statment = (
        select(Director)
        .where(or_(Director.first_name.ilike(f'%{q}%'), Director.last_name.ilike(f'%{q}%')))
        .order_by(Director.last_name)
    )
    object_list = session.exec(statment).all()
    return object_list


@app.patch('/movie/title/update/{pk}/', response_model=Movie)
def update_movie_title(session: SessionDep, pk: int, new_title: str) -> Movie:
    movie = session.get(Movie, pk)
    if not movie:
        raise HTTPException(status_code=404, detail='Movie not found')
    movie.title = new_title
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


@app.delete('/delete/director/{pk}/', response_model=Director)
def delete_director(session: SessionDep, pk: int) -> Director:
    director = session.get(Director, pk)
    if not director:
        raise HTTPException(status_code=404, detail='Director not found')
    session.delete(director)
    session.commit()
    return JSONResponse(content={'message': 'Director is deleted'})




