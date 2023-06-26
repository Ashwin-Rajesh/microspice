
function ret = parse_number(str_inp)
    % Finds the numeric values from strings that include electrical engineers notation
    
    % pattern = '^(?:-)?(?<value>\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(?<prefix>[yzafpnum kMGT]?)(?<unit>[A-Za-z]*)$';
    pattern = '^(?<value>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(?<prefix>[yzafpnum kMGT]?)(?<unit>[A-Za-z]*)$';

    tokens = regexp(str_inp, pattern, 'tokens');

    % If a match is found, convert the value to a double with the correct scaling
    if ~isempty(tokens)
        value   = str2double(tokens{1}{1});
        prefix  = tokens{1}{2};
        unit    = tokens{1}{3};
        % Apply prefix
        if ~isempty(prefix)
            scaling = get_scaling(prefix);
            value = value * scaling;
        end
        % Apply unit transformation to SI units
        if ~isempty(unit)
            value = apply_unit(value, unit);
        end
        ret = value;
    else
        disp("empty")
        ret = NaN;
    end
end

function scaling = get_scaling(prefix)
    % Returns the scaling factor for a given prefix
    switch prefix
        case 'y', scaling = 1e-24;
        case 'z', scaling = 1e-21;
        case 'a', scaling = 1e-18;
        case 'f', scaling = 1e-15;
        case 'p', scaling = 1e-12;
        case 'n', scaling = 1e-9;
        case 'u', scaling = 1e-6;
        case 'm', scaling = 1e-3;
        case 'c', scaling = 1e-2;
        case 'd', scaling = 1e-1;
        case 'k', scaling = 1e3;
        case 'M', scaling = 1e6;
        case 'G', scaling = 1e9;
        case 'T', scaling = 1e12;
        case 'P', scaling = 1e15;
        case 'E', scaling = 1e18;
        case 'Z', scaling = 1e21;
        case 'Y', scaling = 1e24;
        otherwise, scaling = 1;
    end
end
function value = apply_unit(value, unit)
    % Applies the unit conversion factor to the value
    switch lower(unit)
        case {'ohm', 'ohms'}, value = value;
        case 'v', value = value;
        case 'a', value = value;
        case 'f', value = value;
        case 'h', value = value;
        case 's', value = value;
        case 'w', value = value;
        case 'j', value = value;
        case 'n', value = value;
        case 'hz', value = value;
        case 'k', value = value * 1e3;
        case {'c', 'degc'}, value = value + 273.15;
        case {'fahrenheit', 'degf'}, value = (value - 32) * 5/9 + 273.15;
        case 'kat', value = value;
        case 'mol', value = value;
        case 'pa', value = value;
        case 'bar', value = value * 1e5;
        case 'psi', value = value * 6.89476e3;
        case {'inhg', 'in hg'}, value = value * 3.38639e3;
        case {'cmhg', 'cm hg'}, value = value * 1.33322e3;
        case {'mmhg', 'mm hg', 'torr'}, value = value * 133.322;
        case 'atm', value = value * 1.01325e5;
        otherwise, value = NaN;
    end
end