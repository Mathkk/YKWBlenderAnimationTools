import bpy

def get_view3d_context():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    return {
                        'window': bpy.context.window,
                        'screen': bpy.context.window.screen,
                        'area': area,
                        'region': region,
                        'scene': bpy.context.scene,
                        'blend_data': bpy.context.blend_data,
                        'view_layer': bpy.context.view_layer,
                    }
    return None


def clean_non_step_keyframes(action, step, start_frame, end_frame):
    valid_frames = set(range(start_frame, end_frame + 1, step))
    for fcurve in action.fcurves:
        to_remove = [i for i, kp in enumerate(fcurve.keyframe_points) if round(kp.co.x) not in valid_frames]
        for i in reversed(to_remove):
            fcurve.keyframe_points.remove(fcurve.keyframe_points[i])
        for kp in fcurve.keyframe_points:
            kp.co.x = round(kp.co.x)
            kp.handle_left.x = round(kp.handle_left.x)
            kp.handle_right.x = round(kp.handle_right.x)


def copy_fcurves(source_action, target_action):
    """Copy all FCurve data from source to target (overwrite)."""
    # Remove all existing FCurves from target
    for fcurve in list(target_action.fcurves):
        target_action.fcurves.remove(fcurve)

    for src_fcurve in source_action.fcurves:
        tgt_fcurve = target_action.fcurves.new(
            data_path=src_fcurve.data_path,
            index=src_fcurve.array_index
        )
        for kp in src_fcurve.keyframe_points:
            new_kp = tgt_fcurve.keyframe_points.insert(frame=kp.co.x, value=kp.co.y)
            new_kp.interpolation = kp.interpolation
            new_kp.handle_left_type = kp.handle_left_type
            new_kp.handle_right_type = kp.handle_right_type
            new_kp.handle_left = kp.handle_left
            new_kp.handle_right = kp.handle_right


def bake_action_in_place(action, rig, step, bake_ctx):
    frames = [kp.co[0] for fcurve in action.fcurves for kp in fcurve.keyframe_points]
    if not frames:
        print(f"⏩ Skipping (no keyframes): {action.name}")
        return

    start_frame = int(min(frames))
    raw_end = int(max(frames))
    end_frame = raw_end + (step - raw_end % step) if raw_end % step != 0 else raw_end

    if not any(fcurve.data_path.startswith("pose") for fcurve in action.fcurves):
        print(f"⏩ Skipping (no pose data): {action.name}")
        return

    # Setup: Assign original action to play
    original_action = rig.animation_data.action
    rig.animation_data.action = action

    # Set up rig for baking
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')

    # NLA strip to evaluate source animation
    nla_track = rig.animation_data.nla_tracks.new()
    nla_track.name = "TempBakeTrack"
    nla_strip = nla_track.strips.new("TempBakeStrip", start_frame, action)
    nla_strip.action_frame_start = start_frame
    nla_strip.action_frame_end = end_frame

    # Bake into temp action
    with bpy.context.temp_override(**bake_ctx):
        bpy.ops.nla.bake(
            frame_start=start_frame,
            frame_end=end_frame,
            only_selected=True,
            visual_keying=True,
            clear_constraints=False,
            use_current_action=False,  # ➜ Let Blender create a new action
            bake_types={'POSE'},
            step=step
        )

    # Blender assigns the baked action to the rig after bake
    baked_action = rig.animation_data.action

    print(f"♻️ Overwriting: {action.name} using baked data from {baked_action.name}")

    # Overwrite original action with baked data
    copy_fcurves(baked_action, action)

    # Clean original action (now contains baked keyframes)
    clean_non_step_keyframes(action, step, start_frame, end_frame)

    # Delete temporary baked action
    bpy.data.actions.remove(baked_action)

    # Restore original state
    rig.animation_data.nla_tracks.remove(nla_track)
    rig.animation_data.action = original_action


def bake_all_actions_in_place(step=2):
    bake_ctx = get_view3d_context()
    if not bake_ctx:
        print("❌ 3D View context not found. Please open a 3D Viewport.")
        return

    rigs = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
    if not rigs:
        print("⚠️ No rigs found in the scene.")
        return

    for action in bpy.data.actions:
        processed = False
        for rig in rigs:
            if rig.animation_data:
                try:
                    bake_action_in_place(action, rig, step, bake_ctx)
                    processed = True
                    break
                except Exception as e:
                    print(f"❌ Error baking {action.name} on {rig.name}: {e}")
        if not processed:
            print(f"⚠️ Skipped: {action.name} (no suitable rig found)")

    print(f"✅ All actions baked in place every {step} frames.")


# 🟢 Run it!
bake_all_actions_in_place(step=2)