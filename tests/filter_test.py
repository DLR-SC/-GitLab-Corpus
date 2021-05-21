# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
# SPDX-License-Identifier: MIT
from unittest import mock
from filter import Filter
from utils.helpers import Corpus

corpus = Corpus()
corpus.data = {"Projects": [
    {
        'id': 1,
        'description': 'test description',
        'name': 'Test Project',
        'created_at': '2021-05-10T15:00:00.000Z',
        'default_branch': 'master',
        'last_activity_at': '2021-05-10T16:00:00.000Z',
        'archived': False,
        'visibility': 'internal',
        'issues_enabled': True,
        'creator_id': 10,
        'open_issues_count': 0,
        'issue_statistics': {
            "counts": {
                "all": 0,
                "closed": 0,
                "opened": 0
            }
        },
        'languages': {
            "Python": 80.0,
            "HTML": 20.0
        },
        'files': [
            {
                "id": "hash123",
                "name": "test.py",
                "type": "blob"
            }
        ]
    }
]}

language_test_corpus = Corpus()
language_test_corpus.data = {"Projects": [
    {
        "id": 1,
        "languages": {
            "Python": 50.0,
            "C": 50.0
        }
    },
    {
        "id": 2,
        "languages": {
            "TeX": 10.0,
            "C": 90.0
        }
    },
    {
        "id": 3,
        "languages": {}
    },
    {
        "id": 4,
        "languages": {
            "Ada": 30.0,
            "Assembly": 30.0,
            "Batchfile": 40.0
        }
    }
]}

language_test_project = {
    "id": 123,
    "languages": {
        "Python": 50.0,
        "C": 30.0,
        "TeX": 10.0,
        "Assembly": 10.0
    }
}


def test_init_filter_without_file():
    filter = Filter(False, corpus, False, "-")
    assert filter.input_corpus.data == corpus.data


def test_init_filter_from_file():
    mocked_corpus_file = mock.mock_open(read_data="""{"Projects": [
        {
            "id": 1,
            "description": "test description",
            "name": "Test Project",
            "created_at": "2021-05-10T15:00:00.000Z",
            "default_branch": "master",
            "last_activity_at": "2021-05-10T16:00:00.000Z",
            "archived": false,
            "visibility": "internal",
            "issues_enabled": true,
            "creator_id": 10,
            "open_issues_count": 0,
            "issue_statistics": {
                "counts": {
                    "all": 0,
                    "closed": 0,
                    "opened": 0
                }
            },
            "languages": {
                "Python": 80.0,
                "HTML": 20.0
            },
            "files": [
                {
                    "id": "hash123",
                    "name": "test.py",
                    "type": "blob"
                }
            ]
        }
    ]}""")

    with mock.patch("builtins.open", mocked_corpus_file, create=True):
        filter = Filter(False, corpus, True, "corpus.json")

    assert filter.input_corpus.data == corpus.data


def test_load_filters():
    mocked_filters = """
    filters:
        - atmost_languages:
            - Python: "<=//100.0"
            - C: "<=//100.0"
        - id: "==//30"
        - name: "example filter project"
        - issues_enabled: "==//true"
    
    attributes:
        - id
        - name
    """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")

    assert filter.filters == {"id": "==//30", "name": "example filter project", "issues_enabled": "==//true"}
    assert filter.attributes == ["id", "name"]
    assert filter.atmost_languages == {"Python": "<=//100.0", "C": "<=//100.0"}


def test_load_filters_no_file_found(capfd):
    filter = Filter(True, corpus, False, "")
    filter.load_filters(filter_file="not_existing.file")
    assert capfd.readouterr()[0] == "No filter configuration file found. No filters will be applied.\n"


def test_load_languages():
    mocked_filters = """
    filters:
        - atleast_languages:
            - C: "<=//100.0"
        - atmost_languages:
            - Python: "<=//100.0"
        - any_languages:
            - Java: "<=//100.0"
        - explicit_languages:
            - C#: "<=//100.0"
    
    attributes:
    """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")

    assert filter.atleast_languages == {"C": "<=//100.0"}
    assert filter.atmost_languages == {"Python": "<=//100.0"}
    assert filter.any_languages == {"Java": "<=//100.0"}
    assert filter.explicit_languages == {"C#": "<=//100.0"}


def test_check_languages_atleast_true():
    mocked_filters = """
    filters:
        - atleast_languages:
            - C: "<=//100.0"
            - Python: "<=//100.0"
    
    attributes:
    """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, language_test_corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")
    assert filter.check_languages("atleast_languages", language_test_project) is True


def test_check_languages_atleast_false():
    mocked_filters = """
    filters:
        - atleast_languages:
            - C: "<=//100.0"
            - Python: "<=//100.0"
            - ActionScript: "<=//100.0"

    attributes:
    """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, language_test_corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")
    assert filter.check_languages("atleast_languages", language_test_project) is False


def test_check_languages_atmost_true():
    mocked_filters = """
        filters:
            - atmost_languages:
                - C: "<=//100.0"
                - Python: "<=//100.0"
                - TeX: "<=//100.0"
                - Assembly: "<=//100.0"

        attributes:
        """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, language_test_corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")
    assert filter.check_languages("atmost_languages", language_test_project) is True


def test_check_languages_atmost_false():
    mocked_filters = """
        filters:
            - atmost_languages:
                - C: "<=//100.0"
                - Python: "<=//100.0"

        attributes:
        """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, language_test_corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")
    assert filter.check_languages("atmost_languages", language_test_project) is False


def test_check_languages_any_true():
    mocked_filters = """
        filters:
            - any_languages:
                - C: "<=//100.0"
                - Python: "<=//100.0"

        attributes:
        """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, language_test_corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")
    assert filter.check_languages("any_languages", language_test_project) is True


def test_check_languages_any_false():
    mocked_filters = """
        filters:
            - any_languages:
                - CMake: "<=//100.0"

        attributes:
        """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, language_test_corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")
    assert filter.check_languages("any_languages", language_test_project) is False


def test_check_languages_explicit_true():
    mocked_filters = """
        filters:
            - explicit_languages:
                - C: "<=//100.0"
                - Python: "<=//100.0"
                - TeX: "<=//100.0"
                - Assembly: "<=//100.0"

        attributes:
        """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, language_test_corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")
    assert filter.check_languages("explicit_languages", language_test_project) is True


def test_check_languages_explicit_false():
    mocked_filters = """
        filters:
            - explicit_languages:
                - C: "<=//100.0"
                - Python: "<=//100.0"

        attributes:
        """
    mocked_filter_file = mock.mock_open(read_data=mocked_filters)
    filter = Filter(False, language_test_corpus, False, "")
    with mock.patch("builtins.open", mocked_filter_file, create=True):
        filter.load_filters(filter_file="mocked_filters.yaml")
    assert filter.check_languages("explicit_languages", language_test_project) is False
