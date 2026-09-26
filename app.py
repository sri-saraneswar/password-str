from flask import Flask, request, jsonify
from flask_cors import CORS
import string
import math
import os
import re
from datetime import datetime
import logging
import time
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Add CORS with configured origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Add Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=getattr(Config, 'RATELIMIT_DEFAULT_LIMITS', ["200 per day", "50 per hour"]),
    storage_uri=getattr(Config, 'RATELIMIT_STORAGE_URI', "memory://")
)

# Constants
ATTEMPTS_PER_SECOND = getattr(Config, 'ATTEMPTS_PER_SECOND', 1_000_000)
WEAK_PASSWORDS_FILE = getattr(Config, 'WEAK_PASSWORDS_FILE', 'weak_passwords.txt')

def load_weak_passwords():
    if not os.path.exists(WEAK_PASSWORDS_FILE):
        return set()
    with open(WEAK_PASSWORDS_FILE, 'r') as f:
        return {line.strip() for line in f if line.strip()}

WEAK_PASSWORDS = load_weak_passwords()

def get_character_set_info(password):
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_digits = any(c in string.digits for c in password)
    has_spec = any(c in string.punctuation or c not in (string.ascii_letters + string.digits) for c in password)
    
    set_size = 0
    if has_lower: set_size += 26
    if has_upper: set_size += 26
    if has_digits: set_size += 10
    if has_spec: set_size += 32
    return set_size, has_lower, has_upper, has_digits, has_spec

def check_repeated(password):
    if len(password) < 4: return False
    for i in range(len(password) - 3):
        if password[i] == password[i+1] == password[i+2] == password[i+3]: return True
    return False

def check_sequential(password):
    if len(password) < 4: return False
    password_lower = password.lower()
    for i in range(len(password) - 3):
        chunk = password_lower[i:i+4]
        if chunk.isdigit() and all(ord(chunk[j+1]) - ord(chunk[j]) == 1 for j in range(3)): return True
        if all(c in string.ascii_lowercase for c in chunk) and all(ord(chunk[j+1]) - ord(chunk[j]) == 1 for j in range(3)): return True
    return False

def check_obvious_pattern(password):
    if re.search(r'([A-Za-z])\1([A-Za-z])\2([A-Za-z])\3', password, re.IGNORECASE): return True
    if re.search(r'(\d)\1(\d)\2(\d)\3', password): return True
    return False

def check_hybrid_attack(password):
    alpha_part = re.sub(r'[^a-zA-Z]', '', password)
    if alpha_part and alpha_part.lower() in WEAK_PASSWORDS:
        return True
    current_year = datetime.now().year
    years_to_check = [str(current_year - 1), str(current_year), str(current_year + 1)]
    for year in years_to_check:
        if password.startswith(year) or password.endswith(year): return True
    return False

def check_keyboard_pattern(password):
    password_lower = password.lower()
    keyboard_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"]
    for row in keyboard_rows:
        for i in range(len(row) - 3):
            chunk = row[i:i+4]
            if chunk in password_lower: return True
            if chunk[::-1] in password_lower: return True
    return False

def check_reverse_sequence(password):
    if len(password) < 4: return False
    password_lower = password.lower()
    for i in range(len(password_lower) - 3):
        chunk = password_lower[i:i+4]
        if chunk.isdigit() and all(ord(chunk[j]) - ord(chunk[j+1]) == 1 for j in range(3)): return True
        if all(c in string.ascii_lowercase for c in chunk) and all(ord(chunk[j]) - ord(chunk[j+1]) == 1 for j in range(3)): return True
    return False

def check_leetspeak_dictionary(password):
    leetspeak_map = {'@':'a', '0':'o', '1':'i', '3':'e', '5':'s', '7':'t', '$':'s', '!':'i'}
    normalized = ""
    for char in password.lower():
        normalized += leetspeak_map.get(char, char)
    return normalized in WEAK_PASSWORDS

