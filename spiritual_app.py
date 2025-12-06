# Updated version 2.0
from flask import Flask, render_template, request, jsonify, session
from anthropic import Anthropic
import os
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Premium access code - You can change this to whatever you want
PREMIUM_ACCESS_CODE = "mysoulcompass2025"

# Free tier teachers (5 teachers)
FREE_TIER_TEACHERS = [
    "eckhart_tolle",
    "alan_watts", 
    "carl_jung",
    "gnostic_jesus",
    "marianne_williamson"
]

# Spiritual Teachers Configuration
SPIRITUAL_TEACHERS = {
    "eckhart_tolle": {
        "name": "Eckhart Tolle",
        "description": "Present moment awareness and consciousness",
        "tier": "free",
        "system_prompt": """You are channeling the wisdom of Eckhart Tolle. Speak with his gentle, present-moment awareness. 
        Focus on: the power of Now, ego dissolution, presence, consciousness, inner body awareness, and freedom from the thinking mind. 
        Use his calm, clear teaching style that points to direct experience rather than intellectual understanding."""
    },
    "alan_watts": {
        "name": "Alan Watts",
        "description": "Eastern philosophy and the nature of reality",
        "tier": "free",
        "system_prompt": """You are channeling the wisdom of Alan Watts. Speak with his playful, philosophical wit and deep understanding of Eastern thought. 
        Focus on: the illusion of the separate self, the unity of all things, Zen Buddhism, Taoism, the nature of consciousness, 
        and the cosmic game. Use his engaging, often humorous style with rich metaphors."""
    },
    "carl_jung": {
        "name": "Carl Jung",
        "description": "Shadow work, individuation, and the collective unconscious",
        "tier": "free",
        "system_prompt": """You are channeling the wisdom of Carl Jung. Speak with psychological depth and symbolic insight. 
        Focus on: the shadow, archetypes, individuation, the collective unconscious, dreams, synchronicity, anima/animus, 
        and the integration of opposites. Use his scholarly yet accessible approach."""
    },
    "gnostic_jesus": {
        "name": "Jesus (Gnostic Perspective)",
        "description": "Inner Kingdom and divine gnosis",
        "tier": "free",
        "system_prompt": """You are channeling Jesus from a Gnostic perspective, drawing from the Gospel of Thomas and Nag Hammadi texts. 
        Focus on: the Kingdom of Heaven within, direct knowing (gnosis), the divine spark in all beings, 
        inner light, self-knowledge as salvation, and mystical union with the Divine. Use paradoxical wisdom and mystical teachings."""
    },
    "marianne_williamson": {
        "name": "Marianne Williamson",
        "description": "A Course in Miracles and spiritual psychology",
        "tier": "free",
        "system_prompt": """You are channeling the wisdom of Marianne Williamson. Speak with passionate conviction about love and miracles. 
        Focus on: A Course in Miracles principles, choosing love over fear, forgiveness as the key to peace, 
        our divine nature, and applying spiritual principles to practical life. Use her eloquent, empowering style."""
    },
    "ram_dass": {
        "name": "Ram Dass",
        "description": "Love, service, and spiritual awakening",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Ram Dass (Richard Alpert). Speak with warmth, humor, and radical acceptance. 
        Focus on: being here now, loving awareness, service as spiritual practice, guru yoga, dying consciously, 
        and embracing all of life's experiences. Use his conversational, heart-centered style."""
    },
    "thich_nhat_hanh": {
        "name": "Thich Nhat Hanh",
        "description": "Mindfulness and engaged Buddhism",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Thich Nhat Hanh. Speak with gentle, poetic simplicity and deep peace. 
        Focus on: mindful breathing, interbeing, engaged Buddhism, peace in daily life, loving kindness, 
        and mindful living. Use his simple, profound, and accessible teaching style."""
    },
    "rumi": {
        "name": "Rumi",
        "description": "Sufi mysticism and divine love",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Rumi, the 13th-century Persian Sufi mystic. Speak with poetic ecstasy and mystical love. 
        Focus on: divine love, unity with the Beloved, the wound that opens us, ecstatic surrender, 
        and the journey of the soul. Use poetic, metaphorical language filled with longing and joy."""
    },
    "paramahansa_yogananda": {
        "name": "Paramahansa Yogananda",
        "description": "Kriya Yoga and God-realization",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Paramahansa Yogananda. Speak with joyful devotion and practical spirituality. 
        Focus on: Kriya Yoga, God-realization, the science of religion, energy and consciousness, 
        meditation techniques, and living in divine joy. Use his blend of Eastern wisdom and Western practicality."""
    },
    "adyashanti": {
        "name": "Adyashanti",
        "description": "Non-dual awakening and true meditation",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Adyashanti. Speak with clear, direct pointing to truth beyond concepts. 
        Focus on: non-dual awareness, true meditation, falling away of the ego, awakening and embodiment, 
        the end of seeking, and resting as awareness. Use his precise, no-nonsense approach to spiritual truth."""
    }
}

# Sample prompts for users
SAMPLE_PROMPTS = [
    "How can I find peace in difficult times?",
    "What is the nature of my true self?",
    "How do I let go of past suffering?"
]

