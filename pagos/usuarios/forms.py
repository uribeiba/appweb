from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, Contrato, Servicio, Zona, DireccionInstalacion, Pago


### 🔹 FORMULARIO CLIENTE ###
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


### 🔹 FORMULARIO DIRECCIÓN ###
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


### 🔹 FORMULARIO CONTRATO ###
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

    dia_pago = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 31)],
        required=False,
        label="Día de pago",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    direccion_instalacion = forms.ModelChoiceField(
        queryset=DireccionInstalacion.objects.none(),  # Se actualizará en __init__
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

    def __init__(self, *args, cliente_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Carga direcciones según cliente seleccionado
        if cliente_id:
            self.fields['direccion_instalacion'].queryset = DireccionInstalacion.objects.filter(cliente_id=cliente_id)
        else:
            self.fields['direccion_instalacion'].queryset = DireccionInstalacion.objects.none()

        # Cargar los servicios con sus precios como atributos en el HTML
        self.fields['servicios'].queryset = Servicio.objects.all()
        for servicio in self.fields['servicios'].queryset:
            self.fields['servicios'].widget.attrs.update({
                f'data-precio-{servicio.pk}': servicio.precio
            })


### 🔹 FORMULARIO SERVICIO ###
class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }



# Definir las opciones de meses con nombres
MESES_CHOICES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
]

class PagoForm(forms.ModelForm):
    mes_pagado = forms.ChoiceField(choices=MESES_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Pago
        fields = ['contrato', 'mes_pagado', 'anio_pagado', 'monto', 'forma_pago', 'numero_boleta']
        widgets = {
            'contrato': forms.Select(attrs={'class': 'form-control'}),
            'anio_pagado': forms.NumberInput(attrs={'class': 'form-control', 'min': '2000', 'max': '2100'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'numero_boleta': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, cliente_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente_id:
            self.fields['contrato'].queryset = Contrato.objects.filter(cliente_id=cliente_id)
        else:
            self.fields['contrato'].queryset = Contrato.objects.none()

    def clean_contrato(self):
        contrato = self.cleaned_data.get('contrato')
        if not contrato:
            raise forms.ValidationError("Debe seleccionar un contrato válido.")
        return contrato