def check_repeated_block(password):
    length = len(password)
    if length < 4: return False
    for block_size in range(2, length // 2 + 1):
        for i in range(length - (block_size * 2) + 1):
            block1 = password[i:i+block_size]
            block2 = password[i+block_size:i+(block_size*2)]
            if block1 == block2 and len(set(block1)) > 1: return True
    return False

def check_date_pattern(password):
    matches = re.findall(r'\d{8}', password)
    for match in matches:
        p1, p2, p3 = int(match[0:2]), int(match[2:4]), int(match[4:8])
        if 1 <= p1 <= 31 and 1 <= p2 <= 12 and 1900 <= p3 <= 2100: return True
        if 1900 <= int(match[0:4]) <= 2100 and 1 <= int(match[4:6]) <= 12 and 1 <= int(match[6:8]) <= 31: return True
    return False

def format_crack_time(seconds, score):
    # Cap readable time based on score so it doesn't contradict
    if seconds < 60: return f"{int(seconds)} seconds"
    elif seconds < 3600: return f"{int(seconds // 60)} minutes"
    elif seconds < 86400: 
        if score < 30: return "1 day (Max for Weak)"
        return f"{int(seconds // 3600)} hours"
    elif seconds < 31536000:
        if score < 30: return "A few days (Max for Weak)"
        if score < 60: return f"{int(min(seconds // 86400, 365))} days"
        return f"{int(seconds // 86400)} days"
    elif seconds < 31536000 * 100:
        if score < 30: return "A few days (Capped for Weak Score)"
        if score < 60: return "1-5 years (Capped for Moderate Score)"
        if score < 80: return f"{int(min(seconds // 31536000, 100))} years"
        return f"{int(seconds // 31536000)} years"
    else:
        if score < 30: return "A few days (Capped for Weak Score)"
        if score < 60: return "Up to a decade (Capped for Moderate Score)"
        if score < 85: return "Decades (Capped for Strong Score)"
        return "Centuries (Very Safe!)"

def calculate_entropy(password, set_size):
    if not password or set_size == 0: return 0
    return len(password) * math.log2(set_size)

def get_suggestions_from_vulns(vulns, score):
    suggestions = []
    
    for v in vulns:
        v_low = v.lower()
        if "length" in v_low or "short" in v_low: suggestions.append("Increase length to 16+ characters for better security.")
        if "lowercase" in v_low: suggestions.append("Add lowercase letters.")
        if "uppercase" in v_low: suggestions.append("Add uppercase letters.")
        if "numbers" in v_low: suggestions.append("Include digits/numbers.")
        if "special characters" in v_low: suggestions.append("Add special characters (e.g. !@#$%).")
        if "dictionary" in v_low: suggestions.append("Avoid common dictionary words. Use passphrases instead.")
        if "sequential" in v_low or "obvious" in v_low or "keyboard" in v_low or "reverse" in v_low: 
            suggestions.append("Avoid predictable patterns or keyboard walks.")
        if "repeated" in v_low: suggestions.append("Minimize repeated characters or blocks.")
        if "date" in v_low: suggestions.append("Avoid birth dates or predictable date formats.")
        if "leetspeak" in v_low: suggestions.append("Don't rely on simple substitutions like '@' for 'a', attackers check for this.")
        
    # Deduplicate while preserving order
    unique_suggs = []
    for s in suggestions:
        if s not in unique_suggs:
            unique_suggs.append(s)
            
    if score >= 85 and len(unique_suggs) == 0:
        unique_suggs.append("Great password! Keep it safe.")
        
    return unique_suggs

def validate_password_input(password):
    errors = []
    if len(password) > 128: errors.append("Password length cannot exceed 128 characters.")
    if '\x00' in password: errors.append("Password cannot contain null bytes.")
    if not password: errors.append("Password cannot be empty.")
    return errors

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'Password Attack System Active'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'running', 'version': '2.0'})

@app.errorhandler(400)
def bad_request(e): return jsonify(error="Bad Request", message=str(e.description if hasattr(e, 'description') else "Bad request")), 400
@app.errorhandler(404)
def not_found(e): return jsonify(error="Not Found", message="Requested URL not found"), 404
@app.errorhandler(405)
def method_not_allowed(e): return jsonify(error="Method Not Allowed", message="Method not allowed"), 405
@app.errorhandler(500)
def internal_error(e): return jsonify(error="Internal Server Error", message="Unexpected server error"), 500

