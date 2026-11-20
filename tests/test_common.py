import json
import os

import pytest

import common


def _meta(**overrides):
    meta = {
        "id": "bedrock-26.60",
        "type": "minecraft",
        "title_es": "Minecraft Bedrock 26.60",
        "title_en": "Minecraft: Bedrock Edition 26.60",
        "summary_es": "Actualización con cuevas de hielo.",
        "summary_en": "Update with ice caves.",
        "published": "2026-10-27",
        "image": "https://launchercontent.mojang.com/v2/images/26.60.jpg",
        "url": "https://es.minecraft.wiki/wiki/Bedrock_Edition_26.60",
        "version": "26.60",
        "source": "wiki",
    }
    meta.update(overrides)
    return meta


def test_document_roundtrip_preserves_quotes_and_newlines(tmp_path):
    meta = _meta(summary_es='Un resumen con "comillas" y : dos puntos')
    body = "# Título\n\nTexto con **negritas**.\n"
    path = tmp_path / "bedrock-26.60.md"

    common.write_document(str(path), meta, body)
    parsed, parsed_body = common.load_document(str(path))

    assert parsed["summary_es"] == meta["summary_es"]
    assert parsed["published"] == "2026-10-27"
    assert parsed_body.strip() == body.strip()


def test_parse_document_rejects_missing_front_matter():
    with pytest.raises(common.NewsError):
        common.parse_document("# sin front matter\n")


def test_parse_document_rejects_unclosed_front_matter():
    with pytest.raises(common.NewsError):
        common.parse_document("---\nid: \"x\"\n\n# body\n")


@pytest.mark.parametrize("news_id", ["bedrock-26.60", "cianova-v4.0.0", "a", "x_1.2"])
def test_validate_id_accepts_safe_values(news_id):
    assert common.validate_id(news_id) == news_id


@pytest.mark.parametrize("news_id", ["", "../evil", "Bedrock", "-start", "a b", "x" * 90])
def test_validate_id_rejects_unsafe_values(news_id):
    with pytest.raises(common.NewsError):
        common.validate_id(news_id)


def test_slugify_strips_accents_and_symbols():
    assert common.slugify("¡Nuevo sistema de perfiles!") == "nuevo-sistema-de-perfiles"
    assert common.slugify("") == "noticia"


def test_build_item_uses_filename_as_id(tmp_path):
    path = tmp_path / "bedrock-26.60.md"
    item = common.build_item(_meta(), "cuerpo", str(path))
    assert item["id"] == "bedrock-26.60"
    assert item["doc"] == "news/bedrock-26.60.md"
    assert item["title"]["es"].startswith("Minecraft")
    assert item["has_doc"] is True


def test_build_item_rejects_filename_mismatch(tmp_path):
    path = tmp_path / "otro.md"
    with pytest.raises(common.NewsError):
        common.build_item(_meta(), "cuerpo", str(path))


def test_build_item_rejects_unknown_type(tmp_path):
    path = tmp_path / "bedrock-26.60.md"
    with pytest.raises(common.NewsError):
        common.build_item(_meta(type="otro"), "", str(path))


def test_build_item_rejects_bad_date(tmp_path):
    path = tmp_path / "bedrock-26.60.md"
    with pytest.raises(common.NewsError):
        common.build_item(_meta(published="27/10/2026"), "", str(path))


def test_build_item_requires_a_title_and_summary(tmp_path):
    path = tmp_path / "bedrock-26.60.md"
    meta = _meta(title_es="", title_en="", summary_es="", summary_en="")
    with pytest.raises(common.NewsError):
        common.build_item(meta, "", str(path))


def test_build_item_falls_back_to_english(tmp_path):
    path = tmp_path / "bedrock-26.60.md"
    meta = _meta()
    meta.pop("title_es")
    meta.pop("summary_es")
    item = common.build_item(meta, "", str(path))
    assert item["title"]["es"] == meta["title_en"]
    assert item["summary"]["es"] == meta["summary_en"]


def test_build_item_omits_empty_optional_fields(tmp_path):
    path = tmp_path / "cianova-x.md"
    meta = _meta(id="cianova-x", type="cianova", image="", url="", version="")
    item = common.build_item(meta, "", str(path))
    assert "image" not in item
    assert "url" not in item
    assert "version" not in item
    assert "has_doc" not in item


def test_render_document_skips_empty_values():
    text = common.render_document({"id": "x", "empty": "", "none": None}, "body")
    assert "empty" not in text
    assert "none" not in text
