use crate::models::user::User;
use sqlx::SqlitePool;

pub async fn insert_user(
    pool: &SqlitePool,
    username: &str,
    password: &str,
) -> Result<User, sqlx::Error> {
    let result = sqlx::query_as!(
        User,
        "INSERT INTO users (username, password) VALUES (?, ?) RETURNING id, username, password",
        username,
        password
    )
    .fetch_one(pool)
    .await?;

    Ok(result)
}
