from django.contrib import admin

class AllFieldModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

class MetaInferModelAdmin(admin.ModelAdmin):
    def get_admin_list(self):
        try:
            return self.model.admin_list
        except AttributeError:
            return []
    
    def get_list_display(self, request):
        return self.get_admin_list()

class MetaInferTimestampedModelAdmin(MetaInferModelAdmin):
    def get_list_display(self, request):
        return self.get_admin_list() + ['created', 'modified']

class MyModelAdmin(MetaInferTimestampedModelAdmin):
    """
        Customized AdminModel, has 'created', 'modified' fields
        and also shortcut form widget in case of m2m relationship with intermediary table
    """

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        db = kwargs.get('using')

        if db_field.name == self.__class__.M2M_WIDGET_FIELD:
            kwargs['widget'] = admin.widgets.FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        if 'queryset' not in kwargs:
            queryset = self.__class__.M2M_OTHER_MODEL.objects.all()
            if queryset is not None:
                kwargs['queryset'] = queryset
        form_field = db_field.formfield(**kwargs)
        msg = 'Hold down “Control”, or “Command” on a Mac, to select more than one.'
        help_text = form_field.help_text
        form_field.help_text = (
            format_lazy('{} {}', help_text, msg) if help_text else msg
        )
        return form_field