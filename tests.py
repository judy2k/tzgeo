from tzgeo import tz_lookup


def test_border():
    assert tz_lookup(1, 10) == 'Africa/Malabo'
    assert tz_lookup(0.995, 10) == 'Africa/Libreville'
    assert tz_lookup(0.995366, 9.993868) == 'Africa/Malabo'
    assert tz_lookup(0.992871, 10.003417) == 'Africa/Libreville'

    # Other border:
    assert tz_lookup(1.760234, 13.176470) == 'Africa/Libreville'
    assert tz_lookup(1.759548, 13.185225) == 'Africa/Brazzaville'

    assert tz_lookup(0.024526, 13.923454) == 'Africa/Libreville'
    assert tz_lookup(0.05, 13.944998) == 'Africa/Brazzaville'


def test_overlaps():
    assert tz_lookup(-1, 32) == 'Africa/Dar_es_Salaam'
    assert tz_lookup(-19, 41) is None
    assert tz_lookup(-51, 72) is None

if __name__ == "__main__":
    import doctest
    import tzgeo
    doctest.testmod(tzgeo)