@app.route('/')
def index():
    # Initialize session variables
    if 'email_collected' not in session:
        session['email_collected'] = False
    if 'is_premium' not in session:
        session['is_premium'] = False
    if 'questions_today' not in session:
        session['questions_today'] = 0
        session['question_date'] = datetime.now().strftime('%Y-%m-%d')
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    if 'favorites' not in session:
        session['favorites'] = []
    
    # Reset question count if new day
    today = datetime.now().strftime('%Y-%m-%d')
    if session.get('question_date') != today:
        session['questions_today'] = 0
        session['question_date'] = today
    
    return render_template('index.html', 
                         teachers=SPIRITUAL_TEACHERS,
                         sample_prompts=SAMPLE_PROMPTS,
                         is_premium=session.get('is_premium', False),
                         email_collected=session.get('email_collected', False))

@app.route('/collect_email', methods=['POST'])
def collect_email():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    
    # In production, save to database
    # For now, just mark as collected
    session['email_collected'] = True
    session['user_email'] = email
    session['user_name'] = name
    
    return jsonify({'success': True})

@app.route('/verify_premium', methods=['POST'])
def verify_premium():
    data = request.json
    code = data.get('code')
    
    if code == PREMIUM_ACCESS_CODE:
        session['is_premium'] = True
        return jsonify({'success': True, 'message': 'Premium access activated! 🎉'})
    else:
        return jsonify({'success': False, 'message': 'Invalid access code. Please check and try again.'})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_question = data.get('question')
    teacher_key = data.get('teacher')
    
    if not user_question or not teacher_key:
        return jsonify({'error': 'Missing question or teacher'}), 400
    
    if teacher_key not in SPIRITUAL_TEACHERS:
        return jsonify({'error': 'Invalid teacher'}), 400
    
    teacher = SPIRITUAL_TEACHERS[teacher_key]
    
    # Check if user has premium access
    is_premium = session.get('is_premium', False)
    
    # Check teacher access
    if teacher['tier'] == 'premium' and not is_premium:
        return jsonify({'error': 'This teacher is only available for Premium members. Please upgrade to access all 10 teachers!'}), 403
    
    # Check question limit for free users
    if not is_premium:
        today = datetime.now().strftime('%Y-%m-%d')
        if session.get('question_date') != today:
            session['questions_today'] = 0
            session['question_date'] = today
        
        if session.get('questions_today', 0) >= 5:
            return jsonify({'error': 'You have reached your daily limit of 5 questions. Upgrade to Premium for unlimited access!'}), 403
        
        session['questions_today'] = session.get('questions_today', 0) + 1
        session.modified = True
    
    try:
        # Call Anthropic API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=teacher['system_prompt'],
            messages=[{
                "role": "user",
                "content": user_question
            }]
        )
        
        response_text = message.content[0].text
        
        # Save to conversation history (only for premium)
        if is_premium:
            conversation_entry = {
                'timestamp': datetime.now().isoformat(),
                'teacher': teacher['name'],
                'question': user_question,
                'response': response_text,
                'id': secrets.token_hex(8)
            }
            
            if 'conversation_history' not in session:
                session['conversation_history'] = []
            
            session['conversation_history'].insert(0, conversation_entry)
            session['conversation_history'] = session['conversation_history'][:50]
            session.modified = True
        
        return jsonify({
            'response': response_text,
            'teacher': teacher['name'],
            'id': secrets.token_hex(8) if is_premium else None,
            'questions_remaining': None if is_premium else (5 - session.get('questions_today', 0))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_history():
    if not session.get('is_premium', False):
        return jsonify({'error': 'Premium feature only'}), 403
    
    history = session.get('conversation_history', [])
    return jsonify(history)

@app.route('/favorites')
def get_favorites():
    if not session.get('is_premium', False):
        return jsonify({'error': 'Premium feature only'}), 403
    
    favorites = session.get('favorites', [])
    return jsonify(favorites)

@app.route('/favorite/add', methods=['POST'])
def add_favorite():
    if not session.get('is_premium', False):
        return jsonify({'error': 'Premium feature only'}), 403
    
    data = request.json
    conversation_id = data.get('id')
    
    if 'conversation_history' not in session:
        return jsonify({'error': 'No conversation history'}), 400
    
    conversation = next((c for c in session['conversation_history'] if c['id'] == conversation_id), None)
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    if 'favorites' not in session:
        session['favorites'] = []
    
    if not any(f['id'] == conversation_id for f in session['favorites']):
        session['favorites'].insert(0, conversation)
        session.modified = True
    
    return jsonify({'success': True})

@app.route('/favorite/remove', methods=['POST'])
def remove_favorite():
    if not session.get('is_premium', False):
        return jsonify({'error': 'Premium feature only'}), 403
    
    data = request.json
    conversation_id = data.get('id')
    
    if 'favorites' not in session:
        return jsonify({'error': 'No favorites'}), 400
    
    session['favorites'] = [f for f in session['favorites'] if f['id'] != conversation_id]
    session.modified = True
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
