""" Add nozzle movement for taking picture

This file edits the parsed g-code file by adding lines of 
Gcode for nozzle movement to predetermined camera position.
"""

# gcode_path: layerwise_gcode_file
def generate_iron_layer(gcode_path, output_path, E_proportion = 0.2, S_proportion = 0.6):
    new_gcode_list = []
    gcode = [i.strip() for i in open(gcode_path)]
    for line in gcode:
        if line.startswith(";"):
            pass
        elif ' E' not in line and ' S' not in line:
            new_gcode_list.append(line)
        else:
            original_E = 0
            original_S = 0
            ele_list = line.split(" ")
            for i, ele in enumerate(ele_list):
                if ele.startswith("E"):
                    original_E = round(float(ele[1:]), 3)
                    if (original_E < 0):
                        pass
                    else:
                        new_E = original_E * E_proportion
                        ele_list[i] = "E{}".format(round(new_E, 3))
                elif ele.startswith("S"):
                    original_S = round(float(ele[1:]), 3)
                    if (original_S < 0):
                        pass
                    else:
                        new_S = original_S * S_proportion
                        ele_list[i] = "S{}".format(int(new_S))
            new_line = ' '.join(ele_list)
            new_gcode_list.append(new_line)

    file = open(output_path, "w")
    for line in new_gcode_list:
        file.write(line + "\n")