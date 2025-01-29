import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-register',
  standalone: true,
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss'],
  imports: [FormsModule], // 👈 Ajout de FormsModule ici
})
export class RegisterComponent {
  username = '';
  email = '';
  password = '';
  message = '';

  constructor(private userService: UserService) {}

  register() {
    this.userService.register(this.username, this.email, this.password).subscribe(
      response => {
        this.message = 'Inscription réussie ! Vous pouvez vous connecter.';
      },
      error => {
        this.message = 'Erreur lors de l’inscription.';
        console.error(error);
      }
    );
  }
}
