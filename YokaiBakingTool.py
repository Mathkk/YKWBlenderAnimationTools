import bpy

step = 2

# Collect only objects with armature/rig
rigs = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']

# Suffixes that should not be looped
no_loop_suffixes = ("_wii", "_sti", "_hpi", "_ati", "_wci", "_adl", "_dmi", "_dei", "_del", "_spi", "_spo")

for action in bpy.data.actions:
    # Get actual keyframe frames of this action
    action_frames = [kp.co[0] for fcurve in action.fcurves for kp in fcurve.keyframe_points]
    if not action_frames:
        print(f"Skipped (no keyframes): {action.name}")
        continue

    start_frame = int(min(action_frames))
    end_frame = int(max(action_frames))
    valid_frames = set(range(start_frame, end_frame + 1, step))

    processed = False

    for obj in rigs:
        if not obj.animation_data:
            continue

        # Force the current action on this rig
        original_action = obj.animation_data.action
        obj.animation_data.action = action

        # Only process if it has pose curves
        if not any(fcurve.data_path.startswith("pose") for fcurve in action.fcurves):
            obj.animation_data.action = original_action
            continue

        print(f"Baking: {action.name} on {obj.name} (frames {start_frame}-{end_frame})")

        # Select only the current object
        for o in bpy.context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Perform the bake
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

        # Remove keyframes outside of step
        for fcurve in action.fcurves:
            keyframes_to_remove = [kp.co[0] for kp in fcurve.keyframe_points if int(kp.co[0]) not in valid_frames]
            for frame in keyframes_to_remove:
                fcurve.keyframe_points.remove(next(kp for kp in fcurve.keyframe_points if kp.co[0] == frame))

        # Ensure loop (skip if suffix matches no_loop_suffixes)
        if not any(action.name.lower().endswith(suffix) for suffix in no_loop_suffixes):
            for fcurve in action.fcurves:
                first_val = fcurve.evaluate(start_frame)
                fcurve.keyframe_points.insert(end_frame + 1, first_val, options={'FAST'})
            print(f"Looped: {action.name}")
        else:
            print(f"Skipped looping: {action.name}")

        obj.animation_data.action = original_action
        processed = True
        break

    if not processed:
        print(f"Skipped: {action.name} (no suitable rig found)")

print("✅ All actions baked, cleaned, and looped (except excluded suffixes).")
