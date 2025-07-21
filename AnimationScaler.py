import bpy

# Multiplier to speed up animation
speed_multiplier = 2.0  # 2x faster

# Go through all actions in the file
for action in bpy.data.actions:
    print(f"Processing action: {action.name}")
    
    for fcurve in action.fcurves:
        for keyframe in fcurve.keyframe_points:
            # Scale frame position
            new_x = keyframe.co.x / speed_multiplier
            
            # Round to nearest whole number
            rounded_x = round(new_x)
            
            # Update keyframe and its handles
            keyframe.co.x = rounded_x
            keyframe.handle_left.x = rounded_x
            keyframe.handle_right.x = rounded_x

    print(f"Action '{action.name}' sped up by {speed_multiplier}x and keyframes snapped to whole frames.")

print("All animations processed.")
