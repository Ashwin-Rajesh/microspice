import re
import math

def parse_number(str_inp):
    pattern = r'^(?P<value>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(?P<prefix>[yzafpnum kMGT]?)(?P<unit>[A-Za-z]*)$'
    match = re.match(pattern, str_inp)

    if match:
        value = float(match.group('value'))
        prefix = match.group('prefix')
        unit = match.group('unit')
        
        if prefix:
            scaling = get_scaling(prefix)
            value *= scaling
        
        if unit:
            value = apply_unit(value, unit)
        
        return value
    else:
        print("empty")
        return math.nan

def get_scaling(prefix):
    scaling_dict = {
        'y': 1e-24,
        'z': 1e-21,
        'a': 1e-18,
        'f': 1e-15,
        'p': 1e-12,
        'n': 1e-9,
        'u': 1e-6,
        'm': 1e-3,
        'c': 1e-2,
        'd': 1e-1,
        'k': 1e3,
        'M': 1e6,
        'G': 1e9,
        'T': 1e12,
        'P': 1e15,
        'E': 1e18,
        'Z': 1e21,
        'Y': 1e24,
    }
    return scaling_dict.get(prefix, 1)

def apply_unit(value, unit):
    unit_dict = {
        'ohm': 1,
        'ohms': 1,
        'v': 1,
        'a': 1,
        'f': 1,
        'h': 1,
        's': 1,
        'w': 1,
        'j': 1,
        'n': 1,
        'hz': 1,
        'k': 1e3,
        'c': lambda x: x + 273.15,
        'degc': lambda x: x + 273.15,
        'fahrenheit': lambda x: (x - 32) * 5/9 + 273.15,
        'degf': lambda x: (x - 32) * 5/9 + 273.15,
        'kat': 1,
        'mol': 1,
        'pa': 1,
        'bar': 1e5,
        'psi': 6.89476e3,
        'inhg': 3.38639e3,
        'in hg': 3.38639e3,
        'cmhg': 1.33322e3,
        'cm hg': 1.33322e3,
        'mmhg': 133.322,
        'mm hg': 133.322,
        'torr': 133.322,
        'atm': 1.01325e5,
    }
    if unit.lower() in unit_dict:
        conversion = unit_dict[unit.lower()]
        if callable(conversion):
            return conversion(value)
        else:
            return value * conversion
    else:
        return math.nan
