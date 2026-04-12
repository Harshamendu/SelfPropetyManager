import pytest


@pytest.fixture
def sample_property_data():
    return {
        "name": "Test Property",
        "address_line1": "123 Test St",
        "city": "Atlanta",
        "state": "GA",
        "zip_code": "30301",
        "property_type": "house",
    }
