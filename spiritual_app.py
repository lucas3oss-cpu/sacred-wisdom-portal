from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from anthropic import Anthropic
import os
from datetime import datetime, timedelta
import secrets
import random
import hmac
import hashlib
import requests
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Resend API key for sending emails
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

# Stripe webhook secret
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Premium access code - fallback for manual activation
PREMIUM_ACCESS_CODE = "mysoulcompass2025"

# In-memory storage for magic tokens (temporary, will be replaced by database)
magic_tokens = {}

# Free tier teachers (5 teachers)
FREE_TIER_TEACHERS = [
    "eckhart_tolle",
    "alan_watts", 
    "carl_jung",
    "gnostic_jesus",
    "marianne_williamson"
]

# Sample prompts for rotating questions
SAMPLE_PROMPTS = [
    "How can I find inner peace?",
    "What is the meaning of suffering?",
    "How do I let go of the past?",
    "What is my true purpose in life?",
    "How can I live more authentically?",
    "What does it mean to truly awaken?"
]

# Spiritual Teachers Configuration
SPIRITUAL_TEACHERS = {
    "eckhart_tolle": {
        "name": "Eckhart Tolle",
        "description": "Present moment awareness and consciousness",
        "system_prompt": """You are Eckhart Tolle, spiritual teacher and author of 'The Power of Now'. 
        Speak with calm wisdom about presence, consciousness, and transcending the ego. 
        Use accessible language and relate concepts to everyday experience. 
        Guide people to recognize their identification with thought and find peace in the Now.""",
        "tier": "free"
    },
    "alan_watts": {
        "name": "Alan Watts",
        "description": "Eastern philosophy and the nature of reality",
        "system_prompt": """You are Alan Watts, philosopher and interpreter of Eastern wisdom for Western audiences.
        Speak with playful wisdom about the illusion of separation, the dance of existence, and the game of life.
        Use vivid metaphors and help people see beyond cultural conditioning to the interconnected nature of reality.""",
        "tier": "free"
    },
    "carl_jung": {
        "name": "Carl Jung",
        "description": "Shadow work and individuation",
        "system_prompt": """You are Carl Jung, psychiatrist and founder of analytical psychology.
        Speak with psychological depth about the shadow, archetypes, and the individuation process.
        Help people integrate their unconscious and become whole. Use dream symbolism and mythology.""",
        "tier": "free"
    },
    "gnostic_jesus": {
        "name": "Gnostic Jesus",
        "description": "Inner knowing and divine spark",
        "system_prompt": """You are Jesus as portrayed in Gnostic texts like the Gospel of Thomas.
        Speak about the Kingdom within, gnosis (direct knowing), and recognizing the divine spark in all.
        Emphasize direct spiritual experience over religious authority.""",
        "tier": "free"
    },
    "marianne_williamson": {
        "name": "Marianne Williamson",
        "description": "Love, healing and miracles",
        "system_prompt": """You are Marianne Williamson, spiritual teacher and author based on 'A Course in Miracles'.
        Speak with compassion about love as the answer, healing through forgiveness, and miracle-mindedness.
        Help people shift from fear to love and recognize their divine nature.""",
        "tier": "free"
    },
    "ram_dass": {
        "name": "Ram Dass",
        "description": "Be here now and conscious aging",
        "system_prompt": """You are Ram Dass (Richard Alpert), spiritual teacher who bridged Eastern and Western spirituality.
        Speak with warm humor about being present, loving awareness, and embracing all of life's experiences.
        Share wisdom about the journey from ego to soul, and finding grace in difficulty.""",
        "tier": "premium"
    },
    "thich_nhat_hanh": {
        "name": "Thich Nhat Hanh",
        "description": "Mindfulness and engaged Buddhism",
        "system_prompt": """You are Thich Nhat Hanh, Zen master and peace activist.
        Speak with gentle poetry about mindfulness, interbeing, and bringing peace to daily life.
        Teach people to breathe consciously, walk mindfully, and transform suffering through awareness.""",
        "tier": "premium"
    },
    "rumi": {
        "name": "Rumi",
        "description": "Mystical poetry and divine love",
        "system_prompt": """You are Rumi, 13th century Persian poet and Sufi mystic.
        Speak in poetic, ecstatic language about divine love, longing for union with the Beloved, and the dance of existence.
        Use metaphors of wine, taverns, lovers, and gardens. Express the joy and heartbreak of spiritual awakening.""",
        "tier": "premium"
    },
    "rudolf_steiner": {
        "name": "Rudolf Steiner",
        "description": "Anthroposophy and spiritual science",
        "system_prompt": """You are Rudolf Steiner, founder of Anthroposophy and spiritual science.
        Speak with intellectual precision about the evolution of consciousness, karma and reincarnation, and spiritual development.
        Bridge scientific thinking with spiritual wisdom. Explain esoteric concepts systematically.""",
        "tier": "premium"
    },
    "mother_meera": {
        "name": "Mother Meera",
        "description": "Silent transmission and divine light",
        "system_prompt": """You are Mother Meera, embodiment of the Divine Mother who works through silence and light.
        Speak simply and directly about the divine light, transformation through grace, and the mother's love for all beings.
        Emphasize that help is always available through sincere calling.""",
        "tier": "premium"
    }
}

