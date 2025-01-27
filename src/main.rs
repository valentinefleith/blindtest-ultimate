use std::net::SocketAddr;
use tokio::net::TcpListener;

mod routes;

#[tokio::main]
async fn main() {
    let app = routes::create_router();

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    let tcp = TcpListener::bind(&addr).await.unwrap();
    println!("Serveur en cours d'exécution sur http://{}", addr);
    axum::serve(tcp, app).await.unwrap();
}
