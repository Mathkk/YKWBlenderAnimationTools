import bpy

# Script by Math_kk | Discord: oisouomatho

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
                action_start = int(action.frame_range[0])
                action_end = int(action.frame_range[1])
                action_duration = action_end - action_start

                for fcurve in action.fcurves:
                    new_fcurve = merged_action.fcurves.find(fcurve.data_path, index=fcurve.array_index)
                    if not new_fcurve:
                        new_fcurve = merged_action.fcurves.new(data_path=fcurve.data_path, index=fcurve.array_index)

                    for keyframe in fcurve.keyframe_points:
                        # Ajusta o tempo do keyframe em relação ao novo ponto de início
                        frame_offset = keyframe.co[0] - action_start
                        new_frame = current_frame + frame_offset
                        new_keyframe = new_fcurve.keyframe_points.insert(new_frame, keyframe.co[1])
                        new_keyframe.interpolation = keyframe.interpolation

                start_frame = current_frame
                end_frame = current_frame + action_duration
                log.append(f"{action_name.strip()}: Start Frame = {start_frame}, End Frame = {end_frame}")

                # Avança para o próximo espaço disponível, pulando 1 frame
                current_frame = end_frame + 2  # +1 para terminar, +1 para pular um frame

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
