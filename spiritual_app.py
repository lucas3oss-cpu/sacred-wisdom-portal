from flask import Flask, render_template, request, jsonify, session, redirect
from anthropic import Anthropic
import os
from datetime import datetime, timedelta
import secrets
import random
import hmac
import hashlib
import requests

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Resend API key for sending emails
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

# Stripe webhook secret (you'll get this from Stripe dashboard)
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Premium access code - fallback for manual activation
PREMIUM_ACCESS_CODE = "mysoulcompass2025"

# In-memory storage for magic tokens (in production, use a database)
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
        "name": "Gnostic Jesus",
        "description": "Inner knowing and divine spark within",
        "tier": "free",
        "system_prompt": """You are channeling the wisdom of Gnostic Jesus from the Gospel of Thomas and other Gnostic texts. 
        Focus on: the Kingdom of God within, direct gnosis (knowing), the divine spark in all beings, non-dualism, 
        liberation from illusion, and the light within darkness. Speak in a mystical, paradoxical style."""
    },
    "marianne_williamson": {
        "name": "Marianne Williamson",
        "description": "A Course in Miracles and love-based living",
        "tier": "free",
        "system_prompt": """You are channeling the wisdom of Marianne Williamson. Speak with her passionate, spiritually-grounded voice. 
        Focus on: A Course in Miracles principles, choosing love over fear, miracles as shifts in perception, forgiveness, 
        the power of prayer, and practical spirituality. Use her inspiring, empowering style."""
    },
    "ram_dass": {
        "name": "Ram Dass",
        "description": "Be Here Now and loving awareness",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Ram Dass (Richard Alpert). Speak with his warm, loving, humorous presence. 
        Focus on: being here now, loving awareness, the guru within, seva (service), aging consciously, death as transition, 
        and the journey from psychology to spirituality. Use his gentle, often funny teaching style."""
    },
    "thich_nhat_hanh": {
        "name": "Thich Nhat Hanh",
        "description": "Mindfulness and engaged Buddhism",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Thich Nhat Hanh. Speak with his gentle, poetic mindfulness. 
        Focus on: mindful breathing, walking meditation, interbeing, engaged Buddhism, peace practice, mindful living, 
        and the present moment. Use his simple, profound teaching style with beautiful metaphors."""
    },
    "mooji": {
        "name": "Mooji",
        "description": "Direct pointing to Self and non-dual awareness",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Mooji. Speak with his direct, loving guidance to the Self. 
        Focus on: the invitation to BE, recognizing the Self, letting go of the person, the eternal witness, 
        resting as awareness, and the freedom of your true nature. Use his warm, direct pointing style."""
    },
    "byron_katie": {
        "name": "Byron Katie",
        "description": "The Work and inquiry into truth",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of Byron Katie. Speak with her direct, loving inquiry method. 
        Focus on: The Work (four questions and turnaround), questioning stressful thoughts, 'loving what is', 
        reality vs. story, and radical self-inquiry. Use her clear, compassionate questioning style."""
    },
    "buddha": {
        "name": "Buddha",
        "description": "Four Noble Truths and the Noble Eightfold Path",
        "tier": "premium",
        "system_prompt": """You are channeling the wisdom of the Buddha (Siddhartha Gautama). Speak with his profound, compassionate teaching. 
        Focus on: the Four Noble Truths, the Noble Eightfold Path, the end of suffering, mindfulness, the middle way, 
        impermanence, non-self, and compassion. Use his clear, methodical teaching style."""
    }
}

