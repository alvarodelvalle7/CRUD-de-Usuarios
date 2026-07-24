import { UserService } from './../user.service';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Button } from "../../shared/button/button";
import { UserCreate } from '../user.model';

@Component({
  selector: 'app-user-form',
  imports: [ReactiveFormsModule, RouterLink, Button], // Enciende la función de form reactivos para este compomente. Sin esto, formGroup no funcionaría.
  templateUrl: './user-form.html',
  styleUrl: './user-form.css',
})
// Clase para el formulario de creación y edición
// implements OnInit le dice a la clase que hay que tener un método llamado ngOnInit
export class UserForm implements OnInit {
  private formBuilder = inject(FormBuilder); // Herramienta que sirve para crear el form entero de una vez.
  private userService = inject(UserService)
  private router = inject(Router) // Importamos Router para que después podamos redirigirnos a la lista de usuarios.
  private route = inject(ActivatedRoute) // Da acceso a la información de la ruta activa, entre ella, sus parámetros (el :id)

  // Guarda el id del usuario si estamos editando; se queda en null si estamos creando uno nuevo
  protected userId: number | null = null;

  // Nueva variable: true mientras se está guardando (creando o actualizando), para desactivar el botón y evitar doble clic
  protected saving = signal(false);

  // Nueva variable: guarda un mensaje de error legible; null significa "no hay error"
  protected error = signal<string | null>(null);

  // Crea el formulario entero de golpe
  form = this.formBuilder.group({
    name: this.formBuilder.nonNullable.control('', [Validators.required, Validators.minLength(3), Validators.maxLength(100)]),
    age: this.formBuilder.control<number | null>(null, [Validators.required, Validators.min(18)]),
    height: this.formBuilder.control<number | null>(null, [Validators.required, Validators.min(0.01)]),
    weight: this.formBuilder.control<number | null>(null, [Validators.required, Validators.min(0.01)]),
    city: this.formBuilder.nonNullable.control(''),
    is_admin: this.formBuilder.nonNullable.control(false),
  });

  // Método que se ejecuta solo una vez automáticamente, justo al entrar al componente
  ngOnInit(): void {
    // Lee el :id de la URL (una "foto fija" de la ruta, por eso snapshot). Si no hay :id (venimos de /users/new), devuelve null
    const idParam = this.route.snapshot.paramMap.get('id');

    if (idParam) {
      // Convertimos el texto "7" en el número 7, que es lo que espera la API
      this.userId = Number(idParam);

      // Pedimos al servicio los datos de ese usuario para precargar el formulario
      this.userService.getUser(this.userId).subscribe({
        // patchValue solo actualiza los campos que le pasemos, no hace falta pasar todos
        next: (user) => this.form.patchValue(user),
        error: (err) => console.error('Error al cargar usuario', err),
      });
    }
  }

  // Método que se llama para enviar el formulario
  onSubmit(): void {

    // Si se recibe un dato inválido, corta la ejecución
    if (this.form.invalid) {
      return;
    }

    // Se encarga de decir al compilador que esto tiene la forma correcta
    const formValue = this.form.getRawValue() as UserCreate;

    // Antes de lanzar la petición, marcamos que estamos guardando y limpiamos errores anteriores
    this.saving.set(true);
    this.error.set(null);

    // Si userId tiene valor, actualizamos ese usuario; si es null, creamos uno nuevo
    const request$ = this.userId
      ? this.userService.updateUser(this.userId, formValue)
      : this.userService.createUser(formValue);

    request$.subscribe({
      // Al guardar el usuario con éxito, nos lleva de vuelta al listado.
      next: () => this.router.navigate(['/users']),
      // Si falla, mostramos un mensaje en pantalla y dejamos de estar "guardando" para reactivar el botón
      error: (err) => {
        this.error.set('No se ha podido guardar el usuario.');
        this.saving.set(false);
        console.error('Error al guardar usuario', err);
      },
    });
  }
}


