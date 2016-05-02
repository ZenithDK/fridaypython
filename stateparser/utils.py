import re

def remove_comments(text):
    """ remove c-style comments.
        text: blob of text with comments (can include newlines)
        returns: text with comments removed
        Borrowed from: http://www.saltycrane.com/blog/2007/11/remove-c-comments-python/
    """
    pattern = r"""
                            ##  --------- COMMENT ---------
           /\*              ##  Start of /* ... */ comment
           [^*]*\*+         ##  Non-* followed by 1-or-more *'s
           (                ##
             [^/*][^*]*\*+  ##
           )*               ##  0-or-more things which don't start with /
                            ##    but do end with '*'
           /                ##  End of /* ... */ comment
         |                  ##  -OR-  various things which aren't comments:
           (                ## 
                            ##  ------ " ... " STRING ------
             "              ##  Start of " ... " string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^"\\]       ##  Non "\ characters
             )*             ##
             "              ##  End of " ... " string
           |                ##  -OR-
                            ##
                            ##  ------ ' ... ' STRING ------
             '              ##  Start of ' ... ' string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^'\\]       ##  Non '\ characters
             )*             ##
             '              ##  End of ' ... ' string
           |                ##  -OR-
                            ##
                            ##  ------ ANYTHING ELSE -------
             .              ##  Anything other char
             [^/"'\\]*      ##  Chars which doesn't start a comment, string
           )                ##    or escape
    """
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    noncomments = [m.group(2) for m in regex.finditer(text) if m.group(2)]

    return "".join(noncomments)

def enum_parser(filename):
    fh = open(filename, "r")
    file_contents = remove_comments("\n".join(fh.readlines()))
    fh.close()
    class EnumClass:
        def __init__(self):
            self.cache_dict = {}

        def get_number(self, identifier):
            return getattr(self, identifier)

        def get_string(self, number):
            if number in self.cache_dict:
                return self.cache_dict[number]
            for k in dir(self):
                if k.startswith("__") and k.endswith("__"):
                    continue
                if getattr(self, k) == number:
                    self.cache_dict[number] = k
                    return k
        def get_all_strings(self):
            all_strings = []
            for k in dir(self):
                if (k.startswith("__") and k.endswith("__")) or k in ["get_number", "get_string", "get_all_strings", "get_all_numbers", "cache_dict"]:
                    continue
                all_strings.append(k)
            return all_strings

        def get_all_numbers(self):
            all_numbers = []
            for k in self.get_all_strings():
                all_numbers.append(getattr(self, k))
            return all_numbers


    return_object = EnumClass()
    all_tokens = re.split("[\s\;,]+", file_contents)

    found_enum = False
    typedef_enum = False
    enum_values = {}
    current_enum_index = 0
    index = 0

    while True:
        try:
            v = all_tokens[index]
        except IndexError:
            break

        if found_enum and v == "}":
            modify_object = return_object
            if typedef_enum:
                enum_name = all_tokens[index+1]
                setattr(modify_object, enum_name, EnumClass())
                modify_object = getattr(modify_object, enum_name)
            # DO shit
            for k in enum_values.keys():
                setattr(modify_object, k, enum_values[k])
            

            found_enum = False
            typedef_enum = False
            index = index + 1
            enum_values = {}
            continue

        if found_enum:
            if all_tokens[index+1] == "=":
                current_enum_index = int(all_tokens[index+2])
                enum_values[v] = current_enum_index
                index = index + 3
            else:
                enum_values[v] = current_enum_index
                index = index + 1
            
            current_enum_index = current_enum_index + 1
            continue


        if v == "enum" or v == "enum{":
            found_enum = True
            if all_tokens[index-1] == "typedef":
                typedef_enum = True
            if v == "enum{":
                index = index + 1
            else:
                index = index + 2
            continue
        index = index + 1

    return return_object

def table_definition_parser(filename, keyword):
    interesting_section = False
    definitions = []

    c_fh = open(filename, "r")

    while True:
        line = c_fh.readline()
        if not line:
            break

        if interesting_section and ("#endif" in line or line.strip() == ""):
            interesting_section = False

        if interesting_section:
            data = re.findall("\([a-zA-Z0-9_, ]+\)", line)
            if len(data) > 0:
                definitions.append(data[0][1:-1].split(",")[0])

        if not interesting_section and "define" in line and keyword in line:
            interesting_section = True

    c_fh.close()
    return definitions

