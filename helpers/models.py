from django.contrib import admin

class AllFieldModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

class MetaInferModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return self.model.admin_list

class MetaInferTimestampedModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return self.model.admin_list + ('created', 'modified')
