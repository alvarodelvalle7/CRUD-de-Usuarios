import { Component, input, output } from '@angular/core';
import { buttonVariantClasses } from './button-variant';

@Component({
  selector: 'app-button',
  imports: [],
  templateUrl: './button.html',
  styleUrl: './button.css',
})
export class Button {

  // Definimos los estilos que puede tener el botón.
  // Por defecto será primary
  variant = input<'primary' | 'secondary' | 'danger'>('primary');

  // Definimos si puede ser un botón que envía un formulario
  // o un botón que edite o borre
  // Por defecto será button
  type = input<'button' | 'submit'>('button');

  // Si está deshabilitado. Por defecto, false.
  disabled = input(false);

  // Define una variable para avisar de que le acaban de pulsar.
  appClick = output<void>();

  // Cambia de estilo de botón dependiendo de lo que haga ese botón.
  protected get variantClasses(): string {
    return buttonVariantClasses(this.variant());
  }
}
