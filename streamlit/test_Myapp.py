import os
from streamlit.testing.v1 import AppTest

def test_myapp_content():
    # Construct the path to Myapp.py relative to this test file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "Myapp.py")

    # Initialize and run the app
    at = AppTest.from_file(app_path)
    at.run()

    # Assert that the app ran without exceptions
    assert not at.exception

    # Verify the content written by st.title()
    assert len(at.title) > 0
    assert at.title[0].value == "Employee Attendance Tracker"
