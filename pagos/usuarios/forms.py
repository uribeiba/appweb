from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, Contrato, Servicio, Zona, DireccionInstalacion

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get("numero_documento")
        cliente_id = self.instance.pk  # Obtener el ID del cliente si es edición

        # Verificar si el número de documento ya existe en otro cliente
        if Cliente.objects.exclude(pk=cliente_id).filter(numero_documento=numero_documento).exists():
            raise forms.ValidationError("Este número de documento ya está registrado.")

        return numero_documento


class DireccionForm(forms.ModelForm):
    class Meta:
        model = DireccionInstalacion
        fields = ['zona', 'direccion']
        widgets = {
            'direccion': forms.TextInput(attrs={'placeholder': 'Ej: Calle 123, Edificio A'}),
        }


DireccionFormSet = inlineformset_factory(
    Cliente,
    DireccionInstalacion,
    form=DireccionForm,
    extra=1,  # Número mínimo de direcciones a mostrar
    can_delete=True
)

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['cliente', 'direccion', 'fecha_inicio', 'fecha_fin', 'monto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializa el campo de dirección si ya hay un cliente seleccionado
        if self.instance and self.instance.cliente:
            self.fields['direccion'].initial = self.instance.cliente.direccion
    class Meta:
        model = Contrato
        fields = ['cliente', 'direccion', 'fecha_inicio', 'fecha_fin', 'monto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializa el campo de dirección si ya hay un cliente seleccionado
        if self.instance and self.instance.cliente:
            self.fields['direccion'].initial = self.instance.cliente.direccion
    servicios = forms.ModelMultipleChoiceField(
        queryset=Servicio.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        label="Servicios contratados"
    )

    fecha_contratacion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de contratación"
    )

    # Nuevo campo para seleccionar el día de pago (del 1 al 30)
    dia_pago = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 31)],
        required=False,
        label="Día de pago",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    direccion_instalacion = forms.ModelChoiceField(
        queryset=DireccionInstalacion.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Dirección de instalación"
    )

    class Meta:
        model = Contrato
        fields = [
            'cliente', 'direccion_instalacion', 'numero_abonado', 
            'fecha_contratacion', 'dia_pago', 'dias_gracia', 
            'servicios', 'descripcion'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'numero_abonado': forms.TextInput(attrs={'class': 'form-control'}),
            'dias_gracia': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        super().__init__(*args, **kwargs)
        
        # Carga direcciones según cliente seleccionado
        if cliente_id:
            self.fields['direccion_instalacion'].queryset = DireccionInstalacion.objects.filter(cliente_id=cliente_id)
        else:
            self.fields['direccion_instalacion'].queryset = DireccionInstalacion.objects.none()

        # Aquí añadimos el precio de cada servicio como atributo personalizado
        self.fields['servicios'].queryset = Servicio.objects.all()
        for servicio in self.fields['servicios'].queryset:
            self.fields['servicios'].widget.attrs.update({
                f'data-precio-{servicio.pk}': servicio.precio
            })


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }