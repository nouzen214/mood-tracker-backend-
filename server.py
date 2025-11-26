"""
Mood Tracker Backend Server
Flask API for handling Firebase and Gemini AI operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db, auth
import google.generativeai as genai
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Allow requests from Android app

# Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mood-tracker-df3a2-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Initialize Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDiSKNlLqxAqNBqEJmWCMQcDHdWxvOSB4E')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# ============= AUTHENTICATION =============

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        fullname = data.get('fullname')
        
        # Create user in Firebase Auth
        user = auth.create_user(
            email=email,
            password=password,
            display_name=fullname
        )
        
        # Store user data in database
        ref = db.reference(f'users/{user.uid}')
        ref.set({
            'email': email,
            'fullname': fullname,
            'created_at': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'user_id': user.uid,
            'message': 'User created successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/signin', methods=['POST'])
def signin():
    """Sign in user (verification only - actual auth done on client)"""
    try:
        data = request.json
        email = data.get('email')
        
        # Get user by email
        user = auth.get_user_by_email(email)
        
        # Get user data from database
        ref = db.reference(f'users/{user.uid}')
        user_data = ref.get()
        
        return jsonify({
            'success': True,
            'user_id': user.uid,
            'user_data': user_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============= MOOD OPERATIONS =============

@app.route('/api/save_mood', methods=['POST'])
def save_mood():
    """Save a mood entry"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        mood = data.get('mood')
        note = data.get('note', '')
        
        # Create mood entry
        mood_entry = {
            'mood': mood,
            'note': note,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to Firebase
        ref = db.reference(f'users/{user_id}/moods/{year}/{month}/{day}')
        existing = ref.get()
        
        if existing is None:
            ref.set([mood_entry])
        elif isinstance(existing, list):
            existing.append(mood_entry)
            ref.set(existing)
        else:
            ref.set([mood_entry])
        
        return jsonify({
            'success': True,
            'message': 'Mood saved successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get_moods', methods=['POST'])
def get_moods():
    """Get mood entries for a specific date range"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day', None)
        
        if day:
            # Get specific day
            ref = db.reference(f'users/{user_id}/moods/{year}/{month}/{day}')
        else:
            # Get entire month
            ref = db.reference(f'users/{user_id}/moods/{year}/{month}')
        
        moods = ref.get()
        
        return jsonify({
            'success': True,
            'moods': moods if moods else {}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/delete_mood', methods=['POST'])
def delete_mood():
    """Delete a specific mood entry"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        index = data.get('index')
        
        ref = db.reference(f'users/{user_id}/moods/{year}/{month}/{day}')
        moods = ref.get()
        
        if isinstance(moods, list) and 0 <= index < len(moods):
            moods.pop(index)
            if len(moods) == 0:
                ref.delete()
            else:
                ref.set(moods)
            
            return jsonify({
                'success': True,
                'message': 'Mood deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid index'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/delete_all_moods', methods=['POST'])
def delete_all_moods():
    """Delete all moods for a specific day"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        
        ref = db.reference(f'users/{user_id}/moods/{year}/{month}/{day}')
        ref.delete()
        
        return jsonify({
            'success': True,
            'message': 'All moods deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============= MOOD SUMMARIES =============

@app.route('/api/get_summary', methods=['POST'])
def get_summary():
    """Get mood summary for a date range"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year')
        month = data.get('month')
        mode = data.get('mode')  # 'daily', 'weekly', 'monthly'
        value = data.get('value', None)
        
        ref = db.reference(f'users/{user_id}/moods/{year}/{month}')
        month_data = ref.get()
        
        if not month_data:
            return jsonify({
                'success': True,
                'summary': 'No mood data available for this period.'
            })
        
        # Count moods
        mood_counts = {}
        
        if isinstance(month_data, dict):
            for day, entries in month_data.items():
                if isinstance(entries, list):
                    for entry in entries:
                        mood = entry.get('mood', 'Unknown')
                        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Generate summary text
        summary = f"Mood Summary ({mode.title()}):\n\n"
        for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
            summary += f"{mood}: {count} times\n"
        
        return jsonify({
            'success': True,
            'summary': summary,
            'mood_counts': mood_counts
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============= AI CHAT =============

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    """Get AI response using Gemini"""
    try:
        data = request.json
        user_message = data.get('message')
        user_id = data.get('user_id')
        
        # Get user's recent moods for context
        ref = db.reference(f'users/{user_id}/moods')
        moods_data = ref.get()
        
        # Build context
        context = "You are a supportive mental health assistant for a mood tracking app. "
        context += "Be empathetic, encouraging, and provide helpful insights about mood patterns. "
        
        if moods_data:
            context += "\n\nUser's recent mood data is available. "
        
        # Generate response
        full_prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"
        response = model.generate_content(full_prompt)
        
        return jsonify({
            'success': True,
            'response': response.text
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============= ADMIN OPERATIONS =============

@app.route('/api/get_all_users', methods=['POST'])
def get_all_users():
    """Get all users (admin only)"""
    try:
        data = request.json
        admin_id = data.get('admin_id')
        
        # Verify admin (you should implement proper admin verification)
        ref = db.reference('users')
        users = ref.get()
        
        user_list = []
        if users:
            for uid, user_data in users.items():
                user_list.append({
                    'user_id': uid,
                    'email': user_data.get('email'),
                    'fullname': user_data.get('fullname')
                })
        
        return jsonify({
            'success': True,
            'users': user_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============= HEALTH CHECK =============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Mood Tracker API',
        'version': '1.0',
        'endpoints': [
            '/api/signup',
            '/api/signin',
            '/api/save_mood',
            '/api/get_moods',
            '/api/delete_mood',
            '/api/delete_all_moods',
            '/api/get_summary',
            '/api/ai_chat',
            '/api/get_all_users',
            '/api/health'
        ]
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
