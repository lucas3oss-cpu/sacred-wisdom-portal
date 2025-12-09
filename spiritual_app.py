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
@app.
