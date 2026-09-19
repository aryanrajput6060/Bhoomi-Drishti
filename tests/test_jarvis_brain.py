from backend.jarvis.brain import JarvisBrain


def test_parse_intent_for_open_command():
    brain = JarvisBrain()
    result = brain.handle_request("open notepad")
    assert result["intent"] == "open_application"
    assert "notepad" in result["target"].lower()


def test_parse_intent_for_note_creation():
    brain = JarvisBrain()
    result = brain.handle_request("take a note: launch meeting at 3pm")
    assert result["intent"] == "create_note"
    assert "launch meeting" in result["content"].lower()


def test_parse_intent_for_reminder():
    brain = JarvisBrain()
    result = brain.handle_request("remind me to call mom in 30 minutes")
    assert result["intent"] == "set_reminder"
    assert "call mom" in result["content"].lower()
