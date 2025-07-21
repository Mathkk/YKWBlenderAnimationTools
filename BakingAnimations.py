import bpy

# Set your frame range here
start_frame = bpy.context.scene.frame_start
end_frame = bpy.context.scene.frame_end
step = 2  # Bake step size
valid_frames = set(range(start_frame, end_frame + 1, step))

# Iterate over all objects in the scene
for obj in bpy.data.objects:
    # Skip if no animation data
    if not obj.animation_data or not obj.animation_data.action:
        continue

    action = obj.animation_data.action
    print(f"Baking object: {obj.name}, action: {action.name}")

    # Make the object active and selected
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Bake animation
    bpy.ops.nla.bake(
        frame_start=start_frame,
        frame_end=end_frame,
        only_selected=True,
        visual_keying=True,
        clear_constraints=False,
        use_current_action=True,
        bake_types={'POSE'} if obj.type == 'ARMATURE' else {'OBJECT'},
        step=step
    )

    # Remove non-stepped keyframes from the current action
    for fcurve in action.fcurves:
        keyframes_to_remove = [kp.co[0] for kp in fcurve.keyframe_points if int(kp.co[0]) not in valid_frames]
        for frame in keyframes_to_remove:
            fcurve.keyframe_points.remove(next(kp for kp in fcurve.keyframe_points if kp.co[0] == frame))

    print(f"Baked and cleaned action: {action.name} for object: {obj.name}")

print("All animations baked and cleaned.")
