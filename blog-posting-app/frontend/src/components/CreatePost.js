import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown'; // Import ReactMarkdown for preview
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'; // Import SyntaxHighlighter
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'; // Import a syntax highlighting theme
import API from '../services/api';
import '../styles/CreateEditPost.css'; // Import the CSS file


// This component handles the creation of a new blog post
const CreatePost = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState(''); // State for tags
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Format tags: Add # prefix to each tag and remove extra spaces
    const formattedTags = tags
      .split(',')
      .map((tag) => `#${tag.trim()}`)
      .join(', ');
    // Check if the title and content are not empty
    try {
      const response = await API.post(
        '/posts',
        { title, content, topic_tags: formattedTags }, // Include formatted tags
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        }
      );
      setMessage('Post created successfully!');
      setTimeout(() => navigate('/posts'), 2000);
    } catch (error) {
      console.error('Error creating post:', error.response?.data || error.message);
      setMessage('Failed to create post. Please try again.');
    }
  };

  // Render the create post form
  return (
    <div className="create-edit-post-container">
      <div className="form-section">
        <h1>Create New Post</h1>
        <button
          className="back-to-blog-btn"
          onClick={() => navigate('/posts')}
          style={{ marginBottom: '20px' }}
        >
          Back to Blog
        </button>
        <form onSubmit={handleSubmit}>
          <div>
            <label>Title:</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Content (Markdown Supported):</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write your post in Markdown format..."
              required
            />
          </div>
          <div>
            <label>Tags (comma-separated, e.g., tech, programming):</label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="e.g., tech, programming, AI"
            />
          </div>
          <button type="submit">Create Post</button>
        </form>
        {message && <p>{message}</p>}
      </div>
      <div className="preview-section">
        <h2>Preview</h2>
        <div className="preview-content">
          <h1>{title || 'Post Title'}</h1>
          <ReactMarkdown
            children={content || 'Start writing your post content to see the preview here...'}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          />
          {tags && (
            <div className="tags">
              <strong>Tags:</strong>{' '}
              {tags.split(',').map((tag, index) => (
                <span key={index} className="tag">
                  {`#${tag.trim()}`}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreatePost;
