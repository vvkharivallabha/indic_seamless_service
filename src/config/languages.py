"""
Language configuration and mappings for Indic-Seamless Service
"""

from enum import Enum
from typing import Dict


class TargetLanguage(str, Enum):
    """
    Supported languages enum for dropdown in FastAPI docs.
    The enum values (what users see in dropdown) are the full language names.
    """
    Afrikaans = "Afrikaans"
    Amharic = "Amharic"
    Modern_Standard_Arabic = "Modern Standard Arabic"
    Moroccan_Arabic = "Moroccan Arabic"
    Egyptian_Arabic = "Egyptian Arabic"
    Assamese = "Assamese"
    North_Azerbaijani = "North Azerbaijani"
    Belarusian = "Belarusian"
    Bengali = "Bengali"
    Bosnian = "Bosnian"
    Bulgarian = "Bulgarian"
    Catalan = "Catalan"
    Cebuano = "Cebuano"
    Czech = "Czech"
    Central_Kurdish = "Central Kurdish"
    Mandarin_Chinese = "Mandarin Chinese"
    Traditional_Chinese = "Traditional Chinese"
    Welsh = "Welsh"
    Danish = "Danish"
    German = "German"
    Greek = "Greek"
    English = "English"
    Estonian = "Estonian"
    Basque = "Basque"
    Finnish = "Finnish"
    French = "French"
    Nigerian_Fulfulde = "Nigerian Fulfulde"
    West_Central_Oromo = "West Central Oromo"
    Irish = "Irish"
    Galician = "Galician"
    Gujarati = "Gujarati"
    Hebrew = "Hebrew"
    Hindi = "Hindi"
    Croatian = "Croatian"
    Hungarian = "Hungarian"
    Armenian = "Armenian"
    Igbo = "Igbo"
    Indonesian = "Indonesian"
    Icelandic = "Icelandic"
    Italian = "Italian"
    Javanese = "Javanese"
    Japanese = "Japanese"
    Kannada = "Kannada"
    Georgian = "Georgian"
    Kazakh = "Kazakh"
    Halh_Mongolian = "Halh Mongolian"
    Khmer = "Khmer"
    Kyrgyz = "Kyrgyz"
    Korean = "Korean"
    Lao = "Lao"
    Lithuanian = "Lithuanian"
    Ganda = "Ganda"
    Luo = "Luo"
    Standard_Latvian = "Standard Latvian"
    Maithili = "Maithili"
    Malayalam = "Malayalam"
    Marathi = "Marathi"
    Macedonian = "Macedonian"
    Maltese = "Maltese"
    Manipuri = "Manipuri"
    Burmese = "Burmese"
    Dutch = "Dutch"
    Norwegian_Nynorsk = "Norwegian Nynorsk"
    Norwegian_Bokmal = "Norwegian Bokmål"
    Nepali = "Nepali"
    Nyanja = "Nyanja"
    Odia = "Odia"
    Punjabi = "Punjabi"
    Southern_Pashto = "Southern Pashto"
    Western_Persian = "Western Persian"
    Polish = "Polish"
    Portuguese = "Portuguese"
    Romanian = "Romanian"
    Russian = "Russian"
    Santali = "Santali"
    Slovak = "Slovak"
    Slovenian = "Slovenian"
    Shona = "Shona"
    Sindhi = "Sindhi"
    Somali = "Somali"
    Spanish = "Spanish"
    Serbian = "Serbian"
    Swedish = "Swedish"
    Swahili = "Swahili"
    Tamil = "Tamil"
    Telugu = "Telugu"
    Tajik = "Tajik"
    Tagalog = "Tagalog"
    Thai = "Thai"
    Turkish = "Turkish"
    Ukrainian = "Ukrainian"
    Urdu = "Urdu"
    Northern_Uzbek = "Northern Uzbek"
    Vietnamese = "Vietnamese"
    Yoruba = "Yoruba"
    Cantonese = "Cantonese"
    Colloquial_Malay = "Colloquial Malay"
    Zulu = "Zulu"


