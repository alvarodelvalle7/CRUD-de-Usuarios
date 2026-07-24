# PASOS FRONTEND USER CRUD APP CON ANGULAR
---

## 📦 Instalación del proyecto

Comando a ejecutar:
```
ng new frontend --routing --style=tailwind --zoneless --ssr=false --package-manager=pnpm --skip-git --ai-config=none --defaults
```
Desglosamos que hace cada cosa:

- ``ng new``: Crea el proyecto.
- ``frontend``: Nombre de la carpeta raíz de los ficheros generados.
- ``--routing``: Permite tener varias "páginas" dentro de la app (listado, crear, editar) y moverte entre ellas sin recargar.
- ``--style=tailwind``: Instala **TailwindCSS** en nuestro proyecto.
- ``--zoneless``: la app se entera de refrescar la pantalla de forma más directa y moderna, sin un mecanismo antiguo que vigilaba todo por detrás.
- ``--ssr=false``: La página se genera en tu navegador, no en el servidor antes de enviarla.
- ``--package-manager=pnpm``: Usa pnpm para instalar las dependencias.
- ``--skip-git``: No inicializa un repositorio **Git** dentro del frontend.
- ``--ai-confing=none``: No genera ficheros de configuración para asistentes de **IA**.
- ``--defaults``: Usa las opciones normales de Angular sin preguntarte una por una.

## 🗂️ Estructura del proyecto generado

### Raíz del proyecto

| Fichero/carpeta | Qué es | Para qué sirve |
|-----------------|---------|----------------|
| `angular.json` | Configuración del workspace Angular | Le dice al CLI cómo compilar (`build`), servir (`serve`) y testear (`test`) tu proyecto. Aquí está registrado que usas `pnpm`. |
| `package.json` | Manifiesto del proyecto Node | Lista dependencias (`@angular/*`, `tailwindcss`...) y scripts (`pnpm start`, `pnpm build`, `pnpm test`). |
| `pnpm-lock.yaml` | Fichero de bloqueo de versiones | Fija exactamente qué versión de cada paquete (y sus dependencias internas) se instaló, para que la instalación sea reproducible en otra máquina. |
| `tsconfig.json` / `tsconfig.app.json` / `tsconfig.spec.json` | Configuración de TypeScript | El primero son las reglas base (strict mode incluido); el `.app` es para el código de la app; el `.spec` para los tests. |
| `.postcssrc.json` | Configuración de PostCSS | Activa el plugin `@tailwindcss/postcss`, que es lo que hace que las clases de Tailwind se conviertan en CSS real al compilar. |
| `.editorconfig` / `.prettierrc` | Estilo de código | Normas de formato (indentación, comillas...) para que el editor y Prettier formateen igual siempre. |
| `.gitignore` | Lista de exclusión de Git | Qué no subir a un repositorio (p. ej. `node_modules`), por si en el futuro inicializamos Git. |
| `node_modules/` | Dependencias instaladas | Todo el código de las librerías descargadas por `pnpm`. No se toca a mano nunca. |
| `.vscode/` | Configuración de VS Code | Tareas y ajustes recomendados para este proyecto en el editor. |

### Carpeta /src

| Fichero | Qué es | Para qué sirve |
|---------|---------|----------------|
| `index.html` | HTML raíz de la aplicación | Contiene `<app-root></app-root>`, la etiqueta donde Angular "engancha" tu app entera. Es lo único que carga el navegador al principio. |
| `main.ts` | Punto de arranque de la app | Llama a `bootstrapApplication(App, appConfig)`; arranca Angular usando tu componente raíz (`App`) y su configuración (`appConfig`). |
| `styles.css` | Estilos globales | Solo tiene `@import "tailwindcss";` — es lo que activa Tailwind en toda la app. |
| `app/app.ts` | Componente raíz (`App`) | El componente principal. Fíjate que usa `signal('frontend')` para el título; es tu primer contacto con Signals, la forma moderna de manejar estado reactivo en Angular. |
| `app/app.html` | Plantilla del componente raíz | El HTML que se ve al arrancar (ahora mismo es la página de bienvenida por defecto del CLI; la sustituiremos por nuestro layout). |
| `app/app.css` | Estilos propios del componente raíz | Vacío por ahora; con Tailwind normalmente no hace falta casi nunca escribir CSS aquí, se usan clases directamente en el HTML. |
| `app/app.config.ts` | Configuración de la aplicación | Aquí se registran los "providers" globales: `provideRouter(routes)` (activa el router) y `provideBrowserGlobalErrorListeners()` (captura errores no controlados). Este es el fichero donde añadiremos `provideHttpClient()` en el punto 7, para poder hablar con tu API. |
| `app/app.routes.ts` | Definición de rutas | Ahora mismo está vacío (`routes: Routes = []`); aquí añadiremos las rutas del listado, crear y editar usuario. |
| `app/app.spec.ts` | Test del componente raíz | Prueba automática generada por defecto, usa Vitest. |

## 📂 Estructura de carpetas del proyecto

Creamos la estructura del proyecto con los siguientes comandos:

1. `ng generate component users/user-list`: Componente de la lista de usuarios.
2. `ng generate component users/user-form`: Componente del formulario.
3. `ng generate service users/user --type=service --force`: Servicio con las llamadas HTTP. Lo generamos así para que no haya dos cosas llamadas Users en la misma carpeta: La clase servicio y la interfaz del modelo.
4. `ng generate interface users/user model`: El fichero de interfaces TypeScript.

La estructura del proyecto quedaría así:

```
src/app/
├── users/
│   ├── user-list/
│   │   ├── user-list.ts
│   │   ├── user-list.html
│   │   ├── user-list.css
│   │   └── user-list.spec.ts
│   ├── user-form/
│   │   ├── user-form.ts
│   │   ├── user-form.html
│   │   ├── user-form.css
│   │   └── user-form.spec.ts
│   ├── user.service.ts      → las llamadas HTTP a tu API (GET/POST/PUT/DELETE)
│   └── user.model.ts        → las interfaces TypeScript (User, UserCreate, UserUpdate)
├── app.ts
├── app.html
├── app.css
├── app.config.ts
└── app.routes.ts
```

## 🔗 Rutas del proyecto 'app.routes.ts'

Este archivo se encargará del enrutamiento de la página.

```
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
```

## 👤 Definición de los modelos User 'user.model.ts'

```
// Clase userbase con campos comunes para crear/actualizar y leer un usuario.
export interface UserBase {
  name: string;
  age: number;
  height: number;
  weight: number;
  city?: string;
  is_admin: boolean;
}

// Usuario que extiende de UserBase y lo utilizaremos para listar un usuario de la BD.
export interface User extends UserBase{
  id: number;
}

// Al no añadir ningún campo nuevo con respecto a UserBase es la forma más directa de expresarlo.
export type UserCreate = UserBase;
export type UserUpdate = UserBase;
```

## 📡 Acceso a la API

### Activamos 'HttpClient' para conectarnos a nuestra API.

```
providers: [
  provideBrowserGlobalErrorListeners(),
  provideRouter(routes),
  provideHttpClient() // Añadimos httpClient para comunicarnos con el backend
  ]
```

### En el archivo 'user.service.ts' nos conectamos con el backend para poder hacer peticiones HTTP.

```
import { inject, Service } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User, UserCreate, UserUpdate } from './user.model';
import { environment } from '../../environments/environment';

// Variable constante que contiene la URL de nuestra api.
const API_URL = `${environment.apiUrl}/users`;

@Service()
export class UserService {

    // Forma moderna de pedir a Angular la dependencia de HttpClient
    private http = inject(HttpClient)

	  // Peticiones get
    getUsers(): Observable<User[]>{
        return this.http.get<User[]>(API_URL)
    }

    getUser(id: number): Observable<User>{
        return this.http.get<User>(`${API_URL}/${id}`)
    }

	  // Petición post
    createUser(user: UserCreate): Observable<User>{
        return this.http.post<User>(API_URL, user)
    }

	  // Petición put
  	updateUser(id: number, user: UserUpdate): Observable<User>{
		return this.http.put<User>(`${API_URL}/${id}`, user)
    }

    // Petición delete
    deleteUser(id: number): Observable<User>{
      	return this.http.delete<User>(`${API_URL}/${id}`)
    }
}

// Un Observable es como un canal de tele: no pasa nada hasta que te suscribes (.subscribe());
// en ese momento se dispara la petición HTTP y, cuando llega la respuesta, te la entrega.
```

### Antes de editar el archivo 'user.service.ts', debemos añadir la variable de entorno en un archivo 'environment.ts'.

Creamos un archivo de variables de entorno llamado **environment.ts** con el siguiente comando:``ng generates environments``, este generará un archivo de variables en producción y otro de desarrollo.

1. Archivo de desarrollo **environment.development.ts**:

```
// Le decimos que es de desarrollo y le pasamos el url de la API.
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

2. Archivo de producción **environment.ts**:
```
export const environment = {
  production: true,
  apiUrl: 'http://localhost:8000/api/v1' // más adelante, con el despliegue, aquí iría la URL real del backend en producción
};
```

## 🧩 Creación de tabla de usuarios

### Archivo 'user-list.ts'

Se encarga de recoger los usuarios de la base de datos llamando al backend por medio del **UserService**.

```
import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { UserService } from '../user.service';
import { User } from '../user.model';