def do_analysis(password):
    length = len(password)
    set_size, has_lower, has_upper, has_digits, has_spec = get_character_set_info(password)
    
    # Run attack tests
    is_dictionary = password in WEAK_PASSWORDS
    is_repeated = check_repeated(password)
    is_sequential = check_sequential(password)
    is_obvious = check_obvious_pattern(password)
    is_hybrid = check_hybrid_attack(password)
    is_keyboard = check_keyboard_pattern(password)
    is_reverse = check_reverse_sequence(password)
    is_leetspeak = check_leetspeak_dictionary(password)
    is_repeated_block = check_repeated_block(password)
    is_date = check_date_pattern(password)
    
    # Base score
    score = 100
    vulnerabilities = []
    
    # Evaluate lengths and composition
    if length < 8:
        score -= 40
        vulnerabilities.append("Password is very short (< 8 chars)")
    elif length < 12:
        score -= 20
        vulnerabilities.append("Password length is suboptimal (< 12 chars)")
    elif length < 16:
        score -= 10
        vulnerabilities.append("Password length could be improved (< 16 chars)")
        
    if not has_lower: 
        score -= 10
        vulnerabilities.append("Missing lowercase letters")
    if not has_upper: 
        score -= 10
        vulnerabilities.append("Missing uppercase letters")
    if not has_digits: 
        score -= 10
        vulnerabilities.append("Missing numbers")
    if not has_spec: 
        score -= 15
        vulnerabilities.append("Missing special characters")
        
    # Subtract penalties and track vulns atomically
    if is_dictionary:
        score -= 25
        vulnerabilities.append("Dictionary Attack Vulnerability")
    if is_leetspeak:
        score -= 20
        vulnerabilities.append("Leetspeak Dictionary Vulnerability")
    if is_hybrid:
        score -= 15
        vulnerabilities.append("Hybrid Attack Vulnerability (Word + Numbers/Symbols)")
    if is_keyboard:
        score -= 15
        vulnerabilities.append("Keyboard Pattern Vulnerability")
    if is_sequential:
        score -= 20
        vulnerabilities.append("Sequential Pattern Vulnerability")
    if is_reverse:
        score -= 15
        vulnerabilities.append("Reverse Sequence Vulnerability")
    if is_repeated:
        score -= 20
        vulnerabilities.append("Repeated Character Vulnerability")
    if is_repeated_block or is_obvious:
        score -= 15
        vulnerabilities.append("Repeated Block / Obvious Pattern Vulnerability")
    if is_date:
        score -= 15
        vulnerabilities.append("Date-Based Password Vulnerability")
        
    score = max(0, min(100, score))
    
    # Ensure no contradiction (Bug 1 & Bug 5)
    if score < 85 and len(vulnerabilities) == 0:
        vulnerabilities.append("Password lacks sufficient complexity to reach Very Strong status.")
    
    if score >= 85 and len(vulnerabilities) == 0:
        vulnerabilities.append("No specific attack vulnerabilities detected. Excellent!")
        
    if score <= 30: strength_level = "Weak"
    elif score <= 60: strength_level = "Moderate"
    elif score <= 80: strength_level = "Strong"
    else: strength_level = "Very Strong"
        
    # Calculate combinations and entropy using actual math
    total_combinations = float(set_size ** length)
    estimated_crack_time_seconds = total_combinations / ATTEMPTS_PER_SECOND
    entropy_bits = calculate_entropy(password, set_size)
    
    estimated_crack_time_readable = format_crack_time(estimated_crack_time_seconds, score)
    suggestions = get_suggestions_from_vulns(vulnerabilities, score)
    
    attack_summary = {
        'dictionary': is_dictionary,
        'hybrid': is_hybrid,
        'keyboard': is_keyboard,
        'sequential': is_sequential,
        'reverse': is_reverse,
        'repeated': is_repeated,
        'leetspeak': is_leetspeak,
        'date_based': is_date,
        'repeated_block': is_repeated_block
    }

    response = {
        'password': password,
        'password_length': length,
        'character_set_size': set_size,
        'total_combinations': total_combinations,
        'estimated_crack_time_seconds': estimated_crack_time_seconds,
        'estimated_crack_time_readable': estimated_crack_time_readable,
        'entropy_bits': entropy_bits,
        'score': score,
        'strength_level': strength_level,
        'dictionary_attack_result': is_dictionary,
        'pattern_warning': is_repeated or is_sequential or is_obvious or is_repeated_block or is_reverse or is_keyboard,
        'vulnerability_types': vulnerabilities,
        'suggestions': suggestions,
        'attack_summary': attack_summary
    }
    return response

