import bpy

#Script by Math_kk | Discord: oisouomatho

class MergeAnimationsPanel(bpy.types.Panel):
    bl_label = "Yo-kai Watch Animations Merger"
    bl_idname = "OBJECT_PT_merge_animations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "actions_to_merge")
        layout.operator("object.merge_animations")

class MergeAnimationsOperator(bpy.types.Operator):
    bl_idname = "object.merge_animations"
    bl_label = "Merge Animations"

    def execute(self, context):
        scene = context.scene
        actions_to_merge = scene.actions_to_merge.split(',')

        merged_action = bpy.data.actions.new(name="out_00")
        current_frame = 0
        log = []

        for action_name in actions_to_merge:
            action = bpy.data.actions.get(action_name.strip())
            if action:
                for fcurve in action.fcurves:
                    # Verifica se a F-Curve já existe
                    new_fcurve = merged_action.fcurves.find(fcurve.data_path, index=fcurve.array_index)
                    if not new_fcurve:
                        new_fcurve = merged_action.fcurves.new(data_path=fcurve.data_path, index=fcurve.array_index)
                    for keyframe in fcurve.keyframe_points:
                        new_keyframe = new_fcurve.keyframe_points.insert(current_frame + keyframe.co[0], keyframe.co[1])
                        new_keyframe.interpolation = keyframe.interpolation
                start_frame = current_frame
                end_frame = current_frame + action.frame_range[1] - action.frame_range[0]
                log.append(f"{action_name}: Start Frame = {start_frame}, End Frame = {end_frame}")
                current_frame = end_frame + 1

        bpy.context.object.animation_data.action = merged_action

        for entry in log:
            self.report({'INFO'}, entry)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(MergeAnimationsPanel)
    bpy.utils.register_class(MergeAnimationsOperator)
    bpy.types.Scene.actions_to_merge = bpy.props.StringProperty(
        name="Actions to Merge",
        description="Comma-separated list of actions to merge",
        default=""
    )

def unregister():
    bpy.utils.unregister_class(MergeAnimationsPanel)
    bpy.utils.unregister_class(MergeAnimationsOperator)
    del bpy.types.Scene.actions_to_merge

if __name__ == "__main__":
    register()
