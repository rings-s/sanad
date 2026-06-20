from base.search import normalize_arabic


class TestNormalizeArabic:
    """normalize_arabic must keep Arabic letters while folding marks/variants.

    Regression guard for the bug where the diacritics character class spanned
    the Arabic letter block and reduced every Arabic string to ''.
    """

    def test_keeps_letters_after_stripping_tashkeel(self):
        assert normalize_arabic('السَّلامُ عليكُم') == 'السلام عليكم'

    def test_arabic_text_does_not_become_empty(self):
        for text in ('القرآن', 'محمد', 'الصلاة', 'رمضان', 'الحديث الشريف'):
            assert normalize_arabic(text).strip(), f'{text!r} normalized to empty'

    def test_strips_tatweel(self):
        assert normalize_arabic('رمضــــان') == 'رمضان'

    def test_folds_alef_and_taa_marbuta_variants(self):
        assert normalize_arabic('إسلام') == normalize_arabic('اسلام')
        assert normalize_arabic('مكة') == 'مكه'

    def test_lowercases_and_collapses_whitespace(self):
        assert normalize_arabic('  Hello   WORLD  ') == 'hello world'

    def test_empty_and_none(self):
        assert normalize_arabic('') == ''
        assert normalize_arabic(None) == ''
