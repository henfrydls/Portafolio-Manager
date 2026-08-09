"""
Simple utility to compile .po files to .mo files without requiring gettext tools.
This is a basic implementation for development purposes.
"""

import os
import struct
import array
from pathlib import Path


def compile_po_to_mo(po_file_path, mo_file_path):
    """
    Compile a .po file to .mo file format.
    This is a simplified implementation that handles basic cases.
    """
    translations = {}

    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse .po file
    lines = content.split('\n')
    msgid = None
    msgstr = None
    in_msgid = False
    in_msgstr = False

    for line in lines:
        line = line.strip()

        if line.startswith('msgid "'):
            if msgid is not None and msgstr is not None:
                translations[msgid] = msgstr
            msgid = line[7:-1]  # Remove 'msgid "' and ending '"'
            in_msgid = True
            in_msgstr = False
        elif line.startswith('msgstr "'):
            msgstr = line[8:-1]  # Remove 'msgstr "' and ending '"'
            in_msgid = False
            in_msgstr = True
        elif line.startswith('"') and line.endswith('"'):
            if in_msgid and msgid is not None:
                msgid += line[1:-1]
            elif in_msgstr and msgstr is not None:
                msgstr += line[1:-1]
        elif line == '':
            if msgid is not None and msgstr is not None:
                translations[msgid] = msgstr
            msgid = None
            msgstr = None
            in_msgid = False
            in_msgstr = False

    # Add the last translation if exists
    if msgid is not None and msgstr is not None:
        translations[msgid] = msgstr

    # Remove empty translations (but keep the header entry with empty msgid)
    translations = {k: v for k, v in translations.items() if k or (k == "" and v)}

    # Unescape the PO string escape sequences (\\, \", \n, \t) in a single
    # left-to-right pass. A pass is required (rather than sequential
    # str.replace calls) so that, for example, a literal "\\n" (backslash
    # followed by the two characters n) is not mistaken for an escaped
    # newline, and so a backslash produced by unescaping "\\\\" doesn't get
    # reinterpreted by a later replacement.
    def unescape_po_string(s):
        result = []
        i = 0
        length = len(s)
        while i < length:
            ch = s[i]
            if ch == '\\' and i + 1 < length:
                next_ch = s[i + 1]
                if next_ch == 'n':
                    result.append('\n')
                    i += 2
                    continue
                elif next_ch == 't':
                    result.append('\t')
                    i += 2
                    continue
                elif next_ch == '"':
                    result.append('"')
                    i += 2
                    continue
                elif next_ch == '\\':
                    result.append('\\')
                    i += 2
                    continue
            result.append(ch)
            i += 1
        return ''.join(result)

    translations = {unescape_po_string(k): unescape_po_string(v) for k, v in translations.items()}

    # Create .mo file
    keys = sorted(translations.keys())
    values = [translations[k] for k in keys]

    # Build the MO file
    koffsets = []
    voffsets = []
    kencoded = []
    vencoded = []

    for k, v in zip(keys, values):
        kencoded.append(k.encode('utf-8'))
        vencoded.append(v.encode('utf-8'))

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart
    for k in kencoded:
        valuestart += len(k)

    koffsets = []
    voffsets = []

    offset = keystart
    for k in kencoded:
        koffsets.append((len(k), offset))
        offset += len(k)

    offset = valuestart
    for v in vencoded:
        voffsets.append((len(v), offset))
        offset += len(v)

    # Generate the .mo file
    with open(mo_file_path, 'wb') as f:
        # Magic number
        f.write(struct.pack('<I', 0x950412de))
        # Version
        f.write(struct.pack('<I', 0))
        # Number of strings
        f.write(struct.pack('<I', len(keys)))
        # Offset of key table
        f.write(struct.pack('<I', 7 * 4))
        # Offset of value table
        f.write(struct.pack('<I', 7 * 4 + 8 * len(keys)))
        # Hash table size
        f.write(struct.pack('<I', 0))
        # Offset of hash table
        f.write(struct.pack('<I', 0))

        # Key table
        for length, offset in koffsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))

        # Value table
        for length, offset in voffsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))

        # Keys
        for k in kencoded:
            f.write(k)

        # Values
        for v in vencoded:
            f.write(v)

        # Add a null terminator to ensure gettext doesn't complain about end-of-file
        f.write(b'\x00')


def compile_all_translations():
    """Compile all .po files found in the locale directory."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    locale_dir = base_dir / 'locale'

    if not locale_dir.exists():
        print("No locale directory found")
        return

    for lang_dir in locale_dir.iterdir():
        if lang_dir.is_dir():
            po_file = lang_dir / 'LC_MESSAGES' / 'django.po'
            mo_file = lang_dir / 'LC_MESSAGES' / 'django.mo'

            if po_file.exists():
                try:
                    compile_po_to_mo(po_file, mo_file)
                    print(f"Compiled {po_file} -> {mo_file}")
                except Exception as e:
                    print(f"Error compiling {po_file}: {e}")


if __name__ == '__main__':
    compile_all_translations()