# # # # #
# Detect text file
# 
# # # # #
# Really simple test to see if any of our trigger phrases are contain in any of the provided stirngs
#
#
def any_text_triggering(strings: list, trigger_phrases:list)-> bool:
    if type(strings) != list: # Type checking
        if(type(strings) == str): # Allowing for singular string checkking
            strings = [strings]
        else:
            raise TypeError("any_text_triggering() was not provided a string or a list")
    strings = set([x.lower() for x in strings]) # Get all unique, lower cases strings
    trigger_phrases = set([x.lower() for x in trigger_phrases]) # same as above
    for phrase in trigger_phrases: # Combinatory checking.
        for string in strings:
            if phrase in string:
                return True
    return False