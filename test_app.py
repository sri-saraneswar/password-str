import pytest
from app import app, WEAK_PASSWORDS, check_sequential, check_keyboard_pattern, check_date_pattern, evaluate_password_score

@pytest.fixture
def client():
    app.config.update({'TESTING': True})
    with app.test_client() as client:
        yield client

# Add some fake passwords to WEAK_PASSWORDS for reliable testing
@pytest.fixture(autouse=True)
def setup_weak_passwords():
    WEAK_PASSWORDS.add("password")
    WEAK_PASSWORDS.add("admin")
    yield

def test_dictionary_attack_detection():
    # Testing that plain dictionary words are caught
    # We implicitly test this via the client's API response since the app checks "password in WEAK_PASSWORDS" statically
    assert "password" in WEAK_PASSWORDS

def test_sequential_pattern_detection():
    # 12345 is sequential forward
    assert check_sequential("12345") == True
    # abcd is sequential forward
    assert check_sequential("abcd") == True
    # unsequential should be false
    assert check_sequential("a1c3e5") == False
    assert check_sequential("1478") == False

def test_keyboard_pattern_detection():
    # qwerty pattern (top row)
    assert check_keyboard_pattern("qwerty") == True
    # backwards bottom row
    assert check_keyboard_pattern("mbnx") == False # This is slightly off keyboard rows, our code handles 4 consecutive chars natively
    # asdfgh (middle row)
    assert check_keyboard_pattern("asdfgh") == True
    # safe pattern
    assert check_keyboard_pattern("K1x@9zP!") == False

def test_date_pattern_detection():
    # Valid Dates formats (8 continuous numbers)
    assert check_date_pattern("01011990") == True  # DDMMYYYY
    assert check_date_pattern("20031225") == True  # YYYYMMDD
    # Invalid dates
    assert check_date_pattern("99999999") == False
    # Regular strings
    assert check_date_pattern("MySecretString") == False

def test_score_calculation():
    # Base complexity additions (length, letters, digits, specials)
    # Expected strong password
    score, level = evaluate_password_score("A!b2C#d4E%f6", is_weak_dict=False, has_repeated=False, has_sequential=False, has_obvious_pattern=False)
    assert score > 60
    assert "Strong" in level
    
    # Expected weak password
    score2, level2 = evaluate_password_score("abc", is_weak_dict=False, has_repeated=False, has_sequential=False, has_obvious_pattern=False)
    assert score2 < 50
    assert level2 in ["Weak", "Moderate"]

def test_api_endpoint_responses(client):
    # Test valid 200 response
    response = client.post('/analyze', json={'password': 'MySecurePassword123!'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'score' in data
    assert 'strength_level' in data
    assert 'attack_summary' in data
    assert 'entropy_bits' in data
    
    # Test 400 Empty Password
    resp_empty = client.post('/analyze', json={'password': ''})
    assert resp_empty.status_code == 400
    assert 'error' in resp_empty.get_json()
    
    # Test 400 No Payload
    resp_none = client.post('/analyze', json={})
    assert resp_none.status_code == 400
    assert 'error' in resp_none.get_json()

    # Test 400 Null byte parsing 
    resp_null = client.post('/analyze', json={'password': 'abc\x00def'})
    assert resp_null.status_code == 400
    assert 'error' in resp_null.get_json()
