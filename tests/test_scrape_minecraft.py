import json

import pytest

import scrape_minecraft as scraper


WIKITEXT = """
{{No técnico|ing=1}}
{{Infobox versión
| title = v26.60
| edition = Bedrock
| image = Bedrock 26.60 PatchNotes.jpg
| date = October 27, 2026
}}
'''26.60''', también conocida como '''1.26.60''', es una actualización menor para
''[[Bedrock Edition]]'' que añade cuevas de hielo y varios arreglos.<ref name="a">Nota</ref>
También incluye funciones experimentales del próximo game drop.

== Novedades ==
* Añade [[Carámbano|carámbanos]].
"""


def test_clean_wikitext_removes_templates_refs_and_links():
    text = scraper.clean_wikitext(WIKITEXT)
    assert "Infobox" not in text
    assert "<ref" not in text
    assert "[[" not in text
    assert "'''" not in text
    assert "carámbanos" in text
    assert "cuevas de hielo" in text


def test_wiki_intro_uses_rendered_html(monkeypatch):
    html = """
    <div class="mw-parser-output">
      <p>Windows, Xbox: 1.26.6004.0</p>
      <p>26.60, también conocida como 1.26.60, es una actualización menor para
      Bedrock Edition lanzada el 27 de octubre de 2026, que incorpora funciones
      experimentales del cuarto drop de 2026 y corrige errores.[1]</p>
    </div>
    """
    monkeypatch.setattr(scraper, "_wiki_section_html", lambda version: html)
    intro = scraper.wiki_intro("26.60")
    assert intro.startswith("26.60")
    assert "Bedrock Edition lanzada el 27 de octubre de 2026" in intro
    assert "[1]" not in intro
    assert "Windows" not in intro


def test_wiki_intro_falls_back_to_wikitext(monkeypatch):
    monkeypatch.setattr(scraper, "_wiki_section_html", lambda version: "")
    monkeypatch.setattr(
        scraper,
        "fetch_json",
        lambda url: {"parse": {"wikitext": WIKITEXT}},
    )
    intro = scraper.wiki_intro("26.60")
    assert "cuevas de hielo" in intro


def test_wiki_intro_returns_empty_on_error(monkeypatch):
    def boom(url):
        raise RuntimeError("sin red")

    monkeypatch.setattr(scraper, "fetch_json", boom)
    assert scraper.wiki_intro("26.60") == ""


def test_wiki_intro_returns_empty_without_wikitext(monkeypatch):
    monkeypatch.setattr(scraper, "_wiki_section_html", lambda version: "")
    monkeypatch.setattr(scraper, "fetch_json", lambda url: {"parse": {}})
    assert scraper.wiki_intro("26.60") == ""


def test_trim_sentences_cuts_on_sentence_boundary():
    text = "Primera frase. Segunda frase. Tercera frase."
    assert scraper._trim_sentences(text, 30) == "Primera frase. Segunda frase."


def test_trim_sentences_adds_ellipsis_when_no_boundary():
    text = "una sola frase muy larga sin puntos que se corta por palabras"
    result = scraper._trim_sentences(text, 25)
    assert result.endswith("…")
    assert len(result) <= 26


def test_html_to_markdown_removes_scripts_and_absolutises_images():
    html = (
        "<p>Hola <strong>mundo</strong></p><script>alert(1)</script>"
        '<img src="/v2/images/x.png">'
    )
    markdown = scraper.html_to_markdown(html)
    assert "**mundo**" in markdown
    assert "alert(1)" not in markdown
    assert "https://launchercontent.mojang.com/v2/images/x.png" in markdown


def test_absolute_image_handles_relative_and_empty():
    assert (
        scraper._absolute_image({"image": {"url": "/v2/images/26.60.jpg"}})
        == "https://launchercontent.mojang.com/v2/images/26.60.jpg"
    )
    assert scraper._absolute_image({"image": {"url": "https://x/y.png"}}) == "https://x/y.png"
    assert scraper._absolute_image({}) == ""


def test_version_key_is_numeric():
    versions = ["26.9", "26.60", "26.50", "1.21.90"]
    assert sorted(versions, key=scraper._version_key) == ["1.21.90", "26.9", "26.50", "26.60"]


def test_build_document_uses_fixtures(monkeypatch, fixtures_dir):
    feed = json.load(open(f"{fixtures_dir}/bedrock_patch_notes.json", encoding="utf-8"))
    body = json.load(open(f"{fixtures_dir}/bedrock_body.json", encoding="utf-8"))
    entry = feed["entries"][0]

    monkeypatch.setattr(scraper, "wiki_intro", lambda version: "Resumen en español de la wiki.")
    monkeypatch.setattr(
        scraper,
        "fetch_json",
        lambda url: body,
    )

    meta, document = scraper.build_document(entry)

    assert meta["id"] == f"bedrock-{entry['version']}"
    assert meta["type"] == "minecraft"
    assert meta["summary_es"] == "Resumen en español de la wiki."
    assert meta["image"].startswith("https://launchercontent.mojang.com/")
    assert meta["source"] == "wiki"
    assert "CC BY-NC-SA 3.0" in document
    assert "## Notas de la versión" in document


def test_build_document_falls_back_to_english_summary(monkeypatch, fixtures_dir):
    feed = json.load(open(f"{fixtures_dir}/bedrock_patch_notes.json", encoding="utf-8"))
    body = json.load(open(f"{fixtures_dir}/bedrock_body.json", encoding="utf-8"))
    entry = feed["entries"][0]

    monkeypatch.setattr(scraper, "wiki_intro", lambda version: "")
    monkeypatch.setattr(scraper, "fetch_json", lambda url: body)

    meta, _ = scraper.build_document(entry)

    assert meta["source"] == "mojang"
    assert meta["summary_en"]
    assert meta["summary_es"] == meta["summary_en"]


def test_existing_versions_reads_bedrock_files(tmp_path):
    (tmp_path / "bedrock-26.60.md").write_text("x", encoding="utf-8")
    (tmp_path / "cianova-x.md").write_text("x", encoding="utf-8")
    assert scraper.existing_versions(str(tmp_path)) == {"26.60"}
