#!/usr/bin/env python

import yaml
import collections
import re

# https://stackoverflow.com/a/21912744/1831350
from collections import OrderedDict
def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

main = []
with open("languages.yaml", 'r') as inStream:
    data = yaml.load(inStream)
    allMarkers = set()

    for item in data["languages"]:
        allMarkers.update(set(item["markers"]))

    otherLanguages = '|'.join([re.escape(x) for x in allMarkers])

    # TODO add 'plain(text)?' ??
    otherLanguageStart = '^(?=\s*//\s*(?i)('+otherLanguages+')$)'

    for item in data["languages"]:
        uniqueMarkers = set(item["markers"])
        markers = '|'.join([re.escape(x) for x in uniqueMarkers])
        match = '{{comment}}(?i)('+ markers +')$'

        rule = collections.OrderedDict()
        rule['match'] = match
        rule['scope'] = 'comment.line'
        rule['captures'] = {1 : 'meta.separator'}
        rule['push'] = item["push"]

        prototype = [collections.OrderedDict()]
        prototype[0]['match'] = otherLanguageStart
        prototype[0]['pop'] = True

        rule['with_prototype'] = prototype
        main.append(rule)

        if not item.get("shebang"):
            continue

        import copy
        rule = copy.deepcopy(rule)
        rule['match'] = '^#!/.*(?i)(' + markers + ')'
        main.append(rule)

    contexts = { "main" : main }
    data = collections.OrderedDict()

    data["name"] = "Multi Language"
    data["file_extensions"] = ["untitled"]
    data["scope"] = 'source.multi'
    data["uuid"] = 'BB3B672F-2ABB-496E-9D19-E9F1C3F082D1'
    data["variables"] = { "comment": '^\s*//\s*(?i)' }
    data["contexts"] = contexts

    with open("MultiSyntax.sublime-syntax", 'w') as outStream:
        print ordered_dump(data, outStream, default_flow_style=False, explicit_start=True, version=(1,2))
