from django.conf import settings
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from relationaldb.models import (
    CentralizedOracle, Event, Market, Order, OutcomeTokenBalance
)
from .serializers import (
    CentralizedOracleSerializer, EventSerializer, MarketSerializer,
    MarketTradesSerializer, OutcomeTokenBalanceSerializer, MarketParticipantTradesSerializer
)
from .filters import (
    CentralizedOracleFilter, EventFilter, MarketFilter, DefaultPagination,
    MarketTradesFilter
)


class CentralizedOracleListView(generics.ListAPIView):
    queryset = CentralizedOracle.objects.all()
    serializer_class = CentralizedOracleSerializer
    filter_class = CentralizedOracleFilter
    pagination_class = DefaultPagination


class CentralizedOracleFetchView(generics.RetrieveAPIView):
    queryset = CentralizedOracle.objects.all()
    serializer_class = CentralizedOracleSerializer

    def get_object(self):
        return get_object_or_404(CentralizedOracle, address=self.kwargs['oracle_address'])


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_class = EventFilter
    pagination_class = DefaultPagination


class EventFetchView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_object(self):
        return get_object_or_404(Event, address=self.kwargs['event_address'])


class MarketListView(generics.ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    filter_class = MarketFilter
    pagination_class = DefaultPagination


class MarketFetchView(generics.RetrieveAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer

    def get_object(self):
        return get_object_or_404(Market, address=self.kwargs['market_address'])


@api_view(['GET'])
def factories_view(request):
    factories = {}
    for contract in settings.ETH_EVENTS:
        if 'PUBLISH' not in contract or not contract['PUBLISH']:
            continue
        address = contract['ADDRESSES'][0]
        index = contract['NAME']
        if 'PUBLISH_UNDER' in contract:
            pub_index = contract['PUBLISH_UNDER']
            if pub_index in factories:
                factories[pub_index][index] = address
            else:
                factories[pub_index] = {index: address}
        else:
            factories[index] = address

    return Response(factories)


class MarketSharesView(generics.ListAPIView):
    serializer_class = OutcomeTokenBalanceSerializer
    # filter_class = MarketShareEntryFilter
    pagination_class = DefaultPagination

    def get_queryset(self):
        market = get_object_or_404(Market, address=self.kwargs['market_address'])
        outcome_tokens = market.event.outcometoken_set.values_list('address', flat=True)
        return OutcomeTokenBalance.objects.filter(
            owner=self.kwargs['owner_address'],
            outcome_token__address__in=list(outcome_tokens)
        )


class AllMarketSharesView(generics.ListAPIView):
    """
    Returns all outcome token balances (market shares) for all users in a market
    """
    serializer_class = OutcomeTokenBalanceSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        return OutcomeTokenBalance.objects.filter(
            outcome_token__address__in=list(
                Market.objects.get(
                    address=self.kwargs['market_address']
                ).event.outcometoken_set.values_list('address', flat=True)
            )
        )


class MarketParticipantTradesView(generics.ListAPIView):

    serializer_class = MarketParticipantTradesSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Order.objects.filter(
            market=self.kwargs['market_address'],
            sender=self.kwargs['owner_address']
        ).order_by('creation_date_time')


class MarketTradesView(generics.ListAPIView):
    serializer_class = MarketTradesSerializer
    pagination_class = DefaultPagination
    filter_class = MarketTradesFilter

    def get_queryset(self):
        # Check if Market exists
        get_list_or_404(Market, address=self.kwargs['market_address'])
        # return trades
        return Order.objects.filter(
            market=self.kwargs['market_address'],
        )


class AccountTradesView(generics.ListAPIView):
    """
    Returns the orders (trades) for the given account address
    """
    serializer_class = MarketTradesSerializer
    pagination_class = DefaultPagination
    filter_class = MarketTradesFilter

    def get_queryset(self):
        return Order.objects.filter(
            sender=self.kwargs['account_address']
        )


class AccountSharesView(generics.ListAPIView):
    """
    Returns the shares for the given account address
    """
    serializer_class = OutcomeTokenBalanceSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        return OutcomeTokenBalance.objects.filter(
            owner=self.kwargs['account_address'],
        )