def generate_improved_password(weak_password):
    base_word = re.sub(r'[^a-zA-Z]', '', weak_password)
    # Step 1 - Keep meaningful part:
    # Extract the base word from password
    # Remove numbers and symbols
    # Keep first 4-5 letters as base
    if len(base_word) > 4:
        # keep up to 4-5 chars
        base_len = random.randint(4, 5)
        base_word = base_word[:base_len]
    if len(base_word) == 0:
        base_word = random.choice(['Pass', 'Word', 'MyPw', 'Keyw', 'S3cr'])
    
    def try_gen(base_word):
        # Transform it smartly
        base_word = base_word.capitalize()
        # Add random uppercase in middle
        if len(base_word) > 2:
            idx = random.randint(1, len(base_word)-1)
            base_word = base_word[:idx] + base_word[idx].upper() + base_word[idx+1:]
        
        # We need to reach 14-16 chars, ensuring all 4 types and 2 of each
        length = random.randint(14, 16)
        
        spec = "!@#$%"
        nums = "23456789" # not sequential
        
        res = list(base_word)
        # Ensure at least 2 special
        res.append(random.choice(spec))
        res.append(random.choice(spec))
        # Ensure at least 2 numbers
        res.append(random.choice(nums))
        res.append(random.choice(nums))
        
        # Add random chars at end
        while len(res) < length:
            pool = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%"
            res.append(random.choice(pool))
            
        # Shuffle everything except the base word which is at the start (up to len(base_word))
        tail = res[len(base_word):]
        random.shuffle(tail)
        res = res[:len(base_word)] + tail
        
        return "".join(res)
    
    for _ in range(5):
        pw = try_gen(base_word)
        res = do_analysis(pw)
        if res['score'] >= 85 and res['entropy_bits'] >= 80:
            if not any(res['attack_summary'].values()): # pass all checks
                if not re.search(r'123|234|345|456|567|678|789', pw) and not re.search(r'\d{3}', pw):
                    return pw
                    
    # Guaranteed strong format
    def generate_strong(length):
        lower = "abcdefghijkmnopqrstuvwxyz"
        upper = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        num = "23456789"
        special = "!@#$%"
        all_pool = lower + upper + num + special

        pwd = [
            random.choice(lower), random.choice(lower),
            random.choice(upper), random.choice(upper),
            random.choice(num), random.choice(num),
            random.choice(special), random.choice(special)
        ]

        for i in range(8, length):
            pwd.append(random.choice(all_pool))

        random.shuffle(pwd)
        return ''.join(pwd)
        
    for _ in range(5):
        pw = generate_strong(random.randint(14, 16))
        res = do_analysis(pw)
        if res['score'] >= 85 and res['entropy_bits'] >= 80:
            if not any(res['attack_summary'].values()): # pass all checks
                return pw
    return "StR0ng!@#P@ssWOrd89"

