import json
from base64 import b64decode

import bson
import pytest

from mega.aws.message import MessageType
from mega.aws.payload import PayloadType
from mega.aws.sns.message import SnsNotification, SnsMessageType
from mega.aws.sqs.message import SqsMessage
from mega.aws.sqs.subscribe.api import SqsReceiver
from mega.event import deserialize_mega_payload
from tests.mega.aws.sqs import get_sqs_request_data, get_queue_url_from_request, get_request_attribute, \
    get_sqs_response_data
from tests.vcr import build_vcr

vcr = build_vcr(
    path='aws/sqs/subscribe/api',
    match_on=['method', 'scheme', 'host', 'port', 'path', 'query']
)


@pytest.fixture
def queue_url():
    return 'https://sqs.us-east-2.amazonaws.com/424566909325/sqs-mega-test'


def get_sqs_receive_message_response_data(cassette):
    response = get_sqs_response_data(cassette)
    return response['ReceiveMessageResponse']['ReceiveMessageResult']


def assert_request_match_sqs_receiver_attributes(cassette, sqs_receiver):
    request = get_sqs_request_data(cassette)
    assert get_queue_url_from_request(request) == sqs_receiver.queue_url
    assert int(get_request_attribute(request, 'MaxNumberOfMessages')) == sqs_receiver.max_number_of_messages
    assert int(get_request_attribute(request, 'WaitTimeSeconds')) == sqs_receiver.wait_time_seconds
    assert int(get_request_attribute(request, 'VisibilityTimeout')) == sqs_receiver.visibility_timeout


def assert_message_attributes_match_response(message, response):
    assert message.message_id == response['Message']['MessageId']
    assert message.receipt_handle == response['Message']['ReceiptHandle']


def assert_is_sqs_message(message):
    assert message is not None
    assert isinstance(message, SqsMessage)
    assert message.message_type == MessageType.SQS


def assert_is_sns_notification(message):
    assert message is not None
    assert isinstance(message, SnsNotification)
    assert message.message_type == MessageType.SNS
    assert message.sns_message_type == SnsMessageType.NOTIFICATION


def test_receive_message_with_plaintext_payload(queue_url):
    sqs = SqsReceiver(
        queue_url=queue_url,
        max_number_of_messages=1
    )

    with vcr.use_cassette('receive_message_with_plaintext_payload') as cassette:
        messages = sqs.receive_messages()

    assert cassette.all_played
    response = get_sqs_receive_message_response_data(cassette)

    assert len(messages) == 1
    message = messages[0]
    assert_is_sqs_message(message)
    assert_message_attributes_match_response(message, response)

    assert message.payload_type == PayloadType.PLAINTEXT
    assert message.payload == response['Message']['Body']

    assert message.embedded_message is None
    assert_request_match_sqs_receiver_attributes(cassette, sqs)


def test_receive_message_with_base64_encoded_binary_payload(queue_url):
    sqs = SqsReceiver(
        queue_url=queue_url,
        max_number_of_messages=1
    )

    with vcr.use_cassette('receive_message_with_base64_encoded_binary_payload') as cassette:
        messages = sqs.receive_messages()

    assert cassette.all_played
    response = get_sqs_receive_message_response_data(cassette)

    assert len(messages) == 1
    message = messages[0]
    assert_is_sqs_message(message)
    assert_message_attributes_match_response(message, response)

    assert message.payload_type == PayloadType.BINARY
    assert message.payload == b64decode(response['Message']['Body'])

    assert message.embedded_message is None
    assert_request_match_sqs_receiver_attributes(cassette, sqs)


def test_receive_message_with_plaintext_json_payload(queue_url):
    sqs = SqsReceiver(
        queue_url=queue_url,
        max_number_of_messages=1
    )

    with vcr.use_cassette('receive_message_with_plaintext_json_payload') as cassette:
        messages = sqs.receive_messages()

    assert cassette.all_played
    response = get_sqs_receive_message_response_data(cassette)

    assert len(messages) == 1
    message = messages[0]
    assert_is_sqs_message(message)
    assert_message_attributes_match_response(message, response)

    assert message.payload_type == PayloadType.DATA
    assert message.payload == json.loads(response['Message']['Body'])

    assert message.embedded_message is None
    assert_request_match_sqs_receiver_attributes(cassette, sqs)


