import re
import os

with open("d:/passwordproject/app.py", "r") as f:
    app_py_content = f.read()

import_pattern = r"(import time\nfrom flask_limiter import Limiter)"
app_py_content = re.sub(import_pattern, r"import time\nimport random\nfrom flask_limiter import Limiter", app_py_content)

analyze_logic = r"""def do_analysis(password):
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

"""

improve_logic = r"""def generate_improved_password(weak_password):
    base_word = re.sub(r'[^a-zA-Z]', '', weak_password)
    # Step 1 — Keep meaningful part:
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
        
        # avoid sequential numbers by shuffling
        # maybe ensure again
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

    strong_password = generate_improved_password(weak_password)
    
    orig_res = do_analysis(weak_password)
    new_res = do_analysis(strong_password)
    
    score_increase = new_res['score'] - orig_res['score']
    entropy_increase = round(new_res['entropy_bits'] - orig_res['entropy_bits'], 1)
    
    response = {
        'original': orig_res,
        'improved': new_res,
        'improvement': {
            'score_increase': score_increase,
            'entropy_increase': entropy_increase,
            'time_increase': f"From {orig_res['estimated_crack_time_readable']} to {new_res['estimated_crack_time_readable']}",
            'message': "Your password became significantly stronger!" if score_increase > 0 else "Here is a highly secure alternative."
        }
    }
    
    logger.info(f"/improve Request processed in {time.time() - start_time:.4f} seconds")
    return jsonify(response)

"""

replace_point = """@app.route('/analyze', methods=['POST'])"""
with open("d:/passwordproject/app.py", "w") as f:
    f.write(app_py_content.replace(replace_point, analyze_logic + improve_logic + replace_point))

print("Patched app.py!")
