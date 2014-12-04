from ansible.utils.plugins import lookup_loader
import os
import pytest


lookup_loader.add_directory(
    os.path.join(
        os.path.dirname(__file__),
        'lookup_plugins'))


@pytest.fixture
def lookup(tmpdir):
    return lookup_loader.get('multiple', str(tmpdir))


def test_simple_lookup(lookup):
    assert ['1', '2', '3'] == lookup.run([
        ['1', '2', '3']
    ])


@pytest.mark.parametrize('apply_fun', [
    '{{ item | int * 2 }}',
    'item | int * 2',
])
def test_apply(lookup, apply_fun):
    assert ['2', '4', '6'] == lookup.run([
        ['1', '2', '3'],
        {'apply': apply_fun},
    ])


def test_external_lookup(lookup):
    assert [['a', '1'], ['a', '2'], ['b', '1'], ['b', '2']] == lookup.run([
        {'with_items': ['a', 'b']},
        {'with_nested': [
            'items',
            ['1', '2'],
        ]},
    ])
