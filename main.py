from fastapi import FastAPI, HTTPException 
from pymongo import MongoClient
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os



app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client["blog_platform"]

# Define the directory containing your static files
static_dir = os.path.join(os.path.dirname(__file__), "static")

# Mount the static files directory to a specific URL path
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Route for the root URL
@app.get("/")
async def root():
    """
    Return the index.html file when the root URL is accessed
    """
    index_path = os.path.join(static_dir, "index.html")
    print(index_path)
    return FileResponse(index_path)

# Allow requests from your frontend domain (replace "http://localhost:8000" with your frontend URL)
# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Data Models
class User(BaseModel):
    """
    User model with username and email fields
    """
    username: str
    email: str

class Post(BaseModel):
    """
    Post model with title, content, author, comments, likes, and dislikes fields
    """
    title: str
    content: str
    author: str
    comments: List[str] = []
    likes: int = 0
    dislikes: int = 0

class Comment(BaseModel):
    """
    Comment model with content and author fields
    """
    content: str
    author: str

class Like(BaseModel):
    """
    Like model with post_id and user_id fields
    """
    user_id: str
    post_id: str


# CRUD Operations for User
class UserCRUD:
    """
    Class to perform CRUD operations for the User model
    """
    @staticmethod
    def create_user(user: User):
        """
        Create a new user in the database
        """
        user_data = user.model_dump()
        result = db.users.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def get_user(user_id: str):
        """
        Get a user by ID
        """
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return Post(**user)
        else:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    def update_user(user_id: str, user: User):
        """
        Update a user by ID
        """
        user_data = user.model_dump()
        result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    def delete_user(user_id: str):
        """
        Delete a user by ID
        """
        result = db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

# Endpoints
@app.post("/users/")
async def create_user(user: User):
    """
    Create a new user
    """
    user_id = UserCRUD.create_user(user)
    return {"id": user_id}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    """
    Get a user by ID
    """
    user = UserCRUD.get_user(user_id)
    return user

