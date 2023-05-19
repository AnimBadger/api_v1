from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(
            host='localhost', database='api', user='admin', password='admin', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Database connection was successful')
        break

    except Exception as error:
        print('Connection failed')
        print('retrying')
        time.sleep(5)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


@app.get('/posts')
def home():
    cursor.execute(''' SELECT  * FROM social ''')
    posts = cursor.fetchall()
    return {'data': posts}


@app.post('/posts', status_code=status.HTTP_201_CREATED)
def post(post: Post):
    cursor.execute(
        ''' INSERT INTO social (title, content) VALUES (%s, %s) RETURNING *''', (post.title, post.content))
    new_post = cursor.fetchone()
    conn.commit()
    return {'post': new_post}


@app.get('/posts/{id}', status_code=status.HTTP_200_OK)
def one_post(id: int):
    cursor.execute('''SELECT * FROM social WHERE id = %s ''', (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} not found')
    return {'data': post}


@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        '''DELETE FROM social WHERE id = %s RETURNING * ''', (str(id)))
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} not found')


@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    cursor.execute('''UPDATE social SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * ''',
                   (post.title, post.content, post.published, str(id)))
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} not found')
    return {'data': post}
