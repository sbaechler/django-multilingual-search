# coding: utf-8
from __future__ import absolute_import, unicode_literals


def get_analyzer_for(language_code, default='snowball'):
    """
    Get the available language analyzer for the given language code or else the default.
    :param language_code: Django language code
    :param default: The analyzer to return if no language analyzer has been found.
                    Defaults to 'snowball'.
    :return: The Haystack language name. E.g. 'german' or the default analyzer
    """
    languages = {
        'ar': 'arabic',
        # '': 'armenian',
        'eu': 'basque',
        'pt-br': 'brazilian',
        'bg': 'bulgarian',
        'ca': 'catalan',
        'zh-hans': 'chinese',
        'zh-hant': 'chinese',
        # 'cjk',
        'cs': 'czech',
        'da': 'danish',
        'nl': 'dutch',
        'en': 'english',
        'fi': 'finnish',
        'fr': 'french',
        'gl': 'galician',
        'de': 'german',
        'el': 'greek',
        'hi': 'hindi',
        'hu': 'hungarian',
        'id': 'indonesian',
        'ga': 'irish',
        'it': 'italian',
        'lv': 'latvian',
        'no': 'norwegian',
        'fa': 'persian',
        'pt': 'portuguese',
        'ro': 'romanian',
        'ru': 'russian',
        # 'sorani',
        'es': 'spanish',
        'sv': 'swedish',
        'tr': 'turkish',
        'th': 'thai'
    }
    if language_code in languages:
        return languages[language_code]
    elif language_code[:2] in languages:
        return languages[language_code[:2]]
    return default
