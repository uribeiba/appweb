from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, Contrato, Servicio, Zona, DireccionInstalacion

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'numero_documento',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'correo',
            'sexo',
            'fecha_nacimiento',
            'telefono',
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'sexo': forms.Select(),
        }


class DireccionForm(forms.ModelForm):
    class Meta:
        model = DireccionInstalacion
        fields = ['zona', 'direccion']

DireccionFormSet = inlineformset_factory(
    Cliente,
    DireccionInstalacion,
    form=DireccionForm,
    extra=1,
    can_delete=True
)


class ContratoForm(forms.ModelForm):
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

    dia_pago = forms.IntegerField(
        min_value=1, 
        max_value=31,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese día (1-31)'}),
        label="Día de pago"
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
        instance = kwargs.get('instance', None)  # Obtener la instancia si existe
        cliente_id = kwargs.pop('cliente_id', None)  # Obtener cliente_id si se pasa manualmente
        super().__init__(*args, **kwargs)

        # Si se está editando un contrato, obtener el cliente de la instancia
        if instance and instance.cliente:
            cliente = instance.cliente
        else:
            cliente = self.initial.get('cliente') or cliente_id

        # Si hay un cliente, cargar sus direcciones de instalación
        if cliente:
            self.fields['direccion_instalacion'].queryset = DireccionInstalacion.objects.filter(cliente=cliente)
        else:
            self.fields['direccion_instalacion'].queryset = DireccionInstalacion.objects.none()

        # Añadir el precio de cada servicio como atributo personalizado
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