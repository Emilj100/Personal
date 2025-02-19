from project import User
import pytest
from unittest.mock import patch, mock_open

def test_calorie_intake(capsys):
    user = User("Emil", "Male", "186", "19", "100.5", "1", "5")
    user.calorie_intake()
    capsys_output = capsys.readouterr()
    expected_output = "\nThis is your calorie intake: 2719.35 calories\n\n"
    assert capsys_output.out == expected_output

def test_show_user_data():
    user = User("Emil", "Male", "186", "19", "100.5", "1", "5")
    assert user.show_user_data() == "Name: Emil\nGender: Male\nHeight: 186\nAge: 19\nWeight: 100.5\nGoal: Lose weight\nTraining: Training 5 times per week"

def test_give_training_program():
    user = User("Emil", "Male", "186", "19", "100.5", "1", "5")
    with patch("project.open", mock_open(read_data="This is a test")) as mocked_file:
        user.give_training_program()
        program_content = str(user)
    assert program_content == "This is a test"
