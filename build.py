#!/usr/bin/env python

import yaml
import re

def write_syntax_start(stream):
    stream.write("""\
%YAML 1.2
---
name: Multi Language
file_extensions: [untitled]
scope: meta.multilang
uuid: BB3B672F-2ABB-496E-9D19-E9F1C3F082D1

variables:
  comment: '^\s*//\s*?(?i)'

contexts:
""")

def write_prototype_context(stream, contextName, otherLanguageStart, shebangStart):
    stream.write("""\
  {contextName}:
    - match: '{otherLanguageStart}'
      pop: true
    - match: '{shebangStart}'
      pop: true

""".format(**locals()))

def write_rule(stream, otherLanguageStartRuleName, match, push):
    stream.write("""\
    - match: '{match}'
      scope: comment.line
      captures:
        '1': meta.separator
      push: '{push}'
      with_prototype:
        - include: {otherLanguageStartRuleName}

""".format(**locals()))

with open("MultiSyntax.sublime-syntax", 'w') as outStream:
    write_syntax_start(outStream)

    with open("languages.yaml", 'r') as inStream:
        main = []
        data = yaml.load(inStream)
        allMarkers = set()
        shebangMarkers = set()
        for item in data["languages"]:
            allMarkers.update(set(item["markers"]))
            if (item.get("shebang")):
                shebangMarkers.update(set(item["markers"]))

        otherLanguageStartRuleName = 'otherLanguageStart'
        otherLanguages = '|'.join([re.escape(x) for x in allMarkers])
        shebangLanguages = '|'.join([re.escape(x) for x in shebangMarkers])

        otherLanguageStart = r'^(?={{comment}}(?i)(' + otherLanguages + r')$)'
        shebangStart = r'^(?=#!/.*\b(?i)(' + shebangLanguages + r')\b)'

        write_prototype_context(outStream, otherLanguageStartRuleName, otherLanguageStart, shebangStart)
        outStream.write("  main:\n")
        for item in data["languages"]:
            uniqueMarkers = set(item["markers"])
            markers = '|'.join([re.escape(x) for x in uniqueMarkers])
            match = r'{{comment}}(?i)('+ markers + r')$'
            push = item["push"]

            write_rule(outStream, otherLanguageStartRuleName, match, push)

            if item.get("shebang"):
                shebang_match = r'^#!/.*\b('+ markers + r')\b'
                outStream.write("    # shebang version\n")
                write_rule(outStream, otherLanguageStartRuleName, shebang_match, push)
