import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { UserService } from '../user.service';
import { User } from '../user.model';
import { Button } from "../../shared/button/button";
import { buttonVariantClasses } from '../../shared/button/button-variant';

@Component({
	selector: 'app-user-list',
	imports: [RouterLink, Button], // Para poder usar routerLink en la plantilla ("+ Nuevo usuario", "Editar")
	templateUrl: './user-list.html',
	styleUrl: './user-list.css',
})
// implements OnInit le dice a la clase que hay que tener un método llamado ngOnInit
export class UserList implements OnInit{

	// Variable privada que inyecta la clase UserService que sirve para usar los métodos Http
  private userService = inject(UserService)

  // Ponemos estilos personalizados para los botones de editar y crear usuario
  protected editLinkClasses = 'px-4 py-2 rounded font-medium transition inline-block ' + buttonVariantClasses('secondary');
  protected newUserLinkClasses = 'self-start px-4 py-2 rounded font-medium transition inline-block ' + buttonVariantClasses('primary');

	// Variable que de momento no contiene nada, pero cuando hay cambios se actualiza solo
  users = signal<User[]>([])
  // true mientras la petición está en marcha; empieza en true porque, nada más entrar, ya estamos cargando
  loading = signal(true);
  // Guarda un mensaje de error legible para el usuario; null significa "no hay error"
  error = signal<string | null>(null);

	// Método que se ejecuta solo una vez automáticamente.
	ngOnInit(): void {
		this.loadUsers();
	}

	// Pide al servicio la lista de usuarios y la mete en la cajita users. La usan tanto ngOnInit como onDelete.
  private loadUsers(): void {

    // Antes de pedir los datos, marcamos que estamos cargando y limpiamos cualquier error anterior
    this.loading.set(true);
    this.error.set(null);

	  // Se le pide al servicio que recoja todos los usuarios.
    // Tarda un poco llegar la respuesta
    this.userService.getUsers().subscribe({
      // Aquí dice que cuando hayan llegado los datos sin problemas, los mete en la cajita users
      next: (data) => {
        this.users.set(data);
        this.loading.set(false); // Ya ha llegado la respuesta, dejamos de "cargar"
      },
      // Si algo sale mal, guardamos un mensaje para mostrar en pantalla y también lo sacamos por consola
      error: (err) => {
        this.error.set('No se ha podido cargar la lista de usuarios.');
        this.loading.set(false); // Ya ha llegado la respuesta, dejamos de "cargar"
        console.error('Error al cargar la lista de Usuarios', err);
      }
		});
  }


	// Método que se llama al pulsar "Borrar" en una fila
	onDelete(id: number): void {
		this.userService.deleteUser(id).subscribe({
			// Al borrar con éxito, volvemos a pedir la lista para que la tabla se quede actualizada
			next: () => this.loadUsers(),
			error: (err) => console.error('Error al borrar usuario', err),
		});
	}
}