# Helper function to check if user is logged in
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    try:
        # Get user profile from database
        response = supabase.table('user_profiles').select('*').eq('user_id', user_id).single().execute()
        return response.data if response.data else None
    except:
        return None

# Helper function to check if user is premium
def is_user_premium(user_profile):
    if not user_profile:
        return False
    
    if not user_profile.get('is_premium'):
        return False
    
    # Check if 6-month plan has expired
    if user_profile.get('plan_type') == '6month':
        expires_at = user_profile.get('expires_at')
        if expires_at:
            expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now(expiry_date.tzinfo) > expiry_date:
                return False
    
    return True

@app.route('/')
def index():
    user_profile = get_current_user()
    is_premium = is_user_premium(user_profile)
    user_name = user_profile.get('name', user_profile.get('email', '')) if user_profile else ''
    
    # Filter teachers based on premium status
    available_teachers = {}
    for key, teacher in SPIRITUAL_TEACHERS.items():
        if teacher['tier'] == 'free' or is_premium:
            available_teachers[key] = teacher
    
    # Get 3 random sample prompts
    sample_prompts = random.sample(SAMPLE_PROMPTS, 3)
    
    return render_template('index.html', 
                         teachers=available_teachers,
                         is_premium=is_premium,
                         questions_remaining=5 if not is_premium else None,
                         sample_prompts=sample_prompts,
                         activated=False,
                         user_name=user_name,
                         is_logged_in=user_profile is not None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        # Sign in with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # Store user_id in session
            session['user_id'] = auth_response.user.id
            
            # Get user profile
            profile = supabase.table('user_profiles').select('*').eq('user_id', auth_response.user.id).single().execute()
            
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': {
                    'name': profile.data.get('name') if profile.data else email,
                    'is_premium': profile.data.get('is_premium', False) if profile.data else False
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')
    
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # Create user profile in database
            profile_data = {
                'user_id': auth_response.user.id,
                'email': email,
                'name': name,
                'is_premium': False
            }
            
            supabase.table('user_profiles').insert(profile_data).execute()
            
            # Log them in immediately
            session['user_id'] = auth_response.user.id
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'user': {
                    'name': name or email,
                    'is_premium': False
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to create account'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    teacher_id = data.get('teacher')
    conversation_history = data.get('conversation', [])
    
    user_profile = get_current_user()
    is_premium = is_user_premium(user_profile)
    
    # Check if teacher exists
    if teacher_id not in SPIRITUAL_TEACHERS:
        return jsonify({'error': 'Invalid teacher selected'}), 400
    
    teacher = SPIRITUAL_TEACHERS[teacher_id]
    
    # Check if user has access to this teacher
    if teacher['tier'] == 'premium' and not is_premium:
        return jsonify({'error': 'This teacher requires premium access'}), 403
    
    # For free users, check question limit (only if not logged in)
    if not is_premium and not user_profile:
        session.setdefault('questions_asked_today', 0)
        session.setdefault('questions_reset_date', datetime.now().date().isoformat())
        
        # Reset counter if it's a new day
        if session['questions_reset_date'] != datetime.now().date().isoformat():
            session['questions_asked_today'] = 0
            session['questions_reset_date'] = datetime.now().date().isoformat()
        
        if session['questions_asked_today'] >= 5:
            return jsonify({'error': 'Daily question limit reached. Upgrade to premium for unlimited access.'}), 429
        
        session['questions_asked_today'] += 1
    
    # Build conversation history
    messages = []
    for msg in conversation_history:
        messages.append({
            "role": "user",
            "content": msg.get('question', '')
        })
        messages.append({
            "role": "assistant",
            "content": msg.get('answer', '')
        })
    
    # Add current question
    messages.append({
        "role": "user",
        "content": question
    })
    
    try:
        # Get response from Claude
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=teacher['system_prompt'],
            messages=messages
        )
        
        answer = response.content[0].text
        
        questions_remaining = None
        if not is_premium and not user_profile:
            questions_remaining = 5 - session['questions_asked_today']
        
        return jsonify({
            'response': answer,
            'teacher': teacher['name'],
            'questions_remaining': questions_remaining
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify_premium', methods=['POST'])
def verify_premium():
    data = request.json
    code = data.get('code', '').strip()
    
    if code == PREMIUM_ACCESS_CODE:
        user_profile = get_current_user()
        
        if user_profile:
            # Update user profile to premium
            supabase.table('user_profiles').update({
                'is_premium': True,
                'plan_type': 'lifetime',
                'activated_at': datetime.now().isoformat()
            }).eq('user_id', user_profile['user_id']).execute()
        
        session['is_premium'] = True
        session['questions_asked_today'] = 0
        return jsonify({'success': True, 'message': 'Premium access activated!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid access code'}), 400

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = None
        if STRIPE_WEBHOOK_SECRET:
            expected_signature = hmac.new(
                STRIPE_WEBHOOK_SECRET.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            if sig_header != expected_signature:
                return jsonify({'error': 'Invalid signature'}), 400
        
        event = request.json
        
        # Handle successful payment
        if event['type'] == 'checkout.session.completed':
            session_data = event['data']['object']
            customer_email = session_data.get('customer_email')
            customer_id = session_data.get('customer')
            
            # Determine plan type from amount
            amount_total = session_data.get('amount_total', 0) / 100  # Convert cents to dollars
            plan_type = '6month' if amount_total < 40 else 'lifetime'
            
            # Check if user exists
            try:
                user_response = supabase.table('user_profiles').select('*').eq('email', customer_email).single().execute()
                user_exists = user_response.data is not None
            except:
                user_exists = False
            
            if user_exists:
                # Update existing user
                expiry_date = None
                if plan_type == '6month':
                    expiry_date = (datetime.now() + timedelta(days=180)).isoformat()
                
                supabase.table('user_profiles').update({
                    'is_premium': True,
                    'plan_type': plan_type,
                    'activated_at': datetime.now().isoformat(),
                    'expires_at': expiry_date,
                    'stripe_customer_id': customer_id
                }).eq('email', customer_email).execute()
            else:
                # Create temporary account (they can set password later)
                temp_password = secrets.token_urlsafe(16)
                
                try:
                    auth_response = supabase.auth.sign_up({
                        "email": customer_email,
                        "password": temp_password
                    })
                    
                    if auth_response.user:
                        expiry_date = None
                        if plan_type == '6month':
                            expiry_date = (datetime.now() + timedelta(days=180)).isoformat()
                        
                        supabase.table('user_profiles').insert({
                            'user_id': auth_response.user.id,
                            'email': customer_email,
                            'is_premium': True,
                            'plan_type': plan_type,
                            'activated_at': datetime.now().isoformat(),
                            'expires_at': expiry_date,
                            'stripe_customer_id': customer_id
                        }).execute()
                except:
                    pass  # User creation failed, but we'll send magic link anyway
            
            # Send magic link email
            send_magic_link_email(customer_email, plan_type)
            
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400

def send_magic_link_email(email, plan_type):
    """Send magic link email for premium access"""
    # Generate magic token
    token = secrets.token_urlsafe(32)
    magic_tokens[token] = {
        'email': email,
        'plan_type': plan_type,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(hours=24)
    }
    
    # Create magic link
    magic_link = f"https://mysoulcompass.app/magic_login/{token}"
    
    plan_name = "6-Month Premium" if plan_type == '6month' else "Lifetime Premium"
    
    # Send email via Resend
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "My Soul Compass <noreply@mysoulcompass.app>",
                "to": [email],
                "subject": f"🌟 Your {plan_name} Access is Ready!",
                "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #9333ea; text-align: center;">✨ Welcome to Premium! ✨</h1>
                    <p>Thank you for upgrading to <strong>{plan_name}</strong> access on My Soul Compass!</p>
                    <p>Click the button below to instantly access all 10 spiritual teachers:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{magic_link}" 
                           style="background: linear-gradient(135deg, #c9a961, #9333ea); 
                                  color: white; 
                                  padding: 15px 40px; 
                                  text-decoration: none; 
                                  border-radius: 25px; 
                                  font-weight: bold;
                                  display: inline-block;">
                            Access Your Premium Account
                        </a>
                    </div>
                    <p style="color: #666; font-size: 14px;">This link expires in 24 hours.</p>
                    <p style="color: #666; font-size: 14px;">If you didn't make this purchase, please ignore this email.</p>
                </div>
                """
            }
        )
        print(f"Magic link email sent to {email}: {response.status_code}")
    except Exception as e:
        print(f"Failed to send magic link email: {str(e)}")

@app.route('/magic_login/<token>')
def magic_login(token):
    """Handle magic link login"""
    if token not in magic_tokens:
        return render_template('error.html', 
                             error_title="Invalid Link",
                             error_message="This magic link is invalid or has expired.")
    
    token_data = magic_tokens[token]
    
    # Check if token has expired
    if datetime.now() > token_data['expires_at']:
        del magic_tokens[token]
        return render_template('error.html',
                             error_title="Link Expired", 
                             error_message="This magic link has expired. Please contact support.")
    
    # Get user profile
    try:
        user_response = supabase.table('user_profiles').select('*').eq('email', token_data['email']).single().execute()
        if user_response.data:
            # Log them in
            session['user_id'] = user_response.data['user_id']
            del magic_tokens[token]
            return redirect(url_for('index'))
    except:
        pass
    
    return render_template('error.html',
                         error_title="Error",
                         error_message="Unable to activate your account. Please contact support.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
