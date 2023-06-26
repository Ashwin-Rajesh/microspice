function main(file_name)
    close all

    disp("Reading file...")
    p = parser.parser;
    ret = p.read(file_name);
    if(ret.level())
        disp("ERROR : " + ret.to_str());
        return;
    end

    disp("Parsing...")
    ret = p.parse();
    if(ret.level())
        disp("ERROR : " + ret.to_str());
        return;
    end

    for i = 1:numel(p.envs)
        
        e = p.envs(i);
        
        disp("Solving alternative " + i)
        
        figure
        p.eng.set_env(e);
        result = p.eng.run();
        hold on;
        
        title('Transient simulation result ' + string(i));
        ylabel('Voltage (V)'); 
        xlabel('Time (s)'); 

        disp("DC operating point");
        for o = result.keys
            if(o{1} ~= "time")
                data = result(o{1});
                plot(result("time"), data, 'DisplayName', "V(" + o{1} + ")")
                disp("V(" + o{1} + ") : " + data(1))
            end
        end
        
        legend;
        hold off;
        
        shg;
    end
end
