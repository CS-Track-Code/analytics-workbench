from application import create_app
import config


app = create_app()

if __name__ == "__main__":
    app.run(host=config.host_ip_address, port=config.host_port)
