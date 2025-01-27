use sqlx::SqlitePool;
use std::sync::Arc;

pub async fn init_db(database_url: &str) -> Arc<SqlitePool> {
    let pool = SqlitePool::connect(database_url).await.unwrap();
    Arc::new(pool)
}
