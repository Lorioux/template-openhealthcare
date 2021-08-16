from __future__ import absolute_import


import json
import pytest

from flask import url_for


@pytest.mark.run(order=9)
def test_add_schedules(client, schedules):
    url = url_for("schedules.create_schedule")
    rv = client.post(
        url,  # "/schedules/createSchedule",
        data=json.dumps(schedules),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "successfully" in str(rv.data)


@pytest.mark.run(order=10)
def test_update_schedules(client, schedules):
    schedules[0]["weeks"]["week31"]["timeslots"]["fri"] = ["08:00", "14:00"]
    schedules[0]["weeks"].update(
        {"week32": dict(timeslots={"mon": ["08:00", "14:00", "23:00"]})}
    )

    url = url_for("schedules.update_schedule")
    rv = client.put(
        url,
        data=json.dumps(schedules),
        content_type="application/json",
        follow_redirects=True,
    )

    assert "23:00" in str(rv.data)
