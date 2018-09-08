import re

context_regex = re.compile('\[.*?\]')

def removeContext(line):
    return re.sub(context_regex, '', line)
