from unittest.mock import patch
from utils.url_checker import is_url_accessible

def test_is_url_accessible():
    with patch('requests.head') as mocked_head:
        mocked_head.return_value.status_code = 200
        assert is_url_accessible("https://www.google.com") is True

        mocked_head.return_value.status_code = 404
        assert is_url_accessible("http://thisurldoesnotexist.tld") is False