# Mapping from full language names back to language codes for the model
LANGUAGE_NAME_TO_CODE: Dict[str, str] = {
    "Afrikaans": "afr",
    "Amharic": "amh",
    "Modern Standard Arabic": "arb",
    "Moroccan Arabic": "ary",
    "Egyptian Arabic": "arz",
    "Assamese": "asm",
    "North Azerbaijani": "azj",
    "Belarusian": "bel",
    "Bengali": "ben",
    "Bosnian": "bos",
    "Bulgarian": "bul",
    "Catalan": "cat",
    "Cebuano": "ceb",
    "Czech": "ces",
    "Central Kurdish": "ckb",
    "Mandarin Chinese": "cmn",
    "Traditional Chinese": "cmn_Hant",
    "Welsh": "cym",
    "Danish": "dan",
    "German": "deu",
    "Greek": "ell",
    "English": "eng",
    "Estonian": "est",
    "Basque": "eus",
    "Finnish": "fin",
    "French": "fra",
    "Nigerian Fulfulde": "fuv",
    "West Central Oromo": "gaz",
    "Irish": "gle",
    "Galician": "glg",
    "Gujarati": "guj",
    "Hebrew": "heb",
    "Hindi": "hin",
    "Croatian": "hrv",
    "Hungarian": "hun",
    "Armenian": "hye",
    "Igbo": "ibo",
    "Indonesian": "ind",
    "Icelandic": "isl",
    "Italian": "ita",
    "Javanese": "jav",
    "Japanese": "jpn",
    "Kannada": "kan",
    "Georgian": "kat",
    "Kazakh": "kaz",
    "Halh Mongolian": "khk",
    "Khmer": "khm",
    "Kyrgyz": "kir",
    "Korean": "kor",
    "Lao": "lao",
    "Lithuanian": "lit",
    "Ganda": "lug",
    "Luo": "luo",
    "Standard Latvian": "lvs",
    "Maithili": "mai",
    "Malayalam": "mal",
    "Marathi": "mar",
    "Macedonian": "mkd",
    "Maltese": "mlt",
    "Manipuri": "mni",
    "Burmese": "mya",
    "Dutch": "nld",
    "Norwegian Nynorsk": "nno",
    "Norwegian Bokmål": "nob",
    "Nepali": "npi",
    "Nyanja": "nya",
    "Odia": "ory",
    "Punjabi": "pan",
    "Southern Pashto": "pbt",
    "Western Persian": "pes",
    "Polish": "pol",
    "Portuguese": "por",
    "Romanian": "ron",
    "Russian": "rus",
    "Santali": "sat",
    "Slovak": "slk",
    "Slovenian": "slv",
    "Shona": "sna",
    "Sindhi": "snd",
    "Somali": "som",
    "Spanish": "spa",
    "Serbian": "srp",
    "Swedish": "swe",
    "Swahili": "swh",
    "Tamil": "tam",
    "Telugu": "tel",
    "Tajik": "tgk",
    "Tagalog": "tgl",
    "Thai": "tha",
    "Turkish": "tur",
    "Ukrainian": "ukr",
    "Urdu": "urd",
    "Northern Uzbek": "uzn",
    "Vietnamese": "vie",
    "Yoruba": "yor",
    "Cantonese": "yue",
    "Colloquial Malay": "zlm",
    "Zulu": "zul"
}


# Standard mapping from language codes to full names (for backward compatibility)
SUPPORTED_LANGUAGES: Dict[str, str] = {
    'afr': 'Afrikaans',
    'amh': 'Amharic',
    'arb': 'Modern Standard Arabic',
    'ary': 'Moroccan Arabic',
    'arz': 'Egyptian Arabic',
    'asm': 'Assamese',
    'azj': 'North Azerbaijani',
    'bel': 'Belarusian',
    'ben': 'Bengali',
    'bos': 'Bosnian',
    'bul': 'Bulgarian',
    'cat': 'Catalan',
    'ceb': 'Cebuano',
    'ces': 'Czech',
    'ckb': 'Central Kurdish',
    'cmn': 'Mandarin Chinese',
    'cmn_Hant': 'Traditional Chinese',
    'cym': 'Welsh',
    'dan': 'Danish',
    'deu': 'German',
    'ell': 'Greek',
    'eng': 'English',
    'est': 'Estonian',
    'eus': 'Basque',
    'fin': 'Finnish',
    'fra': 'French',
    'fuv': 'Nigerian Fulfulde',
    'gaz': 'West Central Oromo',
    'gle': 'Irish',
    'glg': 'Galician',
    'guj': 'Gujarati',
    'heb': 'Hebrew',
    'hin': 'Hindi',
    'hrv': 'Croatian',
    'hun': 'Hungarian',
    'hye': 'Armenian',
    'ibo': 'Igbo',
    'ind': 'Indonesian',
    'isl': 'Icelandic',
    'ita': 'Italian',
    'jav': 'Javanese',
    'jpn': 'Japanese',
    'kan': 'Kannada',
    'kat': 'Georgian',
    'kaz': 'Kazakh',
    'khk': 'Halh Mongolian',
    'khm': 'Khmer',
    'kir': 'Kyrgyz',
    'kor': 'Korean',
    'lao': 'Lao',
    'lit': 'Lithuanian',
    'lug': 'Ganda',
    'luo': 'Luo',
    'lvs': 'Standard Latvian',
    'mai': 'Maithili',
    'mal': 'Malayalam',
    'mar': 'Marathi',
    'mkd': 'Macedonian',
    'mlt': 'Maltese',
    'mni': 'Manipuri',
    'mya': 'Burmese',
    'nld': 'Dutch',
    'nno': 'Norwegian Nynorsk',
    'nob': 'Norwegian Bokmål',
    'npi': 'Nepali',
    'nya': 'Nyanja',
    'ory': 'Odia',
    'pan': 'Punjabi',
    'pbt': 'Southern Pashto',
    'pes': 'Western Persian',
    'pol': 'Polish',
    'por': 'Portuguese',
    'ron': 'Romanian',
    'rus': 'Russian',
    'sat': 'Santali',
    'slk': 'Slovak',
    'slv': 'Slovenian',
    'sna': 'Shona',
    'snd': 'Sindhi',
    'som': 'Somali',
    'spa': 'Spanish',
    'srp': 'Serbian',
    'swe': 'Swedish',
    'swh': 'Swahili',
    'tam': 'Tamil',
    'tel': 'Telugu',
    'tgk': 'Tajik',
    'tgl': 'Tagalog',
    'tha': 'Thai',
    'tur': 'Turkish',
    'ukr': 'Ukrainian',
    'urd': 'Urdu',
    'uzn': 'Northern Uzbek',
    'vie': 'Vietnamese',
    'yor': 'Yoruba',
    'yue': 'Cantonese',
    'zlm': 'Colloquial Malay',
    'zul': 'Zulu'
} 