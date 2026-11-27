from datetime import date

import pytest
from pydantic import ValidationError


@pytest.mark.parametrize("window_end", [date(2025, 1, 8), date(2025, 1, 7)])
def test_empty_or_reversed_window_is_rejected(make_context, window_end):
    with pytest.raises(ValidationError):
        make_context(window_start=date(2025, 1, 8), window_end=window_end)
