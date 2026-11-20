import sync_releases as sync


def test_first_paragraph_skips_headings_and_short_lines():
    body = "## Cambios\n\n- uno\n\nEsta es la primera frase útil con longitud suficiente."
    assert sync.first_paragraph(body) == "Esta es la primera frase útil con longitud suficiente."


def test_first_paragraph_truncates_long_text():
    body = "palabra " * 100
    result = sync.first_paragraph(body)
    assert result.endswith("…")
    assert len(result) <= 320


def test_first_paragraph_returns_empty_for_markdown_only():
    assert sync.first_paragraph("## Solo título\n\n- lista\n") == ""


def test_strip_leading_heading_removes_title_repetition():
    body = "# CianovaLauncher 4.0.0\n\nCianovaLauncher 4.0.0\n\nNuevo diseño."
    result = sync.strip_leading_heading(body, "CianovaLauncher 4.0.0")
    assert result == "Nuevo diseño."


def test_strip_leading_heading_without_heading():
    assert sync.strip_leading_heading("Texto plano.", "X") == "Texto plano."
