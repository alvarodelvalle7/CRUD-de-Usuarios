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
