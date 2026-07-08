import pytest

from fwfii.atom import AtomRepo


@pytest.fixture(autouse=True)
def clear_atom_repo():
    AtomRepo.clear()
    yield
    AtomRepo.clear()
