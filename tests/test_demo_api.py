from datetime import date

from laborlens.api.demo import (
    demo_episode_detail,
    demo_episodes,
    demo_replay,
)


def test_demo_episode_is_available() -> None:
    result = demo_episodes()

    assert result["count"] == 1

    assert result["episodes"][0]["start_date"] == "2024-06-01"


def test_demo_detail_is_grounded() -> None:
    result = demo_episode_detail(date(2024, 6, 1))

    assert result is not None

    assert result["episode"]["score"] == -0.4606394461100772

    assert result["skeptic"]["verdict"] == "supported"


def test_demo_replay_preserves_detection() -> None:
    result = demo_replay(target=date(2024, 6, 1))

    assert result is not None

    metrics = result["metrics"]

    assert metrics["first_detected_as_of"] == "2024-07-30"

    assert metrics["previous_information_state"] == "2024-07-25"

    assert metrics["detection_release_series"] == [
        "JTSHIR",
        "JTSJOL",
    ]


def test_demo_replay_has_20_states() -> None:
    result = demo_replay(target=date(2024, 6, 1))

    assert result is not None
    assert len(result["states"]) == 20
