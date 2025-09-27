from datetime import UTC, datetime, timedelta, timezone

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime


class TestDateTime:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.integer = 123
        self.aware_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        self.aware_dt_other = datetime(2024, 1, 2, 12, 0, 0, tzinfo=UTC)

    def test_raises_on_naive_datetime(self):
        naive = datetime(2024, 1, 1, 12, 0, 0)
        with pytest.raises(InvariantViolationError):
            DateTime(naive)

    def test_isoformat(self):
        dt = DateTime(self.aware_dt)
        assert dt.isoformat() == self.aware_dt.isoformat()

    def test_astimezone(self):
        dt = DateTime(self.aware_dt)
        new_tz = timezone(timedelta(hours=3))
        dt2 = dt.astimezone(new_tz)
        assert dt2.value.tzinfo == new_tz

    def test_date_and_time(self):
        dt = DateTime(self.aware_dt)
        assert dt.date() == self.aware_dt.date()
        assert dt.time() == self.aware_dt.time()

    def test_timestamp(self):
        dt = DateTime(self.aware_dt)
        assert dt.timestamp() == self.aware_dt.timestamp()

    def test_to_utc(self):
        dt = DateTime(self.aware_dt)
        dt_utc = dt.to_utc()
        assert dt_utc.value.tzinfo == UTC

    def test_comparisons(self):
        dt1 = DateTime(self.aware_dt)
        dt2 = DateTime(self.aware_dt_other)
        assert dt1 < dt2
        assert dt2 > dt1
        assert dt1 <= dt2
        assert dt2 >= dt1
        assert dt1 == DateTime(self.aware_dt)
        assert dt1 != dt2

    def test_add_timedelta(self):
        dt = DateTime(self.aware_dt)
        delta = timedelta(days=1)
        dt2 = dt + delta
        assert isinstance(dt2, DateTime)
        assert dt2.value == self.aware_dt + delta

    def test_sub_timedelta(self):
        dt = DateTime(self.aware_dt)
        delta = timedelta(days=1)
        dt2 = dt - delta
        assert isinstance(dt2, DateTime)
        assert dt2.value == self.aware_dt - delta

    def test_sub_datetime(self):
        dt1 = DateTime(self.aware_dt_other)
        dt2 = DateTime(self.aware_dt)
        diff = dt1 - dt2
        assert diff == self.aware_dt_other - self.aware_dt

    def test_hash(self):
        dt = DateTime(self.aware_dt)
        assert hash(dt) == hash(self.aware_dt)

    def test_eq_and_ne_with_std_datetime_types(self):
        dt = DateTime(self.aware_dt)
        assert dt == dt.value
        assert not (dt != dt.value)

    def test_eq_and_ne_with_other_types(self):
        dt = DateTime(self.aware_dt)
        assert dt != self.integer  # NotImplemented
        assert not (dt == self.integer)

    def test_lt_le_gt_ge_with_std_datetime_types(self):
        dt = DateTime(self.aware_dt)
        # __lt__
        assert (dt < dt.value) is False
        # __le__
        assert (dt <= dt.value) is True
        # __gt__
        assert (dt > dt.value) is False
        # __ge__
        assert (dt >= dt.value) is True

    def test_eq_lt_le_gt_ge_with_other_types(self):
        dt = DateTime(self.aware_dt)

        # __lt__
        with pytest.raises(TypeError):
            assert dt < self.integer
        # __le__
        with pytest.raises(TypeError):
            assert dt <= self.integer
        # __gt__
        with pytest.raises(TypeError):
            assert dt > self.integer
        # __ge__
        with pytest.raises(TypeError):
            assert dt >= self.integer

    def test_add_notimplemented(self):
        dt = DateTime(self.aware_dt)
        with pytest.raises(TypeError):
            assert dt + 123

    def test_sub_notimplemented(self):
        dt = DateTime(self.aware_dt)
        with pytest.raises(TypeError):
            assert dt - 123
