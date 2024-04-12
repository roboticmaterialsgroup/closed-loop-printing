""" 
Extract contour from the gcode file

This file extracts the absolute coordinates of each component of the print,
keeping the external perimeter for ironing.
"""

import matplotlib.pyplot as plt
def get_layer_coordinates(gcode_path, target_layer = 1, target_type = 2):
    # get the number of layers
    num_layer = 0
    # type of layer (1: Perimeter, 2: External Perimeter, 3: Overhang perimeter, 4: Internal infill, 5: Solid infill, 6: Top solid infill,
    # 7: Bridge infill, 8: Skirt/Brim, 9: Custom)
    layer_type = 0
    layer_number_list = []
    layer_type_list = []
    layer_code_list = []
    z_val_dict = {}

    # Gcode parsing linking each line to layer number and layer type
    with open(gcode_path, 'r') as f:
        for line in f.readlines():
            # ignore empty & comments line
            if line == '\n' or line.startswith(';'):
                pass     
            else:
                layer_number_list.append(num_layer)
                layer_type_list.append(layer_type)
                layer_code_list.append(line.strip())
            
            # set layer type and layer number with comments
            if line.strip() == ";LAYER_CHANGE":
                num_layer += 1
                layer_type = 0
            elif line.strip().startswith(";Z:"): 
                z_val_dict[num_layer] = float(line.strip()[3:])
            elif line.strip() == ";TYPE:Perimeter":
                layer_type = 1
            elif line.strip() == ";TYPE:External perimeter":
                layer_type = 2
            elif line.strip() == ";TYPE:Overhang perimeter":
                layer_type = 3
            elif line.strip() == ";TYPE:Internal infill":
                layer_type = 4
            elif line.strip() == ";TYPE:Solid infill":
                layer_type = 5
            elif line.strip() == ";TYPE:Top solid infill":
                layer_type = 6
            elif line.strip() == ";TYPE:Bridge infill":
                layer_type = 7
            elif line.strip() == ";TYPE:Skirt/Brim":
                layer_type = 8
            elif line.strip() == ";TYPE:Custom":
                layer_type = 9
            
    # Gcode parsing for plane coordinates
    X_external_perimeter = []
    Y_external_perimeter = []


    shape_list_X = []
    shape_list_Y = []
    z_val = 0

    for i in range(len(layer_number_list)):
        # break if layer is over
        if layer_number_list[i] > target_layer:
            break
        # if target layer and type is found
        if layer_number_list[i] == target_layer and layer_type_list[i] == target_type:
            z_val = z_val_dict.get(layer_number_list[i])
            line = layer_code_list[i]
            if line.split(" ")[-1][0] == 'E':
                for ele in line.split(" "):
                    if ele[0] == "X":
                        X_external_perimeter.append(float(ele[1:]))
                    elif ele[0] == "Y":
                        Y_external_perimeter.append(float(ele[1:]))
            elif line.startswith("M"):
                pass
            elif line.split(" ")[1][0] == 'F':
                pass
            else:
                if len(X_external_perimeter) != 0:
                    X_external_perimeter.append(X_external_perimeter[0])
                    Y_external_perimeter.append(Y_external_perimeter[0])
                shape_list_X.append(X_external_perimeter)
                shape_list_Y.append(Y_external_perimeter)
                X_external_perimeter = []
                Y_external_perimeter = []
    shape_list_X.append(X_external_perimeter)
    shape_list_Y.append(Y_external_perimeter)

    def remove_empty_lists(input_list):
        output_list = [sublist for sublist in input_list if sublist]
        return output_list

    shape_list_X = remove_empty_lists(shape_list_X)
    shape_list_Y = remove_empty_lists(shape_list_Y)

    return shape_list_X, shape_list_Y, z_val