@app.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    """
    Update a user by ID
    """
    UserCRUD.update_user(user_id, user)
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user by ID
    """
    UserCRUD.delete_user(user_id)
    return {"message": "User deleted successfully"}

# CRUD Operations for Post
class PostCRUD:
    """
    Class to perform CRUD operations for the Post model
    """
    @staticmethod
    def create_post(post: Post):
        """
        Create a new post in the database
        """
        post_data = post.model_dump()
        result = db.posts.insert_one(post_data)
        return str(result.inserted_id)

    @staticmethod
    def get_post(post_id: str):
        """
        Get a post by ID
        """
        post = db.posts.find_one({"_id": ObjectId(post_id)})
        if post:
            return Post(**post)
        else:
            raise HTTPException(status_code=404, detail="Post not found")


    @staticmethod
    def update_post(post_id: str, post: Post):
        """ 
        Update a post by ID
        """
        post_data = post.model_dump()
        result = db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": post_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

    @staticmethod
    def delete_post(post_id: str):
        """
        Delete a post by ID
        """
        result = db.posts.delete_one({"_id": ObjectId(post_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

# Endpoints for Post
@app.post("/posts/")
async def create_post(post: Post):
    """
    Create a new post
    """
    post_id = PostCRUD.create_post(post)
    return {"id": post_id}

@app.get("/posts/{post_id}")
async def read_post(post_id: str):
    """
    Get a post by ID
    """
    if post_id == 'null':
        # Return a specific response or raise an HTTPException with a 404 status code
        # For example:
        return {"message": "Invalid post ID"}
        # or raise HTTPException(status_code=404, detail="Post not found")
    else:
        post = PostCRUD.get_post(post_id)
        return post

@app.put("/posts/{post_id}")
async def update_post(post_id: str, post: Post):
    """
    Update a post by ID
    """
    PostCRUD.update_post(post_id, post)
    return {"message": "Post updated successfully"}

# Endpoint to delete a post by ID
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    """
    Delete a post by ID
    """
    try:
        PostCRUD.delete_post(post_id)
        return {"message": "Post deleted successfully"}
    except Exception as e:
        return {"error": str(e)}, 500  # Return an error response with status code 500

# Endpoint to fetch all posts
@app.get("/posts/")
async def get_all_posts():
    """
    Get all posts from the database
    """
    posts = list(db.posts.find())
    # Convert ObjectId to string for JSON serialization
    serialized_posts = [{**post, "_id": str(post["_id"])} for post in posts]
    return JSONResponse(content={"posts": serialized_posts})




# CRUD Operations for Comment
class CommentCRUD:
    """
    Class to perform CRUD operations for the Comment model
    """
    @staticmethod
    def create_comment(post_id: str, comment: Comment):  # Add post_id as a parameter
        comment_data = comment.model_dump()
        comment_data['post_id'] = post_id  # Assign post_id to the comment data
        result = db.comments.insert_one(comment_data)
        return str(result.inserted_id)

    @staticmethod
    def get_comment(comment_id: str):
        comment = db.comments.find_one({"_id": ObjectId(comment_id)})
        if comment:
            return Post(**comment)
        else:
            raise HTTPException(status_code=404, detail="Comment not found")
    @staticmethod
    def get_comments_for_post(post_id: str):
        comments = db.comments.find({"post_id": post_id})
        return [Comment(**comment) for comment in comments]

    @staticmethod
    def update_comment(comment_id: str, comment: Comment):
        comment_data = comment.model_dump()
        result = db.comments.update_one({"_id": ObjectId(comment_id)}, {"$set": comment_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Comment not found")

    @staticmethod
    def delete_comment(comment_id: str):
        result = db.comments.delete_one({"_id": ObjectId(comment_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Comment not found")

# Endpoints for Comment
@app.post("/comments/{post_id}")
async def create_comment(post_id: str, comment: Comment):  # Include post_id as a route parameter
    try:
        comment_id = CommentCRUD.create_comment(post_id, comment)  # Pass post_id to create_comment method
        return {"id": comment_id}
    except Exception as e:
        return {"error": str(e)}, 500  # Return an error response with status code 500




@app.get("/comments/{comment_id}")
async def read_comment(comment_id: str):
    comment = CommentCRUD.get_comment(comment_id)
    return comment

@app.put("/comments/{comment_id}")
async def update_comment(comment_id: str, comment: Comment):
    CommentCRUD.update_comment(comment_id, comment)
    return {"message": "Comment updated successfully"}

@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str):
    CommentCRUD.delete_comment(comment_id)
    return {"message": "Comment deleted successfully"}

@app.get("/posts/{post_id}/comments")
async def read_comments_for_post(post_id: str):
    comments = CommentCRUD.get_comments_for_post(post_id)
    return {"comments": comments}






# CRUD Operations for Like
class LikeCRUD:
    @staticmethod
    def create_like(like: Like):
        like_data = like.dict()
        result = db.likes.insert_one(like_data)
        return str(result.inserted_id)

    @staticmethod
    def get_like(like_id: str):
        like = db.likes.find_one({"_id": ObjectId(like_id)})
        if like:
            return Post(**like)
        else:
            raise HTTPException(status_code=404, detail="Like not found")

    @staticmethod
    def update_like(like_id: str, like: Like):
        like_data = like.dict()
        result = db.likes.update_one({"_id": ObjectId(like_id)}, {"$set": like_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Like not found")

    @staticmethod
    def delete_like(like_id: str):
        result = db.likes.delete_one({"_id": ObjectId(like_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Like not found")

# Endpoints for Like
# Endpoint to increment the like count for a post
@app.put("/posts/{post_id}/like")
async def like_post(post_id: str):
    result = db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$inc": {"likes": 1}}  # Increment the likes field by 1
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    updated_post = db.posts.find_one({"_id": ObjectId(post_id)})
    return {"likes": updated_post["likes"]}


@app.put("/likes/{like_id}")
async def update_like(like_id: str, like: Like):
    LikeCRUD.update_like(like_id, like)
    return {"message": "Like updated successfully"}

@app.delete("/likes/{like_id}")
async def delete_like(like_id: str):
    LikeCRUD.delete_like(like_id)
    return {"message": "Like deleted successfully"}