@app.route('/improve', methods=['POST'])
@limiter.limit(getattr(Config, 'ANALYZE_ENDPOINT_LIMIT', "30 per minute"))
def improve_password():
    start_time = time.time()
    
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'error': 'Bad Request', 'details': ['Password not provided']}), 400
    
    weak_password = str(data['password'])
    validation_errors = validate_password_input(weak_password)
    if validation_errors:
        return jsonify({'error': 'Validation Failed', 'details': validation_errors}), 400

    orig_res = do_analysis(weak_password)
    
    if orig_res['score'] > 80:
        return jsonify({
            "status": "already_strong",
            "message": "Password is already very strong!",
            "score": orig_res['score'],
            "strength_level": orig_res['strength_level'],
            "suggestion": "Keep this password safe and never share it!"
        })

    strong_password = generate_improved_password(weak_password)
    new_res = do_analysis(strong_password)
    
    score_increase = new_res['score'] - orig_res['score']
    entropy_increase = round(new_res['entropy_bits'] - orig_res['entropy_bits'], 1)
    
    if orig_res['score'] > 60:
        improvement_message = "Good password — here is a slightly stronger alternative"
    else:
        improvement_message = "Your password became significantly stronger!" if score_increase > 0 else "Here is a highly secure alternative."
        
    response = {
        'status': 'improved',
        'original': orig_res,
        'improved': new_res,
        'improvement': {
            'score_increase': score_increase,
            'entropy_increase': entropy_increase,
            'time_increase': f"From {orig_res['estimated_crack_time_readable']} to {new_res['estimated_crack_time_readable']}",
            'message': improvement_message
        }
    }
    
    logger.info(f"/improve Request processed in {time.time() - start_time:.4f} seconds")
    return jsonify(response)

@app.route('/analyze', methods=['POST'])
@limiter.limit(getattr(Config, 'ANALYZE_ENDPOINT_LIMIT', "30 per minute"))
def analyze_password():
    start_time = time.time()
    
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'error': 'Bad Request', 'details': ['Password not provided']}), 400
    
    password = str(data['password'])
    validation_errors = validate_password_input(password)
    if validation_errors:
        return jsonify({'error': 'Validation Failed', 'details': validation_errors}), 400
    
    response = do_analysis(password)
    
    logger.info(f"Request processed in {time.time() - start_time:.4f} seconds")
    return jsonify(response)

@app.route('/compare', methods=['POST'])
@limiter.limit(getattr(Config, 'ANALYZE_ENDPOINT_LIMIT', "30 per minute"))
def compare_passwords():
    start_time = time.time()
    data = request.get_json()
    
    if not data or 'password1' not in data or 'password2' not in data:
        return jsonify({'error': 'Bad Request', 'details': ['Both passwords are required']}), 400
        
    pwd1 = str(data['password1'])
    pwd2 = str(data['password2'])
    label1 = str(data.get('label1', 'Person 1'))
    label2 = str(data.get('label2', 'Person 2'))
    
    val_errs1 = validate_password_input(pwd1)
    val_errs2 = validate_password_input(pwd2)
    if val_errs1 or val_errs2:
        return jsonify({'error': 'Validation Failed', 'details': val_errs1 + val_errs2}), 400
        
    res1 = do_analysis(pwd1)
    res2 = do_analysis(pwd2)
    
    res1['label'] = label1
    res1['password_actual'] = pwd1
    res2['label'] = label2
    res2['password_actual'] = pwd2
    
    score1 = res1['score']
    score2 = res2['score']
    diff = abs(score1 - score2)
    
    if diff <= 5:
        category = "tie"
        verdict = f"Both passwords are equally strong!"
        winner = None
    else:
        if score1 > score2:
            winner = {"label": label1, "password_number": 1, "reason": "Higher score"}
            win_label = label1
        else:
            winner = {"label": label2, "password_number": 2, "reason": "Higher score"}
            win_label = label2
            
        if diff <= 20: category = "slight"
        elif diff <= 40: category = "moderate"
        else: category = "significant"
        
        strength_adverbs = {"slight": "slightly", "moderate": "moderately", "significant": "significantly"}
        verdict = f"{win_label} password is {strength_adverbs[category]} stronger"
        
    response = {
        "password1": res1,
        "password2": res2,
        "winner": winner,
        "comparison": {
            "score_difference": diff,
            "entropy_difference": round(abs(res1['entropy_bits'] - res2['entropy_bits']), 1),
            "verdict": verdict,
            "category": category
        }
    }
    
    logger.info(f"/compare Request processed in {time.time() - start_time:.4f} seconds")
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=getattr(Config, 'DEBUG', True), port=getattr(Config, 'PORT', 5001))
