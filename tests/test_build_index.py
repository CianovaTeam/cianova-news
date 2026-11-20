import json

import pytest

import common


def _write(news_dir, news_id, published, news_type="minecraft", body="cuerpo"):
    meta = {
        "id": news_id,
        "type": news_type,
        "title_es": f"Título {news_id}",
        "summary_es": "Resumen breve.",
        "published": published,
    }
    common.write_document(str(news_dir / f"{news_id}.md"), meta, body)


def test_build_index_sorts_by_date_desc(tmp_path):
    _write(tmp_path, "bedrock-26.50", "2026-09-01")
    _write(tmp_path, "bedrock-26.60", "2026-10-27")
    _write(tmp_path, "cianova-v4.0.0", "2026-11-19", news_type="cianova")

    index = common.build_index(str(tmp_path))

    assert index["schema"] == common.SCHEMA_VERSION
    assert index["count"] == 3
    assert [item["id"] for item in index["items"]] == [
        "cianova-v4.0.0",
        "bedrock-26.60",
        "bedrock-26.50",
    ]
    assert all(item["doc"].startswith("news/") for item in index["items"])


def test_build_index_limits_items(tmp_path):
    for day in range(1, 6):
        _write(tmp_path, f"bedrock-26.{day}", f"2026-10-0{day}")
    index = common.build_index(str(tmp_path), limit=3)
    assert index["count"] == 3
    assert len(index["items"]) == 3


def test_build_index_rejects_duplicate_ids(tmp_path):
    _write(tmp_path, "bedrock-26.60", "2026-10-27")
    (tmp_path / "otro.md").write_text(
        "---\nid: \"bedrock-26.60\"\ntype: \"minecraft\"\n"
        "title_es: \"x\"\nsummary_es: \"y\"\npublished: \"2026-10-27\"\n---\n",
        encoding="utf-8",
    )
    with pytest.raises(common.NewsError):
        common.build_index(str(tmp_path))


def test_build_index_ignores_hidden_and_non_markdown(tmp_path):
    _write(tmp_path, "bedrock-26.60", "2026-10-27")
    (tmp_path / ".draft.md").write_text("no importa", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("no importa", encoding="utf-8")
    index = common.build_index(str(tmp_path))
    assert [item["id"] for item in index["items"]] == ["bedrock-26.60"]


def test_build_index_empty_directory(tmp_path):
    index = common.build_index(str(tmp_path))
    assert index["count"] == 0
    assert index["items"] == []


def test_dump_and_load_index_roundtrip(tmp_path):
    _write(tmp_path, "bedrock-26.60", "2026-10-27")
    index = common.build_index(str(tmp_path))
    path = tmp_path / "news.json"
    common.dump_index(index, str(path))

    loaded = common.load_index(str(path))
    assert loaded["items"] == index["items"]
    assert json.loads(path.read_text(encoding="utf-8"))["schema"] == 1
