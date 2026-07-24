import { Routes } from '@angular/router';

// Importamos las clases UserList y UserForm
import { UserList } from './users/user-list/user-list';
import { UserForm } from './users/user-form/user-form';

export const routes: Routes = [
  // Significa que si no hay nada en el path, redirgirá a users si la ruta está vacía
  { path: '', redirectTo: 'users', pathMatch: 'full' },
  // Referenciamos las rutas para users
  { path: 'users', component: UserList }, // Lista de usuarios
  { path: 'users/new', component: UserForm }, // Formulario de usuarios nuevos
  { path: 'users/:id/edit', component: UserForm }, // Formulario para editar usuarios
];