@Component({
	selector: 'app-user-list',
	imports: [RouterLink], // Para poder usar routerLink en la plantilla ("+ Nuevo usuario", "Editar")
	templateUrl: './user-list.html',
	styleUrl: './user-list.css',
})
// implements OnInit le dice a la clase que hay que tener un método llamado ngOnInit
export class UserList implements OnInit{

	// Variable privada que inyecta la clase UserService que sirve para usar los métodos Http
	private userService = inject(UserService)

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
```

### Archivo 'user-list.html'

Se encarga de hacer la etiqueta para hacer la tabla con usuarios.

```
<a  routerLink="/users/new">+ Nuevo usuario</a>

<!-- @if / @else if / @else es la versión moderna del antiguo *ngIf, y encadena varias condiciones -->
@if (loading()) {
  <!-- Mientras loading() sea true, no mostramos la tabla, solo este aviso -->
  <p>Cargando usuarios...</p>
} @else if (error()) {
  <!-- Si loading ya terminó pero hay un error guardado, mostramos ese mensaje -->
  <p>{{ error() }}</p>
} @else {
  <!-- Si no está cargando y no hay error, ya podemos mostrar la tabla con normalidad -->
  <table>
    <thead>
      <tr>
        <th>Nombre</th>
        <th>Edad</th>
        <th>Altura</th>
        <th>Peso</th>
        <th>Ciudad</th>
        <th>Admin</th>
        <th>Opciones</th>
      </tr>
    </thead>
    <tbody>
      @for (user of users(); track user.id) {
        <tr>
          <td>{{ user.name }}</td>
          <td>{{ user.age }}</td>
          <td>{{ user.height }}</td>
          <td>{{ user.weight }}</td>
          <td>{{ user.city }}</td>
          <td>{{ user.is_admin ? 'Sí' : 'No' }}</td>
          <td>
            <a [routerLink]="['/users', user.id, 'edit']">Editar</a>
            <button (click)="onDelete(user.id)">Borrar</button>
          </td>
        </tr>
      } @empty {
        <tr><td colspan="7">No hay usuarios guardados todavía</td></tr>
      }
    </tbody>
  </table>
}
```

## 🧩 Creación del formulario para crear un usuario nuevo o editarlo.

### Archivo 'user-form.ts'

Archivo que se encarga de recoger los datos del formulario y crear un usuario o editar un usuario.

```
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
```

### Archivo 'user-form.html

Se encarga de hacer la etiqueta para hacer el formulario de creación o de edición.

```
<div class="flex flex-col gap-4">
  <a class="font-medium text-gray-400 hover:text-white" routerLink="/users">← Volver al listado</a>

  <form [formGroup]="form" (ngSubmit)="onSubmit()" class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full rounded-sm bg-gray-950 border border-gray-700 text-sm uppercase tracking wide p-4">
    <label class="flex flex-col gap-2 font-bold">
      Nombre
      <input class="border border-gray-600 bg-gray-900 rounded-sm px-4 py-2 font-normal focus:border-amber-500 focus:outline-none" type="text" formControlName="name" placeholder="Introduce tu nombre y apellidos" />
    </label>

    <label class="flex flex-col gap-2 font-bold">
      Edad
      <input class="border border-gray-600 bg-gray-900 rounded-sm px-4 py-2 font-normal focus:border-amber-500 focus:outline-none" type="number" formControlName="age" placeholder="Introduce tu edad" />
    </label>

    <label class="flex flex-col gap-2 font-bold">
      Altura
      <input class="border border-gray-600 bg-gray-900 rounded-sm px-4 py-2 font-normal focus:border-amber-500 focus:outline-none" type="number" step="0.01" formControlName="height" placeholder="Introduce tu altura" />
    </label>

    <label class="flex flex-col gap-2 font-bold">
      Peso
      <input class="border border-gray-600 bg-gray-900 rounded-sm px-4 py-2 font-normal focus:border-amber-500 focus:outline-none" type="number" step="0.01" formControlName="weight" placeholder="Introduce tu peso" />
    </label>

    <label class="flex flex-col gap-2 font-bold">
      Ciudad
      <input class="border border-gray-600 bg-gray-900 rounded-sm px-4 py-2 font-normal focus:border-amber-500 focus:outline-none" type="text" formControlName="city" placeholder="Introduce tu ciudad de residencia" />
    </label>

