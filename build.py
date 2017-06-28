#!/usr/bin/env python

import yaml
import re

def write_rule(stream, match, push, otherLanguageStart, shebangStart):
    stream.write("""\
    - match: '{match}'
      scope: comment.line
      captures:
        '1': meta.separator
      push: '{push}'
      with_prototype:
        - match: '{otherLanguageStart}'
          pop: true
        - match: '{shebangStart}'
          pop: true

""".format(
        match = match,
        push = push,
        otherLanguageStart = otherLanguageStart,
        shebangStart = shebangStart
    ))

with open("MultiSyntax.sublime-syntax", 'w') as outStream:
    outStream.write("""\
%YAML 1.2
---
name: Multi Language
file_extensions: [untitled]
scope: meta.multilang
uuid: BB3B672F-2ABB-496E-9D19-E9F1C3F082D1

variables:
  comment: '^\s*//\s*(?i)'
  # variables are not supported inside `with_prototype`
  # https://github.com/SublimeTextIssues/Core/issues/1488

contexts:
  main:
""")

    with open("languages.yaml", 'r') as inStream:
        main = []
        data = yaml.load(inStream)
        allMarkers = set()
        shebangMarkers = set()
        for item in data["languages"]:
            allMarkers.update(set(item["markers"]))
            if (item.get("shebang")):
                shebangMarkers.update(set(item["markers"]))

        otherLanguages = '|'.join([re.escape(x) for x in allMarkers])
        shebangLanguages = '|'.join([re.escape(x) for x in shebangMarkers])

        otherLanguageStart = r'^(?=//\s*(?i)(' + otherLanguages + r')$)'
        shebangStart = r'^(?=#!/.*\b(?i)(' + shebangLanguages + r')\b)'

        for item in data["languages"]:
            uniqueMarkers = set(item["markers"])
            markers = '|'.join([re.escape(x) for x in uniqueMarkers])
            match = r'{{comment}}(?i)('+ markers + r')$'
            push = item["push"]

            write_rule(outStream, match, push, otherLanguageStart, shebangStart)

            if item.get("shebang"):
                shebang_match = r'^#!/.*\b('+ markers + r')\b'
                outStream.write("    # shebang version\n")
                write_rule(outStream, shebang_match, push, otherLanguageStart, shebangStart)