def test_receive_message_with_plaintext_mega_payload(queue_url):
    sqs = SqsReceiver(
        queue_url=queue_url,
        max_number_of_messages=1
    )

    with vcr.use_cassette('receive_message_with_plaintext_mega_payload') as cassette:
        messages = sqs.receive_messages()

    assert cassette.all_played
    response = get_sqs_receive_message_response_data(cassette)

    assert len(messages) == 1
    message = messages[0]
    assert_is_sqs_message(message)
    assert_message_attributes_match_response(message, response)

    assert message.payload_type == PayloadType.MEGA
    assert message.payload == deserialize_mega_payload(
        json.loads(response['Message']['Body'])
    )

    assert message.embedded_message is None
    assert_request_match_sqs_receiver_attributes(cassette, sqs)


def test_receive_message_with_base64_encoded_binary_bson_payload(queue_url):
    sqs = SqsReceiver(
        queue_url=queue_url,
        max_number_of_messages=1
    )

    with vcr.use_cassette('receive_message_with_base64_encoded_binary_bson_payload') as cassette:
        messages = sqs.receive_messages()

    assert cassette.all_played
    response = get_sqs_receive_message_response_data(cassette)

    assert len(messages) == 1
    message = messages[0]
    assert_is_sqs_message(message)
    assert_message_attributes_match_response(message, response)

    assert message.payload_type == PayloadType.DATA
    assert message.payload == bson.loads(
        b64decode(response['Message']['Body'])
    )

    assert message.embedded_message is None
    assert_request_match_sqs_receiver_attributes(cassette, sqs)


def test_receive_message_with_base64_encoded_binary_mega_payload(queue_url):
    sqs = SqsReceiver(
        queue_url=queue_url,
        max_number_of_messages=1
    )

    with vcr.use_cassette('receive_message_with_base64_encoded_binary_mega_payload') as cassette:
        messages = sqs.receive_messages()

    assert cassette.all_played
    response = get_sqs_receive_message_response_data(cassette)

    assert len(messages) == 1
    message = messages[0]
    assert_is_sqs_message(message)
    assert_message_attributes_match_response(message, response)

    assert message.payload_type == PayloadType.MEGA
    assert message.payload == deserialize_mega_payload(
        bson.loads(
            b64decode(response['Message']['Body'])
        )
    )

    assert message.embedded_message is None
    assert_request_match_sqs_receiver_attributes(cassette, sqs)


def test_receive_message_with_plaintext_mega_payload_over_sns(queue_url):
    sqs = SqsReceiver(
        queue_url=queue_url,
        max_number_of_messages=1
    )

    with vcr.use_cassette('receive_message_with_plaintext_mega_payload_over_sns') as cassette:
        messages = sqs.receive_messages()

    assert cassette.all_played
    response = get_sqs_receive_message_response_data(cassette)

    assert len(messages) == 1
    message = messages[0]
    assert_is_sqs_message(message)
    assert_message_attributes_match_response(message, response)

    assert message.payload_type == PayloadType.MEGA
    assert message.payload == deserialize_mega_payload(
        json.loads(
            json.loads(response['Message']['Body'])['Message']
        )
    )

    assert_is_sns_notification(message.embedded_message)
    assert_request_match_sqs_receiver_attributes(cassette, sqs)


