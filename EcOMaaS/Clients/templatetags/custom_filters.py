from django import template
import math
from hashlib import sha256
import sys
import os
register = template.Library() # Register the template library to use the filters

#use tags to create custom filters for the templates

@register.filter # Register the filter
def divide(value, arg): # Divide the value by the argument
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None
    
@register.filter 
def roundGB(value): # Round the value to the nearest GB and return it as a string with the right suffix
    a = 0
    while value > 1024: # While the value is bigger than 1024
        suffixes = ('KiB', 'GiB', 'TiB') # Suffixes for the value
        a += 1 #This will go up the suffixes tuple with each division
        value = value / 1024 # Divide the value by 1024 to get the next suffix
    return (str(math.ceil(value)) + " " + suffixes[a]) # Return the rounded value and the suffix

@register.filter 
def name(value): # Capitalize the first letter of the value 
    dist = value.split("-") # Split the value by the "-" character
    string = "" # Create an empty string
    if len(dist) == 0: # If the length of the value is 0
        return "" # Return an empty string
    for i in dist: # Loop through the value
        i = str(i).capitalize()     # Capitalize the first letter of the value
        string += i + " " # Add the value to the string
    return string # Return the string