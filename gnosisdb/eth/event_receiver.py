from abc import ABCMeta, abstractmethod
from relationaldb.serializers import (
    CentralizedOracleSerializer, ScalarEventSerializer, CategoricalEventSerializer,
    UltimateOracleSerializer, MarketSerializer, OutcomeTokenInstanceSerializer,
    CentralizedOracleInstanceSerializer
)

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class AbstractEventReceiver(object):
    """Abstract EventReceiver class."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def save(self, decoded_event, block_info): pass


class CentralizedOracleFactoryReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = CentralizedOracleSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()


class EventFactoryReceiver(AbstractEventReceiver):

    events = {
        'ScalarEventCreation': ScalarEventSerializer,
        'CategoricalEventCreation': CategoricalEventSerializer
    }

    def save(self, decoded_event, block_info):
        from json import dumps
        logger.info('Event Factory Serializer {}'.format(dumps(decoded_event)))
        if self.events.get(decoded_event.get('name')):
            serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            if serializer.is_valid():
                serializer.save()
            else:
                logger.info(serializer.errors)


class UltimateOracleFactoryReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = UltimateOracleSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()


class MarketFactoryReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = MarketSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()


class MarketOrderReceiver(AbstractEventReceiver):
    def save(self, decoded_event, block_info):
        pass


# contract instances
class CentralizedOracleInstanceReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = CentralizedOracleInstanceSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()


class EventInstanceReceiver(AbstractEventReceiver):

    # TODO, develop serializers
    events = {
        'Issuance': '', # sum to totalSupply, update data
        'Revocation': '', # subtract from total Supply, update data
        'OutcomeTokenCreation': OutcomeTokenInstanceSerializer
    }

    def save(self, decoded_event, block_info):
        serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()

# TODO remove
class OutcomeTokenReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = OutcomeTokenInstanceSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()
