import bpy

start_frame = bpy.context.scene.frame_start
end_frame = bpy.context.scene.frame_end
step = 2
valid_frames = set(range(start_frame, end_frame + 1, step))

# Loop over all actions
for action in bpy.data.actions:
    linked = False

    for obj in bpy.data.objects:
        if not obj.animation_data:
            continue

        original_action = obj.animation_data.action
        obj.animation_data.action = action

        # Only process if action matches the object's rig (pose bones)
        if not any(fcurve.data_path.startswith("pose") for fcurve in action.fcurves):
            obj.animation_data.action = original_action
            continue

        print(f"Baking: {action.name} on object: {obj.name}")

        # Activate and select object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Bake only the pose bones, avoid baking visual transforms
        bpy.ops.nla.bake(
            frame_start=start_frame,
            frame_end=end_frame,
            only_selected=True,
            visual_keying=False,
            clear_constraints=False,
            use_current_action=True,
            bake_types={'POSE'},
            step=step
        )

        # Remove unwanted keyframes not on stepped frames
        for fcurve in action.fcurves:
            keyframes_to_remove = [kp.co[0] for kp in fcurve.keyframe_points if int(kp.co[0]) not in valid_frames]
            for frame in keyframes_to_remove:
                fcurve.keyframe_points.remove(next(kp for kp in fcurve.keyframe_points if kp.co[0] == frame))

        obj.animation_data.action = original_action
        linked = True
        break

    if not linked:
        print(f"Skipped: {action.name} (no matching object found)")

print("All actions baked and cleaned.")