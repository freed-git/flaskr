# flaskr

```
python3 -m venv ./venv

source ./venv/bin/activate

python3 -m pip install -r requirements.txt


# init database
FLASK_APP=flaskr FLASK_ENV=development flask init-db

# run flask in development mode
FLASK_APP=flaskr FLASK_ENV=development flask run

# create namespace
kubectl create ns flaskr

# imagePullSecret
ACCESS_TOKEN="..."

kubectl create secret docker-registry regcred \
    --docker-server=https://index.docker.io/v1/ \
    --docker-username=deepvoid \
    --docker-password=$ACCESS_TOKEN \
    -n flaskr

# verify secret
kubectl get secret -n flaskr

# deploy app
kubectl apply -f manifests/ -n flaskr

# verify ingress
kubectl get ing -n flaskr

# verify tls certificate
kubectl get cert -n flaskr
```

```
waitress-serve --listen=127.0.0.1:8080 --call flaskr:create_app


docker run -p 5000:5000 -v instance:/app/instance -e FLASK_APP=flaskr -e FLASK_ENV=development deepvoid/flaskr -- run --host=0.0.0.0
```

```
https://open-telemetry.github.io/opentelemetry-python/getting-started.html
```


https://opentelemetry.io/docs/instrumentation/python/getting-started/




https://opentelemetry.io/docs/instrumentation/python/getting-started/#configure-exporters-to-emit-spans-elsewhere

docker run -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one

http://localhost:16686