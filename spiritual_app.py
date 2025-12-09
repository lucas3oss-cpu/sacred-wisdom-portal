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

# Stripe webhook handler
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    try:
        event = None
        # Verify webhook signature if secret is configured
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            event = json.loads(payload)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session_data = event['data']['object']
            
            # Extract customer email and subscription info
            customer_email = session_data.get('customer_email')
            subscription_id = session_data.get('subscription')
            
            if customer_email:
                # Update user's premium status in Supabase
                try:
                    response = supabase.table('user_profiles').update({
                        'is_premium': True,
                        'subscription_id': subscription_id,
                        'premium_since': datetime.utcnow().isoformat()
                    }).eq('email', customer_email).execute()
                    
                    print(f"Updated premium status for {customer_email}")
                except Exception as e:
                    print(f"Error updating premium status: {str(e)}")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Chat API endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        conversation_history =
