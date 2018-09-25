import os.path
import pytest
from beetagg import detect
from beetagg.parser import parse


@pytest.fixture(scope='module', params=range(5))
def sample(request):
    basename = os.path.dirname(__file__) + '/samples/{:02d}'.format(request.param)
    with open(basename + '.txt', 'r') as f:
        top, bottom = f.read().strip().split('\n')
    yield (basename + '.png', top, bottom)


def test_samples(sample):
    image_path, top, bottom = sample
    result = detect(image_path)
    assert isinstance(result, bytes)
    parsed = parse(result)
    assert top == parsed[2]
    assert bottom == parsed[3]
