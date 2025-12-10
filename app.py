"""
Hacker Hub - Web Version
Deployable on Vercel
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
CORS(app)

# ==================== DATABASE SIMULATION ====================
# In production, replace with PostgreSQL/MySQL
USERS_DB = {}
TOOLS_DB = {}

def load_tools():
    """Load tools from JSON file"""
    try:
        with open('tools.json', 'r') as f:
            return json.load(f)
    except:
        # Fallback to default tools
        return initialize_default_tools()

def initialize_default_tools():
    """Initialize with default tools data"""
    return {
        "linux": {
            "kali": {
                "information_gathering": [
                    {"name": "Nmap", "desc": "Network discovery tool", "difficulty": "beginner", "command": "nmap -sV [target]"},
                    {"name": "theHarvester", "desc": "Email/subdomain enumeration", "difficulty": "beginner", "command": "theHarvester -d [domain] -b all"}
                ],
                "vulnerability_analysis": [
                    {"name": "OpenVAS", "desc": "Vulnerability scanner", "difficulty": "intermediate", "command": "gvm-start"},
                    {"name": "Nikto", "desc": "Web server scanner", "difficulty": "beginner", "command": "nikto -h [url]"}
                ]
            },
            "ubuntu": {
                "container_security": [
                    {"name": "Docker Bench", "desc": "Docker security audit", "difficulty": "intermediate", "command": "git clone https://github.com/docker/docker-bench-security.git"}
                ]
            },
            "termux": {
                "mobile_hacking": [
                    {"name": "Termux-API", "desc": "Access phone features", "difficulty": "beginner", "command": "pkg install termux-api"}
                ]
            }
        },
        "windows": {
            "general": {
                "reverse_engineering": [
                    {"name": "IDA Pro", "desc": "Interactive disassembler", "difficulty": "advanced", "command": ""},
                    {"name": "x64dbg", "desc": "Open-source debugger", "difficulty": "intermediate", "command": ""}
                ]
            }
        },
        "web": {
            "general": {
                "bug_bounty": [
                    {"name": "Burp Suite", "desc": "Web vulnerability scanner", "difficulty": "intermediate", "command": ""}
                ]
            }
        }
    }

def save_tools():
    """Save tools to JSON file"""
    with open('tools.json', 'w') as f:
        json.dump(TOOLS_DB, f, indent=2)

# Initialize tools
TOOLS_DB = load_tools()

# ==================== ROUTES ====================
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        email = data.get('email')
        experience = data.get('experience', 'beginner')
        
        if username in USERS_DB:
            return jsonify({'error': 'Username already exists'}), 400
        
        user = {
            'id': len(USERS_DB) + 1,
            'username': username,
            'email': email,
            'experience': experience,
            'resources': [],
            'followed_tools': [],
            'joined_date': datetime.now().isoformat(),
            'anonymous': False
        }
        
        USERS_DB[username] = user
        session['user'] = username
        
        return jsonify({
            'success': True,
            'user': user,
            'message': 'Account created successfully'
        })
    
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    username = data.get('username')
    
    # Simplified auth for demo
    if username in USERS_DB:
        session['user'] = username
        return jsonify({
            'success': True,
            'user': USERS_DB[username]
        })
    else:
        # Auto-create user for demo
        user = {
            'id': len(USERS_DB) + 1,
            'username': username,
            'experience': 'beginner',
            'resources': [],
            'followed_tools': [],
            'joined_date': datetime.now().isoformat(),
            'anonymous': False
        }
        USERS_DB[username] = user
        session['user'] = username
        
        return jsonify({
            'success': True,
            'user': user,
            'message': 'Auto-created account for demo'
        })

@app.route('/anonymous')
def anonymous():
    """Anonymous access"""
    session['user'] = 'anonymous_' + str(hash(datetime.now()))[:8]
    session['anonymous'] = True
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_data = USERS_DB.get(session['user'], {
        'username': session['user'],
        'anonymous': session.get('anonymous', False),
        'experience': 'beginner'
    })
    
    return render_template('dashboard.html', user=user_data)

@app.route('/api/tools')
def get_tools():
    """API endpoint for tools"""
    platform = request.args.get('platform')
    category = request.args.get('category')
    subcategory = request.args.get('subcategory')
    
    if platform:
        if category:
            if subcategory:
                # Get specific subcategory
                tools = TOOLS_DB.get(platform, {}).get(category, {}).get(subcategory, [])
                return jsonify(tools)
            # Get all subcategories in category
            categories = TOOLS_DB.get(platform, {}).get(category, {})
            return jsonify(categories)
        # Get all categories in platform
        platforms = TOOLS_DB.get(platform, {})
        return jsonify(platforms)
    
    # Get all platforms
    return jsonify(TOOLS_DB)

@app.route('/api/search')
def search_tools():
    """Search tools"""
    query = request.args.get('q', '').lower()
    results = []
    
    for platform, categories in TOOLS_DB.items():
        for category, subcategories in categories.items():
            for subcategory, tools in subcategories.items():
                for tool in tools:
                    if (query in tool['name'].lower() or 
                        query in tool['desc'].lower() or
                        query in platform.lower()):
                        results.append({
                            **tool,
                            'platform': platform,
                            'category': category,
                            'subcategory': subcategory
                        })
    
    return jsonify(results[:20])  # Limit results

@app.route('/api/user/follow', methods=['POST'])
def follow_tool():
    """Follow a tool"""
    if 'user' not in session or session.get('anonymous'):
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    tool_name = data.get('tool')
    
    user = USERS_DB.get(session['user'])
    if user and tool_name not in user['followed_tools']:
        user['followed_tools'].append(tool_name)
    
    return jsonify({'success': True})

@app.route('/api/user/unfollow', methods=['POST'])
def unfollow_tool():
    """Unfollow a tool"""
    if 'user' not in session or session.get('anonymous'):
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    tool_name = data.get('tool')
    
    user = USERS_DB.get(session['user'])
    if user and tool_name in user['followed_tools']:
        user['followed_tools'].remove(tool_name)
    
    return jsonify({'success': True})

@app.route('/api/user/profile', methods=['GET', 'PUT'])
def user_profile():
    """Get or update user profile"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    username = session['user']
    
    if request.method == 'GET':
        user = USERS_DB.get(username, {
            'username': username,
            'anonymous': session.get('anonymous', False),
            'experience': 'beginner',
            'resources': [],
            'followed_tools': []
        })
        return jsonify(user)
    
    elif request.method == 'PUT':
        data = request.json
        if username in USERS_DB:
            USERS_DB[username].update(data)
            return jsonify({'success': True, 'user': USERS_DB[username]})
        return jsonify({'error': 'User not found'}), 404

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    # For Vercel serverless
    gunicorn_app = app