def test_receive_message_with_base64_encoded_binary_mega_payload_over_sns(queue_url):
    sqs = SqsReceiver(
        queue_url=queue_url,
        max_number_of_messages=1
    )

    with vcr.use_cassette('receive_message_with_base64_encoded_binary_mega_payload_over_sns') as cassette:
        messages = sqs.receive_messages()

    assert cassette.all_played
    response = get_sqs_receive_message_response_data(cassette)

    assert len(messages) == 1
    message = messages[0]
    assert_is_sqs_message(message)
    assert_message_attributes_match_response(message, response)

    assert message.payload_type == PayloadType.MEGA
    assert message.payload == deserialize_mega_payload(
        bson.loads(
            b64decode(
                json.loads(response['Message']['Body'])['Message']
            )
        )
    )

    assert_is_sns_notification(message.embedded_message)
    assert_request_match_sqs_receiver_attributes(cassette, sqs)


def test_delete_message_that_exists(queue_url):
    sqs = SqsReceiver(queue_url=queue_url)

    message_id = '96427844-a8c4-41e5-beed-dab5780cc681'
    receipt_handle = (
        'AQEBY/+I4IQJzCkjsop/FaaKLb5VKXL9JHF4BWbJwOD0osZbenehbjp4xQ59r1DD0pEonhUCaILKkQfq7FrPhUomHBzOzK+e4qCGI62QgkLt6V'
        '8vYJtHlhSNrroy+c9LyuZFKtVNJQ/8rjFwEDQ/jnFdA6MLGnG2Aaj+8LTdvXb4aG+r1PwkS4AEEa4IvMty5NJOwmd70QynfopkRO18EGe6pKkE'
        '6d0j1XvZNkd7peisPLxwU9cljjyu+Hdds12atn71Ss7nn/jr2ElhsnzJrB3eQ4XCtjYP/9sfXT8+0BT5SPb2zCIe1bDzXCLxZypikkdEkQq33z'
        '/TtjWk0/b8yyReM4o52m83tYP6fB0XNlQnWebpO/9leappxF5mFXl7kO2N4ga0dBJ0ts+I/j4rn6GP5w=='
    )

    message = SqsMessage(
        message_id=message_id,
        receipt_handle=receipt_handle,
        payload='hello world!',
        payload_type=PayloadType.PLAINTEXT
    )

    with vcr.use_cassette('delete_message_that_exists') as cassette:
        sqs.delete_message(message)

    assert cassette.all_played
    request = get_sqs_request_data(cassette)
    assert get_request_attribute(request, 'ReceiptHandle') == receipt_handle
    assert get_queue_url_from_request(request) == sqs.queue_url


def test_delete_message_that_has_already_been_deleted(queue_url):
    sqs = SqsReceiver(queue_url=queue_url)

    message_id = '96427844-a8c4-41e5-beed-dab5780cc681'
    receipt_handle = (
        'AQEBY/+I4IQJzCkjsop/FaaKLb5VKXL9JHF4BWbJwOD0osZbenehbjp4xQ59r1DD0pEonhUCaILKkQfq7FrPhUomHBzOzK+e4qCGI62QgkLt6V'
        '8vYJtHlhSNrroy+c9LyuZFKtVNJQ/8rjFwEDQ/jnFdA6MLGnG2Aaj+8LTdvXb4aG+r1PwkS4AEEa4IvMty5NJOwmd70QynfopkRO18EGe6pKkE'
        '6d0j1XvZNkd7peisPLxwU9cljjyu+Hdds12atn71Ss7nn/jr2ElhsnzJrB3eQ4XCtjYP/9sfXT8+0BT5SPb2zCIe1bDzXCLxZypikkdEkQq33z'
        '/TtjWk0/b8yyReM4o52m83tYP6fB0XNlQnWebpO/9leappxF5mFXl7kO2N4ga0dBJ0ts+I/j4rn6GP5w=='
    )

    message = SqsMessage(
        message_id=message_id,
        receipt_handle=receipt_handle,
        payload='hello world!',
        payload_type=PayloadType.PLAINTEXT
    )

    with vcr.use_cassette('delete_message_that_has_already_been_deleted') as cassette:
        sqs.delete_message(message)
        sqs.delete_message(message)

    assert cassette.all_played
    request = get_sqs_request_data(cassette)
    assert get_request_attribute(request, 'ReceiptHandle') == receipt_handle
    assert get_queue_url_from_request(request) == sqs.queue_url
