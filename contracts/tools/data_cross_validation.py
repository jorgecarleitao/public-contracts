"""
This module has methods that cross validate the data we have against the data
the official database has.
"""
import requests
import json

if __name__ == '__main__':
    # these first two lines are used to setup a minimal Django environment
    from main.tools import set_up
    set_up.set_up_django_environment('main.settings_for_script')

from contracts.models import Entity, Contract


def get_entity_contracts_difference(base_id):
    """
    Returns a set with the difference between the base_id's of contracts
    from BASE with those we have.
    """

    def _are_entity_contracts_synchronized(entity):
        """
        Checks if the number of contracts in BASE of an entity matches our number
        """
        def get_entity_contracts_count():
            """
            Retrieves the number of contracts from a given entity from BASE
            """
            url = 'http://www.base.gov.pt/base2/rest/contratos?adjudicatariaid=%d' \
                  '&sort(-id)' % entity.base_id

            response = requests.get(url, headers={'Range': 'items=0-24'})

            results_range = response.headers['content-range']
            _, count = results_range.split('/')

            return int(count)

        expected_count = get_entity_contracts_count()
        count = entity.contract_set.count()

        return count == expected_count

    def _get_entity_contracts_difference(entity):
        """
        Returns a set with the difference between base_id's of contracts
        we have with those from BASE.
        """
        def get_entity_contracts():
            """
            Retrieves all contracts from a given entity from BASE
            """
            url = 'http://www.base.gov.pt/base2/rest/contratos?' \
                  'adjudicatariaid=%d' % entity.base_id

            response = requests.get(url, headers={'Range': 'items=0-1000000'})
            return json.loads(response.text)

        expected_ids = set([contract['id'] for contract in
                            get_entity_contracts()])

        existing_ids = set(entity.contract_set.values_list('base_id',
                                                           flat=True))

        return expected_ids.difference(existing_ids)

    entity = Entity.objects.get(base_id=base_id)
    # first we see if counts match, a cheaper operation
    if not _are_entity_contracts_synchronized(entity):
        # if counts don't match, we see difference
        return _get_entity_contracts_difference(entity)
    else:
        return {}


def get_contracts_count():
    """
    Retrieves the number of contracts from a given entity from BASE
    """
    url = 'http://www.base.gov.pt/base2/rest/contratos'

    response = requests.get(url, headers={'Range': 'items=0-24'})

    # should be "items 0-%d/%d", we want the second %d that represents the
    # total
    results_range = response.headers['content-range']
    _, count = results_range.split('/')

    return int(count)


def get_contracts_count_difference():
    """
    Checks if the number of contracts in BASE matches our number.

    Returns the difference as a percentage of all contracts.
    """
    expected_count = get_contracts_count()
    count = Contract.objects.all().count()

    return expected_count - count


def get_contracts_difference():
    """
    Returns a set of all contracts that exist in BASE, but do not exist in our
    database.

    This function is expensive and performs multiple hits to BASE.
    """
    url = 'http://www.base.gov.pt/base2/rest/contratos'

    count = get_contracts_count()

    CONTRACTS_PER_REQUEST = 10000

    total_difference = set()
    for i in reversed(range(int(count/CONTRACTS_PER_REQUEST)+1)):
        response = requests.get(url, headers={
            'Range': 'items=%d-%d' % (i*CONTRACTS_PER_REQUEST,
                                      (i+1)*CONTRACTS_PER_REQUEST - 1)})

        contracts_ids = [contract['id'] for contract in
                         json.loads(response.text)]

        expected_ids = set(contracts_ids)

        existing_ids = set(Contract.objects.values_list('base_id', flat=True)
                           .filter(base_id__range=(contracts_ids[0],
                                                   contracts_ids[-1])))

        difference = expected_ids.difference(existing_ids)

        total_difference = total_difference.union(difference)

    return total_difference


if __name__ == '__main__':
    #print(are_contracts_synchronized())
    print(get_contracts_difference())
