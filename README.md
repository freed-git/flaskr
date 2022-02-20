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

docker run --rm -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one

http://localhost:16686/


https://anecdotes.dev/opentelemetry-observability-as-a-standard-8c0c8bd231f0



https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md





pip install opentelemetry-instrumentation
opentelemetry-bootstrap --action=install


https://opentelemetry.lightstep.com/python/


LOKI filter
{namespace="flaskr"} |~ `trace_id=\w+` != "trace_id=0"

{namespace="flaskr"} |~ "trace_id=[^0]+"


<!-- apiVersion: 1
 
deleteDatasources:
  - name: Prometheus
  - name: Tempo
  - name: Loki
 
datasources:
- name: Prometheus
  type: prometheus
  access: proxy
  orgId: 1
  url: http://prometheus:9090
  basicAuth: false
  isDefault: false
  version: 1
  editable: false
- name: Tempo
  type: tempo
  access: proxy
  orgId: 1
  url: http://tempo-query:16686
  basicAuth: false
  isDefault: false
  version: 1
  editable: false
  apiVersion: 1
  uid: tempo
 
- name: Loki
  type: loki
  access: proxy
  orgId: 1
  url: http://loki:3100
  basicAuth: false
  isDefault: false
  version: 1
  editable: false
  apiVersion: 1
  jsonData:
    derivedFields:
      - datasourceUid: tempo
        matcherRegex: \[.+,(.+),.+\]
        name: TraceID
        url: $${__value.raw} -->


# python logging
https://everythingtech.dev/2021/03/python-logging-with-json-formatter/

gunicorn \
--bind 0.0.0.0:5000 "flaskr:create_app()" \
--access-logfile - \
--error-logfile - \
--capture-output \
--access-logformat  "{'remote_ip':'%(h)s','request_id':'%({X-Request-Id}i)s','response_code':'%(s)s','request_method':'%(m)s','request_path':'%(U)s','request_querystring':'%(q)s','request_timetaken':'%(D)s','response_length':'%(B)s'}"



127.0.0.1 - - [16/Feb/2022:13:25:56 -0500] "GET /static/style.css HTTP/1.1" 304 0 "http://localhost:5000/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"

{'remote_ip':'127.0.0.1','request_id':'-','response_code':'304','request_method':'GET','request_path':'/static/style.css','request_querystring':'','request_timetaken':'1872','response_length':'0'}


{namespace="flaskr"} |= "trace_id=b925b9c2bef46051747062bb365b986e"

{namespace="flaskr"} |~ "trace_id=[^0]"

https://dev.to/camptocamp-ops/implement-prometheus-metrics-in-a-flask-application-p18


# WORKS!!! NO EXEMPLAR

# HELP blog_total blog count
# TYPE blog_total counter
blog_total{endpoint="/",method="GET"} 1.0
# HELP blog_created blog count
# TYPE blog_created gauge
blog_created{endpoint="/",method="GET"} 1.6451326524687583e+09



# BAD!!!

# HELP blog blog count
# TYPE blog counter
blog_total{endpoint="/",method="GET"} 1.0 # {traceID="56334540713124196021878971227834585574"} 1.0 1645132870.0607898
blog_created{endpoint="/",method="GET"} 1.6451328700607107e+09
# EOF


curl -s http://dc.host.tld:9116/metrics | ./promtool check metrics


https://www.robustperception.io/invalid-is-not-a-valid-start-token-and-other-scrape-errors

wget https://github.com/prometheus/prometheus/releases/download/v2.33.3/prometheus-2.33.3.linux-amd64.tar.gz

cd prometheus-2.33.3.linux-amd64/

curl -s https://flaskr.eks01.gameloft.org/metrics | ./promtool check metrics

curl -s -H 'Accept: application/openmetrics-text' https://flaskr.eks01.gameloft.org/metrics | ./promtool check metrics

https://sysdig.com/blog/openmetrics-is-prometheus-unbound/


curl -s -H 'Accept: application/openmetrics-text' https://flaskr.eks01.gameloft.org/metrics | python3 -c 'import sys; from prometheus_client.openmetrics import parser; list(parser.text_string_to_metric_families(sys.stdin.buffer.read().decode("utf-8")))'

https://prometheus.io/docs/instrumenting/exposition_formats/




curl -s -H 'Accept: application/openmetrics-text' http://172.22.191.48:5000/metrics