from typing import Literal
import uuid
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest, UserUpdateProfile

# Fixtures for common test data
@pytest.fixture
def user_base_data():
    return {
        "nickname": "john_doe_123",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "AUTHENTICATED",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe"
    }

@pytest.fixture
def user_create_data(user_base_data: dict[str, str]):
    return {**user_base_data, "password": "SecurePassword123!"}

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "nickname": "j_doe",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg"
    }

@pytest.fixture
def user_response_data(user_base_data: dict[str, str]):
    return {
        "id": uuid.uuid4(),
        "nickname": user_base_data["nickname"],
        "first_name": user_base_data["first_name"],
        "last_name": user_base_data["last_name"],
        "role": user_base_data["role"],
        "email": user_base_data["email"],
        # "last_login_at": datetime.now(),
        # "created_at": datetime.now(),
        # "updated_at": datetime.now(),
        "links": []
    }

@pytest.fixture
def login_request_data():
    return {"email": "john_doe_123@emai.com", "password": "SecurePassword123!"}

# Tests for UserBase
def test_user_base_valid(user_base_data: dict[str, str]):
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_create_data: dict[str, str]):
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_valid(user_update_data: dict[str, str]):
    user_update = UserUpdate(**user_update_data)
    assert user_update.email == user_update_data["email"]
    assert user_update.first_name == user_update_data["first_name"]

# Tests for UserResponse
def test_user_response_valid(user_response_data: dict[str, Any]):
    user = UserResponse(**user_response_data)
    assert user.id == user_response_data["id"]
    # assert user.last_login_at == user_response_data["last_login_at"]

# Tests for LoginRequest
def test_login_request_valid(login_request_data: dict[str, str]):
    login = LoginRequest(**login_request_data)
    assert login.email == login_request_data["email"]
    assert login.password == login_request_data["password"]

# Parametrized tests for nickname and email validation
@pytest.mark.parametrize("nickname", ["test_user", "test-user", "testuser123", "123test"])
def test_user_base_nickname_valid(nickname: Literal['test_user'] | Literal['test-user'] | Literal['testuser123'] | Literal['123test'], user_base_data: dict[str, str]):
    user_base_data["nickname"] = nickname
    user = UserBase(**user_base_data)
    assert user.nickname == nickname

@pytest.mark.parametrize("nickname", ["test user", "test?user", "", "us"])
def test_user_base_nickname_invalid(nickname: Literal['test user'] | Literal['test?user'] | Literal[''] | Literal['us'], user_base_data: dict[str, str]):
    user_base_data["nickname"] = nickname
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Parametrized tests for URL validation
@pytest.mark.parametrize("url", ["http://valid.com/profile.jpg", "https://valid.com/profile.png", None])
def test_user_base_url_valid(url: None | Literal['http://valid.com/profile.jpg'] | Literal['https://valid.com/profile.png'], user_base_data: dict[str, str]):
    user_base_data["profile_picture_url"] = url
    user = UserBase(**user_base_data)
    assert user.profile_picture_url == url

@pytest.mark.parametrize("url", ["ftp://invalid.com/profile.jpg", "http//invalid", "https//invalid"])
def test_user_base_url_invalid(url: Literal['ftp://invalid.com/profile.jpg'] | Literal['http//invalid'] | Literal['https//invalid'], user_base_data: dict[str, str]):
    user_base_data["profile_picture_url"] = url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Tests for comprehensive password validation
password_test_cases = [
    ("Short7!", f"Password must be between {UserCreate.min_length} and {UserCreate.max_length} characters"),
    ("A" * (UserCreate.max_length + 1), f"Password must be between {UserCreate.min_length} and {UserCreate.max_length} characters"),
    ("nouppercase123!", "Password must contain at least one uppercase letter"),
    ("NOLOWERCASE123!", "Password must contain at least one lowercase letter"),
    ("NoDigitPassword!", "Password must contain at least one digit"),
    ("NoSpecialCharacter123", "Password must contain at least one special character"),
    ("Space Password123!", "Password must not contain spaces"),
    ("ValidPassword1!", None)  # This is assumed to be a valid password
]

@pytest.mark.parametrize("password, expected_error", password_test_cases)
def test_password_validation(user_create_data: dict[str, str], password: Any, expected_error: Any):
    user_data = {**user_create_data, "password": password}
    if expected_error:
        with pytest.raises(ValidationError) as excinfo:
            UserCreate(**user_data)
        assert expected_error in str(excinfo.value), f"Expected error message: {expected_error}"
    else:
        user = UserCreate(**user_data)
        assert user.password == password, "Valid password should pass validation without errors."

@pytest.mark.parametrize("input_email, expected_email, expected_error", test_email_validation)
def test_email_validation(user_create_data: dict[str, str], input_email: Any, expected_email: Any, expected_error: Any):
    user_data = {**user_create_data, "email": input_email}
    if expected_error:
        with pytest.raises(ValidationError) as excinfo:
            UserCreate(**user_data)
        assert expected_error in str(excinfo.value), f"Expected error message: '{expected_error}'"
    else:
        user = UserCreate(**user_data)
        assert user.email == expected_email, "Email should be normalized and validated without errors"

# Tests for UserUpdateProfile
# Fixture for valid single field data
@pytest.fixture
def single_field_update_data():
    return {"nickname": "new_nickname"}

# Fixture for all fields set to None
@pytest.fixture
def all_fields_none_update_data():
    return {
        "nickname": None,
        "first_name": None,
        "last_name": None,
        "bio": None,
        "profile_picture_url": None,
        "linkedin_profile_url": None,
        "github_profile_url": None
    }

# Test with valid single field update
def test_user_update_profile_valid(single_field_update_data: dict[str, str]):
    user_update = UserUpdateProfile(**single_field_update_data)
    assert user_update.nickname == single_field_update_data["nickname"]

# Test with invalid update where all fields are None
def test_user_update_profile_invalid(all_fields_none_update_data: dict[str, None]):
    with pytest.raises(ValidationError) as exc_info:
        UserUpdateProfile(**all_fields_none_update_data)
    assert "At least one field must be provided for update" in str(exc_info.value)

# Tests for UserUpdateProfile with reserved nickname
@pytest.mark.parametrize("nickname", ["admin", "moderator", "null", "manager", "anonymous", "authenticated"])
def test_user_update_profile_reserved_nickname(nickname: Literal['admin'] | Literal['moderator'] | Literal['null'] | Literal['manager'] | Literal['anonymous'] | Literal['authenticated']):
    with pytest.raises(ValidationError) as excinfo:
        UserUpdateProfile(nickname=nickname)
    assert "This nickname is reserved and cannot be used." in str(excinfo.value)

# Tests for first and last name validation
@pytest.mark.parametrize("name", ["John-Doe", "O'Reilly", "Anne Marie"])
def test_user_update_profile_name_valid(name: Literal['John-Doe'] | Literal['O\'Reilly'] | Literal['Anne Marie']):
    user = UserUpdateProfile(first_name=name, last_name=name)
    assert user.first_name == name
    assert user.last_name == name

@pytest.mark.parametrize("first_name, last_name, expected_error", [
    ("John@Doe", "JohnDoe", "First name can only contain letters, spaces, hyphens, or apostrophes."),
    ("AnneMarie", "Anne#Marie", "Last name can only contain letters, spaces, hyphens, or apostrophes."),
    ("1234", "Doe", "First name can only contain letters, spaces, hyphens, or apostrophes."),
    ("", "", "At least one field must be provided for update")  # This specifically tests the empty case.
])
def test_user_update_profile_name_invalid(first_name: Literal['John@Doe'] | Literal['AnneMarie'] | Literal['1234'] | Literal[''], last_name: Literal['JohnDoe'] | Literal['Anne#Marie'] | Literal['Doe'] | Literal[''], expected_error: LiteralString | LiteralString | Literal['At least one field must be provided for update']):
    with pytest.raises(ValidationError) as excinfo:
        UserUpdateProfile(first_name=first_name, last_name=last_name)
    assert expected_error in str(excinfo.value)

# Tests for URL validation
@pytest.mark.parametrize("url, expected_error", [
    ("http://example.com/profile.bmp", "Profile picture URL must point to a valid image file (JPEG, PNG)."),  # Invalid file type
    ("ftp://example.com/profile.jpg", "Profile picture URL must use http or https."),  # Incorrect scheme
])
def test_user_update_profile_picture_url_invalid(url: Literal['http://example.com/profile.bmp'] | Literal['ftp://example.com/profile.jpg'], expected_error: LiteralString | Literal['Profile picture URL must use http or https.']):
    with pytest.raises(ValidationError) as excinfo:
        UserUpdateProfile(profile_picture_url=url, first_name="John")
    assert expected_error in str(excinfo.value)

# Tests for LinkedIn URL validation
@pytest.mark.parametrize("url", [
    "https://linkedin.com/in/johndoe",  # Correct format
    "https://linkedin.com/in/jane-doe"  # Another valid example
])
def test_user_update_profile_linkedin_url_valid(url: Literal['https://linkedin.com/in/johndoe'] | Literal['https://linkedin.com/in/jane-doe']):
    # This test confirms that valid URLs do not raise validation errors
    user = UserUpdateProfile(linkedin_profile_url=url, first_name="John")
    assert user.linkedin_profile_url == url

@pytest.mark.parametrize("url, expected_error", [
    ("https://linkedin.com/profile/johndoe", "Invalid LinkedIn profile URL format."),  # Correct domain but incorrect path
    ("http://linkedin.net/in/johndoe", "Invalid LinkedIn profile URL format."),  # Incorrect domain
    ("ftp://linkedin.com/in/johndoe", "LinkedIn profile URL must use http or https.")   # Incorrect scheme
])
def test_user_update_profile_linkedin_url_invalid(url: Literal['https://linkedin.com/profile/johndoe'] | Literal['http://linkedin.net/in/johndoe'] | Literal['ftp://linkedin.com/in/johndoe'], expected_error: Literal['Invalid LinkedIn profile URL format.'] | Literal['LinkedIn profile URL must use http or https.']):
    with pytest.raises(ValidationError) as excinfo:
        UserUpdateProfile(linkedin_profile_url=url, first_name="John")
    assert expected_error in str(excinfo.value)

# Tests for GitHub URL validation
@pytest.mark.parametrize("url, expected_error", [
    ("https://githu.com/", "Invalid GitHub profile URL format."),  # Correct domain but incorrect path
    ("ftp://github.com/johndoe", "GitHub profile URL must use http or https."),  # Incorrect scheme
])
def test_user_update_profile_github_url_invalid(url: Literal['https://githu.com/'] | Literal['ftp://github.com/johndoe'], expected_error: Literal['Invalid GitHub profile URL format.'] | Literal['GitHub profile URL must use http or https.']):
    with pytest.raises(ValidationError) as excinfo:
        UserUpdateProfile(github_profile_url=url, first_name="John")
    assert expected_error in str(excinfo.value)

# Tests for checking at least one field is provided
def test_user_update_profile_no_fields_provided():
    with pytest.raises(ValidationError) as exc_info:
        UserUpdateProfile()
    assert "At least one field must be provided for update" in str(exc_info.value)