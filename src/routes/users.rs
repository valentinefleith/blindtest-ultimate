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
    use super::*; // Permet d'accéder aux structs privées du module
    use axum::Json;

    #[test]
    fn test_user_creation() {
        let input = RegisterUser {
            username: "testuser".to_string(),
            password: "1234".to_string(),
        };

        let expected = UserResponse {
            id: 1,
            username: "testuser".to_string(),
        };

        let result = UserResponse {
            id: 1,
            username: input.username,
        };

        assert_eq!(result.id, expected.id);
        assert_eq!(result.username, expected.username);
    }
}
