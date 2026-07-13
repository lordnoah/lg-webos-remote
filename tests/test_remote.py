from remote import KEY_MAP

def test_key_map():
    assert "up" in KEY_MAP
    assert KEY_MAP["up"] == "UP"
    assert KEY_MAP["vol_up"] == "VOLUMEUP"
    assert KEY_MAP["power"] == "POWER"
    assert "invalid" not in KEY_MAP
