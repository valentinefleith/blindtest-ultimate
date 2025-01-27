use axum::Router;

mod users;

pub fn create_router() -> Router {
    Router::new().nest("/api/users", users::routes())
}
