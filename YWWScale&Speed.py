import bpy

# === SETTINGS ===
step = 2
speed_multiplier = 2.0
location_scale = 10.0

pivot_y = bpy.context.scene.cursor.location.y  # Pivot baseado no 3D Cursor, ajuste conforme necessário

rigs = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']

for action in bpy.data.actions:
    print(f"\n🔧 Processing action: {action.name}")

    # Scale location curves simulating Graph Editor scale with pivot
    for fcurve in action.fcurves:
        if fcurve.data_path.endswith("location"):
            for kp in fcurve.keyframe_points:
                old_val = kp.co.y
                new_val = pivot_y + (old_val - pivot_y) * location_scale
                kp.co.y = new_val
                kp.handle_left.y = pivot_y + (kp.handle_left.y - pivot_y) * location_scale
                kp.handle_right.y = pivot_y + (kp.handle_right.y - pivot_y) * location_scale
    print(f" - Location curves scaled by {location_scale}x with pivot {pivot_y}.")

    # Speed up keyframes
    for fcurve in action.fcurves:
        for kp in fcurve.keyframe_points:
            new_x = kp.co.x / speed_multiplier
            rounded_x = round(new_x)
            kp.co.x = rounded_x
            kp.handle_left.x = rounded_x
            kp.handle_right.x = rounded_x
    print(f" - Frames sped up by {speed_multiplier}x (snapped to whole frames).")

    # (Continue bake, cleanup, etc... como no script anterior)

print("\n✅ Finished scaling and speeding up actions.")
