from parameterized import parameterized

from mega.event.v1.payload import MegaPayload, Event, EventObject
from tests.mega.event.v1.payload.event_object_test import build_event_object_kwargs
from tests.mega.event.v1.payload.event_test import build_event_kwargs


def build_mega_payload_kwargs():
    return dict(
        event=Event(**build_event_kwargs()),
        object=EventObject(**build_event_object_kwargs()),
        extra={
            'channel': 'web/desktop',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
            'user_ip_address': '177.182.205.103'
        }
    )


def test_create_event():
    kwargs = build_mega_payload_kwargs()
    payload = MegaPayload(**kwargs)

    assert payload.event is not None
    assert isinstance(payload.event, Event)
    assert payload.event == kwargs['event']

    assert payload.object is not None
    assert isinstance(payload.object, EventObject)
    assert payload.object == kwargs['object']

    assert payload.extra is not None
    assert payload.extra == kwargs['extra']


@parameterized.expand([
    ['object', None],
    ['extra', {}]
])
def test_create_mega_payload_without_optional_attribute_should_use_default(attribute_name, expected_default):
    kwargs = build_mega_payload_kwargs()
    del kwargs[attribute_name]

    payload = MegaPayload(**kwargs)
    assert getattr(payload, attribute_name) == expected_default


def test_create_mega_payload_with_additional_kwargs_should_be_added_to_the_extra_dictionary():
    payload = MegaPayload(event=Event(**build_event_kwargs()), foo='bar', test=123)

    assert payload.extra == {
        'foo': 'bar',
        'test': 123,
    }


def test_mega_payload_matches_data_when_protocol_and_version_match():
    data = {
        'protocol': 'mega',
        'version': 1
    }
    assert MegaPayload.matches(data) is True


@parameterized.expand([
    [None],
    [''],
    ['MEGA'],
    ['Mega'],
    ['MeGa'],
    ['_mega'],
    [' mega'],
    ['mega_'],
    ['123foobar']
])
def test_mega_payload_does_not_match_data_when_protocol_is(protocol):
    data = {
        'protocol': protocol,
        'version': 1
    }
    assert MegaPayload.matches(data) is False


@parameterized.expand([
    [None],
    ['1'],
    [2],
    [0],
    [-1]
])
def test_mega_payload_does_not_match_data_when_version_is(version):
    data = {
        'protocol': 'mega',
        'version': version
    }
    assert MegaPayload.matches(data) is False


def test_mega_payload_does_match_data_when_protocol_is_missing():
    data = {'version': 1}
    assert MegaPayload.matches(data) is False


def test_mega_payload_does_match_data_when_version_is_missing():
    data = {'protocol': 'mega'}
    assert MegaPayload.matches(data) is False