""" 
Add nozzle movement for taking picture

This file edits the parsed g-code file by adding lines of 
Gcode for nozzle movement to predetermined camera position.
"""

import os 

def add_nozzle_movement(directory_path, X, Y):
    retract_line = "G1 E-1."
    line_to_add = "G1 X{} Y{} F9000".format(X, Y)

    for filename in os.listdir(directory_path):
        if filename.endswith(".gcode") and filename != "end.gcode" and filename != "layer_0.gcode": 
            file_path = os.path.join(directory_path, filename)
            
            # Open the file in append mode
            with open(file_path, 'a') as file:
                # Write the line to the file
                file.write('\n' + retract_line + '\n')
                file.write(line_to_add + '\n')

