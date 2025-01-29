import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  imports: [FormsModule], // 👈 Ajout de FormsModule ici
})
export class LoginComponent {
  username = '';
  password = '';
  message = '';

  constructor(private userService: UserService) {}

  login() {
    this.userService.login(this.username, this.password).subscribe(
      response => {
        localStorage.setItem('token', response.access_token);
        this.message = 'Connexion réussie !';
      },
      error => {
        this.message = 'Email ou mot de passe incorrect.';
        console.error(error);
      }
    );
  }
}
