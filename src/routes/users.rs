#![allow(dead_code, unused_imports, unused_variables)]

use axum::{routing::post, Extension, Json, Router};
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::sync::Arc;

#[derive(Deserialize)]
struct RegisterUser {
    username: String,
    password: String,
}

#[derive(Serialize)]
struct UserResponse {
    id: u32,
    username: String,
}

async fn register(
    Extension(pool): Extension<Arc<SqlitePool>>,
    Json(payload): Json<RegisterUser>,
) -> Result<Json<UserResponse>, String> {
    let result = sqlx::query!(
        "INSERT INTO users (username, password) VALUES (?, ?) RETURNING id",
        payload.username,
        payload.password
    )
    .fetch_one(&*pool)
    .await;

    match result {
        Ok(record) => Ok(Json(UserResponse {
            id: record.id as u32,
            username: payload.username,
        })),
        Err(_) => Err("Failed to create user".to_string()),
    }
}

// Fonction pour enregistrer les routes utilisateurs
pub fn routes() -> Router {
    Router::new().route("/register", post(register))
}

#[cfg(test)]
mod tests {
    use super::*; // Accède aux fonctions et structures privées du module
    use axum::{extract::Extension, Json};
    use sqlx::{sqlite::SqlitePoolOptions, SqlitePool};
    use std::sync::Arc;
    use tokio;

    #[tokio::test]
    async fn test_user_creation() {
        // Crée une base de données temporaire en mémoire
        let pool = SqlitePoolOptions::new()
            .connect("sqlite::memory:")
            .await
            .expect("Failed to connect to database");

        // Exécute la migration pour créer la table `users`
        sqlx::migrate!().run(&pool).await.expect("Migration failed");

        let test_user = RegisterUser {
            username: "testuser".to_string(),
            password: "securepassword".to_string(),
        };

        let response = register(Extension(Arc::new(pool.clone())), Json(test_user)).await;

        assert!(response.is_ok());
        let user_response = response.unwrap().0; // .0 pour extraire Json<UserResponse>
        assert_eq!(user_response.username, "testuser");

        let user_in_db = sqlx::query!("SELECT username FROM users WHERE id = ?", user_response.id)
            .fetch_one(&pool)
            .await
            .expect("User not found in database");

        assert_eq!(user_in_db.username, "testuser");
    }
}
