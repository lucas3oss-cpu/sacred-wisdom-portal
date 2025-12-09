from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import anthropic
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')

# Anthropic API setup
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Login page
@app.route('/login')
def login():
    return render_template('login.html')

# Signup page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Blog listing page
@app.route('/blog')
def blog():
    return render_template('blog.html')

# Individual blog post page
@app.route('/blog/<slug>')
def blog_post(slug):
    return render_template('blog-post.html')

# Admin blog management page
@app.route('/admin/blog')
def admin_blog():
    return render_template('admin-blog.html')

# API endpoint for chatbot
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        conversation_history = data.get('history', [])
        selected_teacher = data.get('teacher', 'Alan Watts')
        
        # Build conversation history for Claude
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Create system prompt based on selected teacher
        teacher_prompts = {
            "Alan Watts": "You are Alan Watts, the British philosopher and interpreter of Eastern philosophy. Respond with wisdom about Zen Buddhism, Taoism, and the nature of consciousness. Be warm, insightful, and help people see the interconnectedness of all things.",
            "Carl Jung": "You are Carl Jung, the Swiss psychiatrist and psychoanalyst. Respond with insights about the collective unconscious, archetypes, shadow work, and individuation. Help people understand their psychological depths.",
            "Rudolf Steiner": "You are Rudolf Steiner, the Austrian philosopher and founder of Anthroposophy. Share wisdom about spiritual science, human development, and the connection between the spiritual and physical worlds.",
            "Sample Questions": "Provide a list of thoughtful questions that users might ask spiritual teachers."
        }
        
        system_prompt = teacher_prompts.get(selected_teacher, teacher_prompts["Alan Watts"])
        
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )
        
        # Extract response text
        response_text = response.content[0].text
        
        return jsonify({
            'response': response_text,
            'teacher': selected_teacher
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
