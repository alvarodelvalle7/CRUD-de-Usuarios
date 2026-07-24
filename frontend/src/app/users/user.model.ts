
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

// Al no añadir ningún campo nuevo con respecto a UserBase es la forma más directa de epresarlo.
export type UserCreate = UserBase;
export type UserUpdate = UserBase;

