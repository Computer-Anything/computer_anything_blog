from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import User, BlogPost, Vote


# Create a blueprint for the routes
routes = Blueprint('routes', __name__)

# USER ROUTES
# User registration route
@routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')  # Add email field
    password = data.get('password')

    # Validate input
    if not username or not email or not password:
        return jsonify({"msg": "Username, email, and password are required"}), 400

    # Check if the user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "User already exists"}), 400

    # Create a new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)  # Hash the password
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201


# Login route
@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if the user exists
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"msg": "User does not exist"}), 404

    # Check if the password is correct
    if not user.check_password(password):
        return jsonify({"msg": "Incorrect password"}), 401

    # Generate access token if login is successful
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=12))
    print(f"User ID: {user.id}")
    return jsonify({"access_token": access_token, "user_id": user.id}), 200


# Route to get the user's profile
@routes.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }), 200


# Route to update the user's profile
@routes.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    # Validate input
    if not username or not email:
        return jsonify({"msg": "Username and email are required"}), 400

    # Update user information
    user.username = username
    user.email = email
    db.session.commit()

    return jsonify({"msg": "Profile updated successfully"}), 200


# Route to get any user's profile by ID
@routes.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }), 200


# Route to get all user profiles
@routes.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users]), 200


# BLOG POST ROUTES
# Route to get all blog posts
@routes.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    posts = BlogPost.query.all()
    print(f"JWT Identity: {get_jwt_identity()}")
    return jsonify([post.to_dict() for post in posts]), 200


# Route to get all posts by a specific user
@routes.route('/users/<int:user_id>/posts', methods=['GET'])
@jwt_required()
def get_user_posts(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    posts = BlogPost.query.filter_by(user_id=user_id).all()
    return jsonify([post.to_dict() for post in posts]), 200


# Route to get a single blog post by ID
@routes.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({"msg": "Post not found"}), 404
    return jsonify(post.to_dict()), 200


# Route to create a new blog post
@routes.route('/posts', methods=['POST'])
# TODO: Uncomment the jwt_required decorator to protect this route
@jwt_required()
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    topic_tags = data.get('topic_tags') # Optional field
    user_id = get_jwt_identity()  # Get the user ID from the JWT token

    # Validate input
    if not title or not content:
        return jsonify({"msg": "Title and content are required"}), 400

    # Create a new blog post
    new_post = BlogPost(title=title, content=content, topic_tags=topic_tags, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201


# Route to update a blog post
@routes.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    post = BlogPost.query.get(post_id)

    if not post:
        return jsonify({"msg": "Post not found"}), 404

    # Ensure the post belongs to the current user
    if post.user_id != int(user_id):
        return jsonify({"msg": "You are not authorized to edit this post"}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    topic_tags = data.get('topic_tags') # Optional field

    # Validate input
    if not title or not content:
        return jsonify({"msg": "Title and content are required"}), 400

    # Update the post
    post.title = title
    post.content = content
    post.topic_tags = topic_tags
    db.session.commit()

    return jsonify({"msg": "Post updated successfully", "post": post.to_dict()}), 200


# Route to delete a blog post
@routes.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    post = BlogPost.query.get(post_id)

    if not post:
        return jsonify({"msg": "Post not found"}), 404

    # Ensure the post belongs to the current user
    if post.user_id != int(user_id):
        return jsonify({"msg": "You are not authorized to delete this post"}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({"msg": "Post deleted successfully"}), 200


# Routes for voting on posts
# Route to upvote a blog post
@routes.route('/posts/<int:post_id>/upvote', methods=['POST'])
@jwt_required()
def upvote_post(post_id):
    user_id = get_jwt_identity()
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({"msg": "Post not found"}), 404

    # Check if the user has already voted
    existing_vote = Vote.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing_vote:
        if existing_vote.vote_type == 'upvote':
            # Remove the upvote
            db.session.delete(existing_vote)
            post.upvotes -= 1
        else:
            # Change the vote to upvote
            existing_vote.vote_type = 'upvote'
            post.upvotes += 1
            post.downvotes -= 1
    else:
        # Add a new upvote
        new_vote = Vote(user_id=user_id, post_id=post_id, vote_type='upvote')
        db.session.add(new_vote)
        post.upvotes += 1

    db.session.commit()
    return jsonify({"msg": "Post upvoted successfully", "upvotes": post.upvotes, "downvotes": post.downvotes}), 200

# Route to downvote a blog post
@routes.route('/posts/<int:post_id>/downvote', methods=['POST'])
@jwt_required()
def downvote_post(post_id):
    user_id = get_jwt_identity()
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({"msg": "Post not found"}), 404

    # Check if the user has already voted
    existing_vote = Vote.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing_vote:
        if existing_vote.vote_type == 'downvote':
            # Remove the downvote
            db.session.delete(existing_vote)
            post.downvotes -= 1
        else:
            # Change the vote to downvote
            existing_vote.vote_type = 'downvote'
            post.downvotes += 1
            post.upvotes -= 1
    else:
        # Add a new downvote
        new_vote = Vote(user_id=user_id, post_id=post_id, vote_type='downvote')
        db.session.add(new_vote)
        post.downvotes += 1

    db.session.commit()
    return jsonify({"msg": "Post downvoted successfully", "upvotes": post.upvotes, "downvotes": post.downvotes}), 200