    <label class="flex flex-col gap-2 items-start font-bold tracking wide">
      ¿Administrador?
      <input class="w-4 h-4 accent-amber-500 cursor-pointer" type="checkbox" formControlName="is_admin" />
    </label>

    <!-- Si hay un mensaje de error guardado, lo mostramos justo antes del botón -->
    @if (error()) {
      <p>{{ error() }}</p>
    }

    <!-- El botón se desactiva si el formulario no es válido O si ya se está guardando -->
    <!-- Este botón es reciclable-->
    <app-button type="submit" [disabled]="form.invalid || saving()">
      {{ saving() ? 'Guardando...' : (userId ? 'Actualizar' : 'Guardar') }}
    </app-button>

  </form>
</div>
```

## 🧩 Creación de botón reutilizable

1. Generación de la carpeta shared y de la carpeta button: ``ng generate component shared/button``.

2. Creación de archivo 'button-variants.ts' para definir el diseño de nuestros botones(la exportaremos):
```
// Diseños de botones
export type ButtonVariant = 'primary' | 'secondary' | 'danger';

// Creamos una función para definir nuestro diseño y la exportaremos
export function buttonVariantClasses(variant: ButtonVariant): string {
  switch (variant) {
    case 'primary': return 'bg-amber-500 text-white hover:bg-amber-600 hover:text-gray-100 ';
    case 'secondary': return 'border border-amber-500 text-amber-500 hover:bg-amber-500 hover:text-white';
    case 'danger': return 'bg-red-600 text-white hover:bg-red-700 hover:text-gray-100 ';
  }
}
```

3. Creación de la lógica del botón en el archivo **button.ts**:
```
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
```

4. Creación de la etiqueta y el resto de estilos del botón en **button.html**:
```
<button
  [type]="type()"
  [disabled]="disabled()"
  [class]="'px-4 py-2 rounded font-medium cursor-pointer transition disabled:opacity-50 disabled:cursor-not-allowed ' + variantClasses"
  (click)="appClick.emit()"
>
  <ng-content />
</button>
```

5. Añadimos los botones a los layouts:

- **user-form.html:**
  - Botón de redirección a la lista de usuario:
  ```
  <a class="font-medium text-gray-400 hover:text-white" routerLink="/users">← Volver al listado</a>
  ```
  - Botón de guardar datos o actualizar:
  ```
  <!-- El botón se desactiva si el formulario no es válido O si ya se está guardando -->
  <!-- Este botón es reciclable-->
  <app-button type="submit" [disabled]="form.invalid || saving()">
    {{ saving() ? 'Guardando...' : (userId ? 'Actualizar' : 'Guardar') }}
  </app-button>
  ```

- **user-list.html:**
  - Botón de redirección a formulario de usuario:
  ```
  <a routerLink="/users/new" [class]="newUserLinkClasses">+ Nuevo usuario</a>
  ```
  - Botón de editar:
  ```
  <a [routerLink]="['/users', user.id, 'edit']" [class]="editLinkClasses">Editar</a>
  ```
  - Botón de borrar:
  ```
  <app-button variant="danger" (appClick)="onDelete(user.id)">Borrar</app-button>
  ```

## Diseño con TailwindCSS

### 🎨 Colores utilizados

| Uso | Clase | Dónde |
|---|---|---|
| Fondo general de la app | `bg-gray-950` | `<body>`, `<header>` (sticky) |
| Texto general | `text-white` | `<body>` |
| Fondo de la cabecera de tabla | `bg-gray-900` | `thead` |
| Fondo de los inputs | `bg-gray-900` | inputs del formulario |
| Bordes generales | `border-gray-700` | tabla (`tr`), inputs, contorno del `<form>` |
| Borde separador del header | `border-gray-800` | `<header>` |
| Hover de fila de tabla | `hover:bg-gray-800` | `tr` del `@for` |
| Color de marca (primario) | `amber-500` / `hover:amber-600` | botón "Guardar", enlace "+ Nuevo usuario", focus de inputs, checkbox (`accent-amber-500`) |
| Color de peligro | `red-600` / `hover:red-700` | botón "Borrar" |
| Texto secundario/enlaces discretos | `text-gray-400` / `hover:text-white` | enlace "← Volver al listado" |

### 📏 Paddings / espaciados

| Clase | Uso |
|---|---|
| `px-4 py-2` | celdas de tabla (`th`/`td`), inputs del formulario, botones |
| `py-8` | `<header>`, `<main>` |
| `p-4` | contenedor del `<form>` |
| `px-4` | `<main>` (margen lateral en móvil) |
| `gap-2` | dentro de cada `<label>` (texto + input) |
| `gap-4` | contenedor general de `user-list` y `user-form`, y entre columnas del `grid` del form |
| `gap-6` | (si lo usaste) entre bloques más grandes |

### ✅ Buenas prácticas aplicadas

- **`lang="es"`** en `<html>` — el idioma real del contenido, para accesibilidad y SEO.
- **HTML semántico**: `<header>`, `<main>`, un único `<h1>` por página.
- **`min-h-screen`** en `<body>` — el fondo cubre toda la pantalla aunque haya poco contenido.
- **`sticky top-0 z-10`** en `<header>` — necesita su propio `bg-gray-950` porque, al flotar, si no tuviera fondo propio se vería el contenido transparentándose por detrás.
- **`rounded-sm` en el `<div>` que envuelve la tabla, no en el `<table>`**: Tailwind aplica `border-collapse: collapse` a las tablas por defecto, lo que anula el redondeo de esquinas del propio `<table>`.
- **`items-start` en el `<label>` del checkbox**: por defecto (`align-items: stretch`), el checkbox se estira y se ve "centrado" (la caja se estira, el cuadradito se pinta en medio). `items-start` lo evita.
- **`self-start` en el enlace "+ Nuevo usuario"**: dentro de un contenedor `flex flex-col`, todos los hijos se estiran a todo el ancho por defecto; `self-start` saca a ese elemento en concreto de esa regla.
- **`gap` en el contenedor en vez de márgenes sueltos** (`mb-`, `mt-`) en cada hijo: evita el problema de que los márgenes verticales no funcionan en elementos `inline` (como un `<a>`) sin añadir además `inline-block`/`block`.
- **`accent-amber-500`** en el checkbox: recolorea el control nativo sin tener que reconstruirlo con CSS (mejor que `appearance-none` para este caso).
- **`focus:border-amber-500 focus:outline-none`** en los inputs: sustituye el contorno azul feo del navegador por un borde de color propio, coherente con la marca.
- **Reutilización de estilos**: la función `buttonVariantClasses()` centraliza los colores de cada variante de botón, y la usan tanto `<app-button>` (botones reales) como los `<a routerLink>` (enlaces que necesitan parecer botones pero no pueden serlo).

### 📱 Responsive

| Clase | Efecto |
|---|---|
| `text-xl sm:text-2xl md:text-4xl` | el `<h1>` crece de tamaño según el ancho de pantalla (móvil → tablet → escritorio) |
| `grid-cols-1 md:grid-cols-2` | el formulario pasa de 1 columna (móvil) a 2 columnas (`md:` en adelante) |
| `max-w-5xl mx-auto` | el contenido de `<main>` nunca crece más de ese ancho máximo, y se centra en pantallas grandes |
| `overflow-x-auto` | en pantallas estrechas, la tabla permite scroll horizontal propio en vez de romper el layout general |

## 🕳️ Estado vacío del listado

Cuando no hay ningún usuario guardado, en vez de dejar una fila suelta y mal alineada dentro de la tabla de siempre, se comprueba `users().length === 0` y se pinta una tabla con un único mensaje centrado en su lugar:

```
@if (users().length === 0) {
  <div class="overflow-x-auto rounded-sm">
    <table class="w-full">
      <thead class="bg-gray-900 text-sm uppercase tracking wide">
        <tr class="border border-gray-700">
          <th class="px-4 py-2 text-left">Nombre</th>
          <th class="px-4 py-2 text-left">Edad</th>
          <th class="px-4 py-2 text-left">Altura</th>
          <th class="px-4 py-2 text-left">Peso</th>
          <th class="px-4 py-2 text-left">Ciudad</th>
          <th class="px-4 py-2 text-left">Admin</th>
          <th class="px-4 py-2 text-left">Opciones</th>
        </tr>
      </thead>
      <tbody>
        <tr class="border border-gray-700">
          <td colspan="7" class="p-16 text-center">No hay usuarios cargados todavía...</td>
        </tr>
      </tbody>
    </table>
  </div>
} @else {
  <!-- la tabla con los usuarios, exactamente igual que antes -->
}
```

- **`users().length === 0`**: como `users` es un signal, se lee con paréntesis; `.length` sobre el array que devuelve dice si está vacío.
- **`colspan="7"`**: imprescindible. Sin este atributo, la celda del mensaje solo ocupa el ancho de una columna (la primera), así que `text-center` centra el texto dentro de ese hueco estrecho, no en el ancho real de la tabla — visualmente parece pegado a la izquierda aunque el CSS de centrado esté bien puesto.
- **`p-16 text-center`**: mucho espaciado y texto centrado, para que se note que es un aviso, no una fila de datos más.

