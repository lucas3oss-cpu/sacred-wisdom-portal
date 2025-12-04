# Sacred Wisdom Portal 🙏✨

A beautiful, responsive web application that provides AI-powered spiritual guidance from 10 renowned spiritual teachers.

## Features

✨ **10 Spiritual Teachers:**
- Eckhart Tolle - Present moment awareness
- Alan Watts - Eastern philosophy and reality
- Carl Jung - Shadow work and individuation
- Ram Dass - Love, service, and awakening
- Marianne Williamson - A Course in Miracles
- Thich Nhat Hanh - Mindfulness and peace
- Rumi - Sufi mysticism and divine love
- Jesus (Gnostic Perspective) - Inner Kingdom and gnosis
- Paramahansa Yogananda - Kriya Yoga and God-realization
- Adyashanti - Non-dual awakening

🎨 **Beautiful Design:**
- Fully responsive (works on phones, tablets, and computers)
- Elegant spiritual aesthetic with gold and purple accents
- Smooth animations and transitions
- Dark theme optimized for meditation

📚 **Core Features:**
- Ask questions to any spiritual teacher
- Conversation history tracking
- Save favorite responses
- Sample prompts to get started

🧘 **Spiritual Tools:**
- Meditation timer (5, 10, 20, 30 minutes)
- Box breathing exercise guide

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Your API Key

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Run Locally

```bash
python spiritual_app.py
```

Open your browser to: http://localhost:5000

## Deployment to Render (Free Hosting)

### Step 1: Prepare for Deployment

Create a `Procfile` (tells Render how to run your app):
```
web: gunicorn spiritual_app:app
```

Add `gunicorn` to your `requirements.txt`:
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

### Step 2: Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit - Sacred Wisdom Portal"
```

Create a new repository on GitHub and push:
```bash
git remote add origin https://github.com/yourusername/sacred-wisdom-portal.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Render

1. Go to https://render.com and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** sacred-wisdom-portal (or your choice)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn spiritual_app:app`
   - **Plan:** Free

5. Add Environment Variable:
   - Click "Environment" tab
   - Add: `ANTHROPIC_API_KEY` = your_api_key

6. Click "Create Web Service"

Your app will be live at: `https://sacred-wisdom-portal.onrender.com`

## Alternative: Deploy to Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create new app
heroku create sacred-wisdom-portal

# Set environment variable
heroku config:set ANTHROPIC_API_KEY=your_api_key_here

# Deploy
git push heroku main

# Open your app
heroku open
```

## Alternative: Deploy to PythonAnywhere

1. Sign up at https://www.pythonanywhere.com (free account)
2. Upload your files via Files tab
3. Create a new web app (Flask)
4. Set environment variable in WSGI configuration
5. Reload your app

## Usage

1. **Choose a Teacher:** Select from the dropdown menu
2. **Ask a Question:** Type your spiritual question
3. **Receive Wisdom:** Click "Receive Wisdom" to get guidance
4. **Save Favorites:** Click the star button to save meaningful responses
5. **View History:** Access your past conversations anytime
6. **Meditation Tools:** Use the timer or breathwork exercises

## Sample Questions

- "How can I find peace in difficult times?"
- "What is the nature of my true self?"
- "How do I let go of past suffering?"
- "What is the path to awakening?"
- "How can I live more mindfully?"

## Cost Considerations

Each question uses Claude Sonnet 4, which costs approximately:
- **Input:** ~$0.003 per question (system prompt + question)
- **Output:** ~$0.015 per response (average response)
- **Total:** ~$0.02 per conversation

With Anthropic's $5 free credit, you get approximately 250 questions.

## Technical Stack

- **Backend:** Flask (Python)
- **AI:** Anthropic Claude Sonnet 4 API
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Fonts:** Crimson Pro, Cormorant Garamond (Google Fonts)
- **Design:** Responsive, mobile-first design

## File Structure

```
sacred-wisdom-portal/
├── spiritual_app.py          # Main Flask application
├── templates/
│   └── index.html            # Frontend HTML template
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your API key (not committed)
├── Procfile                 # Render/Heroku deployment config
└── README.md               # This file
```

## Customization

### Add More Teachers

Edit `SPIRITUAL_TEACHERS` in `spiritual_app.py`:

```python
"your_teacher": {
    "name": "Teacher Name",
    "description": "Brief description",
    "system_prompt": """Your detailed system prompt..."""
}
```

### Change Colors

Edit CSS variables in `templates/index.html`:

```css
:root {
    --primary-bg: #0a0e1a;
    --accent-gold: #d4af37;
    --accent-purple: #8b7ab8;
}
```

### Add More Sample Prompts

Edit `SAMPLE_PROMPTS` list in `spiritual_app.py`.

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
pip install -r requirements.txt
```

### "API key not found"
Make sure `.env` file exists with your API key, or set environment variable:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### Port already in use
Change the port in `spiritual_app.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

## Privacy & Security

- Conversations are stored in session (not permanently saved)
- Sessions clear when browser closes
- API key is never exposed to frontend
- No user data is collected or stored permanently

## License

This project is open source and available for personal and educational use.

## Support

For issues or questions about:
- **Anthropic API:** https://docs.anthropic.com/
- **Flask:** https://flask.palletsprojects.com/
- **Deployment:** Check your hosting provider's documentation

## Credits

Built with love for spiritual seekers everywhere. May this tool serve your journey toward awakening, peace, and understanding.

🙏 Namaste ✨

---

**Note:** This application requires an active internet connection and Anthropic API credits to function. The free tier provides $5 in credits, which is enough for approximately 250 conversations.
