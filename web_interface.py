from click_web import create_click_web_app
import k8s_ssl_updater

app = create_click_web_app(k8s_ssl_updater, k8s_ssl_updater.cli)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
