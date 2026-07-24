import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

// Un componente en Angular es una clase que se le añade un decorador @Component encima.
// El decorador le dice a Angular que esta clase es una pieda de UI.
@Component({
  selector: 'app-root', // Sirve para crear etiquetas, para llamarlo habrá que poner <app-root></app-root> en un HTML
  imports: [RouterOutlet], // Hueco fijo en la pantalla; Angular cambia lo que hay dentro según la URL (como cambiar de canal en la tele)
  templateUrl: './app.html', // Donde se verá el componente
  styleUrl: './app.css' // Donde se podrá editar mi componente
})
export class App {
  protected readonly title = signal('frontend');
}