def send_magic_link_email(email, name, magic_token, plan_type):
    """Send magic link email via Resend"""
    magic_link = f"https://mysoulcompass.app/activate/{magic_token}"
    
    # Determine plan details
    if "lifetime" in plan_type.lower():
        plan_name = "Lifetime Premium"
        plan_description = "lifetime access"
    else:
        plan_name = "6 Months Premium"
        plan_description = "6 months of premium access"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center;">
            <h1 style="color: white; margin: 0;">✨ Welcome to My Soul Compass Premium ✨</h1>
        </div>
        
        <div style="padding: 30px; background: #f9f9f9; border-radius: 10px; margin-top: 20px;">
            <h2 style="color: #333;">Hi {name}! 🙏</h2>
            
            <p style="font-size: 16px; color: #555; line-height: 1.6;">
                Thank you for your purchase of <strong>{plan_name}</strong>! Your spiritual journey just expanded.
            </p>
            
            <p style="font-size: 16px; color: #555; line-height: 1.6;">
                Click the button below to instantly activate your premium access:
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{magic_link}" 
                   style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; 
                          font-size: 18px; font-weight: bold;">
                    🌟 Activate Premium Access
                </a>
            </div>
            
            <p style="font-size: 14px; color: #888; text-align: center;">
                Or copy this link: <a href="{magic_link}" style="color: #667eea;">{magic_link}</a>
            </p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <h3 style="color: #333;">✨ What You Now Have Access To:</h3>
            <ul style="font-size: 15px; color: #555; line-height: 1.8;">
                <li>All 10 renowned spiritual teachers</li>
                <li>Unlimited questions (no daily limit)</li>
                <li>Full conversation history</li>
                <li>Multi-turn conversations with context</li>
                <li>Copy entire conversations</li>
                <li>All meditation & breathwork tools</li>
                <li>{plan_description.capitalize()}</li>
            </ul>
            
            <p style="font-size: 16px; color: #555; line-height: 1.6; margin-top: 30px;">
                If you have any questions, just reply to this email!
            </p>
            
            <p style="font-size: 16px; color: #555;">
                Blessings on your journey,<br>
                <strong>Lucas</strong><br>
                My Soul Compass
            </p>
        </div>
        
        <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
            <p>My Soul Compass - Sacred Wisdom Portal</p>
            <p>https://mysoulcompass.app</p>
        </div>
    </body>
    </html>
    """
    
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
                "subject": f"✨ Your {plan_name} Access is Ready!",
                "html": html_content
            }
        )
        
        if response.status_code == 200:
            print(f"Magic link email sent to {email}")
            return True
        else:
            print(f"Failed to send email: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    # Verify webhook signature (important for security!)
    if STRIPE_WEBHOOK_SECRET:
        try:
            # Verify the signature
            import stripe
            stripe.api_key = os.environ.get("STRIPE_API_KEY", "")
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            print(f"Webhook signature verification failed: {str(e)}")
            return jsonify({'error': 'Invalid signature'}), 400
    else:
        # For testing without signature verification
        import json
        event = json.loads(payload)
    
    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        
        # Extract customer details
        customer_email = session_data.get('customer_details', {}).get('email', '')
        customer_name = session_data.get('customer_details', {}).get('name', 'Friend')
        
        # Get product details to determine plan type
        line_items = session_data.get('line_items', {}).get('data', [])
        plan_type = "6 Months"  # Default
        
        if line_items:
            product_name = line_items[0].get('description', '')
            if 'lifetime' in product_name.lower():
                plan_type = "Lifetime"
        
        # Generate unique magic token
        magic_token = secrets.token_urlsafe(32)
        
        # Store token with expiry (7 days for activation)
        magic_tokens[magic_token] = {
            'email': customer_email,
            'name': customer_name,
            'plan': plan_type,
            'created': datetime.now(),
            'used': False
        }
        
        # Send magic link email
        send_magic_link_email(customer_email, customer_name, magic_token, plan_type)
        
        print(f"Payment received from {customer_email} for {plan_type}")
    
    return jsonify({'status': 'success'}), 200

@app.route('/activate/<token>')
def activate_premium(token):
    """Activate premium access via magic link"""
    if token not in magic_tokens:
        return render_template('error.html', 
                             message="Invalid or expired activation link. Please contact support.")
    
    token_data = magic_tokens[token]
    
    # Check if already used
    if token_data['used']:
        return render_template('error.html',
                             message="This activation link has already been used.")
    
    # Check if expired (7 days)
    if datetime.now() - token_data['created'] > timedelta(days=7):
        return render_template('error.html',
                             message="This activation link has expired. Please contact support.")
    
    # Mark as used
    magic_tokens[token]['used'] = True
    
    # Set premium session
    session['is_premium'] = True
    session['premium_activated'] = datetime.now().isoformat()
    session['user_email'] = token_data['email']
    session['user_name'] = token_data['name']
    session['plan_type'] = token_data['plan']
    
    # Redirect to home with success message
    return redirect('/?activated=true')

@app.route('/')
def index():
    # Check if just activated
    activated = request.args.get('activated') == 'true'
    
    # Initialize session if needed
    if 'is_premium' not in session:
        session['is_premium'] = False
    if 'questions_asked_today' not in session:
        session['questions_asked_today'] = 0
        session['last_question_date'] = datetime.now().date().isoformat()
    
    # Reset daily question count if new day
    if session.get('last_question_date') != datetime.now().date().isoformat():
        session['questions_asked_today'] = 0
        session['last_question_date'] = datetime.now().date().isoformat()
    
    # Get available teachers based on tier
    if session['is_premium']:
        available_teachers = SPIRITUAL_TEACHERS
    else:
        available_teachers = {k: v for k, v in SPIRITUAL_TEACHERS.items() if k in FREE_TIER_TEACHERS}
    
    # Get random sample prompts
    sample_prompts = random.sample(SAMPLE_PROMPTS, 3)
    
    return render_template('index.html', 
                         teachers=available_teachers,
                         is_premium=session['is_premium'],
                         questions_remaining=5 - session['questions_asked_today'],
                         sample_prompts=sample_prompts,
                         activated=activated,
                         user_name=session.get('user_name', ''))

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    teacher_id = data.get('teacher')
    conversation_history = data.get('conversation', [])
    
    # Check if premium or within free limit
    if not session.get('is_premium', False):
        if session['questions_asked_today'] >= 5:
            return jsonify({'error': 'Daily question limit reached. Upgrade to premium for unlimited questions!'}), 403
        
        # Check if teacher is available in free tier
        if teacher_id not in FREE_TIER_TEACHERS:
            return jsonify({'error': 'This teacher is only available to premium members.'}), 403
    
    # Get teacher configuration
    teacher = SPIRITUAL_TEACHERS.get(teacher_id)
    if not teacher:
        return jsonify({'error': 'Invalid teacher selected'}), 400
    
    # Build messages array with conversation history
    messages = [
        {"role": "user", "content": teacher['system_prompt']}
    ]
    
    # Add conversation history if exists
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current question
    messages.append({"role": "user", "content": question})
    
    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=messages
        )
        
        answer = response.content[0].text
        
        # Increment question count for free users
        if not session.get('is_premium', False):
            session['questions_asked_today'] = session.get('questions_asked_today', 0) + 1
        
        # Store in conversation history for premium users
        if session.get('is_premium', False):
            if 'conversation_history' not in session:
                session['conversation_history'] = []
            
            session['conversation_history'].append({
                'teacher': teacher['name'],
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'answer': answer,
            'questions_remaining': 5 - session.get('questions_asked_today', 0) if not session.get('is_premium') else 'unlimited'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify-code', methods=['POST'])
def verify_code():
    """Manual code verification as fallback"""
    data = request.json
    code = data.get('code', '').strip()
    
    if code == PREMIUM_ACCESS_CODE:
        session['is_premium'] = True
        session['premium_activated'] = datetime.now().isoformat()
        return jsonify({'success': True, 'message': 'Premium access activated!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid access code'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
