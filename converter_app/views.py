from django.shortcuts import render
from .zipCodeDB import STATE_MAPPING, CC_MAPPING, ZIP_CITY
from difflib import get_close_matches


# Create your views here.
def index(request):
    result = None
    not_found = 0
    # Check if request is POST.
    if request.method == 'POST':
        # Get data and selected parser.
        data = request.POST.get('raw_data')
        parser = request.POST.get('parser_select')
        fuzzy = request.POST.get('fuzzy')
        # Depending on the type of parser selected - perform transforms.
        if 'CC-CN' == parser:
            if fuzzy == 'true':
                result, not_found = fuzzy_converter(data, CC_MAPPING)
            else:
                result, not_found = converter(data, CC_MAPPING)
        elif 'SC-SN' == parser:
            if fuzzy == 'true':
                result, not_found = fuzzy_converter(data, STATE_MAPPING)
            else:
                result, not_found = converter(data, STATE_MAPPING)
        elif 'CN-CC' == parser:
            # Flip the keys/values in the dict.
            swap_mapping = {v: k for k, v in CC_MAPPING.items()}
            if fuzzy == 'true':
                result, not_found = fuzzy_converter(data, swap_mapping)
            else:
                result, not_found = converter(data, swap_mapping)
        elif 'SN-SC' == parser:
            swap_mapping = {v: k for k, v in STATE_MAPPING.items()}
            if fuzzy == 'true':
                result, not_found = fuzzy_converter(data, swap_mapping)
            else:
                result, not_found = converter(data, swap_mapping)
        elif 'ZC-CT' == parser:
            if fuzzy == 'true':
                result, not_found = fuzzy_converter(data, ZIP_CITY)
            else:
                result, not_found = converter(data, ZIP_CITY)
        # In case no parser is selected.
        else:
            result = 'Please select the parser type!'
    return render(request, 'index.html', context={'result': result, 'not_found': not_found})


# Handles the conversion itself.
def converter(data, mapping):
    not_found_count = 0
    # Case when new line is a separator.
    if '\n' in data:
        line = data.split('\n')  # Make a list of strings.
        for i in range(len(line)):  # Loop through all the items in the list, make necessary changes.
            # Key to look for.
            key = line[i].upper().strip()
            # In case not found - return 'Unable to find'.
            if not mapping.get(key):
                line[i] = 'UNABLE TO FIND'
                not_found_count += 1
                continue
            # If there is a match for the exact key - get the value here.
            else:
                line[i] = mapping.get(key)
        res = '\n'.join(line)  # Convert to string, separator '\n'
    # When comma is a separator.
    elif ',' in data:
        line = data.split(',')  # Make a list of strings. Separator - ','
        for i in range(len(line)):  # Loop through all the items in the list, make necessary changes.
            # Key to look for.
            key = line[i].upper().strip()
            # In case not found - return 'Unable to find'
            if not mapping.get(key):
                line[i] = 'UNABLE TO FIND'
                not_found_count += 1
                continue
            # If there is a match for the exact key - get the value here.
            else:
                line[i] = mapping.get(key)
        res = ', '.join(line)  # Convert to string, separator ', '
    # When there is only one element.
    elif len(data.split()) == 1 or '' in data:
        # Key to look for.
        key = data.upper().strip()
        # In case not found - return 'Unable to find'.
        if not mapping.get(key):
            not_found_count += 1
            return 'UNABLE TO FIND', not_found_count
        # If there is a match for the exact key - get the value here.
        else:
            res = mapping.get(key)
    else:
        res = 'Only comma and paragraph separated values are supported! Check your input.'
    return res, not_found_count


# Handles the conversion when fuzzy logic is selected.
def fuzzy_converter(data, mapping):
    not_found_count = 0
    if '\n' in data:
        line = data.split('\n')  # Make a list of strings.
        for i in range(len(line)):  # Loop through all the items in the list, make necessary changes.
            # Key to look for.
            key = line[i].upper().strip()
            # Try to look for possible matches.
            close_key = ''.join(get_close_matches(key, mapping, n=1, cutoff=.7))
            # In case not found - return 'Unable to find'.
            if close_key is '' or key.isdigit():
                line[i] = 'UNABLE TO FIND'
                not_found_count += 1
                continue
            # Otherwise - look for value using the key we get above.
            line[i] = mapping.get(close_key)
        res = '\n'.join(line)  # Convert to string, separator '\n'
    # When comma is a separator.
    elif ',' in data:
        line = data.split(',')  # Make a list of strings. Separator - ','
        for i in range(len(line)):  # Loop through all the items in the list, make necessary changes.
            # Key to look for.
            key = line[i].upper().strip()
            # Try to look for possible matches.
            close_key = ''.join(get_close_matches(key, mapping, n=1, cutoff=.7))
            # In case not found - return 'Unable to find'
            if close_key is '' or key.isdigit():
                line[i] = 'UNABLE TO FIND'
                not_found_count += 1
                continue
            # Otherwise - look for value using the key we get above.
            line[i] = mapping.get(close_key)
        res = ', '.join(line)  # Convert to string, separator ', '
    # When there is only one element.
    elif len(data.split()) == 1 or '' in data:
        # Key to look for.
        key = data.upper().strip()
        # Try to look for possible matches.
        close_key = ''.join(get_close_matches(key, mapping, n=1, cutoff=.7))
        # In case not found - return 'Unable to find'.
        if close_key is '' or key.isdigit():
            not_found_count += 1
            return 'UNABLE TO FIND', not_found_count
        # Otherwise - look for value using the key we get above.
        res = mapping.get(close_key)
    else:
        res = 'Only comma and paragraph separated values are supported! Check your input.'
    return res, not_found_count


# Modify the delimiter.
def delimiter_modifier(request):
    result = None
    if request.method == 'POST':
        parser_decode = {'comma': ',', 'tab': '\t', 'space': ' ', 'pipe': '|', 'newline': '\n'}
        # Get data and selected parsers.
        data = request.POST.get('raw_data')
        parser_from = request.POST.get('parser_from')
        parser_to = request.POST.get('parser_to')
        lines = data.split(parser_decode.get(parser_from))
        result = parser_decode.get(parser_to).join(lines)
    return render(request, 'delimiter_mod.html', context={'result': result})


# Modify the case of text.
def case_modifier(request):
    result = None
    if request.method == 'POST':
        result = None
        # Get data and selected parser.
        data = request.POST.get('raw_data')
        parser = request.POST.get('parser_select')

        if parser == 'upper':
            result = data.upper()
        elif parser == 'lower':
            result = data.lower()
        elif parser == 'title':
            result = data.title()

    return render(request, 'case_modifier.html', context={'result': result})
