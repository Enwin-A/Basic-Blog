// Function to fetch post details by ID
function fetchPostById(postId) {
    return fetch(`http://localhost:8000/posts/${postId}`)
        .then(response => response.json())
        .catch(error => console.error('Error fetching post:', error));
}

// Function to fetch comments for a post by ID
function fetchCommentsForPost(postId) {
    return fetch(`http://localhost:8000/posts/${postId}/comments`)
        .then(response => response.json())
        .catch(error => console.error('Error fetching comments:', error));
}

// Function to create a new post
function createPost(postData) {
    return fetch('http://localhost:8000/posts/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
    })
    .then(response => response.json())
    .catch(error => console.error('Error creating post:', error));
}

// Function to add a comment to a post
function addCommentToPost(postId, commentData) {
    console.log('Adding comment to post:', postId, commentData);    
    return fetch(`http://localhost:8000/comments/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(commentData),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to create comment');
        }
        return response.json();
    })
    .then(data => {
        console.log('Comment created successfully:', data);
        return data; // Return the created comment data if needed
    })
    .catch(error => {
        console.error('Error adding comment:', error);
        throw error;  // Propagate the error further
    });
}




// Function to display posts on the index.html page
function displayPosts(postsData) {
    const posts = postsData.posts; // Accessing the array of posts
    const postListContainer = document.getElementById('post-list');
    // Check if postListContainer exists before proceeding
    if (!postListContainer) {
        console.error('post-list element not found.');
        return;
    }

    if (posts === null) {
        postListContainer.innerHTML = '<p>No posts available.</p>';
    } else {
        console.log(posts);
        postListContainer.innerHTML = '';
        posts.forEach(post => {
            const postItem = document.createElement('div');
            postItem.innerHTML = `
                <h2>${post.title}</h2>
                <p>${post.content}</p>
                <p>Author: ${post.author}</p>
                <!--<a href="posts/${post._id}">View Details</a>-->
                <a href="static/post.html?id=${post._id}">View Details</a>
                <button onclick="deletePost('${post._id}')">Delete</button> 
                <hr>
            `;
            postListContainer.appendChild(postItem);
        });
    }
}
function fetchAllPosts() {
    return fetch('http://localhost:8000/posts/')
        .then(response => response.json())
        .catch(error => console.error('Error fetching posts:', error));
}

// Fetch all posts and then display them
fetchAllPosts()
    .then(posts => {
        displayPosts(posts);
    })
    .catch(error => console.error('Error fetching posts:', error));

// Function to initialize the create post form
function initCreatePostForm() {
    const createPostForm = document.getElementById('create-post-form');
    if (createPostForm) {
        createPostForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const postData = {
                title: formData.get('title'),
                content: formData.get('content'),
                author: formData.get('author'),
            };
            createPost(postData)
                .then(response => {
                    alert('Post created successfully!');
                    window.location.href = '/';
                })
                .catch(error => console.error('Error creating post:', error));
        });
    } else {
        console.error('Create post form not found.');
    }
}

// Function to display post details on the post.html page
function displayPostDetails(postId) {
    // Fetch post details
    fetchPostById(postId)
        .then(post => {
            // Display post details
            const postDetailsContainer = document.getElementById('post-details');
            postDetailsContainer.innerHTML = `
                <h2>${post.title}</h2>
                <p>${post.content}</p>
                <p>Author: ${post.author}</p>
            `;

            // Fetch comments for the post
            fetchCommentsForPost(postId)
                .then(commentsData => {
                    // Display comments for the post
                    let commentsContainer = document.getElementById('comments-container');
                    if (!commentsContainer) {
                        commentsContainer = document.createElement('div');
                        commentsContainer.id = 'comments-container';
                        document.body.appendChild(commentsContainer);
                    }
                    const comments = commentsData.comments; // Access the comments array
                    commentsContainer.innerHTML = '<h3>Comments</h3>';
                    if (comments.length > 0) {
                        comments.forEach(comment => {
                            commentsContainer.innerHTML += `
                                <div>
                                    <p>${comment.content}</p>
                                    <p>Author: ${comment.author}</p>
                                </div>
                            `;
                        });
                    } else {
                        commentsContainer.innerHTML += '<p>No comments available.</p>';
                    }
                })
                .catch(error => console.error('Error fetching comments:', error));
        })
        .catch(error => console.error('Error displaying post details:', error));
}

// Function to initialize the post details page
function initPostPage() {
    console.log('Initializing post details page');
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('id');

    if (postId) {
        displayPostDetails(postId);
        console.log('Initializing comment form for post:', postId);
        initCommentForm(postId); // Pass postId to initCommentForm
    } else {
        console.error('Post ID not provided in URL');
    }
}

// Function to initialize the comment form
function initCommentForm(postId) {
    const addCommentForm = document.getElementById('add-comment-form');
    if (addCommentForm) {
        addCommentForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const commentData = {
                content: formData.get('comment'),
                author: formData.get('comment-author'),
            };
            if (postId) {
                // Add comment to the post
                addCommentToPost(postId, commentData)
                    .then(response => {
                        // Reload the page to display the new comment
                        window.location.reload();
                    })
                    .catch(error => console.error('Error adding comment:', error));
            } else {
                console.error('Post ID not provided in URL');
            }
        });
    } else {
        console.error('Add comment form not found.');
    }
}

// Function to handle liking a post
function likePost(postId) {
    fetch(`http://localhost:8000/posts/${postId}/like`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        // Update the like count on the frontend
        const likeCountElement = document.getElementById('like-count');
        if (likeCountElement) {
            likeCountElement.textContent = `Likes: ${data.likes}`;
        }
    })
    .catch(error => console.error('Error liking post:', error));
}

// Event listener for the like button
const likeButton = document.getElementById('like-button');
if (likeButton) {
    likeButton.addEventListener('click', function(event) {
        event.preventDefault();
        const urlParams = new URLSearchParams(window.location.search);
        const postId = urlParams.get('id');
        if (postId) {
            likePost(postId);
        } else {
            console.error('Post ID not provided in URL');
        }
    });
}
// Function to delete a post by ID
function deletePost(postId) {
    fetch(`http://localhost:8000/posts/${postId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete post');
        }
        alert('Post deleted successfully!');
        window.location.reload(); // Refresh the page after deletion
    })
    .catch(error => console.error('Error deleting post:', error));
}



// Initialize the create post form when the DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCreatePostForm();
